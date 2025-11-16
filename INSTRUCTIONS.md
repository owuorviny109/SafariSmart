# SafariSmart Kenya - Development Instructions

## Code Quality Standards

This document defines the coding standards and architectural principles for SafariSmart Kenya. All code must adhere to these guidelines.

---

## 1. OBJECT-ORIENTED PROGRAMMING (OOP) PRINCIPLES

### 1.1 Mandatory OOP Approach
- All business logic MUST be encapsulated in classes
- NO procedural code or loose functions for business logic
- Use Django Class-Based Views (CBV) instead of function-based views where appropriate
- Create service classes for complex operations

### 1.2 SOLID Principles
All code must follow SOLID principles:

**S - Single Responsibility Principle**
- Each class should have ONE reason to change
- Separate concerns into distinct classes
- Example: `ItineraryGenerator` only generates itineraries, `ItineraryValidator` only validates

**O - Open/Closed Principle**
- Classes should be open for extension, closed for modification
- Use inheritance and polymorphism
- Example: Base `DestinationFilter` class, extended by `SafariFilter`, `BeachFilter`

**L - Liskov Substitution Principle**
- Derived classes must be substitutable for their base classes
- Maintain consistent interfaces

**I - Interface Segregation Principle**
- Many specific interfaces are better than one general interface
- Use abstract base classes (ABC) for contracts

**D - Dependency Inversion Principle**
- Depend on abstractions, not concretions
- Use dependency injection
- Example: Inject `GeminiService` into `ItineraryGenerator`

### 1.3 Class Structure Requirements

Every class must have:
```python
class ExampleService:
    """
    Brief description of class purpose.
    
    This class handles [specific responsibility].
    
    Attributes:
        attribute_name (type): Description of attribute
        
    Methods:
        method_name: Brief description
        
    Example:
        >>> service = ExampleService(param1, param2)
        >>> result = service.process()
    """
    
    def __init__(self, dependency: DependencyType):
        """
        Initialize the service with required dependencies.
        
        Args:
            dependency (DependencyType): Description of dependency
            
        Raises:
            ValueError: If dependency is invalid
        """
        self._validate_dependency(dependency)
        self._dependency = dependency
        
    def public_method(self, param: str) -> dict:
        """
        Public method description.
        
        Args:
            param (str): Description of parameter
            
        Returns:
            dict: Description of return value
            
        Raises:
            CustomException: When specific condition occurs
        """
        # Implementation
        pass
        
    def _private_method(self) -> None:
        """
        Private helper method description.
        
        This method is internal and should not be called externally.
        """
        # Implementation
        pass
```

---

## 2. DATA STRUCTURES AND ALGORITHMS

### 2.1 Appropriate Data Structure Selection

Choose data structures based on use case:

**Lists** - For ordered collections with frequent iteration
```python
class DestinationList:
    """Manages an ordered collection of destinations."""
    
    def __init__(self):
        self._destinations: List[Destination] = []
        
    def add(self, destination: Destination) -> None:
        """Add destination maintaining order."""
        self._destinations.append(destination)
```

**Dictionaries** - For key-value lookups (O(1) access)
```python
class DestinationCache:
    """Fast lookup cache for destinations by slug."""
    
    def __init__(self):
        self._cache: Dict[str, Destination] = {}
        
    def get(self, slug: str) -> Optional[Destination]:
        """Retrieve destination by slug in O(1) time."""
        return self._cache.get(slug)
```

**Sets** - For unique collections and membership testing
```python
class SelectedDestinations:
    """Manages unique set of selected destinations."""
    
    def __init__(self):
        self._selected: Set[int] = set()
        
    def add(self, destination_id: int) -> bool:
        """Add destination if not already selected."""
        if destination_id in self._selected:
            return False
        self._selected.add(destination_id)
        return True
```

**Queues/Deques** - For FIFO operations
```python
from collections import deque

class ItineraryQueue:
    """Queue for processing itinerary generation requests."""
    
    def __init__(self):
        self._queue: deque = deque()
```

### 2.2 Algorithm Complexity Requirements

- Document time and space complexity for all algorithms
- Optimize for O(n log n) or better where possible
- Avoid nested loops (O(n²)) unless necessary

```python
class RouteOptimizer:
    """
    Optimizes travel routes between destinations.
    
    Uses Dijkstra's algorithm for shortest path calculation.
    Time Complexity: O((V + E) log V) where V=vertices, E=edges
    Space Complexity: O(V)
    """
    
    def find_shortest_path(
        self, 
        start: Destination, 
        end: Destination
    ) -> List[Destination]:
        """
        Find shortest path between two destinations.
        
        Algorithm: Dijkstra's shortest path
        Time Complexity: O((V + E) log V)
        Space Complexity: O(V)
        
        Args:
            start (Destination): Starting destination
            end (Destination): Target destination
            
        Returns:
            List[Destination]: Ordered list of destinations in path
        """
        # Implementation with heap queue
        pass
```

