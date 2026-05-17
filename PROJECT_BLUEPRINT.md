# THE MEDILIFE - Complete Project Blueprint

> Use this document to replicate the exact architecture, UI patterns, styling, and execution flow in a new project.

---

## 1. PROJECT OVERVIEW

- **Type:** Full-stack AI-powered web application
- **Domain:** Medical diagnosis / Disease prediction
- **Architecture:** Monolithic Flask app with Blueprint-based modular routing
- **Database:** PostgreSQL with SQLAlchemy ORM
- **ML Backend:** scikit-learn (RandomForest) + TensorFlow/Keras (CNN)
- **AI Chatbot:** Ollama local LLM (qwen2.5-coder:7b)
- **Deployment:** AWS EC2
- **Port:** 3000

---

## 2. TECH STACK (Exact Versions)

### Backend
| Package | Version | Purpose |
|---------|---------|---------|
| Flask | 2.3.2 | Web framework |
| SQLAlchemy (Flask-SQLAlchemy) | latest | ORM |
| Flask-Login | latest | Session auth |
| Werkzeug | 2.3.7 | Password hashing, WSGI |
| Jinja2 | 3.1.2 | Templating |
| python-dotenv | 1.0.0 | Environment variables |
| gunicorn | 21.2.0 | Production WSGI server |
| psycopg2 | latest | PostgreSQL driver |

### ML/AI
| Package | Version | Purpose |
|---------|---------|---------|
| scikit-learn | 1.3.0 | RandomForestClassifier |
| numpy | 1.26.0 | Array operations |
| pandas | 2.1.0 | Data manipulation |
| tensorflow | latest | CNN models (malaria, pneumonia) |
| Pillow | latest | Image processing |
| h5py | latest | Loading .h5 model files |

### Other
| Package | Version | Purpose |
|---------|---------|---------|
| reportlab | latest | PDF generation |
| requests | latest | Ollama API calls |
| scipy | 1.11.2 | Scientific computing |

### Frontend (CDN-based, no npm)
| Library | Version | CDN |
|---------|---------|-----|
| Bootstrap | 5.3.0 | cdn.jsdelivr.net/npm/bootstrap@5.3.0 |
| Font Awesome | 6.4.0 | cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0 |
| AOS (Animate on Scroll) | 2.3.1 | unpkg.com/aos@2.3.1 |
| Chart.js | latest | cdn.jsdelivr.net/npm/chart.js |
| Google Fonts - Poppins | 300-700 | fonts.googleapis.com |
| Google Fonts - Inter | 300-700 | fonts.googleapis.com (admin only) |

---

## 3. PROJECT STRUCTURE

```
project_root/
├── app.py                      # Main Flask app, model loading, prediction routes
├── models.py                   # All 14 SQLAlchemy models
├── db.py                       # Database init (SQLAlchemy + PostgreSQL)
├── auth.py                     # Flask-Login setup + user_loader
├── retrain.py                  # Background model retraining system
├── explainability.py           # Feature importance extraction
├── email_service.py            # HTML email via Gmail SMTP
├── translations.py             # Multi-language dictionaries (en/hi/mr)
├── validators.py               # Input validation functions
├── routes_auth.py              # Blueprint: login/register/logout
├── routes_user.py              # Blueprint: user dashboard routes
├── routes_admin.py             # Blueprint: admin panel routes
├── routes_logging_api.py       # Blueprint: prediction/chat logging API
├── routes_reports.py           # Blueprint: PDF report generation
├── requirements.txt            # Python dependencies
├── .env                        # Environment variables (secrets)
│
├── models/                     # Trained ML model files
│   ├── diabetes.pkl            # RandomForest pickle
│   ├── cancer.pkl
│   ├── heart.pkl
│   ├── kidney.pkl
│   ├── liver.pkl
│   ├── malaria.h5              # Keras CNN model
│   └── pneumonia.h5            # Keras CNN model
│
├── templates/
│   ├── main.html               # Base layout (public pages)
│   ├── index.html              # Public landing page
│   ├── login.html              # Login form
│   ├── register.html           # Registration form
│   ├── predictors.html         # Disease selection page
│   ├── diabetes.html           # Disease-specific input forms
│   ├── cancer.html
│   ├── heart.html
│   ├── kidney.html
│   ├── liver.html
│   ├── malaria.html
│   ├── pneumonia.html
│   ├── predict.html            # Prediction results display
│   ├── chatbot.html            # AI chatbot interface
│   ├── contact.html            # Contact form
│   ├── 404.html / 500.html     # Error pages
│   │
│   ├── user/
│   │   ├── user_home.html      # User dashboard
│   │   ├── profile.html        # Profile management
│   │   ├── history.html        # Prediction history
│   │   ├── health_trends.html  # Charts & analytics
│   │   ├── appointments.html   # Doctor appointments
│   │   └── support.html        # Support tickets
│   │
│   └── admin/
│       ├── base_admin.html     # Admin base layout (sidebar)
│       ├── admin_dashboard.html # KPI cards + charts
│       ├── users.html          # User CRUD
│       ├── doctors.html        # Doctor CRUD
│       ├── predictions.html    # All predictions view
│       ├── chatlogs.html       # Chat history
│       ├── complaints.html     # Support tickets management
│       ├── appointments.html   # Appointment management
│       └── health_overview.html # Analytics overview
│
├── static/
│   ├── css/style.css           # Main stylesheet
│   ├── img/                    # Images and icons
│   └── reports/                # Generated PDF reports
│
└── Python Notebooks/           # Model training notebooks
```



