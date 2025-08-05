import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import LabelEncoder
import pickle
import os

def train_restaurant_model():
    """Entrenar modelo de predicción de ingresos de restaurantes"""
    
    print("Cargando datos...")
    # Cargar datos de entrenamiento
    df = pd.read_csv('train.csv')
    
    print(f"Datos cargados: {df.shape}")
    print(f"Columnas: {df.columns.tolist()}")
    
    # Preparar características
    print("Preparando características...")
    
    # Codificar variables categóricas
    le_city = LabelEncoder()
    le_city_group = LabelEncoder()
    le_type = LabelEncoder()
    
    df['City_encoded'] = le_city.fit_transform(df['City'])
    df['City Group_encoded'] = le_city_group.fit_transform(df['City Group'])
    df['Type_encoded'] = le_type.fit_transform(df['Type'])
    
    # Convertir fecha a características numéricas
    df['Open Date'] = pd.to_datetime(df['Open Date'])
    df['Year'] = df['Open Date'].dt.year
    df['Month'] = df['Open Date'].dt.month
    df['Day'] = df['Open Date'].dt.day
    
    # Seleccionar características para el modelo
    feature_columns = [
        'City_encoded', 'City Group_encoded', 'Type_encoded',
        'Year', 'Month', 'Day'
    ] + [f'P{i}' for i in range(1, 38)]
    
    X = df[feature_columns]
    y = df['revenue']
    
    print(f"Características seleccionadas: {len(feature_columns)}")
    print(f"Forma de X: {X.shape}")
    print(f"Forma de y: {y.shape}")
    
    # Dividir datos
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )
    
    # Entrenar modelo
    print("Entrenando modelo...")
    model = RandomForestRegressor(
        n_estimators=100,
        max_depth=10,
        random_state=42,
        n_jobs=-1
    )
    
    model.fit(X_train, y_train)
    
    # Evaluar modelo
    train_score = model.score(X_train, y_train)
    test_score = model.score(X_test, y_test)
    
    print(f"R² en entrenamiento: {train_score:.4f}")
    print(f"R² en prueba: {test_score:.4f}")
    
    # Guardar modelo y encoders
    print("Guardando modelo...")
    os.makedirs('models', exist_ok=True)
    
    model_data = {
        'model': model,
        'feature_columns': feature_columns,
        'le_city': le_city,
        'le_city_group': le_city_group,
        'le_type': le_type,
        'train_score': train_score,
        'test_score': test_score
    }
    
    with open('models/restaurant_model.pkl', 'wb') as f:
        pickle.dump(model_data, f)
    
    print("Modelo guardado en models/restaurant_model.pkl")
    
    # Crear modelo simplificado para el MVP
    print("Creando modelo simplificado...")
    simple_model = RandomForestRegressor(
        n_estimators=50,
        max_depth=5,
        random_state=42
    )
    
    # Usar solo características básicas para el MVP
    simple_features = ['City Group_encoded', 'Type_encoded', 'Year']
    X_simple = df[simple_features]
    
    simple_model.fit(X_simple, y)
    
    simple_model_data = {
        'model': simple_model,
        'feature_columns': simple_features,
        'le_city_group': le_city_group,
        'le_type': le_type
    }
    
    with open('models/simple_restaurant_model.pkl', 'wb') as f:
        pickle.dump(simple_model_data, f)
    
    print("Modelo simplificado guardado en models/simple_restaurant_model.pkl")
    
    return model_data

if __name__ == "__main__":
    train_restaurant_model() 