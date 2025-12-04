# 🔄 Comandos para Desvincular y Re-subir el Repositorio

Esta guía te ayudará a desvincular tu proyecto del repositorio actual y subirlo a un nuevo repositorio.

## 📋 Pasos para Desvincular el Repositorio Actual

### Paso 1: Verificar el Repositorio Actual

```bash
# Ver información del remoto actual
git remote -v

# Ver la URL del repositorio
git remote get-url origin
```

### Paso 2: Desvincular el Repositorio

```bash
# Eliminar el remoto 'origin' (desvincula del repositorio actual)
git remote remove origin

# Verificar que se eliminó
git remote -v
```

**Alternativa**: Si quieres mantener el remoto pero cambiar la URL:

```bash
# Cambiar la URL del remoto (sin eliminar)
git remote set-url origin NUEVA_URL

# O eliminar y agregar de nuevo
git remote remove origin
git remote add origin NUEVA_URL
```

## 📤 Pasos para Subir a un Nuevo Repositorio

### Opción A: Repositorio Nuevo en GitHub (Recomendado)

#### 1. Crear el Repositorio en GitHub

1. Ve a [github.com](https://github.com)
2. Haz clic en **"New repository"** o **"+"** > **"New repository"**
3. Completa:
   - **Repository name**: `NetMind` (o el nombre que prefieras)
   - **Description**: (opcional)
   - **Visibility**: Público o Privado
   - **NO marques** "Initialize this repository with a README" (ya tienes archivos)
4. Haz clic en **"Create repository"**

#### 2. Conectar el Proyecto Local al Nuevo Repositorio

```bash
# Navegar al directorio del proyecto
cd "C:\Miguel Zuluaga\NetMind"

# Agregar el nuevo remoto (reemplaza TU_USUARIO y NOMBRE_REPO)
git remote add origin https://github.com/TU_USUARIO/NOMBRE_REPO.git

# O si prefieres usar SSH:
# git remote add origin git@github.com:TU_USUARIO/NOMBRE_REPO.git

# Verificar que se agregó correctamente
git remote -v
```

#### 3. Subir el Código

```bash
# Verificar el estado actual
git status

# Si hay cambios sin commit, agregarlos
git add .

# Hacer commit si hay cambios pendientes
git commit -m "Preparar para despliegue en Heroku"

# Subir a la rama main (o master)
git branch -M main  # Asegurar que la rama se llama 'main'
git push -u origin main

# Si tu rama se llama 'master' en lugar de 'main':
# git branch -M master
# git push -u origin master
```

### Opción B: Repositorio Existente (Reemplazar Contenido)

Si el repositorio ya existe y quieres reemplazar todo su contenido:

```bash
# Agregar el remoto
git remote add origin https://github.com/TU_USUARIO/NOMBRE_REPO.git

# Forzar el push (⚠️ CUIDADO: Esto sobrescribe el repositorio remoto)
git push -u origin main --force

# O si es master:
# git push -u origin master --force
```

**⚠️ ADVERTENCIA**: `--force` sobrescribe todo en el repositorio remoto. Úsalo solo si estás seguro.

## 🔄 Comandos Útiles Adicionales

### Ver Información del Repositorio

```bash
# Ver todos los remotos
git remote -v

# Ver información detallada del remoto
git remote show origin

# Ver la URL del remoto
git remote get-url origin
```

### Cambiar la URL del Remoto

```bash
# Cambiar la URL del remoto 'origin'
git remote set-url origin https://github.com/TU_USUARIO/NUEVO_REPO.git

# Verificar el cambio
git remote -v
```

### Agregar Múltiples Remotos

```bash
# Agregar un remoto adicional (por ejemplo, para un fork o backup)
git remote add backup https://github.com/TU_USUARIO/BACKUP_REPO.git

# Subir a múltiples remotos
git push origin main
git push backup main
```

### Eliminar un Remoto

```bash
# Eliminar un remoto específico
git remote remove nombre_remoto

# Verificar que se eliminó
git remote -v
```

## 🚀 Después de Subir: Configurar Heroku

Una vez que hayas subido el código al nuevo repositorio:

### 1. Conectar Heroku al Nuevo Repositorio

```bash
# Si ya tienes la app de Heroku creada, actualizar el remoto
heroku git:remote -a NOMBRE_APP_HEROKU

# O crear la app y conectarla
heroku create NOMBRE_APP_HEROKU
```

### 2. Desplegar desde el Nuevo Repositorio

```bash
# Opción 1: Push directo a Heroku
git push heroku main

# Opción 2: Configurar en el Dashboard de Heroku
# 1. Ve a dashboard.heroku.com
# 2. Selecciona tu app
# 3. Ve a Settings > Deploy
# 4. Conecta el nuevo repositorio de GitHub
# 5. Habilita "Automatic deploys"
```

## 📝 Ejemplo Completo: Flujo Completo

```bash
# 1. Verificar estado actual
cd "C:\Miguel Zuluaga\NetMind"
git status
git remote -v

# 2. Desvincular del repositorio actual
git remote remove origin

# 3. Verificar que se eliminó
git remote -v

# 4. Agregar el nuevo remoto (reemplaza con tu URL)
git remote add origin https://github.com/TU_USUARIO/NetMind.git

# 5. Verificar que se agregó
git remote -v

# 6. Asegurar que estás en la rama main
git branch -M main

# 7. Subir el código
git push -u origin main

# 8. Si tienes Heroku configurado, actualizar el remoto
heroku git:remote -a netmind-app

# 9. Desplegar a Heroku
git push heroku main
```

## ⚠️ Solución de Problemas

### Error: "remote origin already exists"

```bash
# Eliminar el remoto existente primero
git remote remove origin

# Luego agregar el nuevo
git remote add origin NUEVA_URL
```

### Error: "fatal: refusing to merge unrelated histories"

```bash
# Si el repositorio remoto tiene contenido diferente, usar:
git pull origin main --allow-unrelated-histories

# O forzar el push (si estás seguro de sobrescribir):
git push -u origin main --force
```

### Error: "authentication failed"

```bash
# Verificar credenciales de GitHub
# En Windows, puedes necesitar actualizar las credenciales:
git config --global credential.helper manager-core

# O usar un token de acceso personal en lugar de contraseña
```

### Error: "branch 'main' does not exist"

```bash
# Crear la rama main si no existe
git branch -M main

# O usar master si prefieres
git branch -M master
git push -u origin master
```

## 🔐 Autenticación con GitHub

### Opción 1: HTTPS con Token Personal (Recomendado)

1. Ve a GitHub > Settings > Developer settings > Personal access tokens > Tokens (classic)
2. Genera un nuevo token con permisos `repo`
3. Usa el token como contraseña cuando Git lo solicite

### Opción 2: SSH

```bash
# Generar clave SSH (si no tienes una)
ssh-keygen -t ed25519 -C "tu_email@example.com"

# Agregar la clave a ssh-agent
eval "$(ssh-agent -s)"
ssh-add ~/.ssh/id_ed25519

# Copiar la clave pública
cat ~/.ssh/id_ed25519.pub

# Agregar la clave en GitHub: Settings > SSH and GPG keys > New SSH key
```

Luego usa la URL SSH:
```bash
git remote add origin git@github.com:TU_USUARIO/NOMBRE_REPO.git
```

## ✅ Checklist

Antes de desvincular:

- [ ] Hacer backup del código (por si acaso)
- [ ] Verificar que todos los cambios están commiteados
- [ ] Verificar el estado con `git status`
- [ ] Anotar la URL del repositorio actual (por si necesitas referencia)

Después de desvincular:

- [ ] Verificar que `git remote -v` no muestra remotos
- [ ] Crear el nuevo repositorio en GitHub
- [ ] Agregar el nuevo remoto
- [ ] Verificar que se agregó correctamente
- [ ] Subir el código
- [ ] Verificar en GitHub que el código se subió
- [ ] Actualizar la conexión de Heroku si es necesario

---

¡Listo! Tu proyecto ahora está en el nuevo repositorio y listo para desplegar en Heroku.

