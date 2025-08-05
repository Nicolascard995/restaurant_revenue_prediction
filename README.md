# 🍽️ Restaurant Advisor MVP

Un MVP inteligente para ayudar a emprendedores a evaluar la viabilidad de abrir un restaurante, utilizando análisis de datos, inteligencia artificial y base de datos en la nube.

## 🚀 Características

- **Análisis de Viabilidad**: Predicción de ingresos basada en datos históricos
- **Asistente IA**: Consejos personalizados usando GPT-3.5
- **Base de Datos**: Almacenamiento en Supabase para seguimiento
- **Interfaz Moderna**: UI profesional con Tailwind CSS
- **Seguridad**: Validaciones, sanitización y rate limiting
- **API REST**: Backend con FastAPI

## 📋 Requisitos

- Python 3.8+
- Cuenta en Supabase
- API Key de OpenAI

## 🛠️ Instalación Rápida

### 1. Clonar y configurar
```bash
git clone <tu-repositorio>
cd restaurant_revenue_prediction
```

### 2. Instalar dependencias
```bash
pip install -r requirements.txt
```

### 3. Configurar variables de entorno
```bash
# Copiar archivo de ejemplo
cp .env.example .env

# Editar con tus credenciales
nano .env
```

### 4. Configurar Supabase
1. Ve a [supabase.com](https://supabase.com)
2. Crea un proyecto
3. Ejecuta el SQL en `clean_supabase_setup.sql`

### 5. Entrenar modelo
```bash
python3 train_model.py
```

### 6. Ejecutar aplicación
```bash
python3 app.py
```

## 🌐 Uso

### Acceso Web
- **URL**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

### Funcionalidades
1. **Análisis de Viabilidad**: Introduce datos del restaurante
2. **Consejos de IA**: Recibe recomendaciones personalizadas
3. **Resultados**: Visualización clara de métricas

## 🔒 Seguridad

El MVP implementa múltiples capas de seguridad:

- ✅ **Validación de Entrada**: Pydantic models con sanitización
- ✅ **Rate Limiting**: Control de requests por IP
- ✅ **Sanitización**: Remoción de caracteres peligrosos
- ✅ **Logging**: Registro de actividad sin datos sensibles
- ✅ **CORS**: Configuración apropiada para APIs

Ver [SECURITY.md](SECURITY.md) para detalles completos.

## 🏗️ Arquitectura

```
restaurant_revenue_prediction/
├── app.py                    # Aplicación principal FastAPI
├── train_model.py           # Entrenamiento del modelo ML
├── requirements.txt         # Dependencias de Python
├── .env                     # Variables de entorno
├── clean_supabase_setup.sql # Configuración de base de datos
├── templates/
│   └── index.html          # Interfaz web principal
├── static/                  # Archivos estáticos
├── models/                  # Modelos entrenados
├── train.csv               # Datos de entrenamiento
└── README.md               # Este archivo
```

## 📊 API Endpoints

### POST /api/analyze
Analiza la viabilidad de un restaurante

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
        "viability": "Alta",
        "annual_revenue": 150000.0,
        "annual_profit": 132000.0,
        "roi": 26.4
    }
}
```

### POST /api/ai_advice
Obtiene consejos personalizados de IA

### GET /health
Verifica el estado de los servicios

## 🔧 Configuración

### Variables de Entorno
```env
# Supabase Configuration
SUPABASE_URL=https://tu-proyecto.supabase.co
SUPABASE_KEY=tu-anon-public-key

# OpenAI Configuration
OPENAI_API_KEY=sk-tu-api-key-de-openai

# Model Configuration
MODEL_PATH=./models/restaurant_model.pkl
```

### Base de Datos
Ejecuta las consultas en `clean_supabase_setup.sql` en tu proyecto de Supabase.

## 📈 Modelo de ML

- **Algoritmo**: Random Forest Regressor
- **Precisión**: R² = 0.84 en entrenamiento
- **Datos**: 137 restaurantes reales
- **Características**: 43 variables incluyendo demografía y datos comerciales

## 🚀 Despliegue

### Desarrollo
```bash
python3 app.py
```

### Producción
```bash
uvicorn app:app --host 0.0.0.0 --port 8000
```

### Docker (opcional)
```bash
docker build -t restaurant-advisor .
docker run -p 8000:8000 restaurant-advisor
```

## 📚 Documentación

- [SECURITY.md](SECURITY.md) - Medidas de seguridad
- [DEMO.md](DEMO.md) - Guía de demostración
- [ESTADO_FINAL.md](ESTADO_FINAL.md) - Estado del proyecto

## 🤝 Contribuir

1. Fork el proyecto
2. Crea una rama para tu feature
3. Commit tus cambios
4. Push a la rama
5. Abre un Pull Request

## 📄 Licencia

Este proyecto está bajo la Licencia MIT.

## 📞 Soporte

Para soporte técnico o preguntas sobre el MVP:
- Issues en GitHub
- Email: [tu-email@ejemplo.com]

---

**Desarrollado con ❤️ para ayudar a emprendedores a hacer realidad sus sueños gastronómicos**