---

## 4. APPLICATION EXECUTION FLOW

### 4.1 App Initialization (app.py)

```
1. Load environment variables (.env) via python-dotenv
2. Configure Ollama chatbot URL (localhost:11434) and model name
3. Create Flask app with random SECRET_KEY
4. Inject datetime.now and translation context into Jinja2 globals
5. Load ML models at startup:
   - 5 pickle files → scikit-learn RandomForestClassifier
   - 2 .h5 files → TensorFlow Keras CNN (custom legacy loader)
6. Import and initialize:
   - db.py → init_db(app) → SQLAlchemy with PostgreSQL
   - auth.py → init_auth(app) → Flask-Login
7. Register 5 Blueprints:
   - auth_bp (routes_auth.py)
   - user_bp (routes_user.py)
   - admin_bp (routes_admin.py)
   - logging_bp (routes_logging_api.py)
   - reports_bp (routes_reports.py)
8. Create all database tables (db.create_all())
9. Run on 0.0.0.0:3000 with debug=True
```

### 4.2 Request Flow Diagram

```
User Request
    │
    ├─ Public (not logged in) → index.html (landing page)
    │
    ├─ POST /login → validate → login_user() → redirect based on role
    │   ├─ Admin → /admin/dashboard
    │   └─ User → /home (user_home.html)
    │
    ├─ POST /predict → get form data → load model → predict → render predict.html
    │   ├─ Tabular diseases: extract features → model.predict_proba()
    │   └─ Image diseases: PIL resize → numpy array → model.predict()
    │
    ├─ POST /chat → build context from last 6 messages → POST to Ollama API → format response
    │
    ├─ POST /api/log/prediction → save to disease_predictions + disease-specific table + audit_log + send email
    │
    └─ POST /reports/generate → ReportLab canvas → save PDF → return path
```

### 4.3 Authentication Flow

```
Registration:
  1. Validate all fields (name, email, password, phone, age) via validators.py
  2. Check email uniqueness
  3. Hash password with Werkzeug generate_password_hash()
  4. Create User record → commit to DB
  5. Redirect to login

Login:
  1. Validate email format
  2. Query user by email
  3. check_password() with Werkzeug
  4. login_user() via Flask-Login
  5. Log AuditLog entry (activity="Login", ip_address)
  6. Redirect: admin → /admin/dashboard, user → /home

Session Management:
  - Flask-Login handles session cookies
  - @login_required decorator protects routes
  - user_loader fetches User by user_id from session
  - is_admin check via getattr(current_user, "is_admin", False)
```

### 4.4 Prediction Flow (Detailed)

