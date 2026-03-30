"""
Doculink Daemon - Real-time Documentation Linker

The revolutionary core: A daemon that analyzes code context and surfaces
relevant documentation snippets inline, automatically updating as code changes.
"""

import ast
import os
import re
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Set, Tuple
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileModifiedEvent, FileCreatedEvent
import asttokens


@dataclass
class DocLink:
    """Represents a documentation link for a code element."""
    name: str
    doc_type: str  # 'function', 'class', 'module', 'method', 'attribute'
    source: str  # 'stdlib', 'third_party', 'local'
    description: str
    url: Optional[str] = None
    snippet: Optional[str] = None
    confidence: float = 0.5


@dataclass
class CodeContext:
    """Represents the context around a code element."""
    file_path: str
    line_number: int
    column: int
    name: str
    full_name: str
    doc_links: List[DocLink] = field(default_factory=list)


class DocumentationRegistry:
    """
    Registry of documentation for stdlib and common packages.
    Extensible for custom packages.
    """
    
    def __init__(self):
        self.stdlib_docs: Dict[str, Dict[str, str]] = {}
        self.third_party_docs: Dict[str, Dict[str, str]] = {}
        self._init_stdlib_docs()
    
    def _init_stdlib_docs(self):
        """Initialize basic stdlib documentation."""
        
        # Common built-in functions
        self.stdlib_docs['builtins'] = {
            'print': 'Print values to the standard output.',
            'len': 'Return the length of an object.',
            'range': 'Generate a sequence of numbers.',
            'enumerate': 'Add a counter to an iterable.',
            'zip': 'Aggregate elements from multiple iterables.',
            'map': 'Apply a function to every item in an iterable.',
            'filter': 'Filter items from an iterable.',
            'sum': 'Sum items from an iterable.',
            'min': 'Return the smallest item in an iterable.',
            'max': 'Return the largest item in an iterable.',
        }
        
        # Common modules
        self.stdlib_docs['os'] = {
            'path.exists': 'Return True if path refers to an existing path.',
            'path.join': 'Join one or more path components.',
            'path.basename': 'Return the final component of the path.',
            'path.dirname': 'Return the directory name of pathname.',
            'getcwd': 'Return the current working directory.',
            'listdir': 'Return a list containing the names of the entries.',
        }
        
        self.stdlib_docs['sys'] = {
            'argv': 'Command line arguments passed to the script.',
            'path': 'The module search path.',
            'exit': 'Exit the interpreter.',
            'version': 'Version information string.',
            'version_info': 'Version information as a 5-tuple.',
        }
        
        self.stdlib_docs['json'] = {
            'loads': 'Parse JSON string to Python object.',
            'dumps': 'Serialize Python object to JSON string.',
            'load': 'Parse JSON file to Python object.',
            'dump': 'Serialize Python object to JSON file.',
        }
        
        self.stdlib_docs['re'] = {
            'match': 'Search for pattern at beginning of string.',
            'search': 'Search for pattern anywhere in string.',
            'findall': 'Find all occurrences of pattern.',
            'sub': 'Replace occurrences of pattern with replacement.',
            'compile': 'Compile a regular expression pattern.',
        }
        
        self.stdlib_docs['datetime'] = {
            'datetime': 'Represent a date and time.',
            'date': 'Represent a date.',
            'time': 'Represent a time.',
            'timedelta': 'Represent a duration.',
            'strptime': 'Parse a string to datetime.',
        }
        
        self.stdlib_docs['collections'] = {
            'defaultdict': 'Dictionary with default value for missing keys.',
            'Counter': 'Dictionary subclass for counting hashable objects.',
            'deque': 'List-like container with fast appends/pops.',
            'namedtuple': 'Factory function for tuple subclasses.',
            'OrderedDict': 'Dictionary that remembers insertion order.',
        }
        
        self.stdlib_docs['itertools'] = {
            'chain': 'Chain multiple iterables together.',
            'compress': 'Select elements based on selector.',
            'cycle': 'Cycle through elements indefinitely.',
            'islice': 'Slice an iterator.',
            'groupby': 'Group consecutive elements.',
        }
        
        self.stdlib_docs['functools'] = {
            'lru_cache': 'Cache function calls with LRU eviction.',
            'partial': 'Create a partial function.',
            'reduce': 'Apply function cumulatively to items.',
            'wraps': 'Update wrapper to resemble wrapped function.',
        }
        
        self.stdlib_docs['contextlib'] = {
            'contextmanager': 'Context manager decorator.',
            'closing': 'Context manager that calls close().',
            'suppress': 'Context manager that suppresses exceptions.',
            'redirect_stdout': 'Redirect stdout to a file-like object.',
        }
    
    def get_documentation(self, module: str, name: str) -> Optional[str]:
        """Get documentation for a name in a module."""
        if module in self.stdlib_docs:
            return self.stdlib_docs[module].get(name)
        return None
    
    def suggest_docs(self, name: str, context: str = "") -> List[DocLink]:
        """Suggest documentation links based on name and context."""
        suggestions = []
        
        # Check stdlib
        for module, docs in self.stdlib_docs.items():
            if name in docs:
                suggestions.append(DocLink(
                    name=name,
                    doc_type=self._infer_doc_type(name),
                    source='stdlib',
                    description=docs[name],
                    url=f"https://docs.python.org/3/library/{module}.html#{name}",
                    confidence=0.9
                ))
        
        # Suggest related stdlib items
        if suggestions:
            for module, docs in self.stdlib_docs.items():
                for other_name, other_desc in docs.items():
                    if other_name != name and self._is_related(name, other_name):
                        suggestions.append(DocLink(
                            name=other_name,
                            doc_type=self._infer_doc_type(other_name),
                            source='stdlib',
                            description=other_desc,
                            url=f"https://docs.python.org/3/library/{module}.html#{other_name}",
                            confidence=0.6
                        ))
        
        return suggestions
    
    def _infer_doc_type(self, name: str) -> str:
        """Infer the documentation type from the name."""
        if name[0].isupper():
            return 'class'
        elif name.startswith('__'):
            return 'method'
        else:
            return 'function'
    
    def _is_related(self, name1: str, name2: str) -> bool:
        """Check if two names are related."""
        # Common related patterns
        related_patterns = [
            ('load', 'dump'),
            ('read', 'write'),
            ('open', 'close'),
            ('start', 'stop'),
            ('get', 'set'),
            ('add', 'remove'),
        ]
        
        for a, b in related_patterns:
            if (name1 == a and name2 == b) or (name1 == b and name2 == a):
                return True
        
        return False