### 2.3 Design Patterns

Use appropriate design patterns:

**Factory Pattern** - For object creation
```python
class ItineraryFactory:
    """Factory for creating different types of itineraries."""
    
    @staticmethod
    def create(itinerary_type: str, **kwargs) -> BaseItinerary:
        """Create itinerary based on type."""
        if itinerary_type == 'safari':
            return SafariItinerary(**kwargs)
        elif itinerary_type == 'beach':
            return BeachItinerary(**kwargs)
        raise ValueError(f"Unknown type: {itinerary_type}")
```

**Strategy Pattern** - For interchangeable algorithms
```python
class BudgetCalculationStrategy(ABC):
    """Abstract base for budget calculation strategies."""
    
    @abstractmethod
    def calculate(self, itinerary: Itinerary) -> Decimal:
        """Calculate total budget."""
        pass

class LuxuryBudgetStrategy(BudgetCalculationStrategy):
    """Budget calculation for luxury trips."""
    
    def calculate(self, itinerary: Itinerary) -> Decimal:
        """Calculate with luxury multipliers."""
        pass
```

**Observer Pattern** - For event handling
```python
class ItineraryObserver(ABC):
    """Observer for itinerary changes."""
    
    @abstractmethod
    def update(self, itinerary: Itinerary) -> None:
        """Called when itinerary changes."""
        pass
```

**Singleton Pattern** - For single instance services
```python
class GeminiService:
    """Singleton service for Gemini AI integration."""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
```

---

## 3. DOCUMENTATION REQUIREMENTS

### 3.1 Module-Level Documentation
Every Python file must start with:
```python
"""
Module: module_name.py
Purpose: Brief description of module purpose

This module contains classes and functions for [specific functionality].

Classes:
    ClassName: Brief description
    
Functions:
    function_name: Brief description
    
Author: SafariSmart Kenya Team
Date: YYYY-MM-DD
"""
```

### 3.2 Class Documentation
Use Google-style docstrings:
```python
class ItineraryGenerator:
    """
    Generates personalized travel itineraries using AI.
    
    This class orchestrates the itinerary generation process by:
    1. Validating user preferences
    2. Calling Gemini AI service
    3. Parsing and structuring the response
    4. Saving to database
    
    Attributes:
        gemini_service (GeminiService): AI service for generation
        validator (ItineraryValidator): Validates generated itineraries
        
    Example:
        >>> generator = ItineraryGenerator(gemini_service, validator)
        >>> itinerary = generator.generate(wizard_data)
        >>> print(itinerary.title)
        'Amazing Kenya Safari Adventure'
    """
```

### 3.3 Method Documentation
Every method must have:
```python
def generate_itinerary(
    self, 
    destinations: List[Destination],
    duration: int,
    budget: Decimal
) -> Itinerary:
    """
    Generate a complete travel itinerary.
    
    This method creates a day-by-day itinerary based on user preferences.
    It uses AI to optimize routes and suggest activities.
    
    Args:
        destinations (List[Destination]): Selected destinations
        duration (int): Trip duration in days (1-30)
        budget (Decimal): Total budget in KSh
        
    Returns:
        Itinerary: Generated itinerary with daily plans
        
    Raises:
        ValueError: If duration is invalid or destinations empty
        InsufficientBudgetError: If budget too low for destinations
        AIServiceError: If AI generation fails
        
    Example:
        >>> destinations = [maasai_mara, diani_beach]
        >>> itinerary = generator.generate_itinerary(
        ...     destinations=destinations,
        ...     duration=7,
        ...     budget=Decimal('150000')
        ... )
        >>> len(itinerary.days)
        7
    """
    # Validate inputs
    self._validate_inputs(destinations, duration, budget)
    
    # Generate using AI
    ai_response = self._call_ai_service(destinations, duration, budget)
    
    # Parse and structure
    itinerary = self._parse_response(ai_response)
    
    # Validate output
    self.validator.validate(itinerary)
    
    return itinerary
```

### 3.4 Inline Comments
- Comment WHY, not WHAT
- Explain complex algorithms
- Document edge cases

```python
# Calculate optimal route using Dijkstra's algorithm
# We use this instead of A* because we don't have reliable
# heuristic data for Kenyan road conditions
route = self._dijkstra(start, end)

# Edge case: If only one destination, skip route optimization
if len(destinations) == 1:
    return destinations
```

---

## 4. TYPE HINTS AND VALIDATION

