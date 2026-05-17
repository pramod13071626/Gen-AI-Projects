# Medilife - AI-Powered Medical Diagnosis System

A full-stack web application that uses Machine Learning and Deep Learning models to predict 7 major diseases. Built with Flask, PostgreSQL, and deployed on AWS EC2.

## Features

- Disease prediction for Diabetes, Breast Cancer, Heart Disease, Kidney Disease, Liver Disease, Malaria, and Pneumonia
- AI Healthcare Chatbot powered by Ollama (qwen2.5-coder:7b)
- User authentication and profile management
- Admin dashboard with analytics and user management
- Doctor management and appointment booking
- Prediction history and health trends visualization
- Feature importance explanations for predictions
- Email notifications on prediction results
- Auto-retraining system using collected prediction data
- Multi-language support (English, Hindi, Marathi)
- PDF report generation
- Audit logging for user activities

## Tech Stack

- **Backend:** Flask, SQLAlchemy, Flask-Login
- **Database:** PostgreSQL
- **ML Models:** scikit-learn (RandomForestClassifier), TensorFlow/Keras (CNN)
- **AI Chatbot:** Ollama (local LLM)
- **Frontend:** HTML, Bootstrap 5, Chart.js
- **Deployment:** AWS EC2

## Project Structure

```
├── app.py                     Main Flask application
├── models.py                  SQLAlchemy database models (14 tables)
├── db.py                      Database initialization
├── auth.py                    Flask-Login setup
├── retrain.py                 Auto-retraining system
├── explainability.py          Feature importance explanations
├── email_service.py           Email notifications
├── translations.py            Multi-language support (en/hi/mr)
├── routes_auth.py             Login / Register / Logout
├── routes_user.py             User dashboard routes
├── routes_admin.py            Admin panel routes
├── routes_logging_api.py      Prediction & chat logging API
├── routes_reports.py          PDF report generation
├── requirements.txt           Python dependencies
├── .env                       Environment variables
├── .gitignore
├── LICENSE
│
├── models/                    Trained ML models
│   ├── diabetes.pkl
│   ├── cancer.pkl
│   ├── heart.pkl
│   ├── kidney.pkl
│   ├── liver.pkl
│   ├── malaria.h5
│   └── pneumonia.h5
│
├── templates/                 Jinja2 HTML templates
│   ├── main.html              Base layout
│   ├── index.html             Public home page
│   ├── admin/                 Admin panel (9 templates)
│   └── user/                  User dashboard (6 templates)
│
├── static/                    Static assets
│   ├── css/style.css
│   └── img/
│
├── diagrams/                  UML diagrams (PlantUML)
├── Python Notebooks/          Model training notebooks
└── archive/                   Old files (reference)
```

## Setup

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate        # Linux/Mac
venv\Scripts\activate           # Windows
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up PostgreSQL database:
```bash
createdb medilife
```

4. Configure environment variables in `.env`:
```
DATABASE_URL=postgresql+psycopg2://postgres:postgres@localhost:5432/medilife
EMAIL_SENDER=your_email@gmail.com
EMAIL_RECEIVER=your_email@gmail.com
EMAIL_PASSWORD=your_app_password
```

5. Start Ollama (for AI chatbot):
```bash
ollama serve
ollama pull qwen2.5-coder:7b
```

6. Run the application:
```bash
python app.py
```

The server will be available at `http://localhost:3000`

## Database

14 tables in PostgreSQL with full relationship mapping and cascade deletes:

| Table | Purpose |
|-------|---------|
| users | User accounts and profiles |
| disease_predictions | All prediction records |
| diabetes_data | Diabetes-specific input data |
| heart_disease_data | Heart disease input data |
| kidney_disease_data | Kidney disease input data |
| liver_disease_data | Liver disease input data |
| cancer_data | Cancer input data |
| image_uploads | Malaria/Pneumonia images |
| chatbot_history | AI chatbot conversations |
| reports | Generated PDF reports |
| complaints | User support tickets |
| doctors | Doctor profiles |
| appointments | User-doctor appointments |
| audit_logs | Login/logout/prediction logs |

## ML Models

| Disease | Model Type | Accuracy |
|---------|-----------|----------|
| Diabetes | RandomForestClassifier | 98.25% |
| Breast Cancer | RandomForestClassifier | 98.25% |
| Heart Disease | RandomForestClassifier | 85.25% |
| Kidney Disease | RandomForestClassifier | 99% |
| Liver Disease | RandomForestClassifier | 78% |
| Malaria | CNN (Deep Learning) | 96% |
| Pneumonia | CNN (Deep Learning) | 95% |

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | /predict | Disease prediction |
| POST | /chat | AI chatbot |
| POST | /api/log/prediction | Log prediction to DB |
| POST | /api/log/chat | Log chat to DB |
| POST | /reports/generate | Generate PDF report |
| POST | /admin/retrain | Trigger model retraining |
| GET | /admin/retrain/status | Retraining status |

## License

Licensed under the Apache License, Version 2.0
