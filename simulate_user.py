"""
Integration Test: Simulate Coding Workflow

This script simulates a developer coding and verifies
that Doculink successfully provides documentation links.
"""

import sys
from pathlib import Path

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from doculink import DoculinkDaemon, DocumentationRegistry, CodeAnalyzer, CodeContext, DocLink


def test_documentation_registry():
    """Test that the documentation registry has entries."""
    
    print("🧪 Testing documentation registry...")
    
    registry = DocumentationRegistry()
    
    # Check we have stdlib docs
    if len(registry.stdlib_docs) >= 5:
        print(f"   ✓ Registry contains {len(registry.stdlib_docs)} module documentation sets")
        
        # List some modules
        modules = list(registry.stdlib_docs.keys())[:5]
        print(f"      Examples: {', '.join(modules)}")
        
        return True
    else:
        print(f"   ✗ Registry only has {len(registry.stdlib_docs)} modules (expected >= 5)")
        return False


def test_documentation_lookup():
    """Test that documentation can be looked up."""
    
    print("\n🧪 Testing documentation lookup...")
    
    registry = DocumentationRegistry()
    
    test_cases = [
        ("os", "path.exists", "Return True if path refers to an existing path."),
        ("json", "loads", "Parse JSON string to Python object."),
        ("re", "match", "Search for pattern at beginning of string."),
    ]
    
    passed = 0
    for module, name, expected_desc in test_cases:
        doc = registry.get_documentation(module, name)
        if doc and expected_desc in doc:
            print(f"   ✓ {module}.{name}: Found documentation")
            passed += 1
        else:
            print(f"   ✗ {module}.{name}: Documentation not found")
    
    return passed == len(test_cases)


def test_code_analysis():
    """Test that code analysis extracts documentation contexts."""
    
    print("\n🧪 Testing code analysis...")
    
    registry = DocumentationRegistry()
    analyzer = CodeAnalyzer(registry)
    
    # Create a test file
    test_code = """
import os
import json

def process_data():
    data = json.loads('{"key": "value"}')
    exists = os.path.exists("file.txt")
    return data
"""
    
    test_dir = Path("/tmp/doculink_test_" + str(int(__import__('time').time())))
    test_dir.mkdir(exist_ok=True)
    test_file = test_dir / "test_code.py"
    test_file.write_text(test_code)
    
    try:
        contexts = analyzer.analyze_file(str(test_file))
        
        # Check that we found documentation contexts
        docs_contexts = [c for c in contexts if c.doc_links]
        
        if len(docs_contexts) >= 2:
            print(f"   ✓ Found {len(docs_contexts)} contexts with documentation")
            for ctx in docs_contexts[:3]:
                print(f"      - {ctx.name} at line {ctx.line_number}: {len(ctx.doc_links)} suggestions")
            return True
        else:
            print(f"   ✗ Only found {len(docs_contexts)} contexts with documentation")
            return False
            
    finally:
        import shutil
        shutil.rmtree(test_dir, ignore_errors=True)


def test_suggestion_quality():
    """Test that generated suggestions are relevant."""
    
    print("\n🧪 Testing suggestion quality...")
    
    registry = DocumentationRegistry()
    
    # Test suggestions for common names with module context
    suggestions = registry.suggest_docs("loads", "json")
    
    if len(suggestions) >= 1:
        print(f"   ✓ Generated {len(suggestions)} suggestions for 'loads' in 'json'")
        
        # Check that suggestions have required fields
        valid = all(
            s.name and s.doc_type and s.source and s.description
            for s in suggestions
        )
        
        if valid:
            print(f"      All suggestions have required fields")
            for s in suggestions[:2]:
                print(f"        - {s.name}: {s.description[:50]}...")
            return True
        else:
            print(f"      Some suggestions missing required fields")
            return False
    else:
        print(f"   ✗ No suggestions generated")
        return False


def test_full_workflow():
    """Test a complete coding workflow."""
    
    print("\n🧪 Testing complete workflow...")
    
    daemon = DoculinkDaemon()
    
    contexts_received = []
    
    def on_context(context):
        contexts_received.append(context)
    
    daemon.register_suggestion_callback(on_context)
    
    # Create test code
    test_dir = Path("/tmp/doculink_workflow_" + str(int(__import__('time').time())))
    test_dir.mkdir(exist_ok=True)
    
    test_file = test_dir / "workflow_test.py"
    test_file.write_text("""
import os
import json

def main():
    data = json.loads('{"test": true}')
    return os.path.exists("data.json")
""")
    
    try:
        daemon.start()
        
        # Give it time to analyze
        import time
        time.sleep(2)
        
        # Check that we received contexts
        if len(contexts_received) >= 2:
            print(f"   ✓ Received {len(contexts_received)} documentation contexts")
            print(f"      Contexts include: {[c.name for c in contexts_received[:3]]}")
            return True
        else:
            print(f"   ✗ Only received {len(contexts_received)} contexts")
            return False
            
    finally:
        daemon.stop()
        import shutil
        shutil.rmtree(test_dir, ignore_errors=True)


if __name__ == "__main__":
    print("=" * 60)
    print("DOCULINK INTEGRATION TEST SUITE")
    print("=" * 60)
    
    results = []
    
    # Run tests
    results.append(("Documentation Registry", test_documentation_registry()))
    results.append(("Documentation Lookup", test_documentation_lookup()))
    results.append(("Code Analysis", test_code_analysis()))
    results.append(("Suggestion Quality", test_suggestion_quality()))
    results.append(("Full Workflow", test_full_workflow()))
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    for name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} - {name}")
    
    all_passed = all(passed for _, passed in results)
    
    if all_passed:
        print("\n🎉 All tests passed! Doculink is ready for production.")
        sys.exit(0)
    else:
        print("\n⚠️  Some tests failed. Review the output above.")
        sys.exit(1)
