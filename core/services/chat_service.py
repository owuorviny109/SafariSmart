"""
Module: core/services/chat_service.py
Purpose: Hybrid chat service for trip planning

This module provides a hybrid chat system that intelligently routes
between simple rule-based chat and AI-powered conversation based on
query complexity.

Classes:
    TripPlannerChatService: Main chat service orchestrator
    SimpleChatFlow: Rule-based chat flow handler
    AIChatHandler: AI-powered conversation handler
    
Author: SafariSmart Kenya Team
Date: 2025-11-19
"""

import logging
import re
from typing import Dict, Any, List, Optional, Tuple
from django.conf import settings
import google.generativeai as genai

from ..models_config import ChatConfiguration
from ..exceptions import AIServiceError
from .configuration_service import ConfigurationService

logger = logging.getLogger(__name__)


class ChatMessage:
    """
    Represents a single chat message.
    
    Attributes:
        role (str): 'user' or 'bot'
        content (str): Message content
        timestamp (datetime): When message was sent
        metadata (dict): Additional message data
    """
    
    def __init__(self, role: str, content: str, metadata: Optional[Dict] = None):
        """
        Initialize chat message.
        
        Args:
            role (str): Message sender ('user' or 'bot')
            content (str): Message text
            metadata (dict, optional): Additional data
        """
        self.role = role
        self.content = content
        self.metadata = metadata or {}
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert message to dictionary."""
        return {
            'role': self.role,
            'content': self.content,
            'metadata': self.metadata
        }


class ChatContext:
    """
    Maintains conversation context and extracted data.
    
    Attributes:
        messages (List[ChatMessage]): Conversation history
        extracted_data (dict): Trip data extracted from conversation
        current_step (str): Current question being asked
        turn_count (int): Number of conversation turns
    """
    
    def __init__(self):
        """Initialize empty chat context."""
        self.messages: List[ChatMessage] = []
        self.extracted_data: Dict[str, Any] = {
            'destinations': [],
            'custom_destinations': [],
            'duration_days': None,
            'budget_category': None,
            'interests': []
        }
        self.current_step: str = 'welcome'
        self.turn_count: int = 0
        
    def add_message(self, role: str, content: str, metadata: Optional[Dict] = None):
        """Add message to conversation history."""
        message = ChatMessage(role, content, metadata)
        self.messages.append(message)
        if role == 'user':
            self.turn_count += 1
            
    def get_last_user_message(self) -> Optional[str]:
        """Get the last message from user."""
        for message in reversed(self.messages):
            if message.role == 'user':
                return message.content
        return None
        
    def is_complete(self) -> bool:
        """Check if all required data has been collected."""
        return (
            (self.extracted_data['destinations'] or self.extracted_data['custom_destinations']) and
            self.extracted_data['duration_days'] is not None and
            self.extracted_data['budget_category'] is not None
        )


class SimpleChatFlow:
    """
    Rule-based chat flow for simple queries.
    
    Handles straightforward question-answer flow without AI.
    Fast, reliable, and token-free.
    
    Attributes:
        config (ChatConfiguration): Chat configuration
        flow_steps (list): Ordered list of questions
    """
    
    def __init__(self, config: ChatConfiguration):
        """
        Initialize simple chat flow.
        
        Args:
            config (ChatConfiguration): Chat configuration instance
        """
        self.config = config
        self.flow_steps = ['destination', 'duration', 'budget', 'interests']
        
    def get_next_question(self, context: ChatContext) -> Optional[str]:
        """
        Get next question based on current context.
        
        Args:
            context (ChatContext): Current conversation context
            
        Returns:
            str: Next question to ask, or None if complete
        """
        # Check what data is missing and ask conversationally
        if not context.extracted_data['custom_destinations']:
            return self.config.destination_question
            
        if context.extracted_data['duration_days'] is None:
            # Acknowledge destination
            dest = context.extracted_data['custom_destinations'][0]
            return f"Great choice! {dest} is wonderful. {self.config.duration_question}"
            
        if context.extracted_data['budget_category'] is None:
            return f"Perfect! {self.config.budget_question} (Budget/Mid-range/Luxury)"
            
        if not context.extracted_data['interests']:
            return f"Excellent! {self.config.interests_question} (Wildlife/Culture/Food/Beach/etc.)"
            
        return None
        
    def extract_data(self, user_input: str, context: ChatContext) -> bool:
        """
        Extract trip data from user input.
        
        Args:
            user_input (str): User's message
            context (ChatContext): Current conversation context
            
        Returns:
            bool: True if data was successfully extracted
        """
        user_input_lower = user_input.lower().strip()
        
        # Handle greetings
        greetings = ['hello', 'hi', 'hey', 'jambo', 'hola', 'greetings']
        if user_input_lower in greetings:
            # Don't extract, just acknowledge
            return False
        
        # Extract destination
        if not context.extracted_data['custom_destinations']:
            # Simple extraction - just take the input as destination
            if len(user_input) > 2:
                context.extracted_data['custom_destinations'] = [user_input]
                context.current_step = 'duration'
                return True
                
        # Extract duration
        elif context.extracted_data['duration_days'] is None:
            duration = self._extract_duration(user_input)
            if duration:
                context.extracted_data['duration_days'] = duration
                context.current_step = 'budget'
                return True
                
        # Extract budget
        elif context.extracted_data['budget_category'] is None:
            budget = self._extract_budget(user_input_lower)
            if budget:
                context.extracted_data['budget_category'] = budget
                context.current_step = 'interests'
                return True
                
        # Extract interests
        elif not context.extracted_data['interests']:
            interests = self._extract_interests(user_input_lower)
            if interests:
                context.extracted_data['interests'] = interests
                context.current_step = 'complete'
                return True
                
        return False
        
    def _extract_duration(self, text: str) -> Optional[int]:
        """Extract trip duration from text."""
        # Look for numbers
        numbers = re.findall(r'\d+', text)
        if numbers:
            duration = int(numbers[0])
            if 1 <= duration <= 30:
                return duration
        return None
        
    def _extract_budget(self, text: str) -> Optional[str]:
        """Extract budget category from text."""
        if 'budget' in text or 'cheap' in text or 'affordable' in text:
            return 'budget'
        elif 'luxury' in text or 'premium' in text or 'expensive' in text:
            return 'luxury'
        elif 'mid' in text or 'medium' in text or 'moderate' in text:
            return 'mid-range'
        return None
        
    def _extract_interests(self, text: str) -> List[str]:
        """Extract interests from text."""
        interest_keywords = {
            'wildlife': ['wildlife', 'safari', 'animals', 'game'],
            'culture': ['culture', 'cultural', 'tradition', 'local'],
            'food': ['food', 'cuisine', 'eating', 'restaurant'],
            'adventure': ['adventure', 'hiking', 'climbing', 'sports'],
            'beach': ['beach', 'ocean', 'sea', 'swimming'],
            'nature': ['nature', 'forest', 'hiking', 'eco'],
            'photography': ['photo', 'photography', 'pictures'],
            'relaxation': ['relax', 'spa', 'leisure', 'rest']
        }
        
        found_interests = []
        for interest, keywords in interest_keywords.items():
            if any(keyword in text for keyword in keywords):
                found_interests.append(interest)
                
        return found_interests if found_interests else ['general']


class AIChatHandler:
    """
    AI-powered conversation handler using Gemini.
    
    Handles complex, conversational queries that require
    natural language understanding.
    
    Attributes:
        config (ChatConfiguration): Chat configuration
        model: Gemini AI model instance
    """
    
    def __init__(self, config: ChatConfiguration):
        """
        Initialize AI chat handler.
        
        Args:
            config (ChatConfiguration): Chat configuration instance
            
        Raises:
            AIServiceError: If Gemini API key not configured
        """
        self.config = config
        
        api_key = settings.GEMINI_API_KEY
        if not api_key:
            raise AIServiceError(
                "GEMINI_API_KEY not configured",
                service_name="gemini"
            )
            
        genai.configure(api_key=api_key)
        
        # Use fast model with optimized settings
        generation_config = {
            'temperature': 0.7,
            'top_p': 0.8,
            'top_k': 40,
            'max_output_tokens': 500,  # Short responses for chat
        }
        
        self.model = genai.GenerativeModel(
            'gemini-2.5-flash',
            generation_config=generation_config
        )
        
    def process_message(self, user_input: str, context: ChatContext) -> Tuple[str, Dict[str, Any]]:
        """
        Process user message with AI and extract data.
        
        Args:
            user_input (str): User's message
            context (ChatContext): Current conversation context
            
        Returns:
            Tuple[str, dict]: (Bot response, extracted data)
        """
        prompt = self._build_extraction_prompt(user_input, context)
        
        try:
            response = self.model.generate_content(prompt)
            return self._parse_ai_response(response.text, context)
            
        except Exception as e:
            logger.error(f"AI chat processing failed: {e}")
            # Fallback to simple extraction
            return self.config.error_message, {}
            
    def _build_extraction_prompt(self, user_input: str, context: ChatContext) -> str:
        """Build prompt for AI to extract trip data."""
        
        # Check what's missing
        has_dest = bool(context.extracted_data.get('custom_destinations'))
        has_duration = context.extracted_data.get('duration_days') is not None
        has_budget = bool(context.extracted_data.get('budget_category'))
        has_interests = bool(context.extracted_data.get('interests'))
        
        prompt = f"""You are a Kenyan safari assistant. Extract trip info and respond naturally.

