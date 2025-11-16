"""
Module: services/wizard_service.py
Purpose: Service layer for wizard session management

This module contains classes for managing wizard sessions and state.
It follows OOP principles with clear separation of concerns.

Classes:
    WizardSessionManager: Manages wizard session state
    WizardService: Orchestrates wizard flow operations
    
Author: SafariSmart Kenya Team
Date: 2025-11-16
"""

from typing import Dict, List, Optional, Any
from django.contrib.sessions.backends.base import SessionBase
from django.contrib.auth.models import User

from core.models import WizardSession
from destinations.models import Destination


class WizardSessionManager:
    """
    Manages wizard session state and persistence.
    
    This class handles storing and retrieving wizard data from Django sessions.
    It provides a clean interface for wizard state management.
    
    Attributes:
        session (SessionBase): Django session object
        
    Example:
        >>> manager = WizardSessionManager(request.session)
        >>> manager.save_step_data(1, {'destinations': [1, 2, 3]})
        >>> data = manager.get_step_data(1)
    """
    
    WIZARD_KEY = 'wizard_data'
    
    def __init__(self, session: SessionBase):
        """
        Initialize session manager.
        
        Args:
            session (SessionBase): Django session object
        """
        self._session = session
        self._initialize_wizard_data()
        
    def _initialize_wizard_data(self) -> None:
        """
        Initialize wizard data structure in session if not exists.
        
        Creates empty wizard data dictionary with all steps initialized.
        """
        if self.WIZARD_KEY not in self._session:
            self._session[self.WIZARD_KEY] = {
                'step_1': {},
                'step_2': {},
                'step_3': {},
                'step_4': {},
                'step_5': {},
                'current_step': 1,
                'completed': False
            }
            self._session.modified = True
            
    def save_step_data(self, step: int, data: Dict[str, Any]) -> None:
        """
        Save data for a specific wizard step.
        
        Args:
            step (int): Step number (1-5)
            data (Dict[str, Any]): Step data to save
            
        Raises:
            ValueError: If step number is invalid
        """
        self._validate_step_number(step)
        
        wizard_data = self._session[self.WIZARD_KEY]
        wizard_data[f'step_{step}'] = data
        wizard_data['current_step'] = step
        
        self._session[self.WIZARD_KEY] = wizard_data
        self._session.modified = True
        
    def get_step_data(self, step: int) -> Dict[str, Any]:
        """
        Retrieve data for a specific wizard step.
        
        Args:
            step (int): Step number (1-5)
            
        Returns:
            Dict[str, Any]: Step data or empty dict if not found
            
        Raises:
            ValueError: If step number is invalid
        """
        self._validate_step_number(step)
        
        wizard_data = self._session.get(self.WIZARD_KEY, {})
        return wizard_data.get(f'step_{step}', {})
        
    def get_all_data(self) -> Dict[str, Any]:
        """
        Retrieve all wizard data.
        
        Returns:
            Dict[str, Any]: Complete wizard data
        """
        return self._session.get(self.WIZARD_KEY, {})
        
    def get_current_step(self) -> int:
        """
        Get current wizard step number.
        
        Returns:
            int: Current step (1-5)
        """
        wizard_data = self._session.get(self.WIZARD_KEY, {})
        return wizard_data.get('current_step', 1)
        
    def clear_wizard_data(self) -> None:
        """
        Clear all wizard data from session.
        
        Resets wizard to initial state.
        """
        if self.WIZARD_KEY in self._session:
            del self._session[self.WIZARD_KEY]
            self._session.modified = True
            
    def mark_completed(self) -> None:
        """
        Mark wizard as completed.
        
        Sets completed flag to True in session data.
        """
        wizard_data = self._session[self.WIZARD_KEY]
        wizard_data['completed'] = True
        self._session[self.WIZARD_KEY] = wizard_data
        self._session.modified = True
        
    def is_completed(self) -> bool:
        """
        Check if wizard is completed.
        
        Returns:
            bool: True if wizard completed, False otherwise
        """
        wizard_data = self._session.get(self.WIZARD_KEY, {})
        return wizard_data.get('completed', False)
        
    def _validate_step_number(self, step: int) -> None:
        """
        Validate step number is within valid range.
        
        Args:
            step (int): Step number to validate
            
        Raises:
            ValueError: If step number is not between 1 and 5
        """
        if not isinstance(step, int):
            raise TypeError(f"Step must be an integer, got {type(step)}")
            
        if step < 1 or step > 5:
            raise ValueError(f"Step must be between 1 and 5, got {step}")