```
Tabular Disease (diabetes, cancer, heart, kidney, liver):
  1. User fills HTML form with medical parameters
  2. POST /predict with disease_type in form data
  3. Server extracts form fields
  4. Maps form field names → model feature names (FIELD_MAPPINGS dict)
  5. Builds feature array in correct order (model.feature_names_in_)
  6. model.predict_proba() → get prediction + confidence %
  7. get_feature_importance() → top 8 contributing features
  8. Render predict.html with results + explanations

Image Disease (malaria, pneumonia):
  1. User uploads image file
  2. POST /predict with image file + disease_type
  3. Server opens image with PIL
  4. Resize to 36x36 pixels
  5. Malaria: RGB (36,36,3) | Pneumonia: Grayscale (36,36,1)
  6. Normalize to 0-1 range, expand dims for batch
  7. model.predict() → argmax or threshold at 0.5
  8. Render predict.html with result

Client-side Logging (after result displayed):
  - JavaScript POSTs to /api/log/prediction with all data
  - Server saves to disease_predictions table
  - Also saves to disease-specific table (diabetes_data, etc.)
  - Creates AuditLog entry
  - Sends email notification to user
```

### 4.5 Chatbot Flow

```
1. User types message in chatbot.html
2. JavaScript POSTs to /chat endpoint
3. Server builds context string from last 6 messages (system + user + assistant)
4. POSTs to Ollama API (localhost:11434/api/generate):
   - model: "qwen2.5-coder:7b"
   - stream: false
   - temperature: 0.7
5. Receives response, formats markdown → HTML:
   - Headers → <strong>
   - **bold** → <strong>
   - *italic* → <em>
   - Numbered lists → bullet points
   - Newlines → <br>
6. Returns JSON {reply: "..."}
7. Client-side logs to /api/log/chat
```

### 4.6 Auto-Retraining Flow

```
1. Admin clicks "Retrain All Models" button
2. POST /admin/retrain → starts background thread
3. For each disease (diabetes, heart, kidney, liver, cancer):
   a. Query all DiseasePrediction records for that disease
   b. Extract features from stored form_data JSON
   c. Skip if < 5 samples
   d. Backup current model to models/backups/
   e. Train new RandomForestClassifier (n_estimators=20)
   f. Evaluate on 20% test split
   g. Reject if accuracy < 50%
   h. Save new model pickle if passes
4. Frontend polls /admin/retrain/status every 3 seconds
5. Shows results per disease (success/skipped/rejected)
```



---

## 5. DATABASE SCHEMA (PostgreSQL)

### Connection
```
DATABASE_URL=postgresql+psycopg2://postgres:postgres@localhost:5432/medilife
```

### Tables (14 total)

#### users
| Column | Type | Constraints |
|--------|------|-------------|
| user_id | Integer | PK, auto-increment |
| full_name | String(100) | NOT NULL |
| email | String(100) | UNIQUE, NOT NULL, indexed |
| password_hash | String(255) | NOT NULL (Werkzeug hash) |
| age | Integer | nullable |
| gender | String(10) | nullable |
| phone | String(15) | nullable |
| blood_group | String(5) | nullable |
| address | Text | nullable |
| emergency_contact | String(15) | nullable |
| created_at | DateTime | default=utcnow |
| is_admin | Boolean | default=False |
| is_active | Boolean | default=True |

#### disease_predictions
| Column | Type | Constraints |
|--------|------|-------------|
| prediction_id | Integer | PK |
| user_id | Integer | FK→users.user_id, indexed |
| disease_name | String(100) | NOT NULL |
| prediction_result | String(100) | NOT NULL ("0" or "1") |
| confidence_score | Float | nullable |
| risk_level | String(50) | nullable |
| form_data | Text | nullable (JSON string) |
| prediction_date | DateTime | default=utcnow |

#### chatbot_history
| Column | Type | Constraints |
|--------|------|-------------|
| chat_id | Integer | PK |
| user_id | Integer | FK→users, indexed |
| user_message | Text | NOT NULL |
| bot_response | Text | NOT NULL |
| chat_time | DateTime | default=utcnow |

#### reports
| Column | Type | Constraints |
|--------|------|-------------|
| report_id | Integer | PK |
| user_id | Integer | FK→users, indexed |
| report_name | String(100) | NOT NULL |
| generated_date | DateTime | default=utcnow |
| report_path | Text | NOT NULL |

#### diabetes_data / heart_disease_data / kidney_disease_data / liver_disease_data / cancer_data
Disease-specific tables storing key medical parameters + result + user_id + created_at.

#### image_uploads
| Column | Type | Constraints |
|--------|------|-------------|
| image_id | Integer | PK |
| user_id | Integer | FK→users, indexed |
| disease_type | String(50) | NOT NULL |
| image_path | Text | NOT NULL |
| upload_date | DateTime | default=utcnow |
| prediction_result | String(50) | nullable |

