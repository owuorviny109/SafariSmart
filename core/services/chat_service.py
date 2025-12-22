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

    def to_dict(self) -> Dict[str, Any]:
        """Convert context to dictionary for session storage."""
        return {
            'messages': [m.to_dict() for m in self.messages],
            'extracted_data': self.extracted_data,
            'current_step': self.current_step,
            'turn_count': self.turn_count
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ChatContext':
        """Reconstruct context from dictionary."""
        context = cls()
        context.extracted_data = data.get('extracted_data', context.extracted_data)
        context.current_step = data.get('current_step', 'welcome')
        context.turn_count = data.get('turn_count', 0)
        
        # Reconstruct messages
        for msg_data in data.get('messages', []):
            context.messages.append(ChatMessage(
                role=msg_data['role'],
                content=msg_data['content'],
                metadata=msg_data.get('metadata')
            ))
            
        return context


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
        
        # Use intelligent, conversational settings
        generation_config = {
            'temperature': 0.9,  # Higher for more creative, intelligent responses
            'top_p': 0.95,
            'top_k': 40,
            'max_output_tokens': 800,  # Allow longer, more helpful responses
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
            logger.info(f"AI Response: {response.text[:200]}...")  # Log first 200 chars
            bot_message, extracted = self._parse_ai_response(response.text, context)
            logger.info(f"Extracted data: {extracted}")
            return bot_message, extracted
            
        except Exception as e:
            logger.error(f"AI chat processing failed: {e}")
            # Fallback to simple extraction
            return self.config.error_message, {}
            
    def _build_extraction_prompt(self, user_input: str, context: ChatContext) -> str:
        """Build prompt for AI to extract trip data intelligently with RAG."""
        
        # 1. RAG: Fetch Knowledge Base from DB
        from destinations.models import Destination
        all_destinations = Destination.objects.all()
        
        knowledge_base = "OFFICIAL DESTINATION DATA (Use this for factual accuracy):\n"
        for dest in all_destinations:
            knowledge_base += (
                f"- {dest.name} ({dest.destination_type}):\n"
                f"  * Best Time: {dest.best_time_to_visit}\n"
                f"  * Est. Cost: {dest.average_cost_per_day} KSh/day\n"
                f"  * Activities: {dest.popular_activities}\n"
            )

        # 2. 2025 Pricing Context
        # 2. OFFICIAL KWS FEES 2024 (Source: User Provided Documents)
        pricing_context = """
        OFFICIAL KWS CONSERVATION FEES (2024/2025):
        Use these EXACT figures. Do NOT estimate.

        1. PARK ENTRY FEES (Per Day):
           - PREMIUM PARKS (Amboseli, Lake Nakuru):
             * Citizen/Resident: Adult 860 KSh, Child 215 KSh
             * Non-Resident: Adult $60, Child $35
           - WILDERNESS PARKS A (Tsavo East & West):
             * Citizen/Resident: Adult 515 KSh, Child 215 KSh
             * Non-Resident: Adult $52, Child $35
           - WILDERNESS PARKS B (Meru, Aberdare, Mt. Kenya):
             * Citizen/Resident: Adult 300 KSh, Child 215 KSh
             * Non-Resident: Adult $52, Child $35
           - URBAN SAFARI (Nairobi National Park):
             * Citizen/Resident: Adult 430 KSh, Child 215 KSh
             * Non-Resident: Adult $43, Child $22
           - MARINE PARKS (Kisite Mpunguti):
             * Citizen/Resident: Adult 215 KSh, Child 125 KSh
             * Non-Resident: Adult $17, Child $13

        2. CAMPING FEES (Per Person Per Day):
           - SPECIAL CAMPSITES (Premium Parks):
             * Citizen/Resident: Adult 500 KSh, Child 250 KSh
             * Non-Resident: Adult $50, Child $25
           - SPECIAL CAMPSITES (Other Parks):
             * Citizen/Resident: Adult 250 KSh, Child 200 KSh
             * Non-Resident: Adult $35, Child $20
           - PUBLIC CAMPSITES (Premium Parks):
             * Citizen/Resident: Adult 250 KSh, Child 200 KSh
             * Non-Resident: Adult $30, Child $25
           - PUBLIC CAMPSITES (Other Parks):
             * Citizen/Resident: Adult 200 KSh, Child 150 KSh
             * Non-Resident: Adult $20, Child $15
           - Reservation Fees (Non-Refundable): 7,500 KSh

        3. VEHICLE FEES (Per Day):
           - Less than 6 seats: 300 KSh
           - 6-12 seats: 1,030 KSh
           - 13-24 seats: 2,585 KSh
           - 25-44 seats: 4,050 KSh
           - 45+ seats: 5,000 KSh

        4. SPECIAL ACTIVITIES (Per Person):
           - Night Game Drive: 2,155 KSh (per trip)
           - Lake Boating: 1,290 KSh (per hour)
           - Security/Guided Tours: 1,720 - 3,015 KSh (per guide up to 4hrs)
           - River Rafting: 1,720 KSh
           - Horse Riding (KWS horses): 2,585 KSh (excluding rider)
           - Private Horses: 1,030 KSh (per day)
           - Fishing (per line per day): 515 KSh (Mt. Kenya: 1,550 KSh)
           - Cycling: 215 KSh (per day)
           - Walking Safaris: 1,500 KSh (per person per day)

        5. OTHER CHARGES:
           - Event Security: 75,000 KSh
           - Vehicle Recovery: 7,500 KSh
           - Annual Passes (Adult): 43,100 KSh
        """
        
        # Check what we still need
        needs_dest = not context.extracted_data.get('custom_destinations')
        needs_duration = context.extracted_data.get('duration_days') is None
        needs_budget = not context.extracted_data.get('budget_category')
        needs_interests = not context.extracted_data.get('interests')
        
        # Build conversation history for context
        conversation_history = ""
        for msg in context.messages[-6:]:  # Last 6 messages for context
            role = "User" if msg.role == "user" else "Juma"
            conversation_history += f"{role}: {msg.content}\n"
        
        prompt = f"""You are Juma, an intelligent Kenyan safari planning assistant. 
You have access to official data about specific supported destinations below.
However, you are an expert on ALL of Kenya.

CRITICAL INSTRUCTIONS:
1. If a user asks about a location NOT in the official list (e.g., Migori, Kisumu, Kakamega, Eldoret, Rusinga Island, Western Kenya, etc.), you MUST still provide a DETAILED, helpful response using your general knowledge.
2. ALWAYS extract trip planning data from user messages:
   - If they mention a budget amount (e.g., "5000 ksh", "10k", "50,000"), extract it
   - If they mention days/duration (e.g., "5 days", "a week", "3 nights"), extract the number
   - Classify budget: Under 10,000 KSh/day = "budget", 10,000-30,000 = "mid-range", 30,000+ = "luxury"
3. Be helpful, enthusiastic, and never say "I don't understand" for travel-related queries.

{knowledge_base}

{pricing_context}

CONVERSATION HISTORY:
{conversation_history}

CURRENT USER MESSAGE: "{user_input}"

CURRENT TRIP DATA COLLECTED:
- Destinations: {context.extracted_data.get('custom_destinations', 'Not yet specified')}
- Duration: {context.extracted_data.get('duration_days', 'Not yet specified')} days
- Budget Category: {context.extracted_data.get('budget_category', 'Not yet specified')}
- Interests: {context.extracted_data.get('interests', 'Not yet specified')}

YOUR TASK:
1. Respond helpfully to the user's message
2. If they provide budget/duration/destination info, acknowledge it and incorporate it
3. If they ask for a plan, provide a realistic itinerary suggestion based on their constraints
4. For low budgets (e.g., 5000 KSh for 5 days = 1000 KSh/day), suggest budget-friendly options like local guesthouses, public transport, and free attractions

RESPONSE FORMAT:
Write your helpful response first, then on a new line add:
---EXTRACTION---
DESTINATIONS: [destination names comma-separated, or "none" if not mentioned]
DURATION: [number of days, or "none" if not mentioned]
BUDGET: [budget/mid-range/luxury based on amount, or "none" if not mentioned]
INTERESTS: [interests comma-separated, or "none" if not mentioned]

EXAMPLE 1:
User: "I have 5000 ksh and want to stay for 5 days, plan for me"
Response: That's a great budget-conscious adventure! With 5,000 KSh for 5 days (about 1,000 KSh per day), here's what I'd suggest for Western Kenya:

**Day 1-2: Kisumu City**
- Stay at a budget guesthouse (500-800 KSh/night)
- Visit Kit Mikayi rock formation (free entry)
- Explore Dunga Beach for sunset views

**Day 3-4: Kakamega Forest**
- Take a matatu to Kakamega (300 KSh)
- Budget camping or homestay
- Guided forest walks (200-500 KSh)

**Day 5: Return via Kisumu**
- Final exploration and departure

This keeps you within budget while experiencing the best of Western Kenya! Want me to add more details?

---EXTRACTION---
DESTINATIONS: Western Kenya, Kisumu, Kakamega
DURATION: 5
BUDGET: budget
INTERESTS: nature, culture

EXAMPLE 2:
User: "how much is mara?"
Response: Great question! Based on 2024/2025 rates, Maasai Mara entry fees are:
- **Non-Residents:** $80 per adult per day
- **Kenyan Citizens/Residents:** 1,200 KSh per adult per day

A typical mid-range safari there costs around 15,000-25,000 KSh per day including accommodation and game drives. Shall we add Maasai Mara to your trip?

---EXTRACTION---
DESTINATIONS: Maasai Mara
DURATION: none
BUDGET: none
INTERESTS: wildlife, safari

NOW RESPOND TO THE CURRENT USER MESSAGE."""
        
        return prompt
        

        
    def _parse_ai_response(self, ai_text: str, context: ChatContext) -> Tuple[str, Dict[str, Any]]:
        """Parse AI response and extract structured data intelligently."""
        extracted = {}
        
        # Split by extraction marker
        if '---EXTRACTION---' in ai_text:
            parts = ai_text.split('---EXTRACTION---')
            bot_response = parts[0].strip()
            extraction_section = parts[1] if len(parts) > 1 else ''
        else:
            # Fallback: try to find data fields anywhere
            bot_response = ai_text
            extraction_section = ai_text
        
        # Parse extraction section
        lines = extraction_section.split('\n')
        
        for line in lines:
            line = line.strip()
            
            if line.startswith('DESTINATIONS:'):
                dest_text = line.replace('DESTINATIONS:', '').strip()
                if dest_text.lower() != 'none' and dest_text:
                    destinations = [d.strip() for d in dest_text.split(',') if d.strip()]
                    if destinations:
                        extracted['custom_destinations'] = destinations
                        
            elif line.startswith('DURATION:'):
                duration_text = line.replace('DURATION:', '').strip()
                if duration_text.lower() != 'none':
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
        
        # Clean up bot response - remove any extraction markers that leaked through
        bot_response = bot_response.replace('---EXTRACTION---', '').strip()
        
        # Remove any data field lines from response
        response_lines = []
        for line in bot_response.split('\n'):
            line = line.strip()
            if line and not any(line.startswith(prefix) for prefix in ['DESTINATIONS:', 'DURATION:', 'BUDGET:', 'INTERESTS:']):
                response_lines.append(line)
        
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
        
        Use AI for natural language queries, simple chat for structured input.
        
        Args:
            message (str): User's message
            
        Returns:
            bool: True if complex (use AI), False if simple
        """
        # Use AI for natural conversational queries
        # Simple greetings don't need AI
        message_lower = message.lower().strip()
        
        # Don't use AI for simple greetings
        simple_greetings = ['hello', 'hi', 'hey', 'jambo', 'hola', 'greetings']
        if message_lower in simple_greetings:
            return False
        
        # Use AI for everything else - it's better at understanding natural language
        return True
        
    def _handle_with_simple(
        self,
        user_input: str,
        context: ChatContext
    ) -> Dict[str, Any]:
        """Handle message with simple rule-based chat."""
        user_lower = user_input.lower().strip()
        
        # Handle greetings - just acknowledge, don't ask question again
        greetings = ['hello', 'hi', 'hey', 'jambo', 'hola', 'greetings']
        if user_lower in greetings:
            # Simple acknowledgment
            bot_message = "Hello! 👋"
            context.add_message('bot', bot_message)
            return {
                'message': bot_message,
                'type': 'greeting',
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
