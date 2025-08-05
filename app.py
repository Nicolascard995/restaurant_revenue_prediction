from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer
import pandas as pd
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

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

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

# Application configuration
app = FastAPI(
    title="Restaurant Advisor MVP", 
    version="1.0.0",
    description="MVP for restaurant viability analysis with AI"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify specific domains
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Supabase configuration (optional)
supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_KEY")
supabase = None

if supabase_url and supabase_key and supabase_url != "your_supabase_url":
    try:
        from supabase import create_client, Client
        supabase: Client = create_client(supabase_url, supabase_key)
        logger.info("✅ Supabase configured successfully")
    except Exception as e:
        logger.warning(f"⚠️ Error configuring Supabase: {e}")
        logger.info("MVP will work without database storage")
else:
    logger.warning("⚠️ Supabase not configured - MVP will work without storage")

# OpenAI configuration
openai.api_key = os.getenv("OPENAI_API_KEY")

# Template configuration
templates = Jinja2Templates(directory="templates")

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Simple rate limiting
from collections import defaultdict
import time
request_counts = defaultdict(list)

def check_rate_limit(client_ip: str, limit: int = 10, window: int = 60):
    """Basic rate limiting"""
    now = time.time()
    # Clean old requests
    request_counts[client_ip] = [req_time for req_time in request_counts[client_ip] 
                                if now - req_time < window]
    
    if len(request_counts[client_ip]) >= limit:
        raise HTTPException(status_code=429, detail="Too many requests")
    
    request_counts[client_ip].append(now)

def get_client_ip(request: Request) -> str:
    """Get client IP safely"""
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "unknown"

def sanitize_input(data: Dict[str, Any]) -> Dict[str, Any]:
    """Sanitize input data"""
    sanitized = {}
    for key, value in data.items():
        if isinstance(value, str):
            # Remove dangerous characters
            sanitized[key] = re.sub(r'[<>"\']', '', value.strip())
        else:
            sanitized[key] = value
    return sanitized

def validate_and_sanitize_restaurant_data(data: Dict[str, Any]) -> RestaurantData:
    """Validate and sanitize restaurant data"""
    try:
        # Sanitize input
        sanitized_data = sanitize_input(data)
        
        # Validate with Pydantic
        restaurant_data = RestaurantData(**sanitized_data)
        return restaurant_data
    except Exception as e:
        logger.error(f"Error validating data: {e}")
        raise HTTPException(status_code=400, detail=f"Input data error: {str(e)}")

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Main page"""
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/api/analyze")
async def analyze_restaurant(request: Request, data: Dict[str, Any]):
    """Analyze restaurant viability with security validation"""
    
    # Rate limiting
    client_ip = get_client_ip(request)
    check_rate_limit(client_ip)
    
    try:
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
        
        # Revenue estimation (simplified but secure)
        revenue_estimate = investment * 0.3  # 30% of initial capital
        
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
        
        # Save to Supabase if configured (with error handling)
        if supabase:
            try:
                supabase.table("restaurant_analyses").insert({
                    "restaurant_data": restaurant_data.dict(),
                    "revenue_estimate": revenue_estimate,
                    "viability_analysis": viability_analysis
                }).execute()
                logger.info(f"Analysis saved to Supabase for IP: {client_ip}")
            except Exception as e:
                logger.error(f"Error saving to Supabase: {e}")
                # Don't fail the application if Supabase fails
        
        # Activity log
        logger.info(f"Analysis performed for {restaurant_data.city} by IP: {client_ip}")
        
        return {
            "success": True,
            "revenue_estimate": revenue_estimate,
            "viability_analysis": viability_analysis
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in analysis: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.post("/api/ai_advice")
async def get_ai_advice(request: Request, data: Dict[str, Any]):
    """Get personalized AI advice with security validation"""
    
    # Stricter rate limiting for AI
    client_ip = get_client_ip(request)
    check_rate_limit(client_ip, limit=5, window=60)  # 5 requests per minute
    
    try:
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
        
        # OpenAI call with timeout and error handling
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
            logger.error(f"Error calling OpenAI: {e}")
            raise HTTPException(status_code=500, detail="Error generating AI advice")
        
        # Save to Supabase if configured
        if supabase:
            try:
                supabase.table("ai_advice").insert({
                    "restaurant_data": advice_request.dict(),
                    "advice": advice
                }).execute()
                logger.info(f"AI advice saved for IP: {client_ip}")
            except Exception as e:
                logger.error(f"Error saving advice to Supabase: {e}")
        
        # Activity log
        logger.info(f"AI advice generated for {advice_request.city} by IP: {client_ip}")
        
        return {"success": True, "advice": advice}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in AI advice: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring"""
    return {
        "status": "healthy",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "services": {
            "openai": bool(openai.api_key and openai.api_key != "your_openai_api_key"),
            "supabase": bool(supabase)
        }
    }

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Custom HTTP error handling"""
    logger.warning(f"HTTP Error {exc.status_code}: {exc.detail} from IP: {get_client_ip(request)}")
    return {"error": exc.detail, "status_code": exc.status_code}

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """General error handling"""
    logger.error(f"Unexpected error: {exc} from IP: {get_client_ip(request)}")
    return {"error": "Internal server error", "status_code": 500}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 