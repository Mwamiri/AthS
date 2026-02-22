"""
Page Builder API Tests
Comprehensive test suite for page builder endpoints
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src', 'backend'))

import unittest
import json
from datetime import datetime
from app import app
from models import (
    SessionLocal, PageBuilder, PageSection, PageBlock, 
    Theme, Menu, MenuItem, ComponentLibraryItem, User, init_db
)


class PageBuilderTestCase(unittest.TestCase):
    """Test cases for page builder API"""
    
    @classmethod
    def setUpClass(cls):
        """Set up test database and client"""
        cls.app = app
        cls.app.config['TESTING'] = True
        cls.client = cls.app.test_client()
        
        # Initialize database
        init_db()
        
        # Create test user
        cls.db = SessionLocal()
        try:
            test_user = User(
                name='Test Admin',
                email='admin@test.com',
                role='admin',
                status='active'
            )
            test_user.set_password('testpass123')
            cls.db.add(test_user)
            cls.db.commit()
            cls.test_user_id = test_user.id
        except Exception:
            cls.db.rollback()
            test_user = cls.db.query(User).filter_by(email='admin@test.com').first()
            cls.test_user_id = test_user.id
        
        # Set up auth headers
        cls.headers = {
            'Authorization': 'Bearer test_token_12345',
            'X-User-ID': str(cls.test_user_id),
            'X-User-Role': 'admin',
            'Content-Type': 'application/json'
        }
    
    @classmethod
    def tearDownClass(cls):
        """Clean up test database"""
        cls.db.close()
    
    def setUp(self):
        """Set up before each test"""
        self.db = SessionLocal()
    
    def tearDown(self):
        """Clean up after each test"""
        self.db.close()
    
    # ========== THEME TESTS ==========
    
    def test_01_create_theme(self):
        """Test creating a new theme"""
        theme_data = {
            'name': 'Test Theme',
            'description': 'A test theme',
            'colors': json.dumps({
                'primary': '#ff6b35',
                'secondary': '#06d6a0',
                'text': '#2d2d2d',
                'background': '#ffffff'
            }),
            'fonts': json.dumps({
                'body': 'Inter, sans-serif',
                'heading': 'Poppins, sans-serif'
            }),
            'spacing': json.dumps({
                'padding': '1rem',
                'margin': '1rem'
            }),
            'borderRadius': '8px',
            'shadow': '0 2px 8px rgba(0,0,0,0.1)'
        }
        
        response = self.client.post('/api/builder/themes', 
                                   data=json.dumps(theme_data),
                                   headers=self.headers)
        
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data)
        self.assertTrue(data['success'])
        self.assertIn('data', data)
        self.assertEqual(data['data']['name'], 'Test Theme')
        
        # Store theme ID for later tests
        self.__class__.test_theme_id = data['data']['id']
    
    def test_02_list_themes(self):
        """Test listing all themes"""
        response = self.client.get('/api/builder/themes', headers=self.headers)
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data['success'])
        self.assertIsInstance(data['data'], list)
        self.assertGreater(len(data['data']), 0)
    
    def test_03_update_theme(self):
        """Test updating a theme"""
        if not hasattr(self.__class__, 'test_theme_id'):
            self.skipTest('Theme not created')
        
        update_data = {
            'name': 'Updated Test Theme',
            'description': 'An updated test theme',
            'isActive': True
        }
        
        response = self.client.put(f'/api/builder/themes/{self.test_theme_id}',
                                  data=json.dumps(update_data),
                                  headers=self.headers)
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data['success'])
        self.assertEqual(data['data']['name'], 'Updated Test Theme')
    
    # ========== MENU TESTS ==========
    
    def test_04_create_menu(self):
        """Test creating a new menu"""
        menu_data = {
            'name': 'Test Menu',
            'location': 'header',
            'description': 'A test menu',
            'displayType': 'horizontal',
            'isVisible': True
        }
        
        response = self.client.post('/api/builder/menus',
                                   data=json.dumps(menu_data),
                                   headers=self.headers)
        
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data)
        self.assertTrue(data['success'])
        self.assertIn('data', data)
        self.assertEqual(data['data']['name'], 'Test Menu')
        
        # Store menu ID for later tests
        self.__class__.test_menu_id = data['data']['id']
    
    def test_05_add_menu_item(self):
        """Test adding a menu item"""
        if not hasattr(self.__class__, 'test_menu_id'):
            self.skipTest('Menu not created')
        
        menu_item_data = {
            'label': 'Home',
            'url': '/',
            'icon': 'home',
            'position': 1,
            'isVisible': True,
            'openInNewTab': False
        }
        
        response = self.client.post(f'/api/builder/menus/{self.test_menu_id}/items',
                                   data=json.dumps(menu_item_data),
                                   headers=self.headers)
        
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data)
        self.assertTrue(data['success'])
        self.assertEqual(data['data']['label'], 'Home')
        
        # Store menu item ID for later tests
        self.__class__.test_menu_item_id = data['data']['id']
    
    def test_06_list_menus(self):
        """Test listing all menus"""
        response = self.client.get('/api/builder/menus', headers=self.headers)
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data['success'])
        self.assertIsInstance(data['data'], list)
        self.assertGreater(len(data['data']), 0)
    
    # ========== COMPONENT TESTS ==========
    
    def test_07_create_component(self):
        """Test creating a new component"""
        component_data = {
            'name': 'Hero Section',
            'category': 'hero',
            'description': 'A hero section component',
            'thumbnail': '/images/hero-thumb.jpg',
            'template': json.dumps({
                'type': 'hero',
                'elements': ['heading', 'subheading', 'button']
            }),
            'defaultContent': json.dumps({
                'heading': 'Welcome',
                'subheading': 'Get started',
                'button': 'Learn More'
            }),
            'styles': json.dumps({
                'background': '#f5f5f5',
                'padding': '4rem 2rem'
            }),
            'isFeatured': True
        }
        
        response = self.client.post('/api/builder/components',
                                   data=json.dumps(component_data),
                                   headers=self.headers)
        
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data)
        self.assertTrue(data['success'])
        self.assertEqual(data['data']['name'], 'Hero Section')
        
        # Store component ID for later tests
        self.__class__.test_component_id = data['data']['id']
    
    def test_08_list_components(self):
        """Test listing all components"""
        response = self.client.get('/api/builder/components', headers=self.headers)
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data['success'])
        self.assertIsInstance(data['data'], list)
        self.assertGreater(len(data['data']), 0)
    
    def test_09_list_components_by_category(self):
        """Test listing components by category"""
        if not hasattr(self.__class__, 'test_component_id'):
            self.skipTest('Component not created')
        
        response = self.client.get('/api/builder/components/category/hero', 
                                  headers=self.headers)
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data['success'])
        self.assertIsInstance(data['data'], list)
    
    # ========== PAGE TESTS ==========
    
    def test_10_create_page(self):
        """Test creating a new page"""
        page_data = {
            'title': 'Test Page',
            'slug': 'test-page',
            'description': 'A test page',
            'status': 'draft',
            'isHomepage': False
        }
        
        response = self.client.post('/api/builder/pages',
                                   data=json.dumps(page_data),
                                   headers=self.headers)
        
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data)
        self.assertTrue(data['success'])
        self.assertEqual(data['data']['title'], 'Test Page')
        
        # Store page ID for later tests
        self.__class__.test_page_id = data['data']['id']
    
    def test_11_list_pages(self):
        """Test listing all pages"""
        response = self.client.get('/api/builder/pages', headers=self.headers)
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data['success'])
        self.assertIsInstance(data['data'], list)
    
    def test_12_get_page(self):
        """Test getting a single page"""
        if not hasattr(self.__class__, 'test_page_id'):
            self.skipTest('Page not created')
        
        response = self.client.get(f'/api/builder/pages/{self.test_page_id}',
                                  headers=self.headers)
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data['success'])
        self.assertEqual(data['data']['title'], 'Test Page')
    
    def test_13_update_page(self):
        """Test updating a page"""
        if not hasattr(self.__class__, 'test_page_id'):
            self.skipTest('Page not created')
        
        update_data = {
            'title': 'Updated Test Page',
            'status': 'published'
        }
        
        response = self.client.put(f'/api/builder/pages/{self.test_page_id}',
                                  data=json.dumps(update_data),
                                  headers=self.headers)
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data['success'])
        self.assertEqual(data['data']['title'], 'Updated Test Page')
    
    def test_14_add_page_section(self):
        """Test adding a section to a page"""
        if not hasattr(self.__class__, 'test_page_id'):
            self.skipTest('Page not created')
        
        section_data = {
            'name': 'Header Section',
            'type': 'header',
            'position': 1,
            'styles': json.dumps({
                'background': '#ffffff',
                'padding': '2rem'
            })
        }
        
        response = self.client.post(f'/api/builder/pages/{self.test_page_id}/sections',
                                   data=json.dumps(section_data),
                                   headers=self.headers)
        
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data)
        self.assertTrue(data['success'])
        self.assertEqual(data['data']['name'], 'Header Section')
        
        # Store section ID for later tests
        self.__class__.test_section_id = data['data']['id']
    
    def test_15_add_block_to_section(self):
        """Test adding a block to a section"""
        if not hasattr(self.__class__, 'test_section_id'):
            self.skipTest('Section not created')
        
        block_data = {
            'blockType': 'text',
            'content': json.dumps({
                'text': 'Welcome to our site!',
                'alignment': 'center'
            }),
            'position': 1,
            'gridColumn': '1 / -1',
            'styles': json.dumps({
                'fontSize': '2rem',
                'fontWeight': 'bold'
            })
        }
        
        response = self.client.post(f'/api/builder/sections/{self.test_section_id}/blocks',
                                   data=json.dumps(block_data),
                                   headers=self.headers)
        
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data)
        self.assertTrue(data['success'])
        self.assertEqual(data['data']['blockType'], 'text')
    
    # ========== PERMISSION TESTS ==========
    
    def test_16_unauthorized_access(self):
        """Test that endpoints reject unauthorized requests"""
        response = self.client.get('/api/builder/pages')
        self.assertEqual(response.status_code, 401)
    
    def test_17_insufficient_permissions(self):
        """Test that write operations require admin/moderator role"""
        viewer_headers = self.headers.copy()
        viewer_headers['X-User-Role'] = 'viewer'
        
        page_data = {
            'title': 'Unauthorized Page',
            'slug': 'unauthorized',
            'status': 'draft'
        }
        
        response = self.client.post('/api/builder/pages',
                                   data=json.dumps(page_data),
                                   headers=viewer_headers)
        
        self.assertEqual(response.status_code, 403)
    
    # ========== CLEANUP TESTS ==========
    
    def test_99_cleanup(self):
        """Clean up test data"""
        # Delete test page
        if hasattr(self.__class__, 'test_page_id'):
            self.client.delete(f'/api/builder/pages/{self.test_page_id}',
                             headers=self.headers)
        
        # Delete test component
        if hasattr(self.__class__, 'test_component_id'):
            self.client.delete(f'/api/builder/components/{self.test_component_id}',
                             headers=self.headers)
        
        # Delete test menu
        if hasattr(self.__class__, 'test_menu_id'):
            self.client.delete(f'/api/builder/menus/{self.test_menu_id}',
                             headers=self.headers)
        
        # Delete test theme
        if hasattr(self.__class__, 'test_theme_id'):
            self.client.delete(f'/api/builder/themes/{self.test_theme_id}',
                             headers=self.headers)


def run_tests():
    """Run all tests"""
    suite = unittest.TestLoader().loadTestsFromTestCase(PageBuilderTestCase)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    return result


if __name__ == '__main__':
    print("\n" + "="*70)
    print("PAGE BUILDER API TEST SUITE")
    print("="*70 + "\n")
    
    result = run_tests()
    
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    print(f"Tests Run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Skipped: {len(result.skipped)}")
    print(f"Success Rate: {((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100):.1f}%")
    print("="*70 + "\n")
    
    # Exit with proper code
    sys.exit(0 if result.wasSuccessful() else 1)
