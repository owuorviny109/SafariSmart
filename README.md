# SafariSmart Kenya

**AI-Powered Safari and Travel Planning Platform**

[![Live Demo](https://img.shields.io/badge/demo-live-success)](https://safarismart-kenya.onrender.com)
[![Python](https://img.shields.io/badge/python-3.11-blue)](https://www.python.org/)
[![Django](https://img.shields.io/badge/django-5.0-green)](https://www.djangoproject.com/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

---

## Project Overview

**SafariSmart Kenya** is a travel platform designed to modernize how users plan their Kenyan safaris. By integrating **Google's Gemini AI**, the system generates personalized, budget-conscious, and interest-based itineraries. The platform aims to promote domestic tourism by making travel planning accessible and transparent.

### Mission
To democratize travel planning in Kenya, enabling users to discover destinations and plan affordable trips through intelligent automation.

---

## System Architecture

The following diagram illustrates the high-level architecture of the SafariSmart Kenya platform, detailing the data flow between the user, the Django backend, and the external Gemini AI service.

```mermaid
graph TD
    User[User Client] -->|HTTP Request| LoadBalancer[Load Balancer/Render]
    LoadBalancer -->|Forward| Django[Django Backend]
    
    subgraph "Application Layer"
        Django -->|Route| Views[View Controllers]
        Views -->|Validate| Forms[Form Validation]
        Views -->|Query| ORM[Django ORM]
    end
    
    subgraph "AI Integration Layer"
        Views -->|Prepare Prompt| GeminiService[Gemini Service]
        GeminiService -->|API Call| GeminiAPI[Google Gemini API]
        GeminiAPI -->|JSON Response| GeminiService
    end
    
    subgraph "Data Layer"
        ORM -->|Read/Write| DB[(PostgreSQL Database)]
    end
    
    GeminiService -->|Parsed Data| Views
    Views -->|Render| Templates[HTML Templates]
    Templates -->|Response| User
```

---

## Database Schema

The application uses a relational database to manage users, destinations, and generated itineraries. The core relationships are depicted below.

```mermaid
erDiagram
    User ||--o{ Itinerary : "creates"
    User ||--o{ WizardSession : "has"
    
    Destination ||--o{ Itinerary : "included_in"
    Destination ||--o{ WizardSession : "selected_in"
    
    User {
        int id PK
        string username
        string email
    }
    
    Destination {
        int id PK
        string name
        string destination_type
        decimal average_cost_per_day
        string popular_activities
    }
    
    Itinerary {
        int id PK
        int user_id FK
        string title
        int duration_days
        json itinerary_data
        int total_budget
        string share_code
    }
    
    WizardSession {
        int id PK
        string session_key
        int current_step
        json interests
        int budget_amount
    }
```

---

## Key Features

- **AI-Powered Itinerary Generator**: Utilizes Generative AI to create day-by-day travel plans based on user constraints (budget, group size, interests).
- **Destination Management**: A curated database of over 20 Kenyan destinations with detailed metadata (costs, activities, weather).
- **Wizard-Based Interface**: A multi-step form that guides users through the planning process, storing progress in `WizardSession` to prevent data loss.
- **Security Implementation**:
    - **Brute-force Protection**: Implemented via `django-axes`.
    - **Content Security Policy**: Enforced using `django-csp`.
    - **Rate Limiting**: Applied to API endpoints to prevent abuse.
- **Responsive Design**: Built with Bootstrap 5 and SCSS for a consistent experience across devices.

---

## Technology Stack

- **Backend Framework**: Django 5.0 (Python 3.11)
- **AI Service**: Google Generative AI (Gemini Pro)
- **Database**: PostgreSQL (Production), SQLite (Development)
- **Frontend**: HTML5, SCSS, Bootstrap 5, JavaScript
- **Security Libraries**: Argon2, Bleach, Django-CSP, Django-Axes
- **Deployment Platform**: Render.com

---

## Installation and Setup

### Prerequisites
- Python 3.11 or higher
- Git
- Virtualenv

### Step-by-Step Installation

1.  **Clone the Repository**
    ```bash
    git clone https://github.com/owuorviny109/safarismart-kenya.git
    cd safarismart-kenya
    ```

2.  **Create and Activate Virtual Environment**
    ```bash
    python -m venv venv
    # Windows
    venv\Scripts\activate
    # Linux/Mac
    source venv/bin/activate
    ```

3.  **Install Dependencies**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Environment Configuration**
    Create a `.env` file in the root directory with the following variables:
    ```env
    DEBUG=True
    SECRET_KEY=your-secure-secret-key
    GEMINI_API_KEY=your-google-gemini-api-key
    OPENWEATHER_API_KEY=your-openweather-api-key
    DATABASE_URL=sqlite:///db.sqlite3
    ```

5.  **Apply Database Migrations**
    ```bash
    python manage.py migrate
    ```

6.  **Load Initial Configuration Data**
    This script populates the database with default travel types, budget categories, and system settings.
    ```bash
    python manage.py shell < load_config_data.py
    ```

7.  **Start the Development Server**
    ```bash
    python manage.py runserver
    ```

---

## Code Structure

The project follows a standard Django modular structure:

-   `accounts/`: Handles user authentication, registration, and profile management.
-   `api/`: Contains internal API endpoints for dynamic frontend interactions.
-   `core/`: Manages the main landing page, dashboard, and itinerary generation logic.
-   `destinations/`: Manages destination data, listing views, and detail pages.
-   `safarismart/`: Project-level settings, URL routing, and WSGI configuration.
-   `static/`: Stores static assets (CSS, JavaScript, Images).
-   `templates/`: Contains HTML templates organized by app.
-   `load_config_data.py`: A utility script for seeding the database with initial configuration data.

---

## Contributing

Contributions are welcome. Please follow the standard fork-and-pull request workflow:
1.  Fork the repository.
2.  Create a feature branch.
3.  Commit your changes with clear messages.
4.  Push to your branch.
5.  Open a Pull Request describing your changes.

---

## Contact

**Vincent Owuor**
- GitHub: [@owuorviny109](https://github.com/owuorviny109)
- Email: owuorvincent069@gmail.com
- Portfolio: [owuorvincent.vercel.app](https://owuorvincent.vercel.app/)
