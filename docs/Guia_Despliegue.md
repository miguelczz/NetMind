# 🚀 Guía de Despliegue en Heroku - NetMind

Esta guía te ayudará a desplegar NetMind completamente en Heroku, incluyendo backend y frontend en una sola aplicación.

## 📋 Requisitos Previos

1. **Cuenta de Heroku**: Crea una cuenta en [heroku.com](https://www.heroku.com)
2. **Heroku CLI**: Instala la CLI de Heroku desde [devcenter.heroku.com/articles/heroku-cli](https://devcenter.heroku.com/articles/heroku-cli)
3. **Git**: Asegúrate de tener Git instalado
4. **Repositorio en GitHub**: Tu código debe estar en un repositorio de GitHub

## 🔧 Preparación del Proyecto

### 1. Verificar Archivos Necesarios

Asegúrate de que estos archivos existan en la raíz del proyecto:

- ✅ `Procfile` - Define cómo iniciar la aplicación
- ✅ `runtime.txt` - Especifica la versión de Python
- ✅ `package.json` - Para el build del frontend
- ✅ `build.sh` - Script de build
- ✅ `backend/requirements.txt` - Dependencias de Python
- ✅ `backend/main.py` - Aplicación FastAPI

### 2. Variables de Entorno Necesarias

Prepara las siguientes variables de entorno que configurarás en Heroku:

```env
# OpenAI (REQUERIDO)
OPENAI_API_KEY=tu_api_key_aqui
EMBEDDING_MODEL=text-embedding-3-large
LLM_MODEL=gpt-4o-mini

# Qdrant (REQUERIDO)
# Opción 1: Qdrant Cloud (recomendado)
QDRANT_URL=https://tu-cluster.qdrant.io
QDRANT_API_KEY=tu_api_key_qdrant

# Opción 2: Qdrant local (si usas un addon o servicio externo)
# QDRANT_URL=http://tu-qdrant-instance.com:6333

# PostgreSQL (REQUERIDO)
# Heroku proporcionará DATABASE_URL automáticamente si agregas el addon
# O puedes usar una base de datos externa:
DATABASE_URL=postgresql://usuario:password@host:5432/database

# Redis (REQUERIDO)
# Opción 1: Heroku Redis (recomendado)
# Se configurará automáticamente si agregas el addon

# Opción 2: Redis externo
REDIS_URL=redis://usuario:password@host:6379/0

# App
APP_ENV=production
APP_NAME=NetMind
APP_VERSION=1.0.0
SECRET_KEY=genera_una_clave_secreta_segura_aqui

# Procesamiento
UPLOAD_DIR=./databases/uploads
CHUNK_SIZE=500
CHUNK_OVERLAP=50

# Ragas (Opcional)
RAGAS_ENABLED=true
```

## 📝 Paso a Paso: Despliegue en Heroku

### Paso 1: Instalar Heroku CLI e Iniciar Sesión

```bash
# Verificar instalación
heroku --version

# Iniciar sesión
heroku login
```

### Paso 2: Crear la Aplicación en Heroku

```bash
# Navegar a tu directorio del proyecto
cd "C:\Miguel Zuluaga\NetMind"

# Crear aplicación en Heroku
heroku create netmind-app

# O si quieres especificar una región:
heroku create netmind-app --region us
```

**Nota**: Reemplaza `netmind-app` con el nombre que desees para tu aplicación.

### Paso 3: Agregar Buildpacks

Heroku necesita saber cómo construir tu aplicación. Necesitas dos buildpacks:

1. **Node.js** (para construir el frontend)
2. **Python** (para ejecutar el backend)

```bash
# Agregar buildpack de Node.js primero (se ejecutará primero)
heroku buildpacks:add heroku/nodejs

# Agregar buildpack de Python (se ejecutará después)
heroku buildpacks:add heroku/python

# Verificar buildpacks
heroku buildpacks
```

### Paso 4: Agregar Addons (Servicios)

#### PostgreSQL

```bash
# Agregar PostgreSQL (plan gratuito disponible)
heroku addons:create heroku-postgresql:essential-0
```

Esto creará automáticamente la variable `DATABASE_URL` en tu aplicación.

#### Redis

```bash
# Agregar Redis (plan gratuito disponible)
heroku addons:create heroku-redis:mini
```

Esto creará automáticamente la variable `REDIS_URL` en tu aplicación.

**Nota**: Para Qdrant, necesitarás usar Qdrant Cloud o un servicio externo, ya que Heroku no tiene un addon oficial para Qdrant.

### Paso 5: Configurar Variables de Entorno

```bash
# Configurar variables de entorno una por una
heroku config:set OPENAI_API_KEY="tu_api_key_aqui"
heroku config:set EMBEDDING_MODEL="text-embedding-3-large"
heroku config:set LLM_MODEL="gpt-4o-mini"
heroku config:set QDRANT_URL="https://tu-cluster.qdrant.io"
heroku config:set QDRANT_API_KEY="tu_api_key_qdrant"
heroku config:set APP_ENV="production"
heroku config:set APP_NAME="NetMind"
heroku config:set SECRET_KEY="genera_una_clave_secreta_segura_aqui"
heroku config:set UPLOAD_DIR="./databases/uploads"
heroku config:set CHUNK_SIZE="500"
heroku config:set CHUNK_OVERLAP="50"
heroku config:set RAGAS_ENABLED="true"

# O configurar todas a la vez desde un archivo .env (más fácil)
# Primero crea un archivo .env.heroku con tus variables
# Luego:
heroku config:set $(cat .env.heroku | xargs)
```

**Alternativa**: Puedes configurar las variables desde el dashboard de Heroku:
1. Ve a [dashboard.heroku.com](https://dashboard.heroku.com)
2. Selecciona tu aplicación
3. Ve a **Settings** > **Config Vars**
4. Agrega cada variable manualmente

### Paso 6: Configurar Qdrant

Como Heroku no tiene un addon para Qdrant, tienes dos opciones:

#### Opción A: Qdrant Cloud (Recomendado)

1. Ve a [cloud.qdrant.io](https://cloud.qdrant.io)
2. Crea una cuenta y un cluster
3. Obtén la URL y API key
4. Configúralas en Heroku:

```bash
heroku config:set QDRANT_URL="https://tu-cluster.qdrant.io"
heroku config:set QDRANT_API_KEY="tu_api_key"
```

#### Opción B: Qdrant en otro servicio

Puedes desplegar Qdrant en Railway, Render, o cualquier otro servicio y usar su URL.

### Paso 7: Preparar el Repositorio

Asegúrate de que todos los cambios estén en Git:

```bash
# Verificar estado
git status

# Agregar archivos nuevos
git add .

# Commit (si hay cambios)
git commit -m "Preparar para despliegue en Heroku"

# Push a GitHub
git push origin main
```

### Paso 8: Configurar el Remoto de Heroku

```bash
# Agregar Heroku como remoto (si no se agregó automáticamente)
heroku git:remote -a netmind-app

# Verificar remotos
git remote -v
```

### Paso 9: Desplegar la Aplicación

```bash
# Desplegar a Heroku
git push heroku main

# O si tu rama principal se llama master:
git push heroku master
```

Heroku automáticamente:
1. Detectará los buildpacks
2. Ejecutará `npm install` (gracias al package.json)
3. Ejecutará `npm run build` (gracias al script de build)
4. Instalará las dependencias de Python
5. Iniciará la aplicación usando el Procfile

### Paso 10: Verificar el Despliegue

```bash
# Ver logs en tiempo real
heroku logs --tail

# Abrir la aplicación en el navegador
heroku open

# Verificar el estado
heroku ps
```

### Paso 11: Verificar que Todo Funciona

1. **Backend API**: Visita `https://tu-app.herokuapp.com/docs` (deberías ver la documentación de FastAPI)
2. **Frontend**: Visita `https://tu-app.herokuapp.com` (deberías ver la interfaz de NetMind)
3. **Probar funcionalidad**:
   - Subir un documento PDF
   - Hacer una consulta al agente
   - Verificar que las respuestas funcionan

## 🔄 Actualizaciones Futuras

Para actualizar la aplicación después de hacer cambios:

```bash
# Hacer cambios en tu código
# ...

# Commit y push a GitHub
git add .
git commit -m "Descripción de los cambios"
git push origin main

# Desplegar a Heroku
git push heroku main

# Ver logs
heroku logs --tail
```

## 🛠️ Comandos Útiles de Heroku

```bash
# Ver logs
heroku logs --tail

# Ver variables de entorno
heroku config

# Ver una variable específica
heroku config:get OPENAI_API_KEY

# Actualizar una variable
heroku config:set VARIABLE="nuevo_valor"

# Reiniciar la aplicación
heroku restart

# Abrir la aplicación
heroku open

# Ver procesos corriendo
heroku ps

# Abrir una consola de Python
heroku run python

# Ejecutar un comando en el dyno
heroku run bash

# Ver información de la app
heroku info
```

## 🐛 Solución de Problemas

### Error: "No se pudo detectar un buildpack"

**Solución**: Verifica que los buildpacks estén configurados:
```bash
heroku buildpacks
```

Si faltan, agrégalos:
```bash
heroku buildpacks:add heroku/nodejs
heroku buildpacks:add heroku/python
```

### Error: "Module not found" o errores de dependencias

**Solución**: Verifica que `backend/requirements.txt` tenga todas las dependencias necesarias.

### Error: "Frontend no se muestra"

**Solución**: 
1. Verifica que el build del frontend se completó correctamente
2. Revisa los logs: `heroku logs --tail`
3. Verifica que `backend/frontend_dist` existe después del build
4. Asegúrate de que `APP_ENV=production` esté configurado

### Error: "No se puede conectar a la base de datos"

**Solución**:
1. Verifica que el addon de PostgreSQL esté activo: `heroku addons`
2. Verifica la variable `DATABASE_URL`: `heroku config:get DATABASE_URL`
3. Asegúrate de que la base de datos esté lista: `heroku pg:wait`

### Error: "No se puede conectar a Redis"

**Solución**:
1. Verifica que el addon de Redis esté activo: `heroku addons`
2. Verifica la variable `REDIS_URL`: `heroku config:get REDIS_URL`

### Error: "No se puede conectar a Qdrant"

**Solución**:
1. Verifica que `QDRANT_URL` esté configurada: `heroku config:get QDRANT_URL`
2. Si usas Qdrant Cloud, verifica que la API key sea correcta
3. Prueba la conexión desde tu máquina local

### La aplicación se cae (crashes)

**Solución**:
1. Revisa los logs: `heroku logs --tail`
2. Verifica que todas las variables de entorno estén configuradas
3. Verifica que los servicios (PostgreSQL, Redis, Qdrant) estén accesibles
4. Revisa el Procfile para asegurarte de que el comando sea correcto

## 📊 Monitoreo y Escalado

### Ver Métricas

```bash
# Ver uso de recursos
heroku ps

# Ver métricas detalladas
heroku ps:exec
```

### Escalar la Aplicación

```bash
# Ver dynos actuales
heroku ps

# Escalar a 1 dyno web (gratis)
heroku ps:scale web=1

# Escalar a más dynos (requiere plan de pago)
heroku ps:scale web=2
```

**Nota**: El plan gratuito (Hobby) de Heroku tiene limitaciones:
- Dynos se duermen después de 30 minutos de inactividad
- Solo 1 dyno web
- 550-1000 horas gratis al mes

## 💰 Costos

### Plan Gratuito (Hobby)

- ✅ PostgreSQL: 10,000 filas, 20MB
- ✅ Redis: 25MB
- ✅ 550-1000 horas gratis al mes
- ⚠️ Dynos se duermen después de 30 min de inactividad

### Planes de Pago

- **Eco**: $5/mes - Dynos siempre despiertos
- **Basic**: $7/dyno/mes - Más recursos
- **Standard**: $25-250/dyno/mes - Para producción

## 📚 Recursos Adicionales

- [Documentación de Heroku](https://devcenter.heroku.com/)
- [Buildpacks de Heroku](https://devcenter.heroku.com/articles/buildpacks)
- [Variables de Entorno en Heroku](https://devcenter.heroku.com/articles/config-vars)
- [Addons de Heroku](https://elements.heroku.com/addons)

## ✅ Checklist Final

Antes de considerar el despliegue completo:

- [ ] Aplicación creada en Heroku
- [ ] Buildpacks configurados (Node.js y Python)
- [ ] PostgreSQL addon agregado
- [ ] Redis addon agregado
- [ ] Qdrant configurado (Cloud o externo)
- [ ] Todas las variables de entorno configuradas
- [ ] Código desplegado (`git push heroku main`)
- [ ] Aplicación funcionando (verificar en navegador)
- [ ] Backend API accesible (`/docs`)
- [ ] Frontend cargando correctamente
- [ ] Funcionalidad probada (subir archivo, hacer consulta)

---

¡Felicitaciones! 🎉 Tu aplicación NetMind debería estar funcionando en Heroku.

Si tienes problemas, revisa los logs con `heroku logs --tail` y verifica la sección de solución de problemas arriba.

