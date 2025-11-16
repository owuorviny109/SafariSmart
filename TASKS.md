# SafariSmart Kenya - Development Tasks

## Project Status: Foundation Complete

### COMPLETED
- [x] Django project setup with 4 apps (core, destinations, accounts, api)
- [x] Database models created (Destination, WizardSession, Itinerary)
- [x] Migrations run successfully
- [x] Superuser created (owuorvincent069@gmail.com)
- [x] Admin panels configured
- [x] Bootstrap 5 base template
- [x] Landing page with Kenya theme
- [x] URL routing structure
- [x] Basic views scaffolded

---

## PHASE 1: SEED DATA & ADMIN (Priority: HIGH)

### Task 1.1: Create Kenya Destinations Fixture
- [ ] Create `destinations/fixtures/kenya_destinations.json`
- [ ] Add 20 Kenya destinations with data:
  - Maasai Mara (Safari)
  - Amboseli National Park (Safari)
  - Diani Beach (Beach)
  - Watamu (Beach)
  - Nairobi (City)
  - Mombasa (City)
  - Mount Kenya (Mountain)
  - Hell's Gate (Adventure)
  - Lake Nakuru (Safari)
  - Tsavo National Park (Safari)
  - Lamu Island (Cultural/Beach)
  - Samburu (Safari)
  - Lake Naivasha (Nature)
  - Malindi (Beach)
  - Nairobi National Park (Safari)
  - Giraffe Centre (Cultural)
  - Karen Blixen Museum (Cultural)
  - Ol Pejeta Conservancy (Safari)
  - Aberdare National Park (Mountain)
  - Meru National Park (Safari)
- [ ] Include: name, description, type, county, best time, avg cost, activities
- [ ] Load fixture: `python manage.py loaddata kenya_destinations`

