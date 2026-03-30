"""
Doculink - Real-time Documentation Linker

Production-ready implementation with:
- Comprehensive stdlib documentation (100+ modules)
- PyPI package documentation lookup
- Local project documentation indexing
- Persistent cache
- Context-aware suggestions
"""

from .daemon import (
    DoculinkDaemon,
    DocumentationRegistry,
    CodeAnalyzer,
    DocLink,
    CodeContext
)

__version__ = "1.0.0"
__all__ = ["DoculinkDaemon", "DocumentationRegistry", "CodeAnalyzer", 
           "DocLink", "CodeContext"]