### 4.1 Type Hints Required
All functions and methods must have type hints:
```python
from typing import List, Dict, Optional, Union, Tuple
from decimal import Decimal

def calculate_cost(
    destinations: List[Destination],
    duration: int,
    budget_category: str
) -> Tuple[Decimal, Dict[str, Decimal]]:
    """Calculate total cost and breakdown."""
    pass
```

### 4.2 Input Validation
Validate all inputs at class boundaries:
```python
class ItineraryValidator:
    """Validates itinerary data."""
    
    def validate_duration(self, duration: int) -> None:
        """
        Validate trip duration.
        
        Args:
            duration (int): Duration in days
            
        Raises:
            ValueError: If duration is invalid
        """
        if not isinstance(duration, int):
            raise TypeError("Duration must be an integer")
            
        if duration < 1:
            raise ValueError("Duration must be at least 1 day")
            
        if duration > 30:
            raise ValueError("Duration cannot exceed 30 days")
```

---

## 5. ERROR HANDLING

### 5.1 Custom Exceptions
Create specific exception classes:
```python
class SafariSmartException(Exception):
    """Base exception for SafariSmart application."""
    pass

class ItineraryGenerationError(SafariSmartException):
    """Raised when itinerary generation fails."""
    pass

class InsufficientBudgetError(SafariSmartException):
    """Raised when budget is too low."""
    
    def __init__(self, required: Decimal, provided: Decimal):
        self.required = required
        self.provided = provided
        super().__init__(
            f"Budget insufficient. Required: {required}, Provided: {provided}"
        )
```

### 5.2 Error Handling Pattern
```python
class ItineraryService:
    """Service for itinerary operations."""
    
    def generate(self, wizard_data: dict) -> Itinerary:
        """
        Generate itinerary with comprehensive error handling.
        
        Args:
            wizard_data (dict): User preferences from wizard
            
        Returns:
            Itinerary: Generated itinerary
            
        Raises:
            ItineraryGenerationError: If generation fails
        """
        try:
            # Validate input
            self._validate_wizard_data(wizard_data)
            
            # Generate itinerary
            itinerary = self._generate_from_ai(wizard_data)
            
            # Validate output
            self._validate_itinerary(itinerary)
            
            return itinerary
            
        except ValueError as e:
            # Log and re-raise as domain exception
            logger.error(f"Invalid wizard data: {e}")
            raise ItineraryGenerationError(f"Invalid input: {e}") from e
            
        except AIServiceError as e:
            # Log and provide fallback
            logger.error(f"AI service failed: {e}")
            return self._generate_fallback_itinerary(wizard_data)
            
        except Exception as e:
            # Catch-all for unexpected errors
            logger.exception("Unexpected error in itinerary generation")
            raise ItineraryGenerationError(
                "An unexpected error occurred"
            ) from e
```

---

## 6. TESTING REQUIREMENTS

### 6.1 Unit Tests
Every class must have corresponding unit tests:
```python
class TestItineraryGenerator(TestCase):
    """Unit tests for ItineraryGenerator class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.gemini_service = Mock(spec=GeminiService)
        self.validator = Mock(spec=ItineraryValidator)
        self.generator = ItineraryGenerator(
            self.gemini_service,
            self.validator
        )
        
    def test_generate_with_valid_input(self):
        """Test generation with valid inputs."""
        # Arrange
        destinations = [self._create_destination()]
        duration = 7
        budget = Decimal('100000')
        
        # Act
        result = self.generator.generate_itinerary(
            destinations, duration, budget
        )
        
        # Assert
        self.assertIsInstance(result, Itinerary)
        self.assertEqual(result.duration_days, duration)
        
    def test_generate_with_invalid_duration_raises_error(self):
        """Test that invalid duration raises ValueError."""
        # Arrange
        destinations = [self._create_destination()]
        
        # Act & Assert
        with self.assertRaises(ValueError):
            self.generator.generate_itinerary(
                destinations, duration=0, budget=Decimal('100000')
            )
```

---

## 7. DJANGO-SPECIFIC GUIDELINES

### 7.1 Use Class-Based Views
Prefer CBVs over function-based views:
```python
class DestinationListView(ListView):
    """
    Display list of all destinations.
    
    Attributes:
        model: Destination model
        template_name: Template for rendering
        context_object_name: Name in template context
    """
    model = Destination
    template_name = 'destinations/list.html'
    context_object_name = 'destinations'
    paginate_by = 20
    
    def get_queryset(self):
        """
        Get filtered queryset based on query parameters.
        
        Returns:
            QuerySet: Filtered destinations
        """
        queryset = super().get_queryset()
        destination_type = self.request.GET.get('type')
        
        if destination_type:
            queryset = queryset.filter(destination_type=destination_type)
            
        return queryset.select_related().prefetch_related('activities')
```

