import unittest

class TestBasicSetup(unittest.TestCase):
    """Test basic Django project setup."""
    
    def test_django_import(self):
        """Test that Django can be imported."""
        try:
            import django
            self.assertIsNotNone(django)
        except ImportError:
            self.fail("Django import failed")
    
    def test_settings_import(self):
        """Test that Django settings can be imported."""
        try:
            from household_chores import settings
            self.assertIsNotNone(settings)
        except ImportError:
            self.fail("Settings import failed")
    
    def test_basic_math(self):
        """Test basic math operations to verify test framework works."""
        self.assertEqual(1 + 1, 2)
        self.assertEqual(2 * 3, 6)
        self.assertTrue(4 > 2)

if __name__ == '__main__':
    unittest.main()