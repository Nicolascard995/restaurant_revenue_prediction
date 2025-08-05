# 🧠 Guía de Prompt Engineering - Restaurant Revenue Prediction

## 📋 Introducción
Esta guía contiene los prompts específicos para cada paso del plan de mejora del MVP, optimizados para obtener los mejores resultados de la IA.

---

## 🎯 PASO 1: Análisis de Variables - Prompts

### Prompt 1.1: Análisis Exploratorio de Datos
```
Actúa como un Data Scientist experto en análisis de restaurantes. Analiza el dataset de train.csv y test.csv para:

1. Identificar las variables más correlacionadas con revenue
2. Detectar patrones estacionales o geográficos
3. Sugerir 10 nuevas variables que podrían mejorar la predicción
4. Crear un ranking de importancia de variables actuales

Formato de respuesta:
- Análisis de correlaciones (top 5)
- Variables faltantes más importantes
- Nuevas variables sugeridas con justificación
- Recomendaciones de feature engineering
```

### Prompt 1.2: Diseño de Esquema Extendido
```
Como arquitecto de datos, diseña un esquema de base de datos para un sistema de análisis de restaurantes que incluya:

Variables demográficas:
- Población de la ciudad
- Ingreso promedio
- Edad promedio
- Nivel educativo

Variables de competencia:
- Número de restaurantes en 1km, 5km, 10km
- Tipos de restaurantes cercanos
- Precios promedio de la zona

Variables económicas:
- PIB per cápita
- Tasa de desempleo
- Inflación local
- Turismo anual

Variables estacionales:
- Eventos locales
- Temporada turística
- Clima promedio

Crea el esquema SQL y las relaciones entre tablas.
```

### Prompt 1.3: Validación de Variables
```
Evalúa la siguiente lista de variables para predicción de revenue de restaurantes:

[LISTA_DE_VARIABLES]

Para cada variable, proporciona:
1. Relevancia (1-10)
2. Disponibilidad de datos (1-10)
3. Costo de obtención (1-10)
4. Impacto estimado en precisión del modelo

Prioriza las variables por ROI (impacto/costo) y sugiere un plan de implementación.
```

---

## 🎯 PASO 2: Mejora del Modelo ML - Prompts

### Prompt 2.1: Diseño de Ensemble
```
Como ML Engineer experto, diseña un sistema de ensemble para predicción de revenue de restaurantes:

Requisitos:
- 3-5 modelos diferentes
- Método de combinación (voting, stacking, blending)
- Validación cruzada robusta
- Métricas de evaluación múltiples

Considera:
- Random Forest
- XGBoost
- LightGBM
- Neural Networks
- Linear Regression

Proporciona:
1. Arquitectura del ensemble
2. Hiperparámetros iniciales
3. Estrategia de validación
4. Métricas de evaluación
```

### Prompt 2.2: Feature Engineering
```
Crea un plan de feature engineering avanzado para datos de restaurantes:

Transformaciones numéricas:
- Logaritmos para variables con skew
- Polinomios para relaciones no lineales
- Ratios y proporciones
- Binning de variables continuas

Transformaciones categóricas:
- Target encoding
- Count encoding
- Mean encoding
- Embeddings

Interacciones:
- Variables cruzadas
- Ratios entre variables
- Diferencias y sumas

Proporciona código Python para cada transformación.
```

### Prompt 2.3: Optimización de Hiperparámetros
```
Diseña una estrategia de optimización de hiperparámetros para ensemble de modelos:

1. Espacio de búsqueda para cada modelo
2. Método de optimización (Grid Search, Random Search, Bayesian)
3. Validación cruzada temporal
4. Métricas de evaluación múltiples

Incluye:
- Código de implementación
- Estrategia de early stopping
- Manejo de overfitting
- Interpretabilidad de resultados
```

---

## 🎯 PASO 3: Generación de PDFs - Prompts

