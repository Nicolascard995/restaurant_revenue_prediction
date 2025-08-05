# 🚀 Guía de Despliegue - Restaurant Advisor MVP

## 📋 **Opciones de Despliegue**

### **1. 🆓 Render (GRATIS) - RECOMENDADO**

**Ventajas:**
- ✅ Gratis para MVPs
- ✅ Despliegue automático desde GitHub
- ✅ SSL automático
- ✅ Muy fácil de configurar

**Pasos:**

1. **Crear cuenta en Render:**
   - Ve a [render.com](https://render.com)
   - Regístrate con tu cuenta de GitHub

2. **Conectar repositorio:**
   - Haz clic en "New Web Service"
   - Conecta tu repositorio de GitHub
   - Selecciona el repositorio `restaurant_revenue_prediction`

3. **Configurar el servicio:**
   ```
   Name: restaurant-advisor-mvp
   Environment: Python
   Build Command: pip install -r requirements.txt
   Start Command: uvicorn app:app --host 0.0.0.0 --port $PORT
   ```

4. **Configurar variables de entorno:**
   - Ve a la pestaña "Environment"
   - Agrega estas variables:
   ```
   SUPABASE_URL=https://tu-proyecto.supabase.co
   SUPABASE_KEY=tu-anon-public-key
   OPENAI_API_KEY=sk-tu-api-key-de-openai
   MODEL_PATH=./models/restaurant_model.pkl
   ```

5. **Desplegar:**
   - Haz clic en "Create Web Service"
   - Espera 5-10 minutos para el despliegue

**URL resultante:** `https://restaurant-advisor-mvp.onrender.com`

---

### **2. 🆓 Railway (GRATIS)**

**Ventajas:**
- ✅ Gratis para MVPs
- ✅ Despliegue muy rápido
- ✅ Integración con GitHub

**Pasos:**

1. **Crear cuenta en Railway:**
   - Ve a [railway.app](https://railway.app)
   - Conecta tu cuenta de GitHub

2. **Crear proyecto:**
   - Haz clic en "New Project"
   - Selecciona "Deploy from GitHub repo"
   - Selecciona tu repositorio

3. **Configurar variables:**
   - Ve a "Variables"
   - Agrega las mismas variables de entorno que en Render

4. **Desplegar:**
   - Railway detectará automáticamente que es una app Python
   - Se desplegará automáticamente

---

### **3. 🆓 Heroku (GRATIS limitado)**

**Ventajas:**
- ✅ Muy establecido
- ✅ Buena documentación
- ✅ Integración con GitHub

**Pasos:**

1. **Instalar Heroku CLI:**
   ```bash
   # En Ubuntu/Debian
   curl https://cli-assets.heroku.com/install.sh | sh
   
   # En macOS
   brew install heroku/brew/heroku
   ```

2. **Login y crear app:**
   ```bash
   heroku login
   heroku create restaurant-advisor-mvp
   ```

3. **Configurar variables:**
   ```bash
   heroku config:set SUPABASE_URL=https://tu-proyecto.supabase.co
   heroku config:set SUPABASE_KEY=tu-anon-public-key
   heroku config:set OPENAI_API_KEY=sk-tu-api-key-de-openai
   heroku config:set MODEL_PATH=./models/restaurant_model.pkl
   ```

4. **Desplegar:**
   ```bash
   git push heroku main
   ```

---

### **4. 💰 DigitalOcean App Platform ($5/mes)**

**Ventajas:**
- ✅ Muy confiable
- ✅ Escalable
- ✅ SSL automático

**Pasos:**

1. **Crear cuenta en DigitalOcean**
2. **Ir a App Platform**
3. **Conectar repositorio de GitHub**
4. **Configurar variables de entorno**
5. **Desplegar**

---

### **5. 💰 AWS Elastic Beanstalk**

**Ventajas:**
- ✅ Muy escalable
- ✅ Integración completa con AWS
- ✅ Muy confiable

**Pasos:**

1. **Instalar AWS CLI**
2. **Configurar credenciales**
3. **Crear aplicación EB**
4. **Desplegar con `eb deploy`**

---

## 🔧 **Configuración del Modelo**

### **Para Servidores sin Datos Locales:**

El archivo `setup_deployment.py` creará automáticamente un modelo simple en el servidor:

```bash
# En el servidor, ejecutar:
python3 setup_deployment.py
```

### **Para Servidores con Datos:**

```bash
# Entrenar modelo con datos reales
python3 train_model.py
```

---

## 🌐 **Configuración de Dominio Personalizado**

### **Con Render:**
1. Ve a tu servicio en Render
2. Pestaña "Settings"
3. Sección "Custom Domains"
4. Agrega tu dominio

### **Con Railway:**
1. Ve a tu proyecto
2. Pestaña "Settings"
3. Sección "Domains"
4. Agrega tu dominio

---

## 🔒 **Configuración de Seguridad**

### **Variables de Entorno Requeridas:**
```env
# Supabase
SUPABASE_URL=https://tu-proyecto.supabase.co
SUPABASE_KEY=tu-anon-public-key

# OpenAI
OPENAI_API_KEY=sk-tu-api-key-de-openai

# Modelo
MODEL_PATH=./models/restaurant_model.pkl
```

### **Headers de Seguridad (Opcional):**
```python
# En app.py, agregar:
SECURE_HEADERS = {
    "X-Content-Type-Options": "nosniff",
    "X-Frame-Options": "DENY",
    "X-XSS-Protection": "1; mode=block",
    "Strict-Transport-Security": "max-age=31536000; includeSubDomains"
}
```

---

## 📊 **Monitoreo y Logs**

### **Render:**
- Logs automáticos en la pestaña "Logs"
- Métricas en "Metrics"

### **Railway:**
- Logs en tiempo real
- Métricas de uso

### **Heroku:**
```bash
heroku logs --tail
```

---

## 🚀 **Despliegue Rápido (Recomendado)**

### **Opción 1: Render (Más Fácil)**

1. **Preparar repositorio:**
   ```bash
   git add .
   git commit -m "feat: Add deployment configuration"
   git push origin main
   ```

2. **Ir a Render.com:**
   - Crear cuenta
   - Conectar GitHub
   - Seleccionar repositorio
   - Configurar variables de entorno
   - Desplegar

3. **Obtener URL:**
   - `https://tu-app.onrender.com`

### **Opción 2: Railway (Más Rápido)**

1. **Ir a Railway.app:**
   - Conectar GitHub
   - Seleccionar repositorio
   - Configurar variables
   - Desplegar automáticamente

2. **Obtener URL:**
   - `https://tu-app.railway.app`

---

## 📱 **Compartir tu MVP**

Una vez desplegado, puedes compartir:

### **Link Directo:**
```
https://tu-app.onrender.com
```

### **QR Code:**
- Genera un QR con el link
- Compártelo en presentaciones

### **Embed en Web:**
```html
<iframe src="https://tu-app.onrender.com" width="100%" height="600px"></iframe>
```

---

## 🔄 **Actualizaciones Automáticas**

### **Con GitHub:**
- Cada push a `main` actualiza automáticamente
- No necesitas hacer nada más

### **Variables de Entorno:**
- Actualiza en la plataforma de despliegue
- Se aplican automáticamente

---

## 💰 **Costos Estimados**

| Plataforma | Plan Gratis | Plan Pago |
|------------|-------------|-----------|
| **Render** | ✅ 750h/mes | $7/mes |
| **Railway** | ✅ $5/mes | $20/mes |
| **Heroku** | ❌ No disponible | $7/mes |
| **DigitalOcean** | ❌ No disponible | $5/mes |
| **AWS** | ✅ 12 meses | $10-50/mes |

---

## 🎯 **Recomendación Final**

**Para tu MVP, recomiendo RENDER porque:**
- ✅ **Gratis** para MVPs
- ✅ **Muy fácil** de configurar
- ✅ **Despliegue automático** desde GitHub
- ✅ **SSL automático**
- ✅ **Buena documentación**

**Pasos finales:**
1. Sube los archivos de configuración al repo
2. Ve a render.com
3. Conecta tu repositorio
4. Configura las variables de entorno
5. ¡Despliega!

**Tu MVP estará online en 10 minutos.** 🚀 