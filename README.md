# Doculink 📚

> **Real-time documentation linker for developers**

---

## The Old Way

Documentation is **fragmented and hard to access**:

1. **Code reference** - IDE autocomplete shows minimal info
2. **Browser tab** - Open docs.python.org in a new tab
3. **Search** - Find the exact function you need
4. **Read** - Navigate through pages of documentation
5. **Return** - Go back to your code
6. **Repeat** - Every single time you need a new function

**The cost:** 30+ minutes daily just searching for documentation. Context is broken, focus is lost, and productivity suffers.

---

## The New Paradigm

**Doculink is different.** It's an **intelligent documentation linker** that analyzes your code in real-time and surfaces relevant documentation **inline**.

### How It Works

```python
# You're typing code
import os
path = os.path.exists("file.txt")
#                    ^^^^^^^^^^

# Doculink KNOWS this is os.path.exists()
# It SURFACES documentation automatically:

📚 Doculink: exists
   Location: main.py:2
   → exists: Return True if path refers to an existing path. [stdlib]
     https://docs.python.org/3/library/os.path.html#os.path.exists
```

**No tab switching. No searching. Just documentation.**

---

## Under the Hood

### Architecture

```
┌─────────────────────────────────────────────────────────┐
│                   Doculink Daemon                        │
├─────────────────────────────────────────────────────────┤
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │ File Monitor │  │  Code        │  │  Doc         │  │
│  │  (watchdog)  │─▶│ Analyzer     │─▶│  Registry    │  │
│  └──────────────┘  │  (ast,       │  │  (stdlib)    │  │
│                     asttokens)    │  └──────────────┘  │
│                     └──────────────┘                    │
│                            │                            │
│                    ┌───────▼───────┐                    │
│                    │ Documentation │                    │
│                    │ Suggestions   │                    │
│                    └───────────────┘                    │
└─────────────────────────────────────────────────────────┘
```

### Key Technologies

- **asttokens** - AST parsing with source code positions
- **watchdog** - Cross-platform file system monitoring
- **rich** - Beautiful terminal output
- **anyio** - Cross-platform async primitives

### Documentation Registry

Doculink includes built-in documentation for:

- **Built-in functions** - print, len, range, enumerate, zip, map, filter, sum, min, max
- **os.path** - exists, join, basename, dirname, getcwd, listdir
- **sys** - argv, path, exit, version, version_info
- **json** - loads, dumps, load, dump
- **re** - match, search, findall, sub, compile
- **datetime** - datetime, date, time, timedelta, strptime
- **collections** - defaultdict, Counter, deque, namedtuple, OrderedDict
- **itertools** - chain, compress, cycle, islice, groupby
- **functools** - lru_cache, partial, reduce, wraps
- **contextlib** - contextmanager, closing, suppress, redirect_stdout

### Extensible System

Add your own documentation:

```python
from doculink import DocumentationRegistry

registry = DocumentationRegistry()
registry.stdlib_docs['mylib'] = {
    'my_function': 'My custom function documentation',
}
```

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

Monitors the current directory and shows documentation links as you code.

### As a Library

```python
from doculink import DoculinkDaemon

daemon = DoculinkDaemon(watch_paths=["./src"])

def on_docs(context):
    print(f"Documentation for {context.name}:")
    for link in context.doc_links:
        print(f"  → {link.description}")

daemon.register_suggestion_callback(on_docs)
daemon.start()
```

---

## Proof of Concept

See `simulate_user.py` for a complete integration test that simulates coding scenarios.

```bash
python simulate_user.py
```

---

## Why This Matters

**Doculink is not a documentation viewer. It's documentation awareness.**

- **Invisible Integration** - Runs alongside your code
- **Context-Aware** - Understands what you're typing
- **Always Available** - Documentation surfaces automatically
- **Zero Friction** - No commands, no searching, no tab switching

This is the first tool that **brings documentation to you** rather than requiring you to find it.

---

## License

MIT - Open source, free for personal and commercial use.

---

## The Future

This is just the beginning. Next iterations will add:

- AI-powered documentation suggestions (LLM integration)
- Third-party package documentation (PyPI)
- IDE plugin integration (VSCode, JetBrains)
- Local project documentation indexing
- Cross-file reference tracking

**The goal:** Make documentation as natural as writing code itself.
