from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer
import numpy as np
import pickle
import os
import re
from dotenv import load_dotenv
import openai
from typing import Dict, Any, Optional
import json
from pydantic import BaseModel, validator
import logging
from datetime import datetime, timezone
import sys

# Configure logging with detailed error tracking
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables with error handling
try:
    load_dotenv()
    logger.info("✅ Environment variables loaded successfully")
except Exception as e:
    logger.error(f"❌ Error loading environment variables: {e}")

# Pydantic models for data validation
class RestaurantData(BaseModel):
    city: str
    city_group: str
    type: str
    open_date: str
    investment: float
    monthly_costs: float
    
    @validator('city')
    def validate_city(cls, v):
        if not v or len(v.strip()) == 0:
            raise ValueError('City is required')
        if len(v) > 100:
            raise ValueError('City name too long')
        # Sanitize input
        v = re.sub(r'[<>"\']', '', v.strip())
        return v
    
    @validator('city_group')
    def validate_city_group(cls, v):
        allowed = ['Big Cities', 'Other']
        if v not in allowed:
            raise ValueError(f'city_group must be one of: {allowed}')
        return v
    
    @validator('type')
    def validate_type(cls, v):
        allowed = ['FC', 'IL']
        if v not in allowed:
            raise ValueError(f'type must be one of: {allowed}')
        return v
    
    @validator('investment', 'monthly_costs')
    def validate_amounts(cls, v):
        if v < 0:
            raise ValueError('Amounts cannot be negative')
        if v > 10000000:  # 10 million maximum
            raise ValueError('Amount too high')
        return v

class AIAdviceRequest(BaseModel):
    city: str
    type: str
    investment: float
    monthly_costs: float
    
    @validator('city')
    def validate_city(cls, v):
        if not v or len(v.strip()) == 0:
            raise ValueError('City is required')
        v = re.sub(r'[<>"\']', '', v.strip())
        return v

# Application configuration with error handling
try:
    app = FastAPI(
        title="Restaurant Advisor MVP", 
        version="1.0.0",
        description="MVP for restaurant viability analysis with AI"
    )
    logger.info("✅ FastAPI application created successfully")
except Exception as e:
    logger.error(f"❌ Error creating FastAPI app: {e}")
    sys.exit(1)

# Configure CORS with error handling
try:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    logger.info("✅ CORS middleware configured successfully")
except Exception as e:
    logger.error(f"❌ Error configuring CORS: {e}")

# Supabase configuration with comprehensive error handling
supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_KEY")
supabase = None

if supabase_url and supabase_key and supabase_url != "your_supabase_url":
    try:
        from supabase import create_client, Client
        supabase: Client = create_client(supabase_url, supabase_key)
        logger.info("✅ Supabase configured successfully")
    except ImportError as e:
        logger.warning(f"⚠️ Supabase library not available: {e}")
        logger.info("MVP will work without database storage")
    except Exception as e:
        logger.warning(f"⚠️ Error configuring Supabase: {e}")
        logger.info("MVP will work without database storage")
else:
    logger.warning("⚠️ Supabase not configured - MVP will work without storage")

# OpenAI configuration with error handling
try:
    openai.api_key = os.getenv("OPENAI_API_KEY")
    if openai.api_key:
        logger.info("✅ OpenAI configured successfully")
    else:
        logger.warning("⚠️ OpenAI API key not found")
except Exception as e:
    logger.error(f"❌ Error configuring OpenAI: {e}")

# Template configuration with error handling
try:
    templates = Jinja2Templates(directory="templates")
    logger.info("✅ Templates configured successfully")
except Exception as e:
    logger.error(f"❌ Error configuring templates: {e}")

# Mount static files with error handling
try:
    app.mount("/static", StaticFiles(directory="static"), name="static")
    logger.info("✅ Static files mounted successfully")
except Exception as e:
    logger.error(f"❌ Error mounting static files: {e}")

# Simple rate limiting with error handling
from collections import defaultdict
import time
request_counts = defaultdict(list)

def check_rate_limit(client_ip: str, limit: int = 10, window: int = 60):
    """Basic rate limiting with error handling"""
    try:
        now = time.time()
        # Clean old requests
        request_counts[client_ip] = [req_time for req_time in request_counts[client_ip] 
                                    if now - req_time < window]
        
        if len(request_counts[client_ip]) >= limit:
            raise HTTPException(status_code=429, detail="Too many requests")
        
        request_counts[client_ip].append(now)
    except Exception as e:
        logger.error(f"❌ Rate limiting error: {e}")
        # Don't block requests if rate limiting fails

