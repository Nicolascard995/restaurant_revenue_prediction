# 🔒 Seguridad del Restaurant Advisor MVP

## 🛡️ Medidas de Seguridad Implementadas

### **1. Validación de Entrada**
- ✅ **Pydantic Models**: Validación estricta de tipos y rangos
- ✅ **Sanitización**: Remoción de caracteres peligrosos (`<`, `>`, `"`, `'`)
- ✅ **Validación de Negocio**: Límites en montos y longitudes
- ✅ **Enumeraciones**: Valores permitidos para campos críticos

### **2. Rate Limiting**
- ✅ **Análisis**: 10 requests por minuto por IP
- ✅ **Consejos IA**: 5 requests por minuto por IP (más estricto)
- ✅ **Detección IP**: Manejo seguro de IPs con proxies

### **3. Sanitización de Datos**
```python
# Remover caracteres peligrosos
v = re.sub(r'[<>"\']', '', v.strip())

# Limitar longitud de respuestas
advice = advice[:2000]  # Máximo 2000 caracteres

# Sanitizar HTML en respuestas de IA
advice = re.sub(r'<[^>]*>', '', advice)
```

### **4. Manejo de Errores Seguro**
- ✅ **Logging**: Registro de errores sin exponer datos sensibles
- ✅ **Mensajes Genéricos**: No revelar información interna
- ✅ **Validación de Negocio**: Prevenir valores inválidos

### **5. Configuración de CORS**
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción, especificar dominios
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### **6. Validaciones de Negocio**
- ✅ **Montos**: Entre 0 y 10,000,000 €
- ✅ **Ciudades**: Máximo 100 caracteres
- ✅ **Tipos**: Solo valores permitidos (FC, IL)
- ✅ **Grupos**: Solo valores permitidos (Big Cities, Other)

## 🔧 Configuración de Seguridad

### **Variables de Entorno**
```env
# Supabase (Base de datos)
SUPABASE_URL=https://tu-proyecto.supabase.co
SUPABASE_KEY=tu-anon-public-key

# OpenAI (IA)
OPENAI_API_KEY=sk-tu-api-key-de-openai

# Modelo ML
MODEL_PATH=./models/restaurant_model.pkl
```

### **Headers de Seguridad Recomendados**
```python
# Para producción, agregar estos headers:
SECURE_HEADERS = {
    "X-Content-Type-Options": "nosniff",
    "X-Frame-Options": "DENY",
    "X-XSS-Protection": "1; mode=block",
    "Strict-Transport-Security": "max-age=31536000; includeSubDomains"
}
```

## 🚨 Vulnerabilidades Prevenidas

### **1. SQL Injection**
- ✅ **Pydantic**: Validación de tipos antes de procesar
- ✅ **Sanitización**: Remoción de caracteres peligrosos
- ✅ **Parámetros**: Uso de parámetros en lugar de concatenación

### **2. XSS (Cross-Site Scripting)**
- ✅ **Sanitización**: Remoción de tags HTML
- ✅ **Validación**: Verificación de contenido antes de renderizar
- ✅ **Headers**: Configuración de headers de seguridad

### **3. CSRF (Cross-Site Request Forgery)**
- ✅ **CORS**: Configuración apropiada de CORS
- ✅ **Validación**: Verificación de origen de requests
- ✅ **Tokens**: Preparado para implementar tokens CSRF

### **4. Rate Limiting**
- ✅ **Límites**: Control de requests por IP
- ✅ **Ventanas**: Limpieza automática de requests antiguos
- ✅ **Diferentes**: Límites distintos por funcionalidad

### **5. Information Disclosure**
- ✅ **Logging**: No exponer datos sensibles en logs
- ✅ **Errores**: Mensajes genéricos para errores
- ✅ **Headers**: No exponer información del servidor

## 📊 Monitoreo de Seguridad

### **Logs de Seguridad**
```python
# Logs de actividad
logger.info(f"Análisis realizado para {city} por IP: {client_ip}")
logger.warning(f"Rate limit excedido para IP: {client_ip}")
logger.error(f"Error de validación: {error}")
```

### **Endpoint de Salud**
```bash
GET /health
# Retorna estado de servicios sin información sensible
```

### **Métricas de Seguridad**
- ✅ **Requests por IP**: Monitoreo de actividad
- ✅ **Errores de Validación**: Tracking de intentos maliciosos
- ✅ **Tiempo de Respuesta**: Detección de ataques DoS

## 🔄 Mejoras Futuras de Seguridad

### **Inmediatas**
1. **Autenticación**: Sistema de login/registro
2. **Autorización**: Roles y permisos
3. **HTTPS**: Certificados SSL
4. **WAF**: Web Application Firewall

### **A Mediano Plazo**
1. **Auditoría**: Logs de auditoría completos
2. **Encriptación**: Datos sensibles encriptados
3. **Backup**: Sistema de respaldo automático
4. **Monitoreo**: Alertas de seguridad

### **A Largo Plazo**
1. **Penetration Testing**: Pruebas de penetración
2. **Compliance**: Cumplimiento de regulaciones
3. **Zero Trust**: Arquitectura de confianza cero
4. **Threat Intelligence**: Inteligencia de amenazas

## 🛠️ Comandos de Seguridad

### **Verificar Configuración**
```bash
# Verificar variables de entorno
python3 -c "import os; from dotenv import load_dotenv; load_dotenv(); print('SUPABASE_URL:', bool(os.getenv('SUPABASE_URL'))); print('OPENAI_API_KEY:', bool(os.getenv('OPENAI_API_KEY')))"

# Verificar conectividad
curl -X GET http://localhost:8000/health
```

### **Logs de Seguridad**
```bash
# Ver logs en tiempo real
tail -f logs/app.log | grep -E "(ERROR|WARNING|security)"

# Buscar intentos maliciosos
grep "Rate limit" logs/app.log
```

## 📋 Checklist de Seguridad

### **Antes de Producción**
- [ ] Configurar HTTPS
- [ ] Implementar autenticación
- [ ] Configurar WAF
- [ ] Establecer monitoreo
- [ ] Realizar pruebas de penetración
- [ ] Documentar procedimientos de incidentes

### **Mantenimiento**
- [ ] Actualizar dependencias regularmente
- [ ] Revisar logs de seguridad
- [ ] Monitorear métricas de rendimiento
- [ ] Realizar auditorías de seguridad
- [ ] Actualizar políticas de seguridad

---

**El MVP implementa las mejores prácticas de seguridad para proteger datos de usuarios y prevenir ataques comunes.** 