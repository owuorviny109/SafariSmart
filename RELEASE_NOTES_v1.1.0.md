# SafariSmart Kenya v1.1.0 - Intelligent AI Chatbot 🤖

## 🎉 Major Feature: AI-Powered Trip Planning Chatbot

We're excited to announce the release of our intelligent AI chatbot powered by Google Gemini! Plan your Kenyan safari in seconds through natural conversation.

## ✨ What's New

### Intelligent Conversational Planning
- **Natural Language Understanding**: Just tell the chatbot what you want in plain English
  - "I want a 2 day trip to Kakamega with 50000 budget"
  - "I love adventure and food"
  - "One day trip to Rongo, budget friendly"
- **Smart Data Extraction**: AI automatically extracts destinations, duration, budget, and interests
- **Context-Aware Responses**: The chatbot remembers your conversation and asks intelligent follow-up questions

### End-to-End Automation
- **Instant Itinerary Generation**: No more clicking through wizard steps
- **One Conversation, Complete Trip**: From chat to itinerary in under a minute
- **Seamless Experience**: Chat widget available on all pages

### Powered by Google Gemini 2.5 Flash
- **Advanced AI**: Uses Google's latest Gemini model for superior understanding
- **High Intelligence**: Temperature set to 0.9 for creative, helpful responses
- **Reliable Extraction**: Structured data extraction with intelligent parsing

## 🔧 Technical Improvements

### Chat Service Enhancements
- Enabled Gemini AI for complex query handling
- Improved prompt engineering for better data extraction
- Added intelligent response parsing with `---EXTRACTION---` separator
- Increased max tokens to 800 for more comprehensive responses
- Added logging for AI responses and extracted data

### API Improvements
- Fixed CSRF token handling with `@csrf_exempt` decorators
- Improved error handling and fallback mechanisms
- Better session management for chat context

### User Experience
- Chat widget auto-generates itinerary when all data is collected
- Improved CSRF token retrieval from cookies and forms
- Better loading states and user feedback

## 📊 How It Works

1. **Open Chat**: Click the chat widget on any page
2. **Tell Your Story**: Describe your dream trip naturally
3. **AI Understands**: Gemini extracts all trip details
4. **Instant Itinerary**: Get your personalized safari plan immediately

## 🎯 Example Conversations

**Quick Trip:**
```
User: "I want a one day trip to Kakamega with budget of 10000"
Bot: "Perfect! A day trip to Kakamega Forest with 10,000 KSh is totally doable..."
→ Generates itinerary instantly
```

**Detailed Planning:**
```
User: "I love adventure and cool food"
Bot: "Awesome! Adventure and food experiences make for an unforgettable trip..."
User: "2 days in Nairobi with mid-range budget"
Bot: "Great choice! Generating your personalized itinerary..."
→ Creates complete 2-day Nairobi adventure
```

## 🚀 Getting Started

1. Visit [SafariSmart Kenya](https://safarismart.co.ke)
2. Click the chat widget in the bottom right
3. Start chatting about your dream safari
4. Get your personalized itinerary in seconds!

## 🔄 Migration Notes

- No database migrations required
- Existing wizard flow still available as fallback
- Chat feature can be disabled via admin panel if needed

## 🐛 Bug Fixes

- Fixed Gemini model name (now using correct `gemini-2.5-flash`)
- Resolved 403 Forbidden errors on chat API endpoints
- Fixed greeting handling to prevent message duplication
- Improved data extraction reliability

## 📝 Configuration

Admins can configure the chatbot via Django Admin:
- Enable/disable chat feature
- Customize welcome and completion messages
- Adjust AI complexity threshold
- Set max conversation turns

## 🙏 Acknowledgments

Special thanks to Google Gemini for powering our intelligent chatbot!

## 📞 Support

Having issues? Contact us at info@safarismart.co.ke

---

**Full Changelog**: https://github.com/owuorviny109/SafariSmart/compare/v1.0.0...v1.1.0
