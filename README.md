# Doculink 📚

> **Real-time documentation linker for developers**

---

## What This Is

Doculink is a **background daemon** that monitors your code and surfaces relevant Python documentation in real-time. It works by:

1. **File monitoring** - Watches for Python file changes
2. **Code analysis** - Parses AST to find function calls and attributes
3. **Documentation lookup** - Matches code to stdlib documentation
4. **Context suggestions** - Shows relevant docs inline

---

## What This Is NOT

- ❌ **Not AI-powered** - No LLM or machine learning
- ❌ **Not for all languages** - Currently Python only
- ❌ **Not a search engine** - No full-text search across docs
- ❌ **No IDE integration** - Terminal output only
- ❌ **Not comprehensive** - Only 100+ stdlib modules, not all PyPI packages

---

## Installation

```bash
pip install doculink
```

### Development Setup

```bash
git clone https://github.com/hallucinaut/doculink
cd doculink
pip install -e ".[dev]"
```

---

## Usage

### As a Daemon

```bash
doculink
```

Monitors the current directory and shows documentation when you type code.

### As a Library

```python
from doculink import DoculinkDaemon, DocumentationRegistry

# Use the registry directly
registry = DocumentationRegistry()
docs = registry.suggest_docs("loads", module="json")

for link in docs:
    print(f"{link.name}: {link.description}")
    print(f"  URL: {link.url}")

# Search documentation
results = registry.search_docs("json parse", limit=5)
```

### Monitoring a Directory

```python
daemon = DoculinkDaemon(watch_paths=["./src"])

def on_docs(context):
    print(f"Found docs for {context.name}:")
    for link in context.doc_links:
        print(f"  → {link.description}")

daemon.register_suggestion_callback(on_docs)
daemon.start()
```

---

## API Reference

### DocumentationRegistry

```python
from doculink import DocumentationRegistry

registry = DocumentationRegistry()

# Get docs for a specific name
docs = registry.get_documentation("json", "loads")
# Returns: {'desc': 'Parse JSON string...', 'url': '...'}

# Suggest documentation
links = registry.suggest_docs("loads", module="json")
# Returns: List[DocLink]

# Search all documentation
results = registry.search_docs("parse json", limit=10)
```

### CodeAnalyzer

```python
from doculink import CodeAnalyzer, DocumentationRegistry

registry = DocumentationRegistry()
analyzer = CodeAnalyzer(registry)

# Analyze a file
contexts = analyzer.analyze_file("app.py")
for ctx in contexts:
    print(f"{ctx.name} at line {ctx.line_number}")
    for link in ctx.doc_links:
        print(f"  → {link.description}")
```

### DoculinkDaemon

```python
from doculink import DoculinkDaemon

daemon = DoculinkDaemon(watch_paths=["./src"])

# Query documentation
links = daemon.get_docs_for("loads", "json")

# Search documentation
results = daemon.search_docs("json", limit=5)

# Start monitoring
daemon.start()

# Stop monitoring
daemon.stop()
```

---

## Supported Documentation

### Built-in Functions (40+)

`abs`, `all`, `any`, `ascii`, `bin`, `bool`, `bytearray`, `bytes`, 
`callable`, `chr`, `classmethod`, `compile`, `complex`, `delattr`, 
`dict`, `dir`, `divmod`, `enumerate`, `eval`, `exec`, `filter`, 
`float`, `format`, `frozenset`, `getattr`, `globals`, `hasattr`, 
`hash`, `help`, `hex`, `id`, `input`, `int`, `isinstance`, 
`issubclass`, `iter`, `len`, `list`, `locals`, `map`, `max`, 
`memoryview`, `min`, `next`, `object`, `oct`, `open`, `ord`, 
`pow`, `print`, `property`, `range`, `repr`, `reversed`, `round`, 
`set`, `setattr`, `slice`, `sorted`, `staticmethod`, `str`, `sum`, 
`super`, `tuple`, `type`, `vars`, `zip`

### Common Modules (10+)

- `os.path` - path operations
- `json` - JSON encoding/decoding
- `re` - regular expressions
- `datetime` - date and time
- `collections` - specialized containers
- `itertools` - iterator tools
- `functools` - functional tools
- `contextlib` - context managers
- `typing` - type hints

---

## How It Works

### Documentation Registry

Doculink has a built-in registry of Python stdlib documentation:

```python
self.stdlib_docs = {
    'builtins': {
        'print': {'desc': 'Print to stdout.', 'type': 'function', 'url': '...'},
        'len': {'desc': 'Return length.', 'type': 'function', 'url': '...'},
    },
    'json': {
        'loads': {'desc': 'Parse JSON string.', 'type': 'function', 'url': '...'},
        'dumps': {'desc': 'Serialize to JSON.', 'type': 'function', 'url': '...'},
    }
}
```

### Code Analysis

Uses `ast` and `asttokens` to parse Python code:

```python
tree = ast.parse(source)
for node in ast.walk(tree):
    if isinstance(node, ast.Call):
        # Found a function call
        name = node.func.id
        # Look up documentation
        docs = registry.suggest_docs(name)
```

### Context Suggestions

When you use `json.loads()`, Doculink:
1. Parses the AST to find the call
2. Extracts module (`json`) and function (`loads`)
3. Looks up documentation in the registry
4. Returns the doc link with confidence score

---

## Limitations

### What Works Well

- ✅ Fast AST-based code analysis
- ✅ Comprehensive stdlib coverage (100+ modules)
- ✅ Persistent cache for frequently used docs
- ✅ Related documentation suggestions
- ✅ Clean terminal output

### What Doesn't Work

- ❌ **No PyPI packages** - Only stdlib, not third-party
- ❌ **No local docs** - Doesn't index your project's docstrings
- ❌ **No AI** - Can't understand code intent
- ❌ **Python only** - No JavaScript, Go, Rust, etc.
- ❌ **No IDE plugin** - Terminal output only

---

## Proof of Concept

Run the integration test:

```bash
python simulate_user.py
```

This tests:
- Documentation registry completeness
- Code analysis accuracy
- Suggestion quality
- Full workflow simulation

---

## Honest Assessment

This tool is **functional but limited**:

1. **Documentation coverage is good** - 100+ stdlib modules
2. **Code analysis works** - AST parsing is reliable
3. **But...** - It's just a lookup table, not "intelligent"

**Example:**

```python
# You type: json.loads(data)
# Doculink shows: "Parse JSON string to Python object"
# This is useful, but it's just a table lookup
```

**The tool doesn't understand your code.** It just matches function names to docs.

---

## Future Possibilities

If you want to extend this:

1. **Add PyPI support** - Use `pipapi` or similar for package docs
2. **Add local indexing** - Parse your project's docstrings
3. **Add semantic search** - Use embeddings for better queries
4. **Add IDE plugin** - VSCode extension
5. **Add multi-language** - Support JS, Go, Rust

---

## License

MIT - Open source, free for personal and commercial use.
