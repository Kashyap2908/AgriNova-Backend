# AgriNova Backend API & Machine Learning Engine

[![Python](https://img.shields.io/badge/Python-3.10+-3776AB.svg)](https://www.python.org/)
[![Django](https://img.shields.io/badge/Django-5.0-092E20.svg)](https://www.djangoproject.com/)
[![Django REST Framework](https://img.shields.io/badge/DRF-3.15-Red.svg)](https://www.django-rest-framework.org/)
[![scikit-learn](https://img.shields.io/badge/scikit--learn-1.4-F7931E.svg)](https://scikit-learn.org/)
[![XGBoost](https://img.shields.io/badge/XGBoost-2.0-11557C.svg)](https://xgboost.readthedocs.io/)

AgriNova Backend is a high-performance Django REST framework and Machine Learning server powering the AgriNova smart agricultural ecosystem. It manages user authentication, farm geospatial profiles, weather caching, market price forecasts, ML-based crop recommendations, yield estimations, plant disease image diagnostics, and ICAR-standard fertilizer planning.

---

## Table of Contents

- [Implemented Modules](#implemented-modules)
- [Architecture & Tech Stack](#architecture--tech-stack)
- [Folder Structure](#folder-structure)
- [Database Schema](#database-schema)
- [Installation & Setup](#installation--setup)
- [Environment Variables](#environment-variables)
- [Machine Learning Modules](#machine-learning-modules)
- [Weather Cache Service](#weather-cache-service)
- [Market Cache Service](#market-cache-service)
- [Fertilizer Recommendation Engine](#fertilizer-recommendation-engine)
- [Profit Analysis Engine](#profit-analysis-engine)
- [AI Assistant Service](#ai-assistant-service)
- [API Reference](#api-reference)
- [Future Scope](#future-scope)

---

## Implemented Modules

1. **`authenticate` (User Authentication & JWT):**
   - User registration, login, profile management, and refresh token blacklisting.
   - OTP generation and verification for password recovery.

2. **`farms` (Farm Management & Soil Profiles):**
   - Geolocation-aware farm registration (Latitude, Longitude, Village, District, State).
   - Soil health tracking (Nitrogen, Phosphorus, Potassium, Soil pH, Soil Type, Water Availability).

3. **`weather` (Weather Cache Engine):**
   - Live weather fetching from Open-Meteo API.
   - In-memory/DB caching layer with 7-day forecasts and agricultural weather advisories.

4. **`recommendation` (Crop Advisor & Yield Prediction):**
   - Dual-mode crop advisor (AI classification & Quick rule-based matching).
   - Yield prediction engine calculating expected harvest per unit area and total farm yield.
   - Recommendation history tracking.

5. **`fertilizer_recommendation` (Smart Nutrition Planner):**
   - ICAR agronomic deficiency matrix computation for soil nutrients.
   - Multi-option fertilizer strategy formulation (Budget, Balanced, Premium).
   - Commercial fertilizer catalog and exact dosage/bag requirements calculation.

6. **`market_forecast` (Market Intelligence & Price Prediction):**
   - APMC mandi price cache service.
   - XGBoost price forecasting model for 3-month future market price prediction.

7. **`profit_analysis` (Farm Economics & Profit Calculator):**
   - Financial analysis combining expected yield, CACP/DES cultivation cost benchmarks, and market price predictions.
   - Scenario analysis (Best, Average, Worst case) and custom cost overrides.

8. **`disease_detection` (Plant Disease Image Diagnostics):**
   - Convolutional Deep Learning model analyzing leaf images for crop diseases.
   - Returns disease diagnosis, confidence score, treatment plan (organic/chemical), active ingredients, and government advisories.

9. **`ai_assistant` (Conversational AI Service):**
   - Natural language assistant endpoint for contextual agronomic advice.

10. **`notifications` (System & Farm Advisories):**
    - Notification dispatcher sending agricultural advisories and alerts.

---

## Architecture & Tech Stack

- **Backend Framework:** Django 5.0, Django REST Framework 3.15
- **Authentication:** SimpleJWT (JSON Web Tokens)
- **Database:** SQLite / PostgreSQL
- **Machine Learning Libraries:** scikit-learn, XGBoost, pandas, NumPy, Pillow, Joblib
- **External Services:** Open-Meteo Weather API, Nominatim Geocoding

---

## Folder Structure

```
AgriNova-Backend/
├── agrinova/
│   ├── agrinova/                  # Django project configuration & settings
│   ├── ai_assistant/              # AI Assistant app
│   ├── authenticate/              # User auth app
│   ├── disease_detection/         # Plant disease ML app
│   ├── farms/                     # Farm management app
│   ├── fertilizer_recommendation/ # Smart nutrition planner app
│   ├── market_forecast/           # APMC market cache & ML forecast app
│   ├── notifications/             # Advisories app
│   ├── profit_analysis/           # Farm economics engine app
│   ├── recommendation/            # Crop recommendation & yield prediction app
│   ├── weather/                   # Weather cache app
│   ├── manage.py
│   └── populate_crops.py          # Data population script
├── ml/
│   ├── data/                      # CSV datasets (crop master, fertilizer master, market data)
│   ├── models/                    # Trained ML models (.pkl / .joblib)
│   ├── model_manager.py           # Crop & Yield model loader
│   ├── market_model_manager.py    # Market forecast model loader
│   └── disease_predictor.py       # Disease diagnostic model runner
├── requirements.txt
└── README.md
```

---

## Installation & Setup

1. **Clone the Repository:**
   ```bash
   git clone <repository-url>
   cd AgriNova/AgriNova-Backend
   ```

2. **Create and Activate Virtual Environment:**
   ```bash
   python -m venv venv
   # On Windows:
   venv\Scripts\activate
   ```

3. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Apply Database Migrations:**
   ```bash
   cd agrinova
   python manage.py migrate
   ```

5. **Populate Master Data (Optional):**
   ```bash
   python populate_crops.py
   ```

6. **Run Development Server:**
   ```bash
   python manage.py runserver 0.0.0.0:8000
   ```

---

## Environment Variables

Create `.env` inside `agrinova/agrinova/`:

```env
SECRET_KEY=django-insecure-agrinova-production-key
DEBUG=True
ALLOWED_HOSTS=*
NODE_MAIL_SERVICE_URL=http://localhost:5001/send-otp
```

---

## Machine Learning Modules

1. **Crop Classifier (`crop_model.pkl`):**
   - Trained on multi-state soil and environmental parameters.
   - Evaluates Nitrogen, Phosphorus, Potassium, pH, Temperature, Humidity, and Rainfall to output rank-ordered crop suitability probabilities.

2. **Yield Estimator (`yield_model.pkl`):**
   - Regressor model estimating crop production output (kg/ha) based on soil fertility, water supply, and weather.

3. **Market Price Predictor (`market_price_model.pkl`):**
   - XGBoost time-series model predicting 3-month future APMC commodity prices.

4. **Disease Diagnosis Model (`disease_model.pkl`):**
   - Image classification model determining plant disease state with scientific name, severity, and remedial action.

---

## Weather Cache Service

- `WeatherCacheService` fetches live data from Open-Meteo API using farm latitude and longitude.
- Caches response to reduce external API overhead and supplies parameters to Crop and Yield ML models.

---

## Market Cache Service

- `MarketCacheService` tracks mandi market prices per crop, district, and state.
- Provides modal price benchmarks for profit estimations.

---

## Fertilizer Recommendation Engine

- Implements ICAR/KVK agronomic calculations.
- Determines N, P, K deficiencies based on target crop demand and available soil nutrients.
- Formulates multi-choice fertilizer plans (Budget, Balanced, Premium) with commercial products (Urea, DAP, MOP, NPK 19:19:19, etc.).

---

## Profit Analysis Engine

- Combines farm land area, predicted yield, 3-month forecasted selling price, and CACP cultivation cost benchmarks.
- Computes Gross Revenue, Total Costs, Net Profit, ROI %, Profit Margin %, and Break-even price per Quintal.
- Supports scenario modeling (Best, Average, Worst case).

---

## AI Assistant Service

- Natural language response handler providing farm management recommendations, pest control guidance, and advisory answers.

---

## API Reference

### Auth & User Profile
- `POST /api/auth/register/` - Register account
- `POST /api/auth/login/` - User login
- `POST /api/auth/logout/` - Token logout
- `GET /api/auth/profile/` - Retrieve user profile

### Farms
- `GET /api/farms/` - List user farms
- `POST /api/farms/` - Create new farm
- `GET /api/farms/<id>/` - Retrieve farm details
- `PATCH /api/farms/<id>/` - Update farm details

### Recommendation & Yield
- `POST /api/recommendation/predict/` - Crop recommendation
- `GET /api/recommendation/yield-summary/` - Yield estimate summary

### Fertilizer Planner
- `POST /api/fertilizer/recommend/` - Smart nutrition recommendation
- `GET /api/fertilizer/crops/` - Supported fertilizer crops list

### Profit Analysis
- `POST /api/profit-analysis/` - Compute profit analysis

### Disease Detection
- `POST /api/disease/predict/` - Upload leaf image for disease diagnosis

---

## Future Scope

- Integration with Geospatial Sentinel Satellite APIs.
- Automated IoT sensor stream ingest via MQTT broker.
- Multi-tenant enterprise farm management.
