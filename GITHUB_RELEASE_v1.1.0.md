# 🤖 Intelligent AI Chatbot - Powered by Google Gemini

Plan your Kenyan safari in seconds through natural conversation!

## ✨ Key Features

🗣️ **Natural Language Planning**
- Just chat naturally: "I want a 2 day trip to Kakamega with 50000 budget"
- AI understands context and extracts all trip details automatically

⚡ **Instant Itinerary Generation**
- From conversation to complete itinerary in under a minute
- No more clicking through wizard steps

🧠 **Powered by Gemini 2.5 Flash**
- Google's latest AI model for superior understanding
- Smart data extraction and intelligent responses

## 🎯 What's Included

- ✅ Conversational trip planning chatbot
- ✅ Automatic extraction of destinations, duration, budget, interests
- ✅ End-to-end itinerary generation
- ✅ Context-aware AI responses
- ✅ Available on all pages via chat widget

## 🚀 Try It Now

1. Visit the site
2. Click the chat widget (bottom right)
3. Tell the bot about your dream safari
4. Get your personalized itinerary instantly!

## 🔧 Technical Details

- **AI Model**: Google Gemini 2.5 Flash
- **Temperature**: 0.9 (high intelligence)
- **Max Tokens**: 800 (comprehensive responses)
- **API**: CSRF-protected endpoints
- **Fallback**: Template-based generation if AI fails

## 📝 Files Changed

- `core/services/chat_service.py` - AI integration and intelligent extraction
- `core/views.py` - CSRF-exempt chat API endpoints
- `static/js/chat-widget.js` - End-to-end itinerary generation

## 🐛 Bug Fixes

- Fixed Gemini model name
- Resolved 403 CSRF errors
- Improved greeting handling
- Better data extraction reliability

---

**Full Release Notes**: See RELEASE_NOTES_v1.1.0.md
