#!/usr/bin/env python3
"""
Servicio de traducción automática usando OpenAI
"""

import os
import logging
from typing import Dict, Any, Optional
from openai import OpenAI

logger = logging.getLogger(__name__)

class TranslationService:
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.model = "gpt-3.5-turbo"
    
    def translate_text(self, text: str, target_language: str) -> str:
        """Traduce texto al idioma objetivo"""
        try:
            language_names = {
                "en": "English",
                "es": "Spanish", 
                "de": "German"
            }
            
            target_lang_name = language_names.get(target_language, "English")
            
            prompt = f"""
            Translate the following text to {target_lang_name}. 
            Maintain the same tone and style, but adapt it naturally to the target language.
            
            Text to translate:
            {text}
            
            Respond only with the translated text, nothing else.
            """
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a professional translator. Translate accurately and naturally."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1000,
                temperature=0.3
            )
            
            translated_text = response.choices[0].message.content.strip()
            logger.info(f"✅ Text translated to {target_lang_name}")
            
            return translated_text
            
        except Exception as e:
            logger.error(f"❌ Error translating text: {e}")
            return text  # Return original text if translation fails
    
    def translate_analysis_response(self, response: Dict[str, Any], target_language: str) -> Dict[str, Any]:
        """Traduce una respuesta de análisis completa"""
        try:
            if target_language == "en":
                return response  # No translation needed for English
            
            translated_response = response.copy()
            
            # Translate main fields
            if "viability_analysis" in translated_response:
                viability = translated_response["viability_analysis"]
                if "viability" in viability:
                    viability["viability"] = self._translate_viability_status(
                        viability["viability"], target_language
                    )
            
            # Translate analysis text fields
            text_fields_to_translate = [
                "analysis", "recommendations", "insights", 
                "risk_assessment", "strategic_recommendations"
            ]
            
            for field in text_fields_to_translate:
                if field in translated_response and isinstance(translated_response[field], str):
                    translated_response[field] = self.translate_text(
                        translated_response[field], target_language
                    )
            
            # Translate nested dictionaries
            for key, value in translated_response.items():
                if isinstance(value, dict):
                    translated_response[key] = self._translate_dict(value, target_language)
            
            logger.info(f"✅ Analysis response translated to {target_language}")
            return translated_response
            
        except Exception as e:
            logger.error(f"❌ Error translating analysis response: {e}")
            return response
    
    def _translate_dict(self, data: Dict[str, Any], target_language: str) -> Dict[str, Any]:
        """Traduce un diccionario recursivamente"""
        translated_dict = {}
        
        for key, value in data.items():
            if isinstance(value, str):
                # Translate string values
                translated_dict[key] = self.translate_text(value, target_language)
            elif isinstance(value, dict):
                # Recursively translate nested dictionaries
                translated_dict[key] = self._translate_dict(value, target_language)
            elif isinstance(value, list):
                # Translate list items
                translated_dict[key] = [
                    self.translate_text(item, target_language) if isinstance(item, str) else item
                    for item in value
                ]
            else:
                # Keep non-string values as is
                translated_dict[key] = value
        
        return translated_dict
    
    def _translate_viability_status(self, status: str, target_language: str) -> str:
        """Traduce el estado de viabilidad"""
        status_translations = {
            "en": {"High": "High", "Low": "Low", "Medium": "Medium"},
            "es": {"High": "Alta", "Low": "Baja", "Medium": "Media"},
            "de": {"High": "Hoch", "Low": "Niedrig", "Medium": "Mittel"}
        }
        
        return status_translations.get(target_language, {}).get(status, status)
    
    def get_language_info(self) -> Dict[str, Any]:
        """Obtiene información sobre idiomas disponibles"""
        return {
            "available_languages": [
                {"code": "en", "name": "English", "native_name": "English"},
                {"code": "es", "name": "Spanish", "native_name": "Español"},
                {"code": "de", "name": "German", "native_name": "Deutsch"}
            ],
            "default_language": "en",
            "translation_service": "OpenAI GPT-3.5-turbo",
            "features": [
                "Traducción automática de análisis",
                "Traducción de recomendaciones",
                "Traducción de insights",
                "Traducción de estados de viabilidad"
            ]
        }

# Instancia global del servicio de traducción
translation_service = TranslationService() 