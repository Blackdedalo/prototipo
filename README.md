# Prototipo Denuncia Virtual PNP Con IA

Aplicación demostrativa para registrar una denuncia virtual por pérdida de documentos o especies. Incluye asistente IA, formulario por pasos, generación de código, seguimiento público y panel administrativo abierto,ademas se adjunta dos archivos .bat para poder correr el proyecto como cerrarlo.

## Stack

- Backend: FastAPI, SQLAlchemy, SQLite.
- Frontend: React, Vite.
- IA configurable: Google Gemini API, Ollama, LM Studio o modo mock.

## Ejecutar Backend

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env
uvicorn app.main:app --host 127.0.0.1 --port 8010 --reload
```

El backend queda en `http://127.0.0.1:8010`.

## Ejecutar Frontend

```powershell
cd frontend
npm install
npm run dev
```

El frontend queda en `http://127.0.0.1:5173`.

## Configuración IA

Edita `backend/.env`:

```env
AI_PROVIDER=mock
GOOGLE_API_KEY=
GOOGLE_MODEL=gemini-2.5-flash
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.1
LM_STUDIO_BASE_URL=http://localhost:1234/v1
LM_STUDIO_MODEL=local-model
```

Valores aceptados para `AI_PROVIDER`: `mock`, `google`, `ollama`, `lmstudio`.

Comportamiento del asistente:

```env
ASSISTANT_BEHAVIOR=amable
ASSISTANT_MULETILLA=
```

Valores sugeridos para `ASSISTANT_BEHAVIOR`: `amable`, `directo`, `agresivo`, `muletillas`. Si usas `muletillas`, coloca una frase corta en `ASSISTANT_MULETILLA`, por ejemplo `claro que sí`.

## Rutas

- `/`: inicio y chat IA.
- `/denuncia`: registro de denuncia.
- `/seguimiento`: consulta por código.
- `/admin`: panel abierto para ver denuncias y cambiar estados.

## Pruebas

```powershell
cd backend
python -m pytest
```

## Nota

Este proyecto es un prototipo académico. No se integra con RENIEC, PNP real, correo, SMS, firma digital ni certificado digital. El panel administrativo queda sin login por decisión de prototipo.
