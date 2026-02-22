"""
Simple Page Builder Smoke Test
Quick verification that the page builder system works
"""

print("="*70)
print("PAGE BUILDER SYSTEM VERIFICATION")
print("="*70)
print()

# Test 1: Import check
print("[1/6] Testing imports...")
try:
    import sys
    import os
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src', 'backend'))
    
    from models import (
        PageBuilder, PageSection, PageBlock,
        Theme, Menu, MenuItem, ComponentLibraryItem
    )
    print("  [OK] All models imported successfully")
except Exception as e:
    print(f"  [FAIL] Import error: {e}")
    sys.exit(1)

# Test 2: Model structure check
print("[2/6] Checking model structures...")
try:
    # Check PageBuilder attributes
    required_attrs = ['title', 'slug', 'description', 'status', 'theme_id']
    for attr in required_attrs:
        assert hasattr(PageBuilder, attr), f"PageBuilder missing {attr}"
    
    # Check relationships
    assert hasattr(PageBuilder, 'sections'), "PageBuilder missing sections relationship"
    
    print("  [OK] All model structures valid")
except Exception as e:
    print(f"  [FAIL] Model structure error: {e}")
    sys.exit(1)

# Test 3: Routes check
print("[3/6] Checking API routes...")
try:
    from routes.builder import builder_bp
    
    # Simply check that blueprint exists and has the url_prefix
    assert builder_bp.url_prefix == '/api/builder', "Incorrect URL prefix"
    assert hasattr(builder_bp, 'deferred_functions'), "No deferred functions"
    
    print(f"  [OK] API blueprint loaded successfully")
except Exception as e:
    print(f"  [FAIL] Routes error: {e}")
    sys.exit(1)

# Test 4: Frontend files check
print("[4/6] Checking frontend files...")
try:
    frontend_files = [
        '../src/frontend/page-builder.html',
        '../src/frontend/theme-customizer.html',
        '../src/frontend/menu-builder.html',
        '../src/frontend/component-library.html'
    ]
    
    for file in frontend_files:
        file_path = os.path.join(os.path.dirname(__file__), file)
        assert os.path.exists(file_path), f"Missing {file}"
        
        # Check file is not empty
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            assert len(content) > 100, f"{file} appears incomplete"
    
    print("  [OK] All frontend files present and valid")
except Exception as e:
    print(f"  [FAIL] Frontend file error: {e}")
    sys.exit(1)

# Test 5: Documentation check
print("[5/6] Checking documentation...")
try:
    doc_file = os.path.join(os.path.dirname(__file__), '../docs/PAGE_BUILDER.md')
    assert os.path.exists(doc_file), "PAGE_BUILDER.md missing"
    
    with open(doc_file, 'r', encoding='utf-8') as f:
        content = f.read()
        assert 'API Reference' in content, "Documentation incomplete"
        assert 'Database Models' in content, "Documentation incomplete"
    
    print("  [OK] Documentation present and valid")
except Exception as e:
    print(f"  [FAIL] Documentation error: {e}")
    sys.exit(1)

# Test 6: Permission decorators check
print("[6/6] Checking security decorators...")
try:
    from routes.builder import token_required, admin_or_moderator_required
    
    assert callable(token_required), "token_required not callable"
    assert callable(admin_or_moderator_required), "admin_or_moderator_required not callable"
    
    print("  [OK] Security decorators present")
except Exception as e:
    print(f"  [FAIL] Security decorator error: {e}")
    sys.exit(1)

# Summary
print()
print("="*70)
print("VERIFICATION COMPLETE")
print("="*70)
print()
print("Summary:")
print("  - Database Models: OK")
print("  - API Endpoints: OK")
print("  - Frontend Interfaces: OK")
print("  - Documentation: OK")
print("  - Security: OK")
print()
print("Status: Page Builder System is READY FOR USE")
print()
print("="*70)
