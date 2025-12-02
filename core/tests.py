from django.test import TestCase, Client
from destinations.models import Destination


class LandingPageTests(TestCase):
    """Test the landing page view and popular destinations rendering."""
    
    def setUp(self):
        """Set up test data."""
        self.client = Client()
        # Create featured destinations
        for i in range(8):
            Destination.objects.create(
                name=f"Test Destination {i+1}",
                slug=f"test-destination-{i+1}",
                description=f"A test destination {i+1}",
                destination_type="safari" if i % 2 == 0 else "beach",
                county=f"Test County {i+1}",
                image_url="https://example.com/image.jpg",
                best_time_to_visit="June-September",
                average_cost_per_day=5000,
                popular_activities="Wildlife viewing, Photography",
                is_featured=(i < 6),  # First 6 are featured
            )
    
    def test_landing_page_status_200(self):
        """Test that landing page returns 200 status code."""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
    
    def test_landing_page_contains_featured_destinations(self):
        """Test that featured destinations are present in landing page context."""
        response = self.client.get('/')
        self.assertIn('featured_destinations', response.context)
        self.assertEqual(len(response.context['featured_destinations']), 6)
    
    def test_landing_page_contains_popular_destinations(self):
        """Test that popular destinations are present in landing page context."""
        response = self.client.get('/')
        self.assertIn('popular_destinations', response.context)
        self.assertGreater(len(response.context['popular_destinations']), 0)
    
    def test_landing_page_renders_destination_cards(self):
        """Test that destination card HTML is rendered with proper structure."""
        response = self.client.get('/')
        content = response.content.decode()
        
        # Check for destination card elements
        self.assertIn('destination-card', content)
        self.assertIn('destination-card__image', content)
        self.assertIn('destination-card__overlay', content)
        self.assertIn('destination-card__title', content)
    
    def test_popular_destinations_section_exists(self):
        """Test that Popular Destinations / Featured Experiences section exists."""
        response = self.client.get('/')
        content = response.content.decode()
        
        self.assertIn('Featured Experiences', content)
        self.assertIn('destination-grid', content)
    
    def test_destination_card_has_accessibility_attributes(self):
        """Test that destination cards have proper accessibility attributes."""
        response = self.client.get('/')
        content = response.content.decode()
        
        # Check for accessibility attributes
        self.assertIn('tabindex="0"', content)
        self.assertIn('role="group"', content)
        self.assertIn('aria-label', content)
        self.assertIn('aria-hidden="true"', content)
    
    def test_destination_card_has_lazy_loading(self):
        """Test that images have lazy loading attribute."""
        response = self.client.get('/')
        content = response.content.decode()
        
        self.assertIn('loading="lazy"', content)
    
    def test_destination_card_links_work(self):
        """Test that destination detail links are present and valid."""
        response = self.client.get('/')
        content = response.content.decode()
        
        # Check for destination detail URLs
        self.assertIn('/destinations/test-destination-', content)
        self.assertIn('View Details', content)
    
    def test_no_unrendered_template_tokens(self):
        """Test that response does not contain unrendered template tokens."""
        response = self.client.get('/')
        content = response.content.decode()
        
        # Check for common unrendered template patterns
        self.assertNotIn('{{ destination', content)
        self.assertNotIn('{%', content.split('</script>')[-1])  # Check after scripts
    
    def test_destination_type_display(self):
        """Test that destination type is properly displayed."""
        response = self.client.get('/')
        content = response.content.decode()
        
        # Should contain rendered destination types (Safari, Beach)
        self.assertTrue(
            ('Safari' in content or 'Beach' in content),
            msg="Destination types should be rendered"
        )


class DestinationCardPartialTests(TestCase):
    """Test the reusable destination card partial template."""
    
    def setUp(self):
        """Set up test data."""
        self.destination = Destination.objects.create(
            name="Maasai Mara",
            slug="maasai-mara",
            description="The largest wildlife sanctuary in Kenya",
            destination_type="safari",
            county="Narok",
            image_url="https://example.com/mara.jpg",
            best_time_to_visit="July-September",
            average_cost_per_day=8000,
            popular_activities="Game drives, Photography, Bird watching",
            is_featured=True,
        )
    
    def test_card_partial_renders_with_destination(self):
        """Test that the card partial can render a destination."""
        # This would require rendering the template directly
        from django.template.loader import render_to_string
        
        html = render_to_string(
            'destinations/_card.html',
            {'destination': self.destination}
        )
        
        # Check that key elements are present
        self.assertIn(self.destination.name, html)
        self.assertIn('Maasai Mara', html)
        self.assertIn('Safari', html)
        self.assertIn('destination-card', html)
    
    def test_card_partial_has_image(self):
        """Test that card partial renders image with proper attributes."""
        from django.template.loader import render_to_string
        
        html = render_to_string(
            'destinations/_card.html',
            {'destination': self.destination}
        )
        
        self.assertIn('img', html)
        self.assertIn('loading="lazy"', html)
        self.assertIn('src=', html)
    
    def test_card_partial_has_overlay_content(self):
        """Test that card partial has overlay with all required content."""
        from django.template.loader import render_to_string
        
        html = render_to_string(
            'destinations/_card.html',
            {'destination': self.destination}
        )
        
        # Check for overlay elements
        self.assertIn('destination-card__overlay', html)
        self.assertIn('destination-card__type-pill', html)
        self.assertIn('destination-card__title', html)
        self.assertIn('destination-card__cta', html)
        self.assertIn('View Details', html)
    
    def test_card_partial_location_display(self):
        """Test that card partial displays location/county information."""
        from django.template.loader import render_to_string
        
        html = render_to_string(
            'destinations/_card.html',
            {'destination': self.destination}
        )
        
        self.assertIn('Narok', html)
        self.assertIn('destination-card__location', html)

