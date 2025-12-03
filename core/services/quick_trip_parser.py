"""
Module: services/quick_trip_parser.py
Purpose: Parse natural language trip descriptions

This module parses user input like "2 days trip to Kakamega with 20000 budget"
and extracts structured data for itinerary generation.

Classes:
    QuickTripParser: Main parser for natural language trip descriptions
    
 
"""

import re
from typing import Dict, List, Optional
import logging
from destinations.models import Destination

logger = logging.getLogger(__name__)


class QuickTripValidationError(Exception):
    """Exception raised when quick trip input is invalid."""
    pass


class QuickTripParser:
    """
    Parser for natural language trip descriptions.
    
    Extracts duration, destinations, budget, and other trip details
    from free-form text input.
    
    Example:
        >>> parser = QuickTripParser()
        >>> data = parser.parse("2 days trip to Kakamega with 20000 budget")
        >>> print(data['duration_days'])
        2
    """
    
    # Patterns for extraction
    DURATION_PATTERN = r'(\d+)\s*(?:day|days|night|nights)'
    BUDGET_PATTERN = r'(?:budget|with|ksh|shillings)?\s*(\d+(?:,\d{3})*[kK]?)\s*(?:budget|ksh|shillings)?'
    DESTINATION_KEYWORDS = ['to', 'in', 'at', 'visit', 'safari', 'beach', 'trip to']
    
    # Profanity and spam patterns (basic list - expand as needed)
    BLOCKED_WORDS = [
        'fuck', 'shit', 'damn', 'bitch', 'ass', 'hell',
        'spam', 'click here', 'buy now', 'free money',
        'viagra', 'casino', 'lottery', 'winner'
    ]
    
    def validate_input(self, description: str) -> Optional[str]:
        """
        Validate user input before parsing.
        
        Args:
            description (str): User input
            
        Returns:
            Optional[str]: Error message if invalid, None if valid
        """
        # Length checks
        if len(description) < 15:
            return "Please provide more details. Include: days, destination, and budget."
        
        if len(description) > 200:
            return "Description too long. Please keep it under 200 characters."
        
        # Check for numbers (required for days/budget)
        if not re.search(r'\d+', description):
            return "Please include number of days and budget amount."
        
        # Check for excessive caps (spam indicator)
        if description.isupper() and len(description) > 20:
            return "Please use normal capitalization."
        
        # Check for excessive punctuation
        if len(re.findall(r'[!?]{2,}', description)) > 0:
            return "Please use less punctuation."
        
        # Check for profanity/spam
        description_lower = description.lower()
        for word in self.BLOCKED_WORDS:
            if word in description_lower:
                return "Please use appropriate language."
        
        # Check for repeated characters (spam indicator)
        if re.search(r'(.)\1{4,}', description):
            return "Please avoid repeating characters."
        
        # Check for URLs (spam indicator)
        if re.search(r'https?://|www\.', description, re.IGNORECASE):
            return "Please don't include URLs."
        
        # Check for email addresses (spam indicator)
        if re.search(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', description):
            return "Please don't include email addresses."
        
        # Check for phone numbers (spam indicator)
        if re.search(r'\b\d{10,}\b', description):
            # Allow budget numbers but block phone-like patterns
            if not re.search(r'(?:budget|ksh|shillings)', description_lower):
                return "Please don't include phone numbers."
        
        return None  # Valid
    
    def parse(self, description: str) -> Dict:
        """
        Parse natural language trip description.
        
        Args:
            description (str): User's trip description
            
        Returns:
            Dict: Structured trip data
            
        Example:
            >>> data = parser.parse("3 days safari to Maasai Mara, budget 50000")
            >>> data['duration_days']
            3
            >>> data['budget_amount']
            50000
        """
        description_lower = description.lower()
        
        # Extract duration
        duration_days = self._extract_duration(description_lower)
        
        # Extract budget
        budget_amount = self._extract_budget(description_lower)
        
        # Extract destinations
        destinations, custom_destinations = self._extract_destinations(description)
        
        # Determine budget category
        budget_category = self._determine_budget_category(budget_amount, duration_days)
        
        # Extract travel type hints
        travel_type = self._extract_travel_type(description_lower)
        
        # Build trip data
        trip_data = {
            'duration_days': duration_days,
            'budget_amount': budget_amount,
            'budget_category': budget_category,
            'destinations': destinations,
            'custom_destinations': custom_destinations,
            'adults_count': 2,  # Default
            'children_count': 0,
            'travel_type': travel_type,
            'interests': self._extract_interests(description_lower),
            'original_description': description
        }
        
        logger.info(f"Parsed quick trip: {duration_days} days, KSh {budget_amount}, {len(destinations)} destinations")
        
        return trip_data
    
    def _extract_duration(self, text: str) -> int:
        """
        Extract trip duration from text.
        
        Args:
            text (str): Input text
            
        Returns:
            int: Duration in days (default 3)
        """
        match = re.search(self.DURATION_PATTERN, text, re.IGNORECASE)
        if match:
            days = int(match.group(1))
            return max(1, min(days, 30))  # Limit 1-30 days
        
        # Default duration
        return 3
    
    def _extract_budget(self, text: str) -> int:
        """
        Extract budget amount from text.
        
        Args:
            text (str): Input text
            
        Returns:
            int: Budget in KSh (default 100000)
        """
        # Find all numbers that could be budgets
        number_patterns = [
            r'(?:budget|with)\s+(\d+(?:,\d{3})*[kK]?)',
            r'(\d+(?:,\d{3})*[kK]?)\s+(?:budget|ksh|shillings)',
            r'(\d{4,})',  # Any 4+ digit number
        ]
        
        for pattern in number_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                budget_str = match.group(1).replace(',', '')
                
                # Handle "k" suffix (e.g., "50k" = 50000)
                if budget_str.lower().endswith('k'):
                    budget = int(budget_str[:-1]) * 1000
                else:
                    budget = int(budget_str)
                
                # Only accept reasonable budgets
                if 5000 <= budget <= 10000000:
                    return budget
        
        # Default budget
        return 100000
    
    def _extract_destinations(self, text: str) -> tuple:
        """
        Extract destination names from text.
        
        Args:
            text (str): Input text
            
        Returns:
            tuple: (List[Destination], List[str]) - DB destinations and custom names
        """
        destinations = []
        custom_destinations = []
        
        # Get all destinations from database
        all_destinations = Destination.objects.all()
        
        # Check if any destination names appear in text
        for dest in all_destinations:
            # Check full name and common variations
            name_lower = dest.name.lower()
            if name_lower in text.lower():
                destinations.append(dest)
                continue
            
            # Check for partial matches (e.g., "Mara" for "Maasai Mara")
            words = name_lower.split()
            for word in words:
                if len(word) > 4 and word in text.lower():
                    destinations.append(dest)
                    break
        
        # If no database destinations found, try to extract custom destination
        if not destinations:
            custom_dest = self._extract_custom_destination(text)
            if custom_dest:
                custom_destinations.append(custom_dest)
        
        return destinations, custom_destinations
    
    def _extract_custom_destination(self, text: str) -> Optional[str]:
        """
        Extract custom destination name from text.
        
        Args:
            text (str): Input text
            
        Returns:
            Optional[str]: Destination name or None
        """
        # Look for patterns like "to X" or "in X"
        for keyword in self.DESTINATION_KEYWORDS:
            pattern = rf'{keyword}\s+([A-Z][a-zA-Z\s]+?)(?:\s+with|\s+budget|,|$)'
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                dest_name = match.group(1).strip()
                # Clean up common words
                dest_name = re.sub(r'\s+(with|budget|for|and)$', '', dest_name, flags=re.IGNORECASE)
                if len(dest_name) >= 3:
                    return dest_name.title()
        
        return None
    
    def _determine_budget_category(self, budget: int, days: int) -> str:
        """
        Determine budget category based on amount and duration.
        
        Args:
            budget (int): Total budget
            days (int): Trip duration
            
        Returns:
            str: Budget category (budget/mid-range/luxury)
        """
        per_day = budget / days if days > 0 else budget
        
        if per_day < 15000:
            return 'budget'
        elif per_day < 50000:
            return 'mid-range'
        else:
            return 'luxury'
    
    def _extract_travel_type(self, text: str) -> str:
        """
        Extract travel type from text.
        
        Args:
            text (str): Input text
            
        Returns:
            str: Travel type (solo/couple/family/friends)
        """
        if any(word in text for word in ['solo', 'alone', 'myself']):
            return 'solo'
        elif any(word in text for word in ['couple', 'romantic', 'honeymoon']):
            return 'couple'
        elif any(word in text for word in ['family', 'kids', 'children']):
            return 'family'
        else:
            return 'friends'
    
    def _extract_interests(self, text: str) -> List[str]:
        """
        Extract interests from text.
        
        Args:
            text (str): Input text
            
        Returns:
            List[str]: List of interests
        """
        interests = []
        
        interest_keywords = {
            'wildlife': ['wildlife', 'safari', 'animals', 'game drive'],
            'beach': ['beach', 'ocean', 'swimming', 'diving'],
            'adventure': ['adventure', 'hiking', 'climbing', 'trekking'],
            'culture': ['culture', 'cultural', 'traditional', 'village'],
            'relaxation': ['relax', 'relaxation', 'spa', 'peaceful'],
            'photography': ['photo', 'photography', 'pictures'],
            'food': ['food', 'culinary', 'dining', 'restaurant'],
        }
        
        for interest, keywords in interest_keywords.items():
            if any(keyword in text for keyword in keywords):
                interests.append(interest)
        
        # Default interests if none found
        if not interests:
            interests = ['wildlife', 'nature']
        
        return interests