class CodeAnalyzer:
    """
    Analyzes Python code and extracts documentation contexts.
    """
    
    def __init__(self, registry: DocumentationRegistry):
        self.registry = registry
    
    def analyze_file(self, file_path: str) -> List[CodeContext]:
        """Analyze a Python file and extract code contexts."""
        contexts = []
        
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                source = f.read()
            
            tree = ast.parse(source, filename=file_path)
            at = asttokens.ASTTokens(source, tree=tree)
            
            # Find all names in the code
            for node in ast.walk(tree):
                if isinstance(node, ast.Name):
                    context = self._create_context(node, file_path, at)
                    context.doc_links = self.registry.suggest_docs(node.id)
                    contexts.append(context)
                
                elif isinstance(node, ast.Attribute):
                    # Handle attribute access (e.g., os.path.join)
                    full_name = self._get_full_name(node)
                    if full_name:
                        module, name = self._split_module_name(full_name)
                        if module and name:
                            context = self._create_context(node, file_path, at)
                            context.full_name = full_name
                            context.doc_links = self.registry.suggest_docs(name, module)
                            contexts.append(context)
        
        except SyntaxError:
            pass  # Skip files with syntax errors
        
        return contexts
    
    def _create_context(self, node: ast.AST, file_path: str, at: asttokens.ASTTokens) -> CodeContext:
        """Create a CodeContext from an AST node."""
        start = at.get_token(node.lineno, node.col_offset)
        source = at.text
        return CodeContext(
            file_path=file_path,
            line_number=node.lineno,
            column=node.col_offset,
            name=ast.get_source_segment(source, node) or "",
            full_name=ast.get_source_segment(source, node) or ""
        )
    
    def _get_full_name(self, node: ast.Attribute) -> Optional[str]:
        """Get the full name for an attribute node (e.g., 'os.path.join')."""
        parts = []
        current = node
        
        while isinstance(current, ast.Attribute):
            parts.append(current.attr)
            current = current.value
        
        if isinstance(current, ast.Name):
            parts.append(current.id)
            return '.'.join(reversed(parts))
        
        return None
    
    def _split_module_name(self, full_name: str) -> Tuple[Optional[str], Optional[str]]:
        """Split a full name into module and name parts."""
        parts = full_name.split('.')
        if len(parts) >= 2:
            return '.'.join(parts[:-1]), parts[-1]
        return None, parts[0] if parts else None


