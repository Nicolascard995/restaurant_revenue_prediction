# 🍽️ Restaurant Advisor MVP

An intelligent MVP to help entrepreneurs evaluate the viability of opening a restaurant, using data analysis, artificial intelligence, and cloud database.

## 🚀 Features

- **Viability Analysis**: Revenue prediction based on historical data
- **AI Assistant**: Personalized advice using GPT-3.5
- **Database**: Storage in Supabase for tracking
- **Modern Interface**: Professional UI with Tailwind CSS
- **Security**: Validations, sanitization and rate limiting
- **REST API**: Backend with FastAPI

## 📋 Requirements

- Python 3.8+
- Supabase account
- OpenAI API Key

## 🛠️ Quick Installation

### 1. Clone and configure
```bash
git clone <your-repository>
cd restaurant_revenue_prediction
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure environment variables
```bash
# Copy example file
cp .env.example .env

# Edit with your credentials
nano .env
```

### 4. Configure Supabase
1. Go to [supabase.com](https://supabase.com)
2. Create a project
3. Execute the SQL in `clean_supabase_setup.sql`

### 5. Train model
```bash
python3 train_model.py
```

### 6. Run application
```bash
python3 app.py
```

## 🌐 Usage

### Web Access
- **URL**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

### Features
1. **Viability Analysis**: Enter restaurant data
2. **AI Advice**: Receive personalized recommendations
3. **Results**: Clear visualization of metrics

## 🔒 Security

The MVP implements multiple security layers:

- ✅ **Input Validation**: Pydantic models with sanitization
- ✅ **Rate Limiting**: Request control per IP
- ✅ **Sanitization**: Removal of dangerous characters
- ✅ **Logging**: Activity recording without sensitive data
- ✅ **CORS**: Appropriate configuration for APIs

See [SECURITY.md](SECURITY.md) for complete details.

## 🏗️ Architecture

```
restaurant_revenue_prediction/
├── app.py                    # Main FastAPI application
├── train_model.py           # ML model training
├── requirements.txt         # Python dependencies
├── .env                     # Environment variables
├── clean_supabase_setup.sql # Database configuration
├── templates/
│   └── index.html          # Main web interface
├── static/                  # Static files
├── models/                  # Trained models
├── train.csv               # Training data
└── README.md               # This file
```

## 📊 API Endpoints

### POST /api/analyze
Analyze restaurant viability

**Request:**
```json
{
    "city": "Madrid",
    "city_group": "Big Cities",
    "type": "FC",
    "open_date": "2024-01-15",
    "investment": 500000,
    "monthly_costs": 15000
}
```

**Response:**
```json
{
    "success": true,
    "revenue_estimate": 150000.0,
    "viability_analysis": {
        "viability": "High",
        "annual_revenue": 150000.0,
        "annual_profit": 132000.0,
        "roi": 26.4
    }
}
```

### POST /api/ai_advice
Get personalized AI advice

### GET /health
Check service status

## 🔧 Configuration

### Environment Variables
```env
# Supabase Configuration
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-anon-public-key

# OpenAI Configuration
OPENAI_API_KEY=sk-your-openai-api-key

# Model Configuration
MODEL_PATH=./models/restaurant_model.pkl
```

### Database
Execute the queries in `clean_supabase_setup.sql` in your Supabase project.

## 📈 ML Model

- **Algorithm**: Random Forest Regressor
- **Accuracy**: R² = 0.84 in training
- **Data**: 137 real restaurants
- **Features**: 43 variables including demographics and commercial data

## 🚀 Deployment

### Development
```bash
python3 app.py
```

### Production
```bash
uvicorn app:app --host 0.0.0.0 --port 8000
```

### Docker (optional)
```bash
docker build -t restaurant-advisor .
docker run -p 8000:8000 restaurant-advisor
```

## 📚 Documentation

- [SECURITY.md](SECURITY.md) - Security measures
- [DEPLOYMENT.md](DEPLOYMENT.md) - Deployment guide
- [ESTADO_FINAL.md](ESTADO_FINAL.md) - Project status

## 🤝 Contributing

1. Fork the project
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Open a Pull Request

## 📄 License

This project is under the MIT License.

## 📞 Support

For technical support or questions about the MVP:
- Issues on GitHub
- Email: [your-email@example.com]

---

**Developed with ❤️ to help entrepreneurs make their gastronomic dreams come true**