### 7.2 Service Layer Pattern
Separate business logic from views:
```python
# services/itinerary_service.py
class ItineraryService:
    """Service layer for itinerary operations."""
    
    def __init__(
        self,
        generator: ItineraryGenerator,
        repository: ItineraryRepository
    ):
        """Initialize with dependencies."""
        self._generator = generator
        self._repository = repository
        
    def create_itinerary(self, wizard_data: dict, user: User) -> Itinerary:
        """
        Create and save new itinerary.
        
        Args:
            wizard_data (dict): User preferences
            user (User): User creating itinerary
            
        Returns:
            Itinerary: Created itinerary
        """
        # Generate itinerary
        itinerary = self._generator.generate(wizard_data)
        
        # Associate with user
        itinerary.user = user
        
        # Save to database
        self._repository.save(itinerary)
        
        return itinerary

# views.py
class CreateItineraryView(View):
    """View for creating itineraries."""
    
    def __init__(self):
        """Initialize with service."""
        self.service = ItineraryService(
            ItineraryGenerator(),
            ItineraryRepository()
        )
        
    def post(self, request):
        """Handle itinerary creation."""
        wizard_data = request.session.get('wizard_data')
        itinerary = self.service.create_itinerary(wizard_data, request.user)
        return redirect('itinerary_detail', share_code=itinerary.share_code)
```

---

## 8. CODE REVIEW CHECKLIST

Before submitting code, verify:

- [ ] All classes follow SOLID principles
- [ ] Appropriate data structures used
- [ ] Algorithm complexity documented
- [ ] All methods have docstrings
- [ ] Type hints on all functions
- [ ] Input validation implemented
- [ ] Custom exceptions used
- [ ] Error handling comprehensive
- [ ] Unit tests written
- [ ] No code duplication (DRY)
- [ ] No magic numbers (use constants)
- [ ] Logging implemented
- [ ] No TODO comments in production code

---

## 9. EXAMPLE: COMPLETE CLASS IMPLEMENTATION

