"""
Test quick trip parser
"""
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'safarismart.settings')
django.setup()

from core.services.quick_trip_parser import QuickTripParser

def test_parser():
    """Test various trip descriptions"""
    print("=" * 60)
    print("TESTING QUICK TRIP PARSER")
    print("=" * 60)
    
    parser = QuickTripParser()
    
    test_cases = [
        "2 days trip to Kakamega with 20000 budget",
        "3 days safari to Maasai Mara, budget 50000",
        "Weekend beach trip to Diani",
        "5 days family vacation to Nairobi and Mombasa with 150k budget",
        "solo trip to Amboseli for 4 days, 80000 shillings",
    ]
    
    for description in test_cases:
        print(f"\n📝 Input: \"{description}\"")
        print("-" * 60)
        
        result = parser.parse(description)
        
        print(f"✓ Duration: {result['duration_days']} days")
        print(f"✓ Budget: KSh {result['budget_amount']:,}")
        print(f"✓ Category: {result['budget_category']}")
        print(f"✓ Travel Type: {result['travel_type']}")
        print(f"✓ DB Destinations: {[d.name for d in result['destinations']]}")
        print(f"✓ Custom Destinations: {result['custom_destinations']}")
        print(f"✓ Interests: {result['interests']}")
    
    print("\n" + "=" * 60)
    print("TEST COMPLETE")
    print("=" * 60)

if __name__ == "__main__":
    test_parser()
