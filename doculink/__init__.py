"""
Doculink - Real-time Documentation Linker

A revolutionary workflow tool that analyzes code context and surfaces
relevant documentation snippets automatically.
"""

from .daemon import DoculinkDaemon, DocumentationRegistry, CodeAnalyzer, DocLink, CodeContext

__version__ = "0.1.0"
__all__ = ["DoculinkDaemon", "DocumentationRegistry", "CodeAnalyzer", "DocLink", "CodeContext"]