```python
"""
Module: services/gemini_service.py
Purpose: Integration with Google Gemini AI for itinerary generation

This module provides a service class for interacting with the Gemini AI API.

Classes:
    GeminiService: Main service for AI interactions
    GeminiPromptBuilder: Builds prompts for AI
    GeminiResponseParser: Parses AI responses
    
Author: SafariSmart Kenya Team
Date: 2025-11-16
"""

from typing import Dict, List, Optional
from decimal import Decimal
import logging
from abc import ABC, abstractmethod

import google.generativeai as genai
from django.conf import settings

from core.models import Destination, Itinerary
from core.exceptions import AIServiceError, InvalidResponseError


logger = logging.getLogger(__name__)


class PromptBuilder(ABC):
    """Abstract base class for prompt builders."""
    
    @abstractmethod
    def build(self, **kwargs) -> str:
        """Build prompt string."""
        pass


class GeminiPromptBuilder(PromptBuilder):
    """
    Builds structured prompts for Gemini AI.
    
    This class constructs prompts that guide the AI to generate
    well-structured itineraries in JSON format.
    
    Attributes:
        template (str): Base template for prompts
        
    Example:
        >>> builder = GeminiPromptBuilder()
        >>> prompt = builder.build(
        ...     destinations=['Maasai Mara', 'Diani Beach'],
        ...     duration=7,
        ...     budget=150000
        ... )
    """
    
    TEMPLATE = """
    Create a detailed {duration}-day Kenya travel itinerary.
    
    Destinations: {destinations}
    Budget: KSh {budget}
    Travel Type: {travel_type}
    Interests: {interests}
    
    Return JSON with this structure:
    {{
        "title": "Trip title",
        "days": [
            {{
                "day": 1,
                "location": "Location name",
                "activities": ["Activity 1", "Activity 2"],
                "accommodation": "Hotel suggestion",
                "meals": ["Breakfast", "Lunch", "Dinner"],
                "estimated_cost": 15000
            }}
        ],
        "total_cost": 105000,
        "cost_breakdown": {{
            "accommodation": 50000,
            "activities": 30000,
            "meals": 20000,
            "transport": 5000
        }}
    }}
    """
    
    def build(
        self,
        destinations: List[str],
        duration: int,
        budget: Decimal,
        travel_type: str,
        interests: List[str]
    ) -> str:
        """
        Build prompt from parameters.
        
        Args:
            destinations (List[str]): Destination names
            duration (int): Trip duration in days
            budget (Decimal): Total budget in KSh
            travel_type (str): Type of travel (solo, family, etc.)
            interests (List[str]): User interests
            
        Returns:
            str: Formatted prompt
            
        Raises:
            ValueError: If parameters are invalid
        """
        self._validate_parameters(destinations, duration, budget)
        
        return self.TEMPLATE.format(
            duration=duration,
            destinations=', '.join(destinations),
            budget=budget,
            travel_type=travel_type,
            interests=', '.join(interests)
        )
        
    def _validate_parameters(
        self,
        destinations: List[str],
        duration: int,
        budget: Decimal
    ) -> None:
        """
        Validate prompt parameters.
        
        Args:
            destinations (List[str]): Destination names
            duration (int): Trip duration
            budget (Decimal): Budget amount
            
        Raises:
            ValueError: If any parameter is invalid
        """
        if not destinations:
            raise ValueError("Destinations list cannot be empty")
            
        if duration < 1 or duration > 30:
            raise ValueError("Duration must be between 1 and 30 days")
            
        if budget <= 0:
            raise ValueError("Budget must be positive")


class GeminiService:
    """
    Service for interacting with Google Gemini AI.
    
    This service handles all communication with the Gemini API,
    including prompt building, API calls, and response parsing.
    
    Attributes:
        model: Gemini AI model instance
        prompt_builder: Builder for creating prompts
        
    Example:
        >>> service = GeminiService()
        >>> itinerary_data = service.generate_itinerary(
        ...     destinations=['Maasai Mara'],
        ...     duration=5,
        ...     budget=Decimal('100000')
        ... )
    """
    
    def __init__(
        self,
        prompt_builder: Optional[PromptBuilder] = None,
        api_key: Optional[str] = None
    ):
        """
        Initialize Gemini service.
        
        Args:
            prompt_builder (PromptBuilder, optional): Custom prompt builder
            api_key (str, optional): API key, defaults to settings
            
        Raises:
            AIServiceError: If API key is missing or invalid
        """
        self._api_key = api_key or settings.GEMINI_API_KEY
        self._validate_api_key()
        
        self.prompt_builder = prompt_builder or GeminiPromptBuilder()
        self._initialize_model()
        
    def _validate_api_key(self) -> None:
        """
        Validate API key is present.
        
        Raises:
            AIServiceError: If API key is missing
        """
        if not self._api_key:
            raise AIServiceError("Gemini API key not configured")
            
    def _initialize_model(self) -> None:
        """Initialize Gemini model with configuration."""
        try:
            genai.configure(api_key=self._api_key)
            self.model = genai.GenerativeModel('gemini-pro')
            logger.info("Gemini model initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Gemini model: {e}")
            raise AIServiceError("Failed to initialize AI service") from e
            
    def generate_itinerary(
        self,
        destinations: List[str],
        duration: int,
        budget: Decimal,
        travel_type: str = 'family',
        interests: Optional[List[str]] = None
    ) -> Dict:
        """
        Generate itinerary using Gemini AI.
        
        This method orchestrates the entire generation process:
        1. Build prompt
        2. Call AI API
        3. Parse response
        4. Validate structure
        
        Args:
            destinations (List[str]): Destination names
            duration (int): Trip duration in days
            budget (Decimal): Total budget in KSh
            travel_type (str): Type of travel
            interests (List[str], optional): User interests
            
        Returns:
            Dict: Structured itinerary data
            
        Raises:
            AIServiceError: If generation fails
            InvalidResponseError: If response is malformed
            
        Example:
            >>> service = GeminiService()
            >>> data = service.generate_itinerary(
            ...     destinations=['Maasai Mara', 'Amboseli'],
            ...     duration=7,
            ...     budget=Decimal('150000'),
            ...     travel_type='family',
            ...     interests=['wildlife', 'photography']
            ... )
            >>> print(data['title'])
            'Amazing Kenya Safari Adventure'
        """
        interests = interests or []
        
        try:
            # Build prompt
            prompt = self.prompt_builder.build(
                destinations=destinations,
                duration=duration,
                budget=budget,
                travel_type=travel_type,
                interests=interests
            )
            
            logger.info(f"Generating itinerary for {len(destinations)} destinations")
            
            # Call AI API
            response = self._call_api(prompt)
            
            # Parse response
            itinerary_data = self._parse_response(response)
            
            # Validate structure
            self._validate_response(itinerary_data)
            
            logger.info("Itinerary generated successfully")
            return itinerary_data
            
        except Exception as e:
            logger.error(f"Itinerary generation failed: {e}")
            raise AIServiceError(f"Failed to generate itinerary: {e}") from e
            
    def _call_api(self, prompt: str) -> str:
        """
        Call Gemini API with prompt.
        
        Args:
            prompt (str): Formatted prompt
            
        Returns:
            str: Raw API response
            
        Raises:
            AIServiceError: If API call fails
        """
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            logger.error(f"API call failed: {e}")
            raise AIServiceError("AI service unavailable") from e
            
    def _parse_response(self, response: str) -> Dict:
        """
        Parse JSON response from AI.
        
        Args:
            response (str): Raw response text
            
        Returns:
            Dict: Parsed JSON data
            
        Raises:
            InvalidResponseError: If response is not valid JSON
        """
        import json
        
        try:
            # Extract JSON from response (may have markdown formatting)
            json_start = response.find('{')
            json_end = response.rfind('}') + 1
            json_str = response[json_start:json_end]
            
            return json.loads(json_str)
        except (ValueError, json.JSONDecodeError) as e:
            logger.error(f"Failed to parse response: {e}")
            raise InvalidResponseError("Invalid AI response format") from e
            
    def _validate_response(self, data: Dict) -> None:
        """
        Validate response structure.
        
        Args:
            data (Dict): Parsed response data
            
        Raises:
            InvalidResponseError: If structure is invalid
        """
        required_fields = ['title', 'days', 'total_cost', 'cost_breakdown']
        
        for field in required_fields:
            if field not in data:
                raise InvalidResponseError(f"Missing required field: {field}")
                
        if not isinstance(data['days'], list):
            raise InvalidResponseError("'days' must be a list")
            
        if len(data['days']) == 0:
            raise InvalidResponseError("'days' cannot be empty")
```

