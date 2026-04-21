cd# Cuemath Social Media Studio

An MVP studio for turning a rough social media idea into an editable, on-brand creative.

## Stack

- `FastAPI` for generation and rendering APIs
- `React + Vite` for the studio UI
- `OpenAI API` for text expansion and slide regeneration
- `Pillow` for preview rendering

## Project Structure

```text
backend/
  app/
    config.py
    main.py
    prompts.py
    renderer.py
    schemas.py
    services/openai_service.py
frontend/
  src/
    App.jsx
    api.js
    styles.css
```

## Backend Setup

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
uvicorn app.main:app --reload
```

## Frontend Setup

```bash
cd frontend
npm install
copy .env.example .env
npm run dev
```

Open `http://localhost:5173`.

## Notes

- Keep the real `OPENAI_API_KEY` only in `backend/.env`.
- The app still works without an API key by using mock generation so you can demo the workflow first.
- Current preview export is rendered on the backend with Pillow. A future version can switch to richer HTML-to-image rendering for more polished layouts.