class WizardService:
    """
    Service layer for wizard operations.
    
    This class orchestrates wizard flow operations including validation,
    data processing, and session management.
    
    Attributes:
        session_manager (WizardSessionManager): Session manager instance
        
    Example:
        >>> service = WizardService(request.session)
        >>> service.save_destinations([1, 2, 3])
        >>> destinations = service.get_selected_destinations()
    """
    
    def __init__(self, session: SessionBase):
        """
        Initialize wizard service.
        
        Args:
            session (SessionBase): Django session object
        """
        self.session_manager = WizardSessionManager(session)
        
    def save_destinations(self, destination_ids: List[int]) -> None:
        """
        Save selected destination IDs for step 1.
        
        Validates destination IDs exist before saving.
        
        Args:
            destination_ids (List[int]): List of destination IDs
            
        Raises:
            ValueError: If destination IDs are invalid
        """
        self._validate_destination_ids(destination_ids)
        
        step_data = {
            'destination_ids': destination_ids,
            'destination_count': len(destination_ids)
        }
        
        self.session_manager.save_step_data(1, step_data)
        
    def get_selected_destinations(self) -> List[Destination]:
        """
        Retrieve selected destination objects.
        
        Returns:
            List[Destination]: List of Destination model instances
        """
        step_data = self.session_manager.get_step_data(1)
        destination_ids = step_data.get('destination_ids', [])
        
        if not destination_ids:
            return []
            
        return list(Destination.objects.filter(id__in=destination_ids))
        
    def _validate_destination_ids(self, destination_ids: List[int]) -> None:
        """
        Validate destination IDs exist in database.
        
        Args:
            destination_ids (List[int]): List of destination IDs
            
        Raises:
            ValueError: If any destination ID is invalid
        """
        if not destination_ids:
            raise ValueError("At least one destination must be selected")
            
        if not isinstance(destination_ids, list):
            raise TypeError("Destination IDs must be a list")
            
        # Verify all IDs exist
        existing_count = Destination.objects.filter(
            id__in=destination_ids
        ).count()
        
        if existing_count != len(destination_ids):
            raise ValueError("One or more destination IDs are invalid")
            
    def save_duration(
        self,
        duration_days: int,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> None:
        """
        Save trip duration and dates for step 2.
        
        Validates duration is within acceptable range and dates are valid.
        
        Args:
            duration_days (int): Trip duration in days
            start_date (str, optional): Start date in YYYY-MM-DD format
            end_date (str, optional): End date in YYYY-MM-DD format
            
        Raises:
            ValueError: If duration or dates are invalid
        """
        self._validate_duration(duration_days)
        
        if start_date and end_date:
            self._validate_dates(start_date, end_date, duration_days)
        
        step_data = {
            'duration_days': duration_days,
            'start_date': start_date,
            'end_date': end_date
        }
        
        self.session_manager.save_step_data(2, step_data)
        
    def get_duration_data(self) -> Dict[str, Any]:
        """
        Retrieve duration and date data.
        
        Returns:
            Dict[str, Any]: Duration data or empty dict
        """
        return self.session_manager.get_step_data(2)
        
    def _validate_duration(self, duration_days: int) -> None:
        """
        Validate trip duration is within acceptable range.
        
        Args:
            duration_days (int): Duration in days
            
        Raises:
            ValueError: If duration is invalid
            TypeError: If duration is not an integer
        """
        if not isinstance(duration_days, int):
            raise TypeError("Duration must be an integer")
            
        if duration_days < 1:
            raise ValueError("Duration must be at least 1 day")
            
        if duration_days > 30:
            raise ValueError("Duration cannot exceed 30 days")
            
    def _validate_dates(
        self,
        start_date: str,
        end_date: str,
        duration_days: int
    ) -> None:
        """
        Validate start and end dates are logical.
        
        Args:
            start_date (str): Start date in YYYY-MM-DD format
            end_date (str): End date in YYYY-MM-DD format
            duration_days (int): Expected duration
            
        Raises:
            ValueError: If dates are invalid or illogical
        """
        from datetime import datetime, timedelta
        
        try:
            start = datetime.strptime(start_date, '%Y-%m-%d')
            end = datetime.strptime(end_date, '%Y-%m-%d')
        except ValueError:
            raise ValueError("Invalid date format. Use YYYY-MM-DD")
            
        # Check start date is not in the past
        today = datetime.now().date()
        if start.date() < today:
            raise ValueError("Start date cannot be in the past")
            
        # Check end date is after start date
        if end <= start:
            raise ValueError("End date must be after start date")
            
        # Check duration matches date range
        actual_duration = (end - start).days + 1
        if actual_duration != duration_days:
            raise ValueError(
                f"Date range ({actual_duration} days) does not match "
                f"selected duration ({duration_days} days)"
            )
            
    def save_travel_group(
        self,
        adults_count: int,
        children_count: int,
        travel_type: str
    ) -> None:
        """
        Save travel group information for step 3.
        
        Validates group size and travel type before saving.
        
        Args:
            adults_count (int): Number of adults (minimum 1)
            children_count (int): Number of children (0 or more)
            travel_type (str): Type of travel (solo, family, couple, friends)
            
        Raises:
            ValueError: If group data is invalid
        """
        self._validate_travel_group(adults_count, children_count, travel_type)
        
        step_data = {
            'adults_count': adults_count,
            'children_count': children_count,
            'travel_type': travel_type,
            'total_travelers': adults_count + children_count
        }
        
        self.session_manager.save_step_data(3, step_data)
        
    def get_travel_group_data(self) -> Dict[str, Any]:
        """
        Retrieve travel group data.
        
        Returns:
            Dict[str, Any]: Travel group data or empty dict
        """
        return self.session_manager.get_step_data(3)
        
    def _validate_travel_group(
        self,
        adults_count: int,
        children_count: int,
        travel_type: str
    ) -> None:
        """
        Validate travel group parameters.
        
        Args:
            adults_count (int): Number of adults
            children_count (int): Number of children
            travel_type (str): Type of travel
            
        Raises:
            ValueError: If any parameter is invalid
            TypeError: If types are incorrect
        """
        # Validate types
        if not isinstance(adults_count, int):
            raise TypeError("Adults count must be an integer")
            
        if not isinstance(children_count, int):
            raise TypeError("Children count must be an integer")
            
        if not isinstance(travel_type, str):
            raise TypeError("Travel type must be a string")
            
        # Validate adults count
        if adults_count < 1:
            raise ValueError("At least 1 adult is required")
            
        if adults_count > 20:
            raise ValueError("Maximum 20 adults allowed")
            
        # Validate children count
        if children_count < 0:
            raise ValueError("Children count cannot be negative")
            
        if children_count > 20:
            raise ValueError("Maximum 20 children allowed")
            
        # Validate total group size
        total = adults_count + children_count
        if total > 30:
            raise ValueError("Total group size cannot exceed 30 people")
            
        # Validate travel type
        valid_types = ['solo', 'family', 'couple', 'friends']
        if travel_type not in valid_types:
            raise ValueError(
                f"Invalid travel type. Must be one of: {', '.join(valid_types)}"
            )

    def save_budget(
        self,
        budget_amount: int,
        budget_category: str
    ) -> None:
        """
        Save budget information for step 4.

        Validates budget amount and category before saving.

        Args:
            budget_amount (int): Total budget in KSh
            budget_category (str): Budget category (budget, mid-range, luxury)

        Raises:
            ValueError: If budget data is invalid
        """
        self._validate_budget(budget_amount, budget_category)

        # Calculate per person budget
        group_data = self.get_travel_group_data()
        total_travelers = group_data.get('total_travelers', 1)
        per_person_budget = budget_amount // total_travelers

        step_data = {
            'budget_amount': budget_amount,
            'budget_category': budget_category,
            'per_person_budget': per_person_budget,
            'total_travelers': total_travelers
        }

        self.session_manager.save_step_data(4, step_data)

    def get_budget_data(self) -> Dict[str, Any]:
        """
        Retrieve budget data.

        Returns:
            Dict[str, Any]: Budget data or empty dict
        """
        return self.session_manager.get_step_data(4)

    def _validate_budget(
        self,
        budget_amount: int,
        budget_category: str
    ) -> None:
        """
        Validate budget parameters.

        Args:
            budget_amount (int): Budget amount in KSh
            budget_category (str): Budget category

        Raises:
            ValueError: If any parameter is invalid
            TypeError: If types are incorrect
        """
        # Validate types
        if not isinstance(budget_amount, int):
            raise TypeError("Budget amount must be an integer")

        if not isinstance(budget_category, str):
            raise TypeError("Budget category must be a string")

        # Validate budget amount
        MIN_BUDGET = 10000  # KSh 10,000
        MAX_BUDGET = 500000  # KSh 500,000

        if budget_amount < MIN_BUDGET:
            raise ValueError(f"Budget must be at least KSh {MIN_BUDGET:,}")

        if budget_amount > MAX_BUDGET:
            raise ValueError(f"Budget cannot exceed KSh {MAX_BUDGET:,}")

        # Validate budget category
        valid_categories = ['budget', 'mid-range', 'luxury']
        if budget_category not in valid_categories:
            raise ValueError(
                f"Invalid budget category. Must be one of: {', '.join(valid_categories)}"
            )
