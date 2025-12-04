# Guía de Instalación - Frontend NetMind

## Prerrequisitos

- Node.js 18+ y npm instalados
- Backend FastAPI corriendo en `http://localhost:8000`

## Pasos de Instalación

### 1. Instalar Dependencias

Desde la carpeta `frontend`:

```bash
cd frontend
npm install
```

### 2. Configurar Variables de Entorno

Crea un archivo `.env` en la raíz de `frontend`:

```env
VITE_API_URL=http://localhost:8000
```

### 3. Verificar Backend

Asegúrate de que el backend FastAPI esté corriendo y tenga CORS configurado. El archivo `main.py` ya incluye la configuración de CORS.

### 4. Iniciar Servidor de Desarrollo

```bash
npm run dev
```

El frontend estará disponible en: `http://localhost:5173`

## Estructura de Carpetas

```
frontend/
├── src/
│   ├── components/      # Componentes React
│   │   ├── ui/         # Componentes base (Button, Input, etc.)
│   │   ├── chat/       # Componentes de chat
│   │   └── layout/     # Layout principal
│   ├── pages/          # Páginas (ChatPage, FilesPage)
│   ├── hooks/          # Custom hooks (useChat)
│   ├── services/       # Servicios API
│   ├── config/         # Configuración (colores, constantes)
│   ├── utils/          # Utilidades
│   └── App.jsx         # Componente principal
├── public/             # Archivos estáticos
├── package.json
├── vite.config.js
└── tailwind.config.js
```

## Comandos Disponibles

- `npm run dev` - Servidor de desarrollo
- `npm run build` - Build para producción
- `npm run preview` - Previsualizar build
- `npm run lint` - Ejecutar linter

## Solución de Problemas

### Error de CORS
Si ves errores de CORS, verifica que:
1. El backend esté corriendo en el puerto 8000
2. El archivo `main.py` tenga la configuración de CORS activa

### Error de conexión
Verifica que:
1. La variable `VITE_API_URL` en `.env` apunte al backend correcto
2. El backend esté accesible

## Personalización

### Colores
Los colores están centralizados en:
- `src/config/colors.js` - Variables JavaScript
- `tailwind.config.js` - Clases de Tailwind

Modifica estos archivos para cambiar el tema.