### Task 1.2: Test Admin Panel
- [ ] Login to admin (http://127.0.0.1:8000/admin/)
- [ ] Verify destinations are loaded
- [ ] Mark 6 destinations as "featured"
- [ ] Test adding/editing destinations

---

## PHASE 2: WIZARD FLOW (Priority: HIGH)

### Task 2.1: Wizard Step 1 - Destinations
- [ ] Create template: `templates/core/wizard_step_1.html`
- [ ] Display all destinations in grid with cards
- [ ] Add multi-select functionality (JavaScript)
- [ ] Show destination type filters (Safari, Beach, City, Mountain)
- [ ] Add "Next" button (disabled until at least 1 selected)
- [ ] Save selections to session via AJAX

### Task 2.2: Wizard Step 2 - Duration & Dates
- [ ] Create template: `templates/core/wizard_step_2.html`
- [ ] Add duration selector buttons (1 day, 2-3 days, 4-5 days, 1 week, 2 weeks)
- [ ] Add date picker for travel dates
- [ ] Show progress indicator (Step 2/5)
- [ ] Save to session and navigate to Step 3

### Task 2.3: Wizard Step 3 - Travel Group
- [ ] Create template: `templates/core/wizard_step_3.html`
- [ ] Add adults counter (+/- buttons)
- [ ] Add children counter (+/- buttons)
- [ ] Add travel type buttons (Solo, Family, Couple, Friends)
- [ ] Show progress indicator (Step 3/5)
- [ ] Save to session and navigate to Step 4

### Task 2.4: Wizard Step 4 - Budget
- [ ] Create template: `templates/core/wizard_step_4.html`
- [ ] Add budget slider (KSh 10,000 - 200,000)
- [ ] Add budget category buttons (Budget, Mid-Range, Luxury)
- [ ] Show "per person" indicator
- [ ] Show progress indicator (Step 4/5)
- [ ] Save to session and navigate to Step 5

### Task 2.5: Wizard Step 5 - Interests
- [ ] Create template: `templates/core/wizard_step_5.html`
- [ ] Add interest cards (Wildlife, Culture, Food, Adventure, Relaxation, Photography)
- [ ] Multi-select with visual feedback
- [ ] Show progress indicator (Step 5/5)
- [ ] "Generate My Itinerary" button
- [ ] Save to session and navigate to generating screen

### Task 2.6: Generating Screen
- [ ] Create template: `templates/core/wizard_generating.html`
- [ ] Add loading animation
- [ ] Show progress messages:
  - "Analyzing your preferences..."
  - "Finding best routes between destinations..."
  - "Calculating optimal safari times..."
  - "Creating your perfect itinerary..."
- [ ] Trigger AI generation via AJAX
- [ ] Redirect to itinerary result page

---

## PHASE 3: GEMINI AI INTEGRATION (Priority: HIGH)

### Task 3.1: Setup Gemini API
- [ ] Get Gemini API key from Google AI Studio
- [ ] Add to `.env` file
- [ ] Create `core/services/gemini_service.py`
- [ ] Test basic Gemini connection

### Task 3.2: Create Itinerary Generation Logic
- [ ] Build prompt template for Gemini
- [ ] Include: destinations, duration, budget, interests, travel group
- [ ] Request structured JSON response with:
  - Day-by-day itinerary
  - Activities per day
  - Estimated costs
  - Travel times between locations
  - Accommodation suggestions
  - Food recommendations
- [ ] Parse Gemini response
- [ ] Save to Itinerary model

### Task 3.3: Handle AI Errors
- [ ] Add error handling for API failures
- [ ] Add retry logic
- [ ] Show user-friendly error messages
- [ ] Fallback to template-based itinerary if AI fails

---

## PHASE 4: ITINERARY DISPLAY (Priority: HIGH)

### Task 4.1: Itinerary Result Page
- [ ] Create template: `templates/core/itinerary_detail.html`
- [ ] Display trip summary header
- [ ] Show day-by-day timeline with cards
- [ ] Add interactive map (Google Maps or Leaflet)
- [ ] Show cost breakdown table
- [ ] Add action buttons:
  - Save Trip (requires login)
  - Share Trip (copy link)
  - Download PDF (future)
  - Adjust Trip (back to wizard with pre-filled data)

### Task 4.2: Social Proof & Weather
- [ ] Add view counter display
- [ ] Show "X people visited this destination this month"
- [ ] Integrate weather API for travel dates
- [ ] Display weather forecast per destination

### Task 4.3: Share Functionality
- [ ] Generate unique share code (UUID)
- [ ] Create shareable URL: `/trip/<share-code>/`
- [ ] Add "Copy Link" button with clipboard API
- [ ] Public view (no login required)
- [ ] Add "Create My Own" CTA for visitors

---

## PHASE 5: USER ACCOUNTS (Priority: MEDIUM)

### Task 5.1: Authentication Templates
- [ ] Create `templates/accounts/login.html`
- [ ] Create `templates/accounts/register.html`
- [ ] Create `templates/accounts/password_reset.html`
- [ ] Style with Bootstrap
- [ ] Add social login buttons (optional)

### Task 5.2: Dashboard
- [ ] Create template: `templates/core/dashboard.html`
- [ ] List saved itineraries
- [ ] Show trip cards with preview
- [ ] Add "Create New Trip" button
- [ ] Add edit/delete options
- [ ] Filter by date

### Task 5.3: Save Itinerary Feature
- [ ] Add "Save Trip" button on itinerary page
- [ ] Prompt login if not authenticated
- [ ] Associate itinerary with user
- [ ] Show success message
- [ ] Redirect to dashboard

---

## PHASE 6: DESTINATIONS PAGES (Priority: MEDIUM)

### Task 6.1: Destinations List Page
- [ ] Create template: `templates/destinations/list.html`
- [ ] Display all 20 destinations in grid
- [ ] Add filter by type (Safari, Beach, City, Mountain)
- [ ] Add search functionality
- [ ] Show quick facts per destination
- [ ] Link to detail pages

### Task 6.2: Destination Detail Page
- [ ] Create template: `templates/destinations/detail.html`
- [ ] Show photo gallery
- [ ] Display full description
- [ ] Show best time to visit
- [ ] Display average costs
- [ ] List popular activities
- [ ] Add "Include in My Trip" button (opens wizard with pre-selected)

### Task 6.3: Destination Modal in Wizard
- [ ] Create modal component for destination details
- [ ] Show on card click in wizard
- [ ] Display key info without leaving wizard flow
- [ ] Add "Select This" button in modal

---

## PHASE 7: POLISH & UX (Priority: MEDIUM)

### Task 7.1: Responsive Design
- [ ] Test on mobile devices
- [ ] Adjust wizard for mobile
- [ ] Fix navigation on small screens
- [ ] Optimize images for mobile

### Task 7.2: Loading States
- [ ] Add spinners for AJAX calls
- [ ] Disable buttons during processing
- [ ] Show skeleton loaders

### Task 7.3: Form Validation
- [ ] Client-side validation for wizard steps
- [ ] Server-side validation
- [ ] User-friendly error messages
- [ ] Highlight invalid fields

### Task 7.4: Animations & Transitions
- [ ] Add smooth transitions between wizard steps
- [ ] Animate destination card selections
- [ ] Add fade-in effects for content
- [ ] Progress bar animation

---

## PHASE 8: TESTING & DEPLOYMENT (Priority: LOW)

### Task 8.1: Testing
- [ ] Test full wizard flow
- [ ] Test AI generation with various inputs
- [ ] Test share functionality
- [ ] Test user registration/login
- [ ] Test on different browsers
- [ ] Test mobile responsiveness

### Task 8.2: Performance
- [ ] Optimize database queries
- [ ] Add caching for destinations
- [ ] Compress images
- [ ] Minify CSS/JS

### Task 8.3: SEO & Meta Tags
- [ ] Add meta descriptions
- [ ] Add Open Graph tags for sharing
- [ ] Create sitemap
- [ ] Add robots.txt

### Task 8.4: Deployment Prep
- [ ] Set DEBUG=False
- [ ] Configure production database (PostgreSQL)
- [ ] Setup static files serving
- [ ] Configure email backend
- [ ] Add error logging
- [ ] Create deployment guide

---

## FUTURE ENHANCEMENTS (Priority: BACKLOG)

- [ ] PDF download functionality
- [ ] Email itinerary feature
- [ ] Multi-language support (Swahili)
- [ ] Currency converter (USD, EUR, GBP)
- [ ] User reviews for destinations
- [ ] Photo upload for trips
- [ ] Trip collaboration (share with friends)
- [ ] Mobile app (React Native)
- [ ] WhatsApp integration
- [ ] Payment integration for bookings
- [ ] Affiliate links for hotels/tours

---

## NOTES

- Focus on MVP first (Phases 1-4)
- Use Bootstrap components for speed
- Keep Gemini prompts simple and structured
- Test AI generation frequently
- Get user feedback early

## NEXT IMMEDIATE TASK

**START HERE:** Task 1.1 - Create Kenya Destinations Fixture
