"""
Script to create default static pages.
Run with: python create_default_pages.py
"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'safarismart.settings')
django.setup()

from core.models_pages import StaticPage

# About Us
about_content = """
<h2>About SafariSmart Kenya</h2>
<p>SafariSmart Kenya is your intelligent trip planning platform for exploring the best of Kenya. We help travelers discover and plan unforgettable adventures across Kenya's diverse landscapes.</p>

<h3>Our Mission</h3>
<p>To make trip planning simple, personalized, and accessible for everyone who dreams of exploring Kenya.</p>

<h3>What We Offer</h3>
<ul>
    <li>Personalized itinerary planning</li>
    <li>Curated destination guides</li>
    <li>Real-time weather forecasts</li>
    <li>Budget optimization tools</li>
    <li>Expert local recommendations</li>
</ul>

<h3>Why Choose Us</h3>
<p>We combine intelligent algorithms with local expertise to create trip plans that match your preferences, budget, and travel style. Whether you're planning a safari adventure, beach vacation, or cultural exploration, we've got you covered.</p>
"""

# Privacy Policy
privacy_content = """
<h2>Privacy Policy</h2>
<p><strong>Last Updated: November 19, 2025</strong></p>

<h3>Information We Collect</h3>
<p>We collect information you provide directly to us when you:</p>
<ul>
    <li>Create an account</li>
    <li>Plan a trip</li>
    <li>Contact us</li>
</ul>

<h3>How We Use Your Information</h3>
<p>We use the information we collect to:</p>
<ul>
    <li>Provide and improve our services</li>
    <li>Create personalized itineraries</li>
    <li>Communicate with you</li>
    <li>Ensure platform security</li>
</ul>

<h3>Data Security</h3>
<p>We implement appropriate security measures to protect your personal information.</p>

<h3>Contact Us</h3>
<p>For privacy concerns, contact us at: <a href="mailto:owuorvincent069@gmail.com">owuorvincent069@gmail.com</a></p>
"""

# Terms of Service
terms_content = """
<h2>Terms of Service</h2>
<p><strong>Last Updated: November 19, 2025</strong></p>

<h3>Acceptance of Terms</h3>
<p>By accessing and using SafariSmart Kenya, you accept and agree to be bound by these Terms of Service.</p>

<h3>Use of Service</h3>
<p>You agree to use our service only for lawful purposes and in accordance with these Terms.</p>

<h3>User Accounts</h3>
<p>You are responsible for maintaining the confidentiality of your account credentials.</p>

<h3>Itinerary Information</h3>
<p>While we strive for accuracy, itineraries are suggestions and should be verified before travel.</p>

<h3>Limitation of Liability</h3>
<p>SafariSmart Kenya is not liable for any damages arising from your use of the service.</p>

<h3>Changes to Terms</h3>
<p>We reserve the right to modify these terms at any time.</p>

<h3>Contact</h3>
<p>Questions about these terms? Contact: <a href="mailto:owuorvincent069@gmail.com">owuorvincent069@gmail.com</a></p>
"""

# Contact
contact_content = """
<h2>Contact Us</h2>
<p>We'd love to hear from you! Whether you have questions, feedback, or need assistance, feel free to reach out.</p>

<h3>Get in Touch</h3>
<p><strong>Email:</strong> <a href="mailto:owuorvincent069@gmail.com">owuorvincent069@gmail.com</a></p>
<p><strong>Location:</strong> Nairobi, Kenya</p>

<h3>Meet the Creator</h3>
<p>SafariSmart Kenya is built by Vincent Owuor, a passionate developer creating solutions for travelers.</p>
<p><a href="https://owuorvincent.vercel.app/" target="_blank">Explore my work →</a></p>

<h3>Business Inquiries</h3>
<p>For partnerships, collaborations, or business inquiries, please email us directly.</p>
"""

# Create pages
pages = [
    {
        'title': 'About Us',
        'content': about_content,
        'meta_description': 'Learn about SafariSmart Kenya - your intelligent trip planning platform for exploring Kenya.',
        'footer_order': 1
    },
    {
        'title': 'Contact',
        'content': contact_content,
        'meta_description': 'Get in touch with SafariSmart Kenya. We\'re here to help with your trip planning needs.',
        'footer_order': 2
    },
    {
        'title': 'Privacy Policy',
        'content': privacy_content,
        'meta_description': 'SafariSmart Kenya Privacy Policy - How we collect, use, and protect your information.',
        'footer_order': 3
    },
    {
        'title': 'Terms of Service',
        'content': terms_content,
        'meta_description': 'SafariSmart Kenya Terms of Service - Rules and guidelines for using our platform.',
        'footer_order': 4
    },
]

for page_data in pages:
    page, created = StaticPage.objects.get_or_create(
        title=page_data['title'],
        defaults=page_data
    )
    if created:
        print(f"✓ Created: {page.title}")
    else:
        print(f"- Already exists: {page.title}")

print("\n✅ Default pages setup complete!")
print("You can now edit these pages in the Django admin panel.")