#### audit_logs
| Column | Type | Constraints |
|--------|------|-------------|
| log_id | Integer | PK |
| user_id | Integer | FK→users, indexed |
| activity | Text | NOT NULL |
| ip_address | String(50) | nullable |
| log_time | DateTime | default=utcnow |

#### complaints
| Column | Type | Constraints |
|--------|------|-------------|
| complaint_id | Integer | PK |
| user_id | Integer | FK→users, NOT NULL |
| subject | String(200) | NOT NULL |
| description | Text | NOT NULL |
| category | String(50) | NOT NULL |
| status | String(20) | default="open" |
| admin_response | Text | nullable |
| created_at | DateTime | default=utcnow |
| updated_at | DateTime | auto-update |

#### doctors
| Column | Type | Constraints |
|--------|------|-------------|
| doctor_id | Integer | PK |
| name | String(100) | NOT NULL |
| specialization | String(100) | NOT NULL |
| qualification | String(200) | nullable |
| experience_years | Integer | nullable |
| consultation_fee | Integer | nullable |
| hospital | String(200) | nullable |
| phone | String(15) | nullable |
| email | String(100) | nullable |
| available_days | String(100) | nullable |
| bio | Text | nullable |
| is_active | Boolean | default=True |

#### appointments
| Column | Type | Constraints |
|--------|------|-------------|
| appointment_id | Integer | PK |
| user_id | Integer | FK→users, NOT NULL |
| doctor_id | Integer | FK→doctors, NOT NULL |
| appointment_date | Date | NOT NULL |
| appointment_time | String(10) | NOT NULL |
| reason | String(200) | nullable |
| status | String(20) | default="scheduled" |
| created_at | DateTime | default=utcnow |

### Relationships & Cascade
- All FK relationships use `cascade="all, delete-orphan"` on backref
- Deleting a user cascades to: predictions, chat_history, reports, diabetes_records, heart_records, kidney_records, liver_records, cancer_records, image_uploads, audit_logs, complaints, appointments



---

## 6. UI & STYLING BLUEPRINT

### 6.1 Design System - CSS Variables

```css
:root {
    --primary-color: #2c3e50;      /* Dark blue-gray (navbar, headings) */
    --secondary-color: #3498db;    /* Bright blue (buttons, accents, links) */
    --accent-color: #e74c3c;       /* Red (alerts, danger) */
    --text-color: #2c3e50;         /* Body text */
    --light-bg: #f8f9fa;           /* Light gray backgrounds */
    --dark-bg: #2c3e50;            /* Dark backgrounds */
    --success-color: #2ecc71;      /* Green */
    --warning-color: #f1c40f;      /* Yellow */
    --danger-color: #e74c3c;       /* Red */
    --border-radius: 15px;         /* Card corners */
    --box-shadow: 0 5px 15px rgba(0,0,0,0.1);
    --transition: all 0.3s ease;
}
```

### 6.2 Typography

| Context | Font | Weights | Source |
|---------|------|---------|--------|
| Public pages | Poppins | 300,400,500,600,700 | Google Fonts |
| Admin panel | Inter | 300,400,500,600,700 | Google Fonts |
| Legacy (CSS file) | Roboto | 300,400,500,700,900 | Google Fonts |

### 6.3 Color Palette

