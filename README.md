# DevNotes

DevNotes is a local, single-user Markdown workspace for developer notes, snippets, and things worth remembering. It pairs a focused three-panel React interface with a FastAPI and SQLite service.

## Features

- Autosaving Markdown notes with editable titles, folders, tags, pinning, and archive/restore.
- Search note titles and content; browse pinned, recent, archived, folder, and tag views.
- Write, split, and rendered preview modes with GFM tables, task lists, and safe fenced code display.
- Keyboard shortcuts: Ctrl/Cmd+N creates a note, Ctrl/Cmd+K focuses search, Ctrl/Cmd+S saves.
- SQLite persistence and a JSON REST API documented at `/docs`.

## Stack and architecture

- Backend: Python 3.11+, FastAPI, SQLAlchemy 2, Pydantic, SQLite.
- Frontend: React, Vite, JavaScript, React Markdown, remark-gfm, Lucide.
- `backend/app`: database setup, SQLAlchemy models, Pydantic schemas, and API routes.
- `backend/tests`: isolated API tests.
- `frontend/src`: workspace UI and visual system.

## Screenshots

No screenshots have been captured yet. Add genuine product screenshots to `screenshots/` before referencing them here.

## Requirements

Python 3.11+ and Node.js 20+ with npm.

## Run on Windows (PowerShell)

In a first terminal:

```powershell
cd devnotes-markdown-notes/backend
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
uvicorn app.main:app --reload
```

In a second terminal:

```powershell
cd devnotes-markdown-notes/frontend
npm install
npm run dev
```

Open http://localhost:5173. The backend API is at http://127.0.0.1:8000 and its interactive documentation is at http://127.0.0.1:8000/docs.

## Configuration and persistence

The default database is `devnotes.db` in the project root. Set `DEVNOTES_DB` to an alternate SQLite path before starting the backend. `.env.example` documents the variable; the application reads process environment variables directly. Tables are initialized on startup. For this MVP, back up notes before manually changing database schema; a migration tool can be added as the schema evolves.

## API

`GET /api/health`; notes use `GET/POST /api/notes`, `GET/PATCH/DELETE /api/notes/{id}`. Listing supports `q`, `folder_id`, `tag`, `pinned`, `archived`, `sort`, `limit`, and `offset`. Folder and tag endpoints are under `/api/folders` and `/api/tags`. Deleting folders unfiles notes; deleting tags removes their assignments, not notes.

## Markdown

The source remains Markdown. Preview uses `react-markdown` and `remark-gfm`, without raw HTML rendering. Standard Markdown links open in a separate tab with `noopener noreferrer`. GFM supports tables, task lists, and strikethrough. Preview keeps fenced code readable; syntax highlighting and one-click code-copy are not currently included.

## Tests and build

```powershell
cd backend
python -m pytest
cd ..\frontend
npm run build
```

## Troubleshooting

- If port 8000 is occupied, run Uvicorn with `--port 8001` and update `frontend/vite.config.js` proxy.
- If PowerShell blocks activation, use `Set-ExecutionPolicy -Scope Process Bypass` for that terminal, then activate the venv again.
- If the API is unreachable, check both server processes and the Vite `/api` proxy.
- To start with a clean local workspace, stop the API and move or back up `devnotes.db`.

## Security and scope

This MVP has no authentication or multi-user data isolation. Keep it on a trusted local machine; do not expose it as a shared service without authentication and proper isolation. Rendered Markdown does not allow arbitrary raw HTML. CORS is limited to the local Vite origins.

## Future improvements

Add syntax-highlighted code blocks with copy controls, robust migration support, richer filtering/sorting controls, and browser-based end-to-end coverage.

## License

MIT. See [LICENSE](LICENSE).