---

## 10. NAMING CONVENTIONS

### Python Code

#### Classes
**Convention:** `PascalCase` (CapitalizedWords)

**Examples:**
```python
✅ DestinationSelectionView
✅ DurationSelectionView
✅ WizardService
✅ WizardSessionManager

❌ WizardStep1View  # Don't use numbers
❌ wizard_service   # Not snake_case for classes
```

#### Functions and Methods
**Convention:** `snake_case` (lowercase_with_underscores)

**Examples:**
```python
✅ save_destinations()
✅ get_selected_destinations()
✅ validate_duration()

❌ saveDestinations()     # Not camelCase
❌ save_step_1_data()     # Avoid numbers
```

#### Variables
**Convention:** `snake_case`

#### Constants
**Convention:** `UPPER_SNAKE_CASE`

### Files and Directories

#### Python Files
**Convention:** `snake_case.py`

**Examples:**
```
✅ wizard_service.py
✅ destination_selection.py

❌ WizardService.py        # Not PascalCase
❌ wizardStep1.py          # Not camelCase
```

#### Template Files
**Convention:** `snake_case.html` or `descriptive_name.html`

**Examples:**
```
✅ destination_selection.html
✅ duration_selection.html

❌ wizard_step_1.html      # Don't use numbers
❌ WizardStep1.html        # Not PascalCase
```

### URLs

#### URL Patterns
**Convention:** `kebab-case` (lowercase-with-hyphens)

**Examples:**
```python
✅ path('wizard/destinations/', ...)
✅ path('wizard/travel-group/', ...)

❌ path('wizard/step_1/', ...)        # Not snake_case
❌ path('wizard/travelGroup/', ...)   # Not camelCase
```

#### URL Names
**Convention:** `snake_case`

**Examples:**
```python
✅ name='destination_selection'
✅ name='travel_group_selection'

❌ name='wizard_step_1'        # Don't use numbers
❌ name='destinationSelection' # Not camelCase
```

### View Names

#### Class-Based Views
**Convention:** `DescriptiveNameView`

**Pattern:** `[Purpose][Action]View`

**Examples:**
```python
✅ DestinationSelectionView
✅ DurationSelectionView
✅ ItineraryDetailView

❌ WizardStep1View         # Don't use numbers
❌ Step1View               # Not descriptive enough
```

### Service Layer

**Convention:** `PurposeService` or `PurposeManager`

**Examples:**
```python
✅ WizardService
✅ WizardSessionManager
✅ GeminiService

❌ WizardServiceClass      # Don't add "Class"
❌ wizard_service          # Not snake_case for classes
```

### Summary Table

| Element | Convention | Example |
|---------|-----------|---------|
| Classes | PascalCase | `DestinationSelectionView` |
| Functions | snake_case | `save_destinations()` |
| Variables | snake_case | `destination_ids` |
| Constants | UPPER_SNAKE_CASE | `MAX_DURATION_DAYS` |
| Files | snake_case.py | `wizard_service.py` |
| Templates | snake_case.html | `destination_selection.html` |
| URLs | kebab-case | `/wizard/travel-group/` |
| URL Names | snake_case | `travel_group_selection` |

---

## 11. FILE ORGANIZATION AND CODE SPLITTING

