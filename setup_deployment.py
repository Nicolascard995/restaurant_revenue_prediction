#!/usr/bin/env python3
"""
Script para configurar el modelo en el servidor de producción
"""

import os
import sys
import pickle
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import LabelEncoder
import numpy as np

def create_simple_model():
    """Crear un modelo simple para producción"""
    print("🔄 Creando modelo simple para producción...")
    
    # Crear datos de ejemplo para el modelo
    np.random.seed(42)
    n_samples = 100
    
    # Generar datos sintéticos
    cities = ['Madrid', 'Barcelona', 'Valencia', 'Sevilla', 'Bilbao']
    city_groups = ['Big Cities', 'Other']
    types = ['FC', 'IL']
    
    data = {
        'city': np.random.choice(cities, n_samples),
        'city_group': np.random.choice(city_groups, n_samples),
        'type': np.random.choice(types, n_samples),
        'investment': np.random.uniform(100000, 1000000, n_samples),
        'monthly_costs': np.random.uniform(5000, 50000, n_samples)
    }
    
    df = pd.DataFrame(data)
    
    # Crear target (revenue) basado en las características
    df['revenue'] = (
        df['investment'] * 0.3 +  # 30% del capital inicial
        df['monthly_costs'] * 12 * 0.8 +  # 80% de costos anuales
        np.random.normal(0, 50000, n_samples)  # Ruido
    )
    
    # Codificar variables categóricas
    le_city = LabelEncoder()
    le_city_group = LabelEncoder()
    le_type = LabelEncoder()
    
    df['city_encoded'] = le_city.fit_transform(df['city'])
    df['city_group_encoded'] = le_city_group.fit_transform(df['city_group'])
    df['type_encoded'] = le_type.fit_transform(df['type'])
    
    # Preparar features
    features = ['city_encoded', 'city_group_encoded', 'type_encoded', 'investment', 'monthly_costs']
    X = df[features]
    y = df['revenue']
    
    # Entrenar modelo
    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(X, y)
    
    # Crear directorio models si no existe
    os.makedirs('models', exist_ok=True)
    
    # Guardar modelo y encoders
    model_data = {
        'model': model,
        'city_encoder': le_city,
        'city_group_encoder': le_city_group,
        'type_encoder': le_type,
        'features': features
    }
    
    with open('models/restaurant_model.pkl', 'wb') as f:
        pickle.dump(model_data, f)
    
    print("✅ Modelo creado y guardado en models/restaurant_model.pkl")
    return True

def check_environment():
    """Verificar variables de entorno"""
    print("🔍 Verificando configuración...")
    
    required_vars = ['SUPABASE_URL', 'SUPABASE_KEY', 'OPENAI_API_KEY']
    missing_vars = []
    
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"⚠️ Variables de entorno faltantes: {', '.join(missing_vars)}")
        print("💡 Configura estas variables en tu servidor de despliegue")
        return False
    else:
        print("✅ Todas las variables de entorno están configuradas")
        return True

def main():
    """Función principal"""
    print("🚀 Configurando Restaurant Advisor MVP para producción...")
    
    # Crear modelo
    if not create_simple_model():
        print("❌ Error creando el modelo")
        sys.exit(1)
    
    # Verificar entorno
    check_environment()
    
    print("✅ Configuración completada!")
    print("🌐 Tu MVP está listo para ser desplegado")

if __name__ == "__main__":
    main() 