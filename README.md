# SafariSmart Kenya

AI-powered trip planning platform for Kenya adventures using Google Gemini AI.

## Project Overview

SafariSmart Kenya helps travelers plan their perfect Kenyan adventure through an intelligent 5-step wizard that generates personalized day-by-day itineraries.

## Features

- 5-step wizard for trip planning
- 20 curated Kenya destinations
- AI-powered itinerary generation using Gemini
- Budget optimization
- Shareable trip links
- User dashboard for saved trips
- Responsive Bootstrap 5 design

## Tech Stack

- **Backend**: Django 5.0.1
- **Frontend**: Bootstrap 5, Vanilla JavaScript
- **AI**: Google Gemini API
- **Database**: SQLite (development), PostgreSQL (production)
- **Python**: 3.13+

## Project Structure

```
safarismart-kenya/
├── core/              # Main app (wizard, itineraries, landing)
├── destinations/      # Destination management
├── accounts/          # User authentication
├── api/              # REST API endpoints
├── templates/        # HTML templates
├── static/           # CSS, JS, images
├── TASKS.md          # Development task list
├── INSTRUCTIONS.md   # Code quality standards
└── requirements.txt  # Python dependencies
```

## Setup Instructions

### 1. Clone Repository
```bash
git clone https://github.com/owuorviny109/SafariSmart.git
cd SafariSmart
```

### 2. Create Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment
```bash
cp .env.example .env
# Edit .env and add your GEMINI_API_KEY
```

**Get Gemini API Key:**
1. Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Sign in and create an API key
3. Add to `.env`: `GEMINI_API_KEY=your-key-here`

See [AI_SETUP.md](AI_SETUP.md) for detailed AI configuration.

### 5. Run Migrations
```bash
python manage.py migrate
```

### 6. Create Superuser
```bash
python manage.py createsuperuser
```

### 7. Load Destinations
```bash
python manage.py loaddata destinations/fixtures/kenya_destinations.json
```

### 8. Test AI Integration (Optional)
```bash
python manage.py shell < test_ai_generation.py
```

### 9. Run Development Server
```bash
python manage.py runserver
```

Visit http://127.0.0.1:8000/

## Development Status

### ✅ Completed (Phase 1-3)
- [x] Django project setup
- [x] Database models
- [x] Admin panels
- [x] Base templates with Bootstrap 5
- [x] Landing page
- [x] URL routing
- [x] Kenya destinations fixture (20 destinations)
- [x] Wizard flow (5 steps complete)
- [x] **Gemini AI integration** 🎉
- [x] Template fallback system
- [x] Itinerary generation API
- [x] Loading animations

### 🚧 In Progress (Phase 4)
- [ ] Itinerary detail page styling
- [ ] User authentication flow
- [ ] Dashboard with saved trips
- [ ] Share functionality

### 📋 Planned (Phase 5+)
- [ ] Rate limiting (5 itineraries/month free)
- [ ] Premium tier (Stripe/M-Pesa)
- [ ] PDF export
- [ ] Email itineraries

See [TASKS.md](TASKS.md) for detailed task list.

## Code Quality Standards

All code must follow the standards defined in [INSTRUCTIONS.md](INSTRUCTIONS.md):
- Strict OOP principles
- SOLID design patterns
- Comprehensive documentation
- Type hints
- Unit tests

## AI Integration

SafariSmart uses **Google Gemini AI** to generate personalized itineraries:

- **Cost**: ~$0.002 per itinerary (negligible for MVP)
- **Fallback**: Automatic template generation if AI fails
- **Free Tier**: 60 requests/minute (generous for testing)

### How It Works

1. User completes 5-step wizard
2. AI analyzes preferences (destinations, budget, interests)
3. Generates day-by-day itinerary with activities, costs, tips
4. Falls back to templates if AI unavailable
5. Saves to database with shareable link

See [AI_SETUP.md](AI_SETUP.md) for detailed documentation.

## API Keys Required

- **Gemini API**: Get from [Google AI Studio](https://makersuite.google.com/app/apikey)
  - Free tier: 60 requests/minute
  - Cost: ~$0.002 per itinerary

## Contributing

1. Follow code standards in INSTRUCTIONS.md
2. Check TASKS.md for available tasks
3. Create feature branch
4. Submit pull request

## License

Proprietary - SafariSmart Kenya Team

## Contact

For questions or support, contact: owuorvincent069@gmail.com

---

**Built with ❤️ for Kenya travelers**