### Prompt 3.1: Diseño de Templates PDF
```
Diseña templates de PDF para reportes de análisis de restaurantes:

Secciones requeridas:
1. Resumen ejecutivo
2. Análisis de viabilidad
3. Predicción de revenue
4. Recomendaciones estratégicas
5. Análisis de riesgos
6. Gráficos y visualizaciones

Especificaciones:
- Formato profesional
- Colores corporativos
- Gráficos interactivos
- Secciones numeradas
- Índice automático

Proporciona código Python con ReportLab.
```

### Prompt 3.2: Contenido Dinámico PDF
```
Crea un sistema de generación de contenido dinámico para PDFs de análisis:

Tipos de contenido:
- Análisis de mercado local
- Comparación con competencia
- Proyecciones financieras
- Recomendaciones personalizadas
- Alertas de riesgo

Variables dinámicas:
- Nombre del restaurante
- Ubicación específica
- Tipo de restaurante
- Inversión inicial
- Fecha de análisis

Genera código Python que combine templates con datos dinámicos.
```

---

## 🎯 PASO 4: Prompt Engineering Avanzado - Prompts

### Prompt 4.1: Sistema de Contexto
```
Diseña un sistema de gestión de contexto para prompts de análisis de restaurantes:

Componentes:
1. Contexto histórico (análisis previos)
2. Contexto geográfico (datos de la ciudad)
3. Contexto económico (indicadores actuales)
4. Contexto estacional (temporada actual)
5. Contexto competitivo (restaurantes cercanos)

Implementa:
- Sistema de memoria de contexto
- Actualización automática de datos
- Personalización por tipo de análisis
- Optimización de tokens
```

### Prompt 4.2: Templates de Prompts
```
Crea templates de prompts para diferentes tipos de análisis:

1. Análisis de Viabilidad:
"Analiza la viabilidad de abrir un restaurante [TIPO] en [CIUDAD] con inversión de [MONTO]. Considera [CONTEXTO_GEOGRAFICO] y [CONTEXTO_ECONOMICO]."

2. Predicción de Revenue:
"Predice el revenue mensual para un restaurante [TIPO] en [CIUDAD] con [CARACTERISTICAS]. Usa datos históricos de [PERIODO]."

3. Análisis de Competencia:
"Analiza la competencia en un radio de [RADIO] km de [UBICACION]. Identifica oportunidades y amenazas."

4. Recomendaciones Estratégicas:
"Proporciona recomendaciones estratégicas para optimizar revenue en [RESTAURANTE] basado en [DATOS_ACTUALES]."

Implementa sistema de variables dinámicas.
```

### Prompt 4.3: Optimización de Prompts
```
Implementa un sistema de optimización de prompts basado en:

1. Métricas de calidad:
   - Relevancia de respuesta
   - Completitud de información
   - Utilidad práctica
   - Claridad de recomendaciones

2. Feedback loop:
   - Calificación de usuario
   - Tiempo de respuesta
   - Tasa de conversión
   - Satisfacción del cliente

3. A/B testing:
   - Variaciones de prompts
   - Medición de performance
   - Optimización automática
   - Personalización

Proporciona código Python para implementación.
```

---

## 🎯 PASO 5: API REST Mejorada - Prompts

### Prompt 5.1: Diseño de Endpoints
```
Diseña una API REST completa para análisis de restaurantes:

Endpoints principales:
1. POST /api/analyze - Análisis completo
2. GET /api/predict/{id} - Obtener predicción
3. POST /api/pdf/generate - Generar PDF
4. GET /api/history - Historial de análisis
5. POST /api/feedback - Feedback de usuario
6. GET /api/health - Health check
7. GET /api/metrics - Métricas del sistema

Especificaciones:
- Autenticación JWT
- Rate limiting
- Validación de datos
- Manejo de errores
- Documentación automática

Proporciona código FastAPI completo.
```