class DocLinkMonitor(FileSystemEventHandler):
    """
    Watches for file changes and updates documentation links.
    """
    
    def __init__(self, analyzer: CodeAnalyzer, callback: Callable):
        self.analyzer = analyzer
        self.callback = callback
        self.buffer: Dict[str, float] = {}
        self.buffer_delay = 0.5
    
    def _should_process(self, path: str) -> bool:
        """Skip system files and virtual environments."""
        skip_patterns = {'.git', '__pycache__', 'node_modules', '.venv', 'venv', '.tox'}
        path_lower = path.lower()
        return not any(pattern in path_lower for pattern in skip_patterns)
    
    def on_modified(self, event):
        """Handle file modification events."""
        if event.is_directory:
            return
        if not self._should_process(event.src_path):
            return
        
        # Debounce rapid changes
        now = time.time()
        if event.src_path in self.buffer:
            if now - self.buffer[event.src_path] < self.buffer_delay:
                return
        self.buffer[event.src_path] = now
        
        contexts = self.analyzer.analyze_file(event.src_path)
        for ctx in contexts:
            if ctx.doc_links:
                self.callback(ctx)
    
    def on_created(self, event):
        """Handle file creation events."""
        if event.is_directory:
            return
        if not self._should_process(event.src_path):
            return
        
        contexts = self.analyzer.analyze_file(event.src_path)
        for ctx in contexts:
            if ctx.doc_links:
                self.callback(ctx)


class DoculinkDaemon:
    """
    The main daemon that provides real-time documentation links.
    """
    
    def __init__(self, watch_paths: List[str] = None):
        self.watch_paths = watch_paths or [os.getcwd()]
        self.registry = DocumentationRegistry()
        self.analyzer = CodeAnalyzer(self.registry)
        self.monitor = DocLinkMonitor(self.analyzer, self._on_context_change)
        self.observer = Observer()
        self.running = False
        self.suggestion_callbacks: List[Callable] = []
    
    def _on_context_change(self, context: CodeContext):
        """Called when a code context changes."""
        for callback in self.suggestion_callbacks:
            try:
                callback(context)
            except Exception as e:
                print(f"[Doculink] Callback error: {e}", file=sys.stderr)
    
    def register_suggestion_callback(self, callback: Callable):
        """Register a callback to receive documentation suggestions."""
        self.suggestion_callbacks.append(callback)
    
    def start(self):
        """Start the daemon and begin monitoring."""
        self.running = True
        
        # Start file monitoring
        for path in self.watch_paths:
            if os.path.exists(path):
                self.observer.schedule(self.monitor, path, recursive=True)
        
        self.observer.start()
        
        print("[Doculink] Daemon started. Monitoring:", ", ".join(self.watch_paths))
        print("[Doculink] Analyzing code for documentation links...")
        
        # Initial analysis
        self._analyze_current_files()
    
    def _analyze_current_files(self):
        """Analyze all files in watch paths on startup."""
        for path in self.watch_paths:
            if os.path.exists(path):
                for root, dirs, files in os.walk(path):
                    for file in files:
                        if file.endswith('.py'):
                            file_path = os.path.join(root, file)
                            contexts = self.analyzer.analyze_file(file_path)
                            for ctx in contexts:
                                if ctx.doc_links:
                                    self._on_context_change(ctx)
    
    def stop(self):
        """Stop the daemon."""
        self.running = False
        self.observer.stop()
        self.observer.join()
        print("[Doculink] Daemon stopped.")
    
    def get_links_for(self, file_path: str, line: int) -> List[DocLink]:
        """Get documentation links for a specific line in a file."""
        contexts = self.analyzer.analyze_file(file_path)
        for ctx in contexts:
            if ctx.file_path == file_path and ctx.line_number == line:
                return ctx.doc_links
        return []


def main():
    """Entry point for the doculink CLI."""
    daemon = DoculinkDaemon()
    
    # Demo callback
    def show_links(context):
        print(f"\n📚 Doculink: {context.name}")
        print(f"   Location: {os.path.basename(context.file_path)}:{context.line_number}")
        for link in context.doc_links[:3]:
            print(f"   → {link.name}: {link.description} [{link.source}]")
            if link.url:
                print(f"     {link.url}")
    
    daemon.register_suggestion_callback(show_links)
    
    try:
        daemon.start()
        while daemon.running:
            time.sleep(1)
    except KeyboardInterrupt:
        daemon.stop()


if __name__ == "__main__":
    main()