def get_client_ip(request: Request) -> str:
    """Get client IP safely with error handling"""
    try:
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            return forwarded.split(",")[0].strip()
        return request.client.host if request.client else "unknown"
    except Exception as e:
        logger.error(f"❌ Error getting client IP: {e}")
        return "unknown"

def sanitize_input(data: Dict[str, Any]) -> Dict[str, Any]:
    """Sanitize input data with error handling"""
    try:
        sanitized = {}
        for key, value in data.items():
            if isinstance(value, str):
                # Remove dangerous characters
                sanitized[key] = re.sub(r'[<>"\']', '', value.strip())
            else:
                sanitized[key] = value
        return sanitized
    except Exception as e:
        logger.error(f"❌ Error sanitizing input: {e}")
        return data

def validate_and_sanitize_restaurant_data(data: Dict[str, Any]) -> RestaurantData:
    """Validate and sanitize restaurant data with comprehensive error handling"""
    try:
        # Sanitize input
        sanitized_data = sanitize_input(data)
        
        # Validate with Pydantic
        restaurant_data = RestaurantData(**sanitized_data)
        return restaurant_data
    except Exception as e:
        logger.error(f"❌ Error validating data: {e}")
        raise HTTPException(status_code=400, detail=f"Input data error: {str(e)}")