### Prompt 5.2: Sistema de Autenticación
```
Implementa un sistema de autenticación robusto para la API:

Características:
1. Registro de usuarios
2. Login con JWT
3. Refresh tokens
4. Roles y permisos
5. Rate limiting por usuario
6. Logging de actividades

Seguridad:
- Hashing de contraseñas
- Validación de tokens
- Protección CSRF
- Headers de seguridad
- Rate limiting inteligente

Proporciona código Python con FastAPI y SQLAlchemy.
```

---

## 🎯 PASO 6: Base de Datos - Prompts

### Prompt 6.1: Diseño de Esquema
```
Diseña un esquema de base de datos PostgreSQL para el sistema de análisis de restaurantes:

Tablas principales:
1. users - Usuarios del sistema
2. restaurants - Datos de restaurantes
3. analyses - Análisis realizados
4. predictions - Predicciones generadas
5. pdf_reports - Reportes PDF
6. feedback - Feedback de usuarios
7. metrics - Métricas del sistema

Relaciones:
- Usuario puede tener múltiples análisis
- Análisis puede tener múltiples predicciones
- Predicciones pueden tener múltiples PDFs
- Feedback relacionado con análisis

Incluye índices, constraints y triggers.
```

### Prompt 6.2: Sistema de Cache
```
Implementa un sistema de cache Redis para optimizar performance:

Cache layers:
1. Cache de predicciones (TTL: 1 hora)
2. Cache de análisis (TTL: 24 horas)
3. Cache de PDFs (TTL: 7 días)
4. Cache de métricas (TTL: 1 minuto)

Estrategias:
- Cache-aside pattern
- Write-through cache
- Cache invalidation
- Compression de datos
- Distributed cache

Proporciona código Python con Redis.
```

---

## 🎯 PASO 7: UI Mejorada - Prompts

### Prompt 7.1: Dashboard Interactivo
```
Diseña un dashboard interactivo para análisis de restaurantes:

Componentes:
1. Formulario de entrada de datos
2. Gráficos de predicción
3. Análisis de competencia
4. Generación de PDFs
5. Historial de análisis
6. Métricas de performance

Tecnologías:
- HTML5/CSS3
- JavaScript ES6+
- Chart.js para gráficos
- Bootstrap/Tailwind
- AJAX para API calls

Características:
- Responsive design
- Dark/light mode
- Animaciones suaves
- Loading states
- Error handling
```

### Prompt 7.2: Formularios Avanzados
```
Crea formularios avanzados para entrada de datos:

Secciones:
1. Información básica del restaurante
2. Datos de ubicación
3. Información financiera
4. Características del negocio
5. Análisis de competencia

Validaciones:
- Validación en tiempo real
- Mensajes de error claros
- Autocompletado
- Validación de rangos
- Formato de datos

UX/UI:
- Progreso visual
- Guardado automático
- Navegación intuitiva
- Accesibilidad
```

---

## 🎯 PASO 8: Sistema de Alertas - Prompts

### Prompt 8.1: Alertas Inteligentes
```
Diseña un sistema de alertas inteligentes para el análisis de restaurantes:

Tipos de alertas:
1. Alertas de riesgo (revenue bajo)
2. Alertas de oportunidad (mercado favorable)
3. Alertas de competencia (nuevos restaurantes)
4. Alertas de rendimiento (modelo degradado)
5. Alertas de sistema (errores, latencia)

Configuración:
- Thresholds personalizables
- Frecuencia de verificación
- Canales de notificación
- Escalación automática
- Supresión de alertas duplicadas

Implementa con Python y servicios de email/SMS.
```

### Prompt 8.2: Notificaciones Push
```
Implementa sistema de notificaciones push:

Características:
1. Notificaciones en tiempo real
2. Personalización por usuario
3. Diferentes tipos de notificación
4. Gestión de suscripciones
5. Métricas de engagement

Tecnologías:
- WebSockets
- Service Workers
- Push API
- Firebase Cloud Messaging

Funcionalidades:
- Notificaciones inmediatas
- Notificaciones programadas
- Notificaciones basadas en eventos
- Gestión de preferencias
```