### Maximum File Size Guidelines

**GUIDELINE: Aim to keep files under 500 lines when possible.**

**However, there are valid exceptions:**

#### When to Keep Files Together (Even if >500 lines)

**Valid Reasons to Exceed 500 Lines:**

1. **Cohesive Functionality**
   - All code serves ONE clear purpose
   - Splitting would break logical flow
   - Example: `wizard_service.py` with all wizard operations

2. **Related Views**
   - Multiple views for same feature
   - Share common logic and context
   - Example: All wizard step views in one file

3. **Model Definitions**
   - Complex model with many fields
   - Related model methods
   - Manager classes for same model

4. **API Endpoints**
   - All endpoints for one resource
   - Shared serializers and permissions
   - RESTful resource operations

**Key Question: "Would splitting make it HARDER to understand?"**

If YES → Keep together even if large
If NO → Split into smaller files

### Why This Matters

**Problems with Large Files:**
- Hard to navigate and find code
- Difficult to understand and maintain
- Merge conflicts in version control
- Violates Single Responsibility Principle
- Slows down IDE performance
- Makes code reviews painful

**Benefits of Small Files:**
- Easy to locate specific functionality
- Clear separation of concerns
- Easier to test individual components
- Better code organization
- Faster to load and navigate
- Simpler code reviews

### How to Split Files

#### Views (core/views.py)

**BAD - Everything in one file:**
```python
# core/views.py (1000+ lines)
class DestinationSelectionView(View):
    pass

class DurationSelectionView(View):
    pass

class TravelGroupSelectionView(View):
    pass

class BudgetSelectionView(View):
    pass

class InterestsSelectionView(View):
    pass
```

**GOOD - Split by feature:**
```python
# core/views/__init__.py
from .landing import landing_page
from .wizard_views import (
    DestinationSelectionView,
    DurationSelectionView,
    TravelGroupSelectionView,
    BudgetSelectionView,
    InterestsSelectionView
)
from .itinerary_views import (
    ItineraryDetailView,
    SharedItineraryView
)
from .dashboard_views import DashboardView

# core/views/wizard_views.py (200 lines)
class DestinationSelectionView(View):
    pass

class DurationSelectionView(View):
    pass

# core/views/itinerary_views.py (150 lines)
class ItineraryDetailView(View):
    pass
```

#### Services (core/services/)

**BAD - One giant service:**
```python
# core/services/wizard_service.py (800+ lines)
class WizardService:
    # 50 methods handling everything
    pass
```

**GOOD - Split by responsibility:**
```python
# core/services/wizard_session_manager.py
class WizardSessionManager:
    """Handles session operations only."""
    pass

# core/services/wizard_validator.py
class WizardValidator:
    """Handles validation only."""
    pass

# core/services/wizard_service.py
class WizardService:
    """Orchestrates wizard operations."""
    def __init__(self):
        self.session_manager = WizardSessionManager()
        self.validator = WizardValidator()
```

#### Models

**BAD - All models in one file:**
```python
# core/models.py (600+ lines)
class Destination(models.Model):
    pass

class Itinerary(models.Model):
    pass

class WizardSession(models.Model):
    pass

class Review(models.Model):
    pass
```

**GOOD - Split by domain:**
```python
# core/models/__init__.py
from .destination import Destination
from .itinerary import Itinerary
from .wizard import WizardSession
from .review import Review

# core/models/destination.py (100 lines)
class Destination(models.Model):
    pass

# core/models/itinerary.py (150 lines)
class Itinerary(models.Model):
    pass
```

### File Organization Patterns

#### Pattern 1: Feature-Based Organization
```
core/
├── views/
│   ├── __init__.py
│   ├── landing.py          # Landing page views
│   ├── wizard_views.py     # Wizard step views
│   ├── itinerary_views.py  # Itinerary views
│   └── dashboard_views.py  # Dashboard views
├── services/
│   ├── __init__.py
│   ├── wizard_service.py
│   ├── itinerary_service.py
│   └── gemini_service.py
└── models/
    ├── __init__.py
    ├── destination.py
    ├── itinerary.py
    └── wizard.py
```

#### Pattern 2: Component-Based Organization
```
core/
├── wizard/
│   ├── __init__.py
│   ├── views.py
│   ├── services.py
│   ├── models.py
│   └── validators.py
├── itinerary/
│   ├── __init__.py
│   ├── views.py
│   ├── services.py
│   └── models.py
└── dashboard/
    ├── __init__.py
    └── views.py
```

### When to Split a File

**MUST Split When:**
- File has MULTIPLE unrelated responsibilities
- Contains classes from different domains
- Mixing different layers (views + services + models)
- Causes frequent merge conflicts
- Code review is confusing due to mixed concerns

