# AgriNova Backend API & Machine Learning Engine

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![Django](https://img.shields.io/badge/Django-6.0%2B-092E20.svg)](https://www.djangoproject.com/)
[![Django REST Framework](https://img.shields.io/badge/DRF-3.17%2B-red.svg)](https://www.django-rest-framework.org/)
[![XGBoost](https://img.shields.io/badge/XGBoost-2.1%2B-orange.svg)](https://xgboost.readthedocs.io/)
[![Scikit-Learn](https://img.shields.io/badge/Scikit--Learn-1.5%2B-F7931E.svg)](https://scikit-learn.org/)
[![TensorFlow](https://img.shields.io/badge/TensorFlow-2.21%2B-FF6F00.svg)](https://www.tensorflow.org/)
[![Node.js](https://img.shields.io/badge/Node.js-18%2B-339933.svg)](https://nodejs.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](#license)

AgriNova Backend is a high-performance agricultural microservices and Machine Learning platform built with **Django**, **Django REST Framework (DRF)**, **Python**, and **Node.js**. It powers intelligent decision-support tools for modern farming, including state-aware crop recommendations, yield estimations, dynamic multi-criteria fertilizer scoring, live mandi price forecasting, plant disease image diagnosis, smart weather caching, profit analysis, and AI-driven agricultural assistance.

---

## Table of Contents

- [Project Overview](#project-overview)
- [Features](#features)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Installation & Setup](#installation--setup)
- [Environment Variables](#environment-variables)
- [Machine Learning Architecture](#machine-learning-architecture)
- [API Modules](#api-modules)
- [Project Workflow](#project-workflow)
- [Running the Backend](#running-the-backend)
- [Future Improvements](#future-improvements)
- [License & Authors](#license--authors)

---

## Project Overview

The AgriNova Backend serves as the computational backbone for the AgriNova ecosystem. Designed with modularity, performance, and scalability in mind, it combines Django REST Framework for robust API endpoints with custom Machine Learning predictors and a dedicated Node.js microservice for transactional email and OTP delivery.

### Key Objectives:
- **Agronomic Intelligence:** Deliver precision recommendations tailored to soil NPK values, regional climate, state, season, and water availability.
- **Economic Optimization:** Help farmers predict crop yields, analyze potential profits, and forecast market commodity prices to maximize farm revenue.
- **Smart Caching & Resilience:** Implement caching layers for weather data and mandi prices to reduce external API overhead and guarantee high availability.
- **Automated Lifecycle Management:** Enforce an automated 3-case ML retraining policy that handles missing models, dataset updates, and model degradation over time.

---

## Features

The backend implements the following core modules:

- **JWT Authentication:** Secure user authentication using Simple JWT with access/refresh token rotation and token blacklisting.
- **User Profile Management:** Comprehensive user profiles tracking personal details, location preferences, language settings, and onboarding progress.
- **Farm Management:** Complete CRUD operations for farm portfolios including land area, soil type, irrigation sources, and location resolution.
- **Weather Module & Smart Weather Cache:** Real-time weather data integration with intelligent DB-backed caching to optimize API quota usage.
- **Crop Recommendation:** ML classification engine evaluating soil nutrients and environmental parameters to suggest optimal crops.
- **Yield Prediction:** ML regression model estimating crop output (kg/ha) tailored to user-specific farm parameters.
- **Fertilizer Recommendation:** Agronomic engine calculating exact NPK deficits and scoring 50+ commercial fertilizers with customized application guides.
- **Market Intelligence & Market Cache:** Mandi price tracking backed by live Data.gov.in integration and local market data caching.
- **Market Price Prediction:** XGBoost time-series regression model forecasting future commodity price trends.
- **Profit Analysis:** Comprehensive financial calculator estimating gross income, total input costs, net profit, ROI, and break-even pricing.
- **Disease Detection:** CNN deep learning model for crop disease diagnosis from uploaded leaf images, coupled with FAISS visual similarity search.
- **AI Assistant:** Conversational AI chatbot powered by Groq / Google GenAI LLMs providing contextual farming advice.
- **Forgot Password with OTP:** Secure multi-step password recovery workflow using time-sensitive one-time passcodes.
- **Email Service Integration:** Microservice built on Node.js/Express and Nodemailer for dependable email and OTP dispatching.

---

## Tech Stack

### Core Frameworks & APIs
- **Python 3.10+** - Core language for backend logic and machine learning.
- **Django 6.0+** - High-level Python web framework.
- **Django REST Framework (DRF) 3.17+** - Flexible toolkit for building Web APIs.
- **djangorestframework-simplejwt 5.3+** - JSON Web Token authentication for DRF.
- **django-cors-headers** - Handling Cross-Origin Resource Sharing (CORS).

### Database & Storage
- **SQLite3** - Lightweight default relational database (configurable for PostgreSQL/MySQL in production).

### Machine Learning & Data Science
- **XGBoost 2.1+** - Gradient boosting framework for yield prediction and market forecasting.
- **Scikit-Learn 1.5+** - Classification and regression algorithms, encoders, and metrics.
- **Pandas 2.2+** & **NumPy 2.1+** - High-performance data manipulation and numerical computation.
- **Joblib 1.4+** - Efficient serialization of Python/ML objects.
- **TensorFlow / Keras 2.21+** - Convolutional Neural Networks for plant disease recognition.
- **FAISS (faiss-cpu)** - Efficient similarity search and clustering of dense vector embeddings.
- **OpenCV & Pillow** - Image processing utilities.

### AI & LLM Integrations
- **Groq API (`groq`)** - Ultra-fast LLM inference engine for the AI Assistant.
- **Google GenAI (`google-genai`)** - Alternative generative AI integration.

### Microservices & Email
- **Node.js 18+** & **Express** - Lightweight runtime for the email service.
- **Nodemailer 6.9+** - SMTP client for sending verification and password reset OTP emails.

---

## Project Structure

```
AgriNova-Backend/
├── agrinova/                          # Main Django Project Root
│   ├── agrinova/                      # Core Settings, WSGI/ASGI, Root URLs
│   │   ├── settings.py                # Installed apps, SimpleJWT, DB & CORS config
│   │   ├── urls.py                    # Root API URL routing
│   │   └── wsgi.py                    # WSGI application entry point
│   ├── authenticate/                  # Auth App (JWT, User Profile, OTP Reset)
│   ├── farms/                         # Farm Portfolio & Location Management App
│   ├── recommendation/                # Crop Recommendation & Yield Prediction App
│   ├── fertilizer_recommendation/     # Fertilizer Calculation & Agronomic Scoring App
│   ├── market_forecast/               # Mandi Market Prices & Price Prediction App
│   ├── disease_detection/             # Plant Disease Diagnosis & FAISS Search App
│   ├── weather/                       # Weather Service & Smart Cache App
│   ├── ai_assistant/                  # LLM Conversational Assistant App
│   ├── profit_analysis/               # Financial Calculation & ROI Analysis App
│   ├── notifications/                 # System Notifications App
│   ├── db.sqlite3                     # SQLite Database
│   └── manage.py                      # Django Administrative CLI
├── email-service/                     # Node.js Email Microservice
│   ├── server.js                      # Express server with /send-otp endpoint
│   ├── package.json                   # Node.js dependencies
│   └── .env                           # Email service configuration
├── ml/                                # Machine Learning Engine
│   ├── models/                        # Serialized ML binaries (.pkl, .keras, json)
│   │   ├── crop_model.pkl             # Crop Recommendation Classifier
│   │   ├── yield_model.pkl            # Yield Prediction Regressor
│   │   ├── fertilizer_model.pkl       # Fertilizer Matching Model
│   │   ├── market_prediction_model.pkl# Mandi Price Regressor
│   │   └── disease_model.keras        # Plant Disease CNN Model
│   ├── data/                          # Master Datasets & Reference CSVS
│   ├── model_manager.py               # Singleton ML Manager with 3-case retraining
│   ├── market_model_manager.py        # Singleton Market Model Manager
│   ├── predictor.py                   # Crop & Yield inference engine
│   ├── fertilizer_predictor.py        # Agronomic dynamic scoring engine
│   ├── disease_predictor.py           # Image inference & FAISS similarity engine
│   ├── market_predictor.py            # Mandi price forecasting engine
│   ├── trainer.py                     # Training script for Crop & Yield models
│   ├── market_trainer.py              # Training script for Market price model
│   └── train_disease_model.py         # CNN training script for Disease Detection
└── requirements.txt                   # Python package dependencies
```

---

## Installation & Setup

### Prerequisites
- **Python 3.10** or higher
- **Node.js 18** or higher and `npm`
- **Git**

### Step-by-Step Installation

1. **Clone the Repository:**
   ```bash
   git clone https://github.com/your-organization/AgriNova.git
   cd AgriNova/AgriNova-Backend
   ```

2. **Create and Activate Virtual Environment:**
   - On Windows (PowerShell):
     ```powershell
     python -m venv venv
     .\venv\Scripts\Activate.ps1
     ```
   - On Linux/macOS:
     ```bash
     python3 -m venv venv
     source venv/bin/activate
     ```

3. **Install Python Dependencies:**
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

4. **Install Node.js Dependencies for Email Service:**
   ```bash
   cd email-service
   npm install
   cd ..
   ```

5. **Configure Environment Variables:**
   - Create `.env` inside `agrinova/` (refer to [Environment Variables](#environment-variables)).
   - Create `.env` inside `email-service/` if overriding default ports or SMTP details.

6. **Apply Database Migrations:**
   ```bash
   cd agrinova
   python manage.py migrate
   ```

7. **Create Superuser (Optional):**
   ```bash
   python manage.py createsuperuser
   ```

---

## Environment Variables

Create a `.env` file in the `agrinova/` directory. Use the following template:

| Variable Name | Description | Example / Default |
| :--- | :--- | :--- |
| `SECRET_KEY` | Django secret key for cryptographic signing | `your-django-secret-key` |
| `DEBUG` | Enables or disables Django debug mode | `True` |
| `ALLOWED_HOSTS` | Comma-separated list of allowed host domains | `localhost,127.0.0.1` |
| `DB_ENGINE` | Database backend engine | `django.db.backends.sqlite3` |
| `DB_NAME` | Database filename or database name | `db.sqlite3` |
| `MAIL_HOST` | SMTP server host address | `smtp.gmail.com` |
| `MAIL_PORT` | SMTP server port | `587` |
| `MAIL_USER` | Email account for sending system emails | `example@gmail.com` |
| `MAIL_PASSWORD` | App-specific password for SMTP server | `your-app-password` |
| `MAIL_FROM` | Sender name and email header | `AgriNova <noreply@agrinova.com>` |
| `NODE_MAIL_SERVICE_URL` | URL of the Node.js email sending microservice | `http://localhost:5001/send-otp` |
| `DATA_GOV_IN_API_KEY` | API Key for Govt of India Mandi Market Data | `your-data-gov-api-key` |
| `GROQ_API_KEY` | Groq Cloud API Key for AI Assistant LLM | `gsk_your_groq_api_key` |

---

## Machine Learning Architecture

The AgriNova Backend integrates multiple specialized ML models managed via Singleton instances to ensure minimal memory overhead and instant inference.

```
                    ┌─────────────────────────┐
                    │    Incoming API View    │
                    └────────────┬────────────┘
                                 │
                    ┌────────────▼────────────┐
                    │   ModelManager (Class)  │
                    └────────────┬────────────┘
                                 │
           ┌─────────────────────┼─────────────────────┐
           │                     │                     │
  ┌────────┴────────┐   ┌────────┴────────┐   ┌────────┴────────┐
  │  Case 1 Check   │   │  Case 2 Check   │   │  Case 3 Check   │
  │ Missing .pkl?   │   │ CSV Modified?   │   │ Older >30 Days? │
  └────────┬────────┘   └────────┬────────┘   └────────┬────────┘
           │                     │                     │
           └─────────────────────┼─────────────────────┘
                                 │
                        [Should Retrain?]
                        ├── YES ──> Train Fresh Models & Update Metadata
                        └── NO  ──> Load Serialized .pkl into Memory
```

### 1. Crop Recommendation Model
- **Algorithm:** RandomForestClassifier / XGBoost Classifier
- **Features:** Nitrogen (N), Phosphorus (P), Potassium (K), Temperature, Humidity, pH, Rainfall, State, Season.
- **Output:** Top-K suitable crops with probabilistic confidence scores.

### 2. Yield Prediction Model
- **Algorithm:** XGBoost Regressor / RandomForest Regressor
- **Features:** NPK values, climate parameters, season, encoded crop name, soil type, and water availability.
- **Output:** Expected crop yield in kilograms per hectare (kg/ha).

### 3. Fertilizer Recommendation Engine
- **Mechanism:** Multi-criteria agronomic scoring algorithm.
- **Functionality:** Computes soil nutrient deficits against target crop requirements and ranks 50+ commercial fertilizers based on elemental percentage, price per kg, application method, and environmental suitability.

### 4. Market Price Prediction Model
- **Algorithm:** XGBoost Regressor for time-series commodity trends.
- **Features:** Historical mandi arrival prices, state, commodity, month, and volume.
- **Output:** Predicted future market prices per quintal.

### 5. Plant Disease Detection Model
- **Algorithm:** Convolutional Neural Network (CNN) built on TensorFlow/Keras with MobileNetV2 architecture.
- **Embedding Search:** FAISS vector database for retrieving visual similarities and treatment suggestions.

### Automatic Retraining Policy
The ML pipeline is controlled by `ModelManager` and `MarketModelManager`, enforcing a strict 3-case retraining policy:
1. **Case 1 (Missing Models):** If model binaries (`.pkl` / `.keras`) are missing from `ml/models/`, the backend automatically triggers model training on startup.
2. **Case 2 (Dataset Modification):** If any source dataset in `ml/data/` has a file modification timestamp newer than the model's training timestamp, the manager automatically initiates retraining.
3. **Case 3 (Model Aging):** If the trained model is older than 30 days (`RETRAIN_DAYS = 30`), the system retrains the models to ensure freshness.

---

## API Modules

| Module Route | Purpose & Key Features | Auth Required |
| :--- | :--- | :--- |
| `/api/auth/` | Registration, Login, Token Refresh, Profile Management, Password Reset OTP flow | Optional / Required |
| `/api/farms/` | CRUD for farm portfolios, active farm selection, location resolution | Required |
| `/api/recommendation/` | Crop suitability recommendations, yield predictions, recommendation history | Required |
| `/api/fertilizer/` | Soil deficit calculations, fertilizer recommendations, application guidance | Required |
| `/api/market-forecast/` | Real-time mandi prices, market price forecasting, price cache management | Required |
| `/api/disease/` | Leaf image upload, disease classification, treatment plans, FAISS search | Required |
| `/api/weather/` | Current weather, 5-day forecast, agricultural advisory, smart cache status | Required |
| `/api/profit-analysis/` | Cost breakdown, gross revenue estimation, net profit, ROI calculator | Required |
| `/api/assistant/` | Interactive AI Chatbot powered by Groq / Google GenAI LLMs | Required |
| `/api/notifications/` | Fetch user alerts, system updates, and farm advisories | Required |

---

## Project Workflow

```
[React Frontend] 
       │
       ├── (HTTP / JSON + Bearer JWT)
       │
       ▼
[Django REST Framework API Router]
       │
       ├── Auth Interceptor / SimpleJWT Verification
       │
       ├──> [App Controllers: farms, recommendation, weather, market, etc.]
       │         │
       │         ├──> [Smart Caching Layer (DB Weather & Market Cache)]
       │         │
       │         ├──> [ModelManager / ML Predictor Engine]
       │         │         │
       │         │         └──> [Scikit-Learn / XGBoost / TensorFlow Inference]
       │         │
       │         └──> [Node.js Email Microservice (Port 5001)]
       │                   │
       │                   └──> [SMTP Gmail Service] ──> [User Email / OTP]
       │
       ▼
[SQLite / Database Storage]
```

---

## Running the Backend

To run the complete AgriNova backend service suite, you need to launch both the Node.js Email Microservice and the Django Backend Server.

### 1. Launch Node.js Email Service (Port 5001):
```bash
cd email-service
npm start
```

### 2. Launch Django Backend Server (Port 8000):
In a separate terminal window:
```bash
cd agrinova
python manage.py runserver 0.0.0.0:8000
```

The Django REST API will be accessible at: `http://localhost:8000/api/`

---

## Future Improvements

- **Database Upgrade:** Migrate from SQLite to PostgreSQL with PostGIS for spatial polygon mapping of farm boundaries.
- **Asynchronous Task Queue:** Integrate Celery and Redis for asynchronous background ML retraining and bulk email delivery.
- **Dockerization:** Complete containerization using Docker and `docker-compose` for single-command production deployment.
- **IoT Telemetry Integration:** Direct API support for MQTT and ESP32/LoRaWAN soil moisture and NPK sensor hardware.
- **Multi-Tenant Dashboard:** Agronomist and co-operative multi-tenant management portals.

---

## License & Authors

### License
This project is licensed under the **MIT License** - see the `LICENSE` file for details.

### Author
Developed with ❤️ by the **AgriNova Engineering Team**.