---

## 🎯 PASO 9: Testing - Prompts

### Prompt 9.1: Tests Unitarios
```
Crea suite completa de tests unitarios:

Cobertura:
1. Tests de modelos ML
2. Tests de API endpoints
3. Tests de generación PDF
4. Tests de prompts
5. Tests de base de datos

Frameworks:
- pytest para Python
- unittest para casos básicos
- mock para dependencias
- coverage para métricas

Estrategias:
- Test-driven development
- Fixtures reutilizables
- Parametrized tests
- Test isolation
- Performance testing
```

### Prompt 9.2: Tests de Integración
```
Diseña tests de integración comprehensivos:

Escenarios:
1. Flujo completo de análisis
2. Generación de PDFs
3. Sistema de alertas
4. Autenticación completa
5. Cache y base de datos

Herramientas:
- pytest-asyncio
- httpx para API testing
- Testcontainers para DB
- Selenium para UI
- Locust para performance

Métricas:
- Tiempo de respuesta
- Tasa de éxito
- Cobertura de código
- Performance bajo carga
```

---

## 🎯 PASO 10: Documentación - Prompts

### Prompt 10.1: Documentación Técnica
```
Crea documentación técnica completa:

Secciones:
1. Arquitectura del sistema
2. API documentation
3. Guía de deployment
4. Troubleshooting
5. Performance tuning

Formato:
- Markdown
- OpenAPI/Swagger
- Diagramas de arquitectura
- Ejemplos de código
- Casos de uso

Herramientas:
- Sphinx para documentación
- Swagger UI para API
- Mermaid para diagramas
- Jupyter notebooks
```

### Prompt 10.2: Guía de Usuario
```
Escribe guía de usuario completa:

Contenido:
1. Introducción al sistema
2. Tutorial paso a paso
3. Casos de uso comunes
4. FAQ
5. Troubleshooting

Formato:
- Guía visual
- Screenshots
- Videos tutoriales
- Ejemplos prácticos
- Glosario de términos

Características:
- Lenguaje claro
- Ejemplos concretos
- Navegación fácil
- Búsqueda integrada
- Feedback de usuarios
```

---

## 🎯 Prompts de Optimización Continua

### Prompt OPT.1: Análisis de Performance
```
Analiza el performance del sistema y sugiere optimizaciones:

Métricas a monitorear:
1. Tiempo de respuesta API
2. Precisión de modelos
3. Uso de recursos
4. Satisfacción de usuarios
5. Tasa de conversión

Optimizaciones:
- Cache optimization
- Model retraining
- Database indexing
- Code optimization
- Infrastructure scaling

Implementa sistema de monitoreo automático.
```

### Prompt OPT.2: Feedback Loop
```
Implementa sistema de feedback loop para mejora continua:

Componentes:
1. Recolección de feedback
2. Análisis de sentimientos
3. Identificación de patrones
4. Generación de insights
5. Implementación de mejoras

Métricas:
- NPS score
- User satisfaction
- Feature usage
- Error rates
- Performance metrics

Automatización:
- Análisis automático
- Alertas de tendencias
- Sugerencias de mejora
- A/B testing
```

---

## 📊 Métricas de Éxito de Prompts

### Calidad de Respuestas:
- [ ] Relevancia > 90%
- [ ] Completitud > 85%
- [ ] Utilidad práctica > 80%
- [ ] Claridad > 90%

### Performance:
- [ ] Tiempo de respuesta < 5 segundos
- [ ] Tasa de éxito > 95%
- [ ] Satisfacción de usuario > 4.5/5
- [ ] Reutilización de prompts > 70%

### Optimización:
- [ ] Reducción de tokens > 20%
- [ ] Mejora de precisión > 15%
- [ ] Aumento de velocidad > 30%
- [ ] Reducción de errores > 50%

---

¿Te gustaría que implementemos algún prompt específico o comencemos con el Paso 1 del plan de mejora? 