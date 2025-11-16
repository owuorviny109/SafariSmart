"""
Test quick trip validation
"""
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'safarismart.settings')
django.setup()

from core.services.quick_trip_parser import QuickTripParser

def test_validation():
    """Test input validation"""
    print("=" * 60)
    print("TESTING QUICK TRIP VALIDATION")
    print("=" * 60)
    
    parser = QuickTripParser()
    
    test_cases = [
        # Valid inputs
        ("2 days trip to Kakamega with 20000 budget", True, "Valid trip description"),
        ("3 days safari to Maasai Mara, budget 50000", True, "Valid with destination"),
        
        # Invalid inputs
        ("short", False, "Too short"),
        ("I want to travel", False, "No numbers"),
        ("SCREAMING ALL CAPS FOR NO REASON!!!", False, "All caps"),
        ("2 days trip!!!!!", False, "Excessive punctuation"),
        ("aaaaaaaaaa trip", False, "Repeated characters"),
        ("Visit http://spam.com for deals", False, "Contains URL"),
        ("Contact me at test@email.com", False, "Contains email"),
        ("Call 0712345678 for booking", False, "Contains phone"),
        ("This is a very long description that goes on and on and on and on and on and on and on and on and on and on and on and on and on and on and on and on and on and on and on and on and on and on", False, "Too long"),
    ]
    
    for description, should_be_valid, reason in test_cases:
        error = parser.validate_input(description)
        is_valid = error is None
        
        status = "✓" if is_valid == should_be_valid else "✗"
        
        print(f"\n{status} {reason}")
        print(f"   Input: \"{description[:50]}...\"" if len(description) > 50 else f"   Input: \"{description}\"")
        
        if is_valid:
            print(f"   Result: VALID")
        else:
            print(f"   Result: INVALID - {error}")
        
        if is_valid != should_be_valid:
            print(f"   ⚠️  UNEXPECTED RESULT!")
    
    print("\n" + "=" * 60)
    print("TEST COMPLETE")
    print("=" * 60)

if __name__ == "__main__":
    test_validation()