| Usage | Color | Hex |
|-------|-------|-----|
| Primary gradient start | Deep navy | #1a237e |
| Primary gradient end | Blue | #3498db |
| Navbar background | Dark gradient | linear-gradient(90deg, #2c3e50, #34495e) |
| Hero section | Diagonal gradient | linear-gradient(135deg, #1a237e, #3498db) |
| Footer | Deep navy | #1a237e |
| Admin sidebar | Dark slate | linear-gradient(180deg, #1e293b, #0f172a) |
| Positive/Danger | Red | #c62828 |
| Negative/Success | Green | #2e7d32 |
| KPI blue | Blue | #3b82f6 |
| KPI green | Green | #16a34a |
| KPI amber | Amber | #d97706 |
| KPI purple | Purple | #4f46e5 |

### 6.4 Layout Patterns

#### Public Pages (main.html base)
```
┌─────────────────────────────────────────┐
│ NAVBAR (fixed-top, dark gradient)       │
│ Logo | Nav Links | Language Dropdown    │
├─────────────────────────────────────────┤
│                                         │
│ MAIN CONTENT (padding-top: 80px)        │
│ {% block content %}                     │
│                                         │
├─────────────────────────────────────────┤
│ FOOTER (3-column: brand | copyright |   │
│         links + social icons)           │
└─────────────────────────────────────────┘
```

#### Admin Pages (base_admin.html)
```
┌──────────┬──────────────────────────────┐
│ SIDEBAR  │ TOPBAR (sticky, white)       │
│ 250px    │ Page Title | Admin Avatar    │
│ fixed    ├──────────────────────────────┤
│          │                              │
│ Brand    │ PAGE CONTENT                 │
│ Nav      │ (padding: 25px 30px)         │
│ Sections │                              │
│          │ Flash Messages               │
│ Logout   │ {% block content %}          │
│          │                              │
└──────────┴──────────────────────────────┘
Mobile: sidebar collapses to 60px (icons only)
```

#### User Dashboard (user_home.html)
```
┌─────────────────────────────────────────┐
│ HERO BANNER (gradient, welcome message) │
│ Left: Text + CTA buttons               │
│ Right: Illustration image              │
├─────────────────────────────────────────┤
│ QUICK ACTION CARDS (3x2 grid)           │
│ Each: icon circle + title + description │
├─────────────────────────────────────────┤
│ RECENT PREDICTIONS (3 cards)            │
│ Color-coded left border (red/green)     │
├─────────────────────────────────────────┤
│ FEATURE HIGHLIGHTS (4-column icons)     │
└─────────────────────────────────────────┘
```

### 6.5 Component Patterns

#### Cards
```css
.card {
    border: none;
    border-radius: 12px;
    box-shadow: 0 4px 20px rgba(0,0,0,0.08);
    padding: 24px;
}
.card:hover {
    transform: translateY(-5px);
    box-shadow: 0 8px 25px rgba(0,0,0,0.12);
}
```

#### Buttons
```css
.btn-custom {
    background: var(--secondary-color);  /* #3498db */
    color: white;
    border: none;
    padding: 12px 30px;
    border-radius: 30px;               /* Pill shape */
    transition: all 0.3s ease;
}
.btn-custom:hover {
    background: var(--primary-color);
    transform: translateY(-3px);
    box-shadow: 0 5px 15px rgba(0,0,0,0.2);
}
```

#### Form Controls
```css
.form-control {
    border-radius: 8px;
    padding: 10px 14px;
    border: 1.5px solid #e0e0e0;
}
.form-control:focus {
    border-color: #3498db;
    box-shadow: 0 0 0 3px rgba(52, 152, 219, 0.1);
}
```

#### KPI Cards (Admin)
```css
.kpi-card {
    background: #fff;
    border-radius: 12px;
    padding: 20px;
    border: 1px solid #e2e8f0;
}
.kpi-icon {
    width: 42px; height: 42px;
    border-radius: 10px;
    /* Background color varies per metric */
}
.kpi-value { font-size: 1.6rem; font-weight: 700; color: #1e293b; }
.kpi-label { font-size: 0.78rem; color: #64748b; }
```

#### Data Tables (Admin)
```css
.admin-table th {
    font-size: 0.72rem;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    color: #64748b;
    background: #f8fafc;
}
.admin-table td {
    font-size: 0.85rem;
    color: #334155;
}
.admin-table tr:hover td { background: #f8fafc; }
```

#### Badges
```css
.badge-success { background: #dcfce7; color: #166534; border-radius: 20px; }
.badge-danger  { background: #fee2e2; color: #991b1b; border-radius: 20px; }
.badge-warning { background: #fef3c7; color: #92400e; border-radius: 20px; }
.badge-info    { background: #dbeafe; color: #1e40af; border-radius: 20px; }
```

### 6.6 Responsive Breakpoints

| Breakpoint | Behavior |
|------------|----------|
| > 992px | Full layout, sidebar visible |
| 768-991px | Navbar collapses, sidebar icons only (60px) |
| < 768px | Mobile stack, hero centered, cards full-width |

### 6.7 Animations & Effects

- **AOS (Animate on Scroll):** `data-aos="fade-up"`, `data-aos-delay="100/200/300"`, duration=1000ms, once=true
- **Card hover:** `transform: translateY(-5px)` + enhanced box-shadow
- **Button hover:** `transform: translateY(-3px)` + shadow
- **Nav link underline:** pseudo-element `::after` width animation from center
- **Custom scrollbar:** 6px width, #bbb thumb, #f1f1f1 track
- **Page transitions:** CSS `transition: all 0.3s ease` on interactive elements

### 6.8 Icon System

- **Library:** Font Awesome 6.4.0 (Free, solid + brands)
- **Usage pattern:** `<i class="fas fa-{icon}"></i>` before text
- **Key icons used:**
  - Navigation: fa-home, fa-stethoscope, fa-robot, fa-headset, fa-user, fa-sign-out-alt
  - Dashboard: fa-microscope, fa-comments, fa-history, fa-calendar-check, fa-chart-line
  - Admin: fa-th-large, fa-users, fa-user-md, fa-chart-pie, fa-heartbeat, fa-ticket-alt
  - Status: fa-exclamation-triangle, fa-spinner fa-spin, fa-sync-alt
  - Also uses emoji icons: 🧬 🎯 📊 🤖 🩸 🎗️ ❤️ 🫘 🫁 🦟



---

## 7. COMPLETE ROUTE MAP

### 7.1 Public Routes (app.py)

| Method | URL | Function | Template |
|--------|-----|----------|----------|
| GET | / or /home | home() | index.html (guest) or user/user_home.html (logged in) |
| GET | /about | about() | about.html |
| GET | /predictors | predictors_page() | predictors.html |
| GET/POST | /contact | contact() | contact.html |
| GET | /HealthCareAssistant | healthcare_assistant() | chatbot.html |
| POST | /chat | chat() | JSON response |
| GET | /diabetes | diabetesPage() | diabetes.html |
| GET | /cancer | cancerPage() | cancer.html |
| GET | /heart | heartPage() | heart.html |
| GET | /kidney | kidneyPage() | kidney.html |
| GET | /liver | liverPage() | liver.html |
| GET | /malaria | malariaPage() | malaria.html |
| GET | /pneumonia | pneumoniaPage() | pneumonia.html |
| POST | /predict | predict_disease() | predict.html |
| GET | /set-language/<lang> | set_language() | redirect (sets cookie) |

### 7.2 Auth Routes (routes_auth.py) - Blueprint prefix: none

| Method | URL | Function | Template |
|--------|-----|----------|----------|
| GET/POST | /login | login() | login.html |
| GET/POST | /register | register() | register.html |
| GET | /logout | logout() | redirect to home |
| GET | /admin | admin_home() | redirect to admin.dashboard |

### 7.3 User Routes (routes_user.py) - Blueprint prefix: none

| Method | URL | Function | Auth | Template |
|--------|-----|----------|------|----------|
| GET | /dashboard | dashboard() | ✓ | redirect to profile |
| GET | /profile | profile() | ✓ | user/profile.html |
| POST | /profile/update | update_profile() | ✓ | redirect |
| POST | /profile/delete | delete_account() | ✓ | redirect (deletes user) |
| GET | /history | history() | ✓ | user/history.html |
| GET | /history/<id> | view_report() | ✓ | predict.html |
| GET/POST | /support | support() | ✓ | user/support.html |
| GET | /health-trends | health_trends() | ✓ | user/health_trends.html |
| GET/POST | /appointments | appointments() | ✓ | user/appointments.html |

### 7.4 Admin Routes (routes_admin.py) - Blueprint prefix: none

| Method | URL | Function | Template |
|--------|-----|----------|----------|
| GET | /admin/dashboard | dashboard() | admin/admin_dashboard.html |
| GET | /admin/users | users() | admin/users.html |
| POST | /admin/users/add | add_user() | redirect |
| POST | /admin/users/<id>/edit | edit_user() | redirect |
| POST | /admin/users/<id>/delete | delete_user() | redirect |
| GET | /admin/doctors | doctors() | admin/doctors.html |
| POST | /admin/doctors/add | add_doctor() | redirect |
| POST | /admin/doctors/<id>/edit | edit_doctor() | redirect |
| POST | /admin/doctors/<id>/delete | delete_doctor() | redirect |
| GET | /admin/predictions | predictions() | admin/predictions.html |
| GET | /admin/chatlogs | chatlogs() | admin/chatlogs.html |
| POST | /admin/retrain | trigger_retrain() | redirect |
| GET | /admin/retrain/status | retrain_status_view() | JSON |
| GET | /admin/complaints | complaints() | admin/complaints.html |
| POST | /admin/complaints/<id>/respond | respond_complaint() | redirect |
| GET | /admin/appointments | admin_appointments() | admin/appointments.html |
| POST | /admin/appointments/<id>/update | update_appointment() | redirect |
| GET | /admin/health-overview | health_overview() | admin/health_overview.html |

### 7.5 API Routes (routes_logging_api.py + routes_reports.py)

| Method | URL | Purpose | Response |
|--------|-----|---------|----------|
| POST | /api/log/prediction | Log prediction to DB + email | JSON {ok, prediction_id} |
| POST | /api/log/chat | Log chat message to DB | JSON {ok, chat_id} |
| POST | /reports/generate | Generate PDF report | JSON {ok, report_id, pdf_path} |



---

## 8. KEY FEATURES & IMPLEMENTATION PATTERNS

### 8.1 Multi-Language Support (i18n)

```python
# translations.py - Dictionary-based (no external library)
TRANSLATIONS = {
    "en": {"home": "Home", "login": "Login", ...},
    "hi": {"home": "होम", "login": "लॉगिन", ...},
    "mr": {"home": "मुख्यपृष्ठ", "login": "लॉगिन", ...},
}

# Language stored in cookie (max_age=1 year)
# Injected via @app.context_processor → {{ t.key }} in templates
# Language switcher: GET /set-language/<lang> → sets cookie → redirects back
```

### 8.2 Email Notifications

```python
# email_service.py - Gmail SMTP with HTML template
# Triggered after prediction is logged
# Uses MIMEMultipart("alternative") with HTML body
# SMTP: smtp.gmail.com:587 with STARTTLS
# Env vars: EMAIL_SENDER, EMAIL_PASSWORD (App Password)
```

### 8.3 PDF Report Generation

```python
# routes_reports.py - ReportLab canvas
# Generates simple text-based PDF with:
#   - Title, disease name, result, confidence
#   - Form data key-value pairs
# Saved to static/reports/ with UUID filename
# Record saved to reports table
```

### 8.4 Feature Importance / Explainability

```python
# explainability.py
# Extracts model.feature_importances_ (RandomForest)
# Or abs(model.coef_) for linear models
# Returns top 8 features sorted by contribution %
# Displayed as bar chart or list on predict.html
```

### 8.5 Input Validation Pattern

```python
# validators.py - Server-side validation functions
# validate_email(email) → error string or None
# validate_phone(phone) → error string or None
# validate_name(name) → error string or None
# validate_password(password) → error string or None
# validate_age(age) → error string or None

# Client-side: HTML5 pattern attributes + JavaScript custom validity
# Example: pattern="^[a-zA-Z\s.\-]{2,}$" for names
# Password: min 6 chars, must include letter + number
```

### 8.6 Flash Messages Pattern

```python
# Server: flash("message", "success" or "error")
# Template rendering:
{% with messages = get_flashed_messages(with_categories=true) %}
  {% for category, message in messages %}
    <div class="alert alert-{{ 'success' if category == 'success' else 'danger' }}
         alert-dismissible fade show">
      {{ message }}
      <button class="btn-close" data-bs-dismiss="alert"></button>
    </div>
  {% endfor %}
{% endwith %}
```

### 8.7 Chart.js Integration (Admin Dashboard)

```javascript
// Doughnut chart for disease distribution
new Chart(ctx, {
  type: 'doughnut',
  data: { labels, datasets: [{ data: values, backgroundColor: colors, borderWidth: 0 }] },
  options: { plugins: { legend: { position: 'bottom' } } }
});

// Stacked bar chart for positive vs negative
new Chart(ctx, {
  type: 'bar',
  data: { labels, datasets: [
    { label: 'Positive', data: [...], backgroundColor: '#ef4444' },
    { label: 'Negative', data: [...], backgroundColor: '#10b981' }
  ]},
  options: { scales: { x: { stacked: true }, y: { stacked: true } } }
});
```

### 8.8 Modal Pattern (Bootstrap 5)

```html
<!-- Trigger -->
<button data-bs-toggle="modal" data-bs-target="#myModal">Open</button>

<!-- Modal -->
<div class="modal fade" id="myModal" tabindex="-1">
  <div class="modal-dialog modal-dialog-centered">
    <div class="modal-content" style="border-radius: 15px;">
      <div class="modal-header border-0">
        <h5 class="modal-title">Title</h5>
        <button class="btn-close" data-bs-dismiss="modal"></button>
      </div>
      <div class="modal-body">
        <form method="POST" action="...">
          <!-- form fields -->
          <button type="submit" class="btn btn-primary w-100">Submit</button>
        </form>
      </div>
    </div>
  </div>
</div>
```

---

## 9. ENVIRONMENT VARIABLES (.env)

```env
DATABASE_URL=postgresql+psycopg2://postgres:postgres@localhost:5432/medilife
EMAIL_SENDER=your_email@gmail.com
EMAIL_RECEIVER=your_email@gmail.com
EMAIL_PASSWORD=your_gmail_app_password
OPENAI_API_KEY=optional_not_used
```

---

## 10. DEPLOYMENT NOTES (AWS EC2)

```bash
# Production setup
1. Ubuntu EC2 instance
2. Install Python 3.10+, PostgreSQL, Nginx
3. Clone repo, create venv, install requirements
4. Set up .env with production DATABASE_URL
5. Install and start Ollama for chatbot
6. Run with gunicorn:
   gunicorn app:app -b 0.0.0.0:3000 -w 4
7. Nginx reverse proxy on port 80 → localhost:3000
8. SSL via Let's Encrypt (optional)
```

---

## 11. HOW TO REPLICATE THIS PROJECT FOR A NEW DOMAIN

### Step-by-step:

1. **Setup Flask skeleton:**
   - app.py with Flask, SECRET_KEY, context_processor
   - db.py with SQLAlchemy + PostgreSQL
   - auth.py with Flask-Login
   - Create Blueprints for auth, user, admin, api

2. **Database models:**
   - User model with UserMixin, password hashing
   - Domain-specific prediction/data models
   - AuditLog, Complaints, Reports tables
   - Use cascade="all, delete-orphan" on relationships

3. **Frontend setup (no npm needed):**
   - Base template with Bootstrap 5.3.0 CDN
   - Font Awesome 6.4.0 for icons
   - AOS 2.3.1 for scroll animations
   - Google Fonts (Poppins for public, Inter for admin)
   - Chart.js for admin analytics
   - CSS variables for theming

4. **Two base templates:**
   - `main.html` → public/user pages (navbar + footer)
   - `admin/base_admin.html` → admin pages (sidebar + topbar)

5. **Styling approach:**
   - Inline `<style>` blocks in base templates for core styles
   - CSS variables for colors/spacing
   - Utility classes from Bootstrap
   - Hover effects: translateY + box-shadow
   - Gradient backgrounds for hero sections
   - Pill-shaped buttons (border-radius: 30px)
   - Cards with border-radius: 12-15px, no border, shadow

6. **ML Integration pattern:**
   - Load models at app startup (pickle for sklearn, h5 for keras)
   - Form → extract features → predict → render results
   - Store predictions in DB for retraining
   - Background thread for retraining with backup

7. **Chatbot pattern:**
   - Ollama running locally on port 11434
   - Maintain conversation context (last 6 messages)
   - POST to /api/generate with prompt
   - Format markdown response to HTML

8. **Key patterns to copy:**
   - Cookie-based language switching
   - Flash messages with Bootstrap alerts
   - Client-side form validation + server-side validators
   - Audit logging on login/logout/predictions
   - Email notifications on key events
   - PDF generation with ReportLab
   - Admin KPI dashboard with Chart.js
   - Role-based access (is_admin flag)
   - Cascade deletes for data cleanup

---

## 12. QUICK REFERENCE - CDN LINKS

```html
<!-- Bootstrap 5.3.0 -->
<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>

<!-- Font Awesome 6.4.0 -->
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">

<!-- AOS 2.3.1 -->
<link href="https://unpkg.com/aos@2.3.1/dist/aos.css" rel="stylesheet">
<script src="https://unpkg.com/aos@2.3.1/dist/aos.js"></script>
<script>AOS.init({ duration: 1000, once: true });</script>

<!-- Chart.js -->
<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>

<!-- Google Fonts -->
<link href="https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap" rel="stylesheet">
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
```

---

*Generated on: 2026-05-17 | Project: The Medilife - AI-Powered Medical Diagnosis System*