**SHOULD Split When:**
- File exceeds 1000 lines
- Contains more than 10 classes
- Has multiple independent features
- Difficult to find specific code
- Takes more than 5 seconds to scroll through

**MAY Keep Together When:**
- File is 500-1000 lines but cohesive
- All code serves ONE clear purpose
- Splitting would require complex imports
- Related functionality that's easier to understand together
- Single feature with multiple related components

**Example: Our Current Files**

```python
# core/views.py (904 lines)
# Contains: All wizard views (5 steps)
# Decision: KEEP TOGETHER
# Reason: All views are for wizard feature, share context,
#         easier to see full wizard flow in one place

# core/services/wizard_service.py (614 lines)  
# Contains: All wizard business logic
# Decision: KEEP TOGETHER
# Reason: Single responsibility (wizard operations),
#         methods are interdependent, cohesive unit
```

**Counter-Example: When to Split**

```python
# BAD: core/views.py (1500 lines)
# Contains: Wizard views + Dashboard + Admin + API + Reports
# Decision: MUST SPLIT
# Reason: Multiple unrelated features, different domains

# GOOD: Split into:
# - core/views/wizard.py (500 lines)
# - core/views/dashboard.py (300 lines)  
# - core/views/admin.py (400 lines)
# - core/views/api.py (300 lines)
```

### Refactoring Checklist

When splitting a large file:

1. **Identify Logical Groups**
   - Group related classes/functions
   - Look for natural boundaries
   - Consider Single Responsibility Principle

2. **Create New Files**
   - Use descriptive names
   - Follow naming conventions
   - Add proper docstrings

3. **Update Imports**
   - Create __init__.py with exports
   - Update all import statements
   - Test that nothing breaks

4. **Verify Functionality**
   - Run tests
   - Check for import errors
   - Ensure all features work

### Example: Splitting core/views.py

**Current State (Too Large):**
```python
# core/views.py (1000+ lines)
# Contains: landing, 5 wizard views, itinerary views, dashboard
```

**Refactored Structure:**
```python
# core/views/__init__.py
"""
Module: views package
Purpose: View layer for core application

This package contains all view classes organized by feature.
"""

from .landing import landing_page
from .wizard import (
    DestinationSelectionView,
    DurationSelectionView,
    TravelGroupSelectionView,
    BudgetSelectionView,
    InterestsSelectionView
)
from .itinerary import ItineraryDetailView, SharedItineraryView
from .dashboard import DashboardView

__all__ = [
    'landing_page',
    'DestinationSelectionView',
    'DurationSelectionView',
    'TravelGroupSelectionView',
    'BudgetSelectionView',
    'InterestsSelectionView',
    'ItineraryDetailView',
    'SharedItineraryView',
    'DashboardView',
]

# core/views/landing.py (50 lines)
"""Landing page view."""

def landing_page(request):
    pass

# core/views/wizard.py (300 lines)
"""Wizard step views."""

class DestinationSelectionView(View):
    pass

class DurationSelectionView(View):
    pass

# core/views/itinerary.py (200 lines)
"""Itinerary display views."""

class ItineraryDetailView(View):
    pass

# core/views/dashboard.py (100 lines)
"""User dashboard views."""

class DashboardView(View):
    pass
```

### Enforcement

**Code Review Requirements:**
- [ ] Each file has single, clear purpose (CRITICAL)
- [ ] Files over 1000 lines must be justified
- [ ] No mixing of unrelated concerns
- [ ] Related code is grouped together
- [ ] Imports are clean and organized
- [ ] __init__.py properly exports public API when split

**File Size Thresholds:**
- **< 500 lines**: ✅ Ideal
- **500-1000 lines**: ⚠️ Acceptable if cohesive
- **> 1000 lines**: 🚫 Requires justification or split

**Automated Checks:**
```bash
# Check for files over 1000 lines (warning threshold)
find . -name "*.py" -exec wc -l {} \; | awk '$1 > 1000 {print}'
```

**Pull Request Guidelines:**
- Files under 1000 lines: Generally accepted
- Files over 1000 lines: Reviewer must verify single responsibility
- Files with mixed concerns: Must be split regardless of size

---

## 12. SUMMARY

All code in SafariSmart Kenya must:
1. Follow OOP principles strictly
2. Use appropriate data structures
3. Document complexity
4. Include comprehensive docstrings
5. Use type hints
6. Validate inputs
7. Handle errors properly
8. Include unit tests
9. Follow Django best practices
10. Follow naming conventions strictly
11. Keep files under 500 lines (split if larger)
12. Pass code review checklist

No exceptions to these standards will be accepted.
