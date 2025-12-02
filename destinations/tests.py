from django.test import TestCase, Client
from .models import Destination


class DestinationsTemplateRenderingTests(TestCase):
    """Test that destination templates render properly without unrendered tokens."""
    
    def setUp(self):
        """Set up test data."""
        self.client = Client()
        self.destination = Destination.objects.create(
            name="Test Destination",
            slug="test-destination",
            description="A test destination",
            destination_type="safari",
            county="Test County",
            image_url="https://example.com/image.jpg",
            best_time_to_visit="June-September",
            average_cost_per_day=5000,
            popular_activities="Wildlife viewing, Photography"
        )
    
    def test_destinations_list_no_unrendered_tokens(self):
        """
        Test that /destinations/ response does not contain unrendered template tokens.
        This verifies that {{ destination.get_destination_type_display }} is properly rendered.
        """
        response = self.client.get('/destinations/')
        self.assertEqual(response.status_code, 200)
        
        # Check that the raw template token is NOT in the response
        content = response.content.decode()
        self.assertNotIn('{{ destination.get_destination_type_display', content,
                        msg="Unrendered template token found in /destinations/ response")
        
        # Verify that the rendered value IS in the response
        self.assertIn('Safari', content,
                     msg="Rendered destination type should appear in response")
    
    def test_destinations_list_displays_destination_type(self):
        """Test that destination type is properly displayed in list view."""
        response = self.client.get('/destinations/')
        self.assertEqual(response.status_code, 200)
        
        # Should display the rendered type
        self.assertContains(response, 'Safari')
    
    def test_no_split_line_template_expressions(self):
        """
        Regression test: verify no split-line template expressions {{ ... }} exist.
        Split-line expressions can cause Django template parser to emit them literally.
        """
        response = self.client.get('/destinations/')
        self.assertEqual(response.status_code, 200)
        content = response.content.decode()
        
        # These are common patterns of problematic split-line tags
        problematic_patterns = [
            '{{ \n',
            '{{\n',
            '{{ \r',
        ]
        
        for pattern in problematic_patterns:
            self.assertNotIn(pattern, content,
                           msg=f"Found potential split-line template expression pattern: {pattern!r}")
