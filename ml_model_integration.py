import pickle
import pandas as pd
import numpy as np
from typing import Dict, Any, Optional
import logging
from datetime import datetime
import os

logger = logging.getLogger(__name__)

class MLModelIntegration:
    def __init__(self):
        self.model_data = None
        self.simple_model_data = None
        self.load_models()
    
    def load_models(self):
        """Carga los modelos entrenados"""
        try:
            # Cargar modelo completo
            with open('models/restaurant_model.pkl', 'rb') as f:
                self.model_data = pickle.load(f)
            logger.info("✅ Modelo completo cargado")
            
            # Cargar modelo simplificado
            with open('models/simple_restaurant_model.pkl', 'rb') as f:
                self.simple_model_data = pickle.load(f)
            logger.info("✅ Modelo simplificado cargado")
            
        except Exception as e:
            logger.error(f"❌ Error cargando modelos: {e}")
            self.model_data = None
            self.simple_model_data = None
    
    def prepare_features(self, restaurant_data: Dict[str, Any], pdf_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Prepara características para el modelo ML"""
        try:
            # Características básicas del restaurante
            features = {
                'City': restaurant_data.get('city', ''),
                'City Group': restaurant_data.get('city_group', ''),
                'Type': restaurant_data.get('type', ''),
                'Open Date': restaurant_data.get('open_date', ''),
                'Investment': restaurant_data.get('investment', 0),
                'Monthly Costs': restaurant_data.get('monthly_costs', 0)
            }
            
            # Procesar fecha
            try:
                open_date = pd.to_datetime(features['Open Date'])
                features['Year'] = open_date.year
                features['Month'] = open_date.month
                features['Day'] = open_date.day
            except:
                features['Year'] = 2010
                features['Month'] = 1
                features['Day'] = 1
            
            # Codificar variables categóricas
            if self.model_data:
                features['City_encoded'] = self.model_data['le_city'].transform([features['City']])[0]
                features['City Group_encoded'] = self.model_data['le_city_group'].transform([features['City Group']])[0]
                features['Type_encoded'] = self.model_data['le_type'].transform([features['Type']])[0]
            
            # Agregar características de PDF si están disponibles
            if pdf_data and pdf_data.get('analysis'):
                pdf_analysis = pdf_data['analysis']
                
                # Extraer datos demográficos
                demographics = pdf_analysis.get('datos_demograficos', {})
                features['Population'] = demographics.get('poblacion', 100000)
                features['Avg_Income'] = demographics.get('ingreso_promedio', 50000)
                features['Avg_Age'] = demographics.get('edad_promedio', 35)
                
                # Extraer datos de competencia
                competition = pdf_analysis.get('competencia', {})
                features['Nearby_Restaurants'] = competition.get('restaurantes_cercanos', 10)
                features['Avg_Prices'] = competition.get('precios_promedio', 25)
                
                # Extraer indicadores económicos
                economics = pdf_analysis.get('indicadores_economicos', {})
                features['GDP_Per_Capita'] = economics.get('pib_per_capita', 30000)
                features['Unemployment_Rate'] = economics.get('tasa_desempleo', 5)
                
            else:
                # Valores por defecto si no hay PDF
                features['Population'] = 100000
                features['Avg_Income'] = 50000
                features['Avg_Age'] = 35
                features['Nearby_Restaurants'] = 10
                features['Avg_Prices'] = 25
                features['GDP_Per_Capita'] = 30000
                features['Unemployment_Rate'] = 5
            
            return features
            
        except Exception as e:
            logger.error(f"❌ Error preparando características: {e}")
            return {}
    
    def predict_revenue_ml(self, restaurant_data: Dict[str, Any], pdf_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Predice revenue usando el modelo ML original"""
        try:
            if not self.model_data:
                logger.warning("⚠️ Modelo ML no disponible, usando predicción simple")
                return self.fallback_prediction(restaurant_data)
            
            # Preparar características
            features = self.prepare_features(restaurant_data, pdf_data)
            
            if not features:
                return self.fallback_prediction(restaurant_data)
            
            # Crear vector de características para el modelo
            feature_vector = []
            
            # Características básicas del modelo original
            feature_vector.extend([
                features['City_encoded'],
                features['City Group_encoded'],
                features['Type_encoded'],
                features['Year'],
                features['Month'],
                features['Day']
            ])
            
            # Agregar características P1-P37 (usando valores por defecto)
            for i in range(1, 38):
                feature_vector.append(features.get(f'P{i}', 3.0))
            
            # Predicción con modelo completo
            prediction_full = self.model_data['model'].predict([feature_vector])[0]
            
            # Predicción con modelo simplificado
            simple_features = [
                features['City Group_encoded'],
                features['Type_encoded'],
                features['Year']
            ]
            prediction_simple = self.simple_model_data['model'].predict([simple_features])[0]
            
            # Calcular confianza basada en la diferencia entre modelos
            confidence = max(0.5, 1 - abs(prediction_full - prediction_simple) / prediction_full)
            
            # Ajustar predicción basado en datos de PDF
            pdf_adjustment = 1.0
            if pdf_data and pdf_data.get('analysis'):
                pdf_analysis = pdf_data['analysis']
                
                # Ajustes basados en análisis de PDF
                if pdf_analysis.get('oportunidades'):
                    pdf_adjustment *= 1.1  # 10% más si hay oportunidades
                
                if pdf_analysis.get('riesgos'):
                    pdf_adjustment *= 0.95  # 5% menos si hay riesgos
                
                # Ajuste por competencia
                competition = pdf_analysis.get('competencia', {})
                if competition.get('nivel_competencia') == 'alto':
                    pdf_adjustment *= 0.9
                elif competition.get('nivel_competencia') == 'bajo':
                    pdf_adjustment *= 1.05
            
            final_prediction = prediction_full * pdf_adjustment
            
            return {
                "success": True,
                "revenue_prediction": final_prediction,
                "prediction_full": prediction_full,
                "prediction_simple": prediction_simple,
                "confidence": confidence,
                "pdf_adjustment": pdf_adjustment,
                "model_used": "ML_Original_Kaggle",
                "features_used": len(feature_vector),
                "pdf_integrated": pdf_data is not None
            }
            
        except Exception as e:
            logger.error(f"❌ Error en predicción ML: {e}")
            return self.fallback_prediction(restaurant_data)
    
    def fallback_prediction(self, restaurant_data: Dict[str, Any]) -> Dict[str, Any]:
        """Predicción de respaldo si el modelo ML falla"""
        try:
            investment = restaurant_data.get('investment', 0)
            city_group = restaurant_data.get('city_group', 'Other')
            restaurant_type = restaurant_data.get('type', 'IL')
            
            # Predicción simple basada en inversión
            base_revenue = investment * 0.3
            
            # Ajustes
            city_multiplier = 1.2 if city_group == "Big Cities" else 0.8
            type_multiplier = 1.1 if restaurant_type == "FC" else 0.9
            
            revenue = base_revenue * city_multiplier * type_multiplier
            
            return {
                "success": True,
                "revenue_prediction": revenue,
                "prediction_full": revenue,
                "prediction_simple": revenue,
                "confidence": 0.5,
                "pdf_adjustment": 1.0,
                "model_used": "Fallback_Simple",
                "features_used": 3,
                "pdf_integrated": False
            }
            
        except Exception as e:
            logger.error(f"❌ Error en predicción de respaldo: {e}")
            return {
                "success": False,
                "revenue_prediction": 0,
                "error": str(e),
                "model_used": "Error"
            }
    
    def get_model_info(self) -> Dict[str, Any]:
        """Obtiene información sobre los modelos disponibles"""
        try:
            info = {
                "models_loaded": {
                    "full_model": self.model_data is not None,
                    "simple_model": self.simple_model_data is not None
                },
                "model_performance": {}
            }
            
            if self.model_data:
                info["model_performance"]["full_model"] = {
                    "train_score": self.model_data.get('train_score', 0),
                    "test_score": self.model_data.get('test_score', 0),
                    "feature_count": len(self.model_data.get('feature_columns', []))
                }
            
            if self.simple_model_data:
                info["model_performance"]["simple_model"] = {
                    "feature_count": len(self.simple_model_data.get('feature_columns', []))
                }
            
            return info
            
        except Exception as e:
            logger.error(f"❌ Error obteniendo info del modelo: {e}")
            return {"error": str(e)}

# Instancia global
ml_integration = MLModelIntegration() 