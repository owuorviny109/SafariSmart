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