def simple_revenue_prediction(investment: float, monthly_costs: float, city_group: str, restaurant_type: str) -> float:
    """Simple revenue prediction without ML model - ultra robust"""
    try:
        # Base revenue from investment
        base_revenue = investment * 0.3  # 30% of initial capital
        
        # Adjust based on city group
        city_multiplier = 1.2 if city_group == "Big Cities" else 0.8
        
        # Adjust based on restaurant type
        type_multiplier = 1.1 if restaurant_type == "FC" else 0.9
        
        # Calculate final revenue
        revenue = base_revenue * city_multiplier * type_multiplier
        
        # Add some randomness for realistic prediction
        try:
            np.random.seed(hash(f"{investment}{monthly_costs}{city_group}{restaurant_type}") % 2**32)
            revenue += np.random.normal(0, revenue * 0.1)
        except Exception as e:
            logger.warning(f"⚠️ Error adding randomness to prediction: {e}")
            # Continue without randomness
        
        return max(revenue, 0)  # Ensure non-negative
    except Exception as e:
        logger.error(f"❌ Error in revenue prediction: {e}")
        # Fallback to simple calculation
        return max(investment * 0.3, 0)

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Main page with error handling"""
    try:
        return templates.TemplateResponse("index.html", {"request": request})
    except Exception as e:
        logger.error(f"❌ Error serving home page: {e}")
        return HTMLResponse(content="<h1>Restaurant Advisor MVP</h1><p>Service is running</p>")

@app.post("/api/analyze")
async def analyze_restaurant(request: Request, data: Dict[str, Any]):
    """Analyze restaurant viability with comprehensive error handling"""
    
    try:
        # Rate limiting
        client_ip = get_client_ip(request)
        check_rate_limit(client_ip)
        
        # Validate and sanitize data
        restaurant_data = validate_and_sanitize_restaurant_data(data)
        
        # Basic analysis with additional validations
        investment = restaurant_data.investment
        monthly_costs = restaurant_data.monthly_costs
        
        # Business validations
        if investment <= 0:
            raise HTTPException(status_code=400, detail="Investment must be greater than 0")
        
        if monthly_costs <= 0:
            raise HTTPException(status_code=400, detail="Monthly costs must be greater than 0")
        
        # Revenue estimation using simple prediction
        revenue_estimate = simple_revenue_prediction(
            investment, 
            monthly_costs, 
            restaurant_data.city_group, 
            restaurant_data.type
        )
        
        # Viability analysis
        annual_revenue = revenue_estimate
        annual_costs = monthly_costs * 12
        annual_profit = annual_revenue - annual_costs
        roi = (annual_profit / investment) * 100 if investment > 0 else 0
        
        viability_analysis = {
            "viability": "High" if annual_profit > 0 else "Low",
            "annual_revenue": annual_revenue,
            "annual_profit": annual_profit,
            "roi": roi,
            "analysis_date": datetime.now(timezone.utc).isoformat()
        }
        
        # Save to Supabase if configured (with comprehensive error handling)
        if supabase:
            try:
                supabase.table("restaurant_analyses").insert({
                    "restaurant_data": restaurant_data.dict(),
                    "revenue_estimate": revenue_estimate,
                    "viability_analysis": viability_analysis
                }).execute()
                logger.info(f"✅ Analysis saved to Supabase for IP: {client_ip}")
            except Exception as e:
                logger.error(f"❌ Error saving to Supabase: {e}")
                # Don't fail the application if Supabase fails
        
        # Activity log
        logger.info(f"✅ Analysis performed for {restaurant_data.city} by IP: {client_ip}")
        
        return {
            "success": True,
            "revenue_estimate": revenue_estimate,
            "viability_analysis": viability_analysis
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Unexpected error in analysis: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.post("/api/ai_advice")
async def get_ai_advice(request: Request, data: Dict[str, Any]):
    """Get personalized AI advice with comprehensive error handling"""
    
    try:
        # Stricter rate limiting for AI
        client_ip = get_client_ip(request)
        check_rate_limit(client_ip, limit=5, window=60)  # 5 requests per minute
        
        # Validate data for AI advice
        if not openai.api_key or openai.api_key == "your_openai_api_key":
            return {
                "success": True,
                "advice": "To receive personalized AI advice, configure your OpenAI API key in the .env file"
            }
        
        # Validate input
        advice_request = AIAdviceRequest(**sanitize_input(data))
        
        # Create safe prompt
        safe_prompt = f"""
        Analyze this restaurant project professionally and constructively:
        
        City: {advice_request.city}
        Type: {advice_request.type}
        Investment: ${advice_request.investment:,.0f}
        Monthly costs: ${advice_request.monthly_costs:,.0f}
        
        Provide:
        1. 3 specific recommendations to improve viability
        2. Marketing strategies for the location
        3. Cost considerations and optimization
        4. Main risks to consider
        
        Respond in English in a professional and practical manner.
        """
        
        # OpenAI call with comprehensive error handling
        try:
            response = openai.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are an expert restaurant consultant with 20 years of experience."},
                    {"role": "user", "content": safe_prompt}
                ],
                max_tokens=500,
                temperature=0.7
            )
            
            advice = response.choices[0].message.content
            
            # Sanitize AI response
            advice = re.sub(r'<[^>]*>', '', advice)  # Remove HTML tags
            advice = advice[:2000]  # Limit length
            
        except Exception as e:
            logger.error(f"❌ Error calling OpenAI: {e}")
            raise HTTPException(status_code=500, detail="Error generating AI advice")
        
        # Save to Supabase if configured
        if supabase:
            try:
                supabase.table("ai_advice").insert({
                    "restaurant_data": advice_request.dict(),
                    "advice": advice
                }).execute()
                logger.info(f"✅ AI advice saved for IP: {client_ip}")
            except Exception as e:
                logger.error(f"❌ Error saving advice to Supabase: {e}")
        
        # Activity log
        logger.info(f"✅ AI advice generated for {advice_request.city} by IP: {client_ip}")
        
        return {"success": True, "advice": advice}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Unexpected error in AI advice: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/health")
async def health_check():
    """Health check endpoint with comprehensive status"""
    try:
        return {
            "status": "healthy",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "services": {
                "openai": bool(openai.api_key and openai.api_key != "your_openai_api_key"),
                "supabase": bool(supabase),
                "python_version": sys.version,
                "environment": os.getenv("ENVIRONMENT", "production")
            }
        }
    except Exception as e:
        logger.error(f"❌ Error in health check: {e}")
        return {"status": "error", "message": str(e)}

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Custom HTTP error handling with logging"""
    client_ip = get_client_ip(request)
    logger.warning(f"⚠️ HTTP Error {exc.status_code}: {exc.detail} from IP: {client_ip}")
    return {"error": exc.detail, "status_code": exc.status_code}

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """General error handling with comprehensive logging"""
    client_ip = get_client_ip(request)
    logger.error(f"❌ Unexpected error: {exc} from IP: {client_ip}")
    return {"error": "Internal server error", "status_code": 500}

if __name__ == "__main__":
    try:
        import uvicorn
        logger.info("🚀 Starting Restaurant Advisor MVP...")
        uvicorn.run(app, host="0.0.0.0", port=8000)
    except Exception as e:
        logger.error(f"❌ Error starting application: {e}")
        sys.exit(1) 