User: "{user_input}"

Current data:
Destinations: {context.extracted_data.get('custom_destinations', [])}
Duration: {context.extracted_data.get('duration_days', 'none')}
Budget: {context.extracted_data.get('budget_category', 'none')}
Interests: {context.extracted_data.get('interests', [])}

CRITICAL: You MUST extract data from the user's message and output it in the format below.

Rules:
1. Extract ANY Kenya location names mentioned → add to DESTINATIONS
2. Extract ANY numbers that could be days → set as DURATION
3. If user mentions "budget", "cheap", "affordable" → BUDGET: budget
4. If user mentions "luxury", "premium", "expensive" → BUDGET: luxury  
5. If user mentions "mid-range", "moderate" → BUDGET: mid-range
6. Extract interests: wildlife, culture, food, adventure, beach, nature, etc.

Response format (REQUIRED):
[Your friendly 1-2 sentence response]

DESTINATIONS: [comma-separated Kenya places, or "none"]
DURATION: [just the number, or "none"]
BUDGET: [budget/mid-range/luxury, or "none"]
INTERESTS: [comma-separated, or "none"]

Example:
User: "I want to visit Rongo for 3 days"
Great! Rongo is a wonderful choice. What's your budget level?

DESTINATIONS: Rongo
DURATION: 3
BUDGET: none
INTERESTS: none"""
        
        return prompt
        
    def _parse_ai_response(self, ai_text: str, context: ChatContext) -> Tuple[str, Dict[str, Any]]:
        """Parse AI response and extract structured data."""
        extracted = {}
        
        # Split response and data
        lines = ai_text.split('\n')
        response_lines = []
        
        for line in lines:
            line = line.strip()
            
            if line.startswith('DESTINATIONS:'):
                dest_text = line.replace('DESTINATIONS:', '').strip()
                if dest_text.lower() != 'none' and dest_text:
                    # Extract destination names
                    destinations = [d.strip() for d in dest_text.split(',') if d.strip()]
                    if destinations:
                        extracted['custom_destinations'] = destinations
                        
            elif line.startswith('DURATION:'):
                duration_text = line.replace('DURATION:', '').strip()
                if duration_text.lower() != 'none':
                    # Extract number
                    import re
                    numbers = re.findall(r'\d+', duration_text)
                    if numbers:
                        extracted['duration_days'] = int(numbers[0])
                        
            elif line.startswith('BUDGET:'):
                budget_text = line.replace('BUDGET:', '').strip().lower()
                if budget_text in ['budget', 'mid-range', 'luxury']:
                    extracted['budget_category'] = budget_text
                    
            elif line.startswith('INTERESTS:'):
                interests_text = line.replace('INTERESTS:', '').strip()
                if interests_text.lower() != 'none' and interests_text:
                    interests = [i.strip().lower() for i in interests_text.split(',') if i.strip()]
                    if interests:
                        extracted['interests'] = interests
            else:
                # This is part of the response
                if line and not any(line.startswith(prefix) for prefix in ['DESTINATIONS:', 'DURATION:', 'BUDGET:', 'INTERESTS:']):
                    response_lines.append(line)
        
        # Join response lines
        bot_response = ' '.join(response_lines).strip()
        if not bot_response:
            bot_response = self.config.error_message
            
        return bot_response, extracted


class TripPlannerChatService:
    """
    Main chat service orchestrator.
    
    Intelligently routes between simple and AI chat based on
    query complexity. Manages conversation flow and data extraction.
    
    Attributes:
        config (ChatConfiguration): Chat configuration
        simple_chat (SimpleChatFlow): Simple chat handler
        ai_chat (AIChatHandler): AI chat handler
    """
    
    def __init__(self):
        """Initialize chat service with configuration."""
        self.config = ChatConfiguration.get_config()
        self.simple_chat = SimpleChatFlow(self.config)
        
        # Initialize AI handler if enabled
        self.ai_chat = None
        if self.config.use_ai_for_complex:
            try:
                self.ai_chat = AIChatHandler(self.config)
            except AIServiceError as e:
                logger.warning(f"AI chat disabled: {e}")
                
    def start_conversation(self) -> Dict[str, Any]:
        """
        Start a new conversation.
        
        Returns:
            dict: Initial response with welcome message
        """
        context = ChatContext()
        context.add_message('bot', self.config.welcome_message)
        
        return {
            'message': self.config.welcome_message,
            'type': 'welcome',
            'context_id': id(context),  # In production, use proper session management
            'completed': False
        }
        
    def process_message(
        self,
        user_input: str,
        context: ChatContext
    ) -> Dict[str, Any]:
        """
        Process user message and return response.
        
        Args:
            user_input (str): User's message
            context (ChatContext): Current conversation context
            
        Returns:
            dict: Response with bot message and status
        """
        if not self.config.is_enabled:
            return {
                'message': 'Chat is currently disabled.',
                'type': 'error',
                'completed': False
            }
            
        # Add user message to context
        context.add_message('user', user_input)
        
        # Check if max turns reached
        if context.turn_count >= self.config.max_chat_turns:
            return self._force_completion(context)
            
        # Determine if query is complex
        is_complex = self._is_complex_query(user_input)
        
        # Route to appropriate handler
        if is_complex and self.ai_chat:
            return self._handle_with_ai(user_input, context)
        else:
            return self._handle_with_simple(user_input, context)
            
    def _is_complex_query(self, message: str) -> bool:
        """
        Determine if query requires AI processing.
        
        Use simple chat for reliability. AI can be unpredictable.
        
        Args:
            message (str): User's message
            
        Returns:
            bool: True if complex (use AI), False if simple
        """
        # Use simple chat by default for reliability
        # AI is too unpredictable and doesn't follow format well
        return False
        
    def _handle_with_simple(
        self,
        user_input: str,
        context: ChatContext
    ) -> Dict[str, Any]:
        """Handle message with simple rule-based chat."""
        user_lower = user_input.lower().strip()
        
        # Handle greetings
        greetings = ['hello', 'hi', 'hey', 'jambo', 'hola', 'greetings']
        if user_lower in greetings:
            # Get the first question
            bot_message = self.simple_chat.get_next_question(context)
            if not bot_message:
                bot_message = self.config.welcome_message
            context.add_message('bot', bot_message)
            return {
                'message': bot_message,
                'type': 'simple',
                'completed': False,
                'extracted_data': context.extracted_data
            }
        
        # Try to extract data
        extracted = self.simple_chat.extract_data(user_input, context)
        
        if not extracted:
            # Didn't understand - ask current question again
            bot_message = self.simple_chat.get_next_question(context)
            if not bot_message:
                bot_message = self.config.error_message
        else:
            # Get next question
            next_question = self.simple_chat.get_next_question(context)
            
            if next_question:
                bot_message = next_question
            else:
                # All data collected
                bot_message = self.config.completion_message
                context.add_message('bot', bot_message)
                return {
                    'message': bot_message,
                    'type': 'completion',
                    'completed': True,
                    'extracted_data': context.extracted_data
                }
                
        context.add_message('bot', bot_message)
        
        return {
            'message': bot_message,
            'type': 'simple',
            'completed': False,
            'extracted_data': context.extracted_data
        }
        
    def _handle_with_ai(
        self,
        user_input: str,
        context: ChatContext
    ) -> Dict[str, Any]:
        """Handle message with AI-powered chat."""
        bot_message, extracted_data = self.ai_chat.process_message(user_input, context)
        
        # Update context with extracted data
        if extracted_data:
            for key, value in extracted_data.items():
                if key == 'custom_destinations' and value:
                    # Append to existing destinations
                    existing = context.extracted_data.get('custom_destinations', [])
                    for dest in value:
                        if dest not in existing:
                            existing.append(dest)
                    context.extracted_data['custom_destinations'] = existing
                elif key == 'interests' and value:
                    # Append to existing interests
                    existing = context.extracted_data.get('interests', [])
                    for interest in value:
                        if interest not in existing:
                            existing.append(interest)
                    context.extracted_data['interests'] = existing
                else:
                    # Replace other fields
                    context.extracted_data[key] = value
            
        context.add_message('bot', bot_message)
        
        # Check if complete
        if context.is_complete():
            completion_msg = self.config.completion_message
            context.add_message('bot', completion_msg)
            return {
                'message': completion_msg,
                'type': 'completion',
                'completed': True,
                'extracted_data': context.extracted_data
            }
            
        return {
            'message': bot_message,
            'type': 'ai',
            'completed': False,
            'extracted_data': context.extracted_data
        }
        
    def _force_completion(self, context: ChatContext) -> Dict[str, Any]:
        """Force completion when max turns reached."""
        if context.is_complete():
            message = self.config.completion_message
        else:
            message = "Let me work with what we have so far..."
            
        return {
            'message': message,
            'type': 'forced_completion',
            'completed': True,
            'extracted_data': context.extracted_data
        }
