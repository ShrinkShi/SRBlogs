# Repository Guidelines

## Project Structure & Module Organization

SRBlogs is a Vue 3 + Vite + TypeScript blog system with a FastAPI backend.

- `frontend/`: public reader SPA. Main code is in `frontend/src/` (`views/`, `components/`, `stores/`, `api/`, `styles.css`).
- `admin/`: management SPA with the same Vue/Vite layout under `admin/src/`.
- `backend/`: FastAPI service. Routers live in `backend/app/api/`, service logic in `backend/app/services/`, schemas in `backend/app/models/`, and Markdown/JSON runtime content in `backend/data/`.
- `docs/`: API contracts, deployment notes, QA checklists, and security guidance.
- `deploy/`: nginx, systemd, health check, and Linux deployment scripts.

## Build, Test, and Development Commands

Install dependencies per package:

```powershell
cd frontend; npm install
cd admin; npm install
cd backend; python -m pip install -r requirements.txt
```

- `npm run dev`: start Vite. Frontend uses `127.0.0.1:5173`; admin uses `127.0.0.1:5174`.
- `npm run build`: run `vue-tsc` and produce a production build.
- `npm run lint` / `npm run format`: apply ESLint and Prettier fixes in `src/`.
- `uvicorn app.main:app --reload --host 127.0.0.1 --port 8000`: run the API from `backend/`.
- `start-all.cmd`: start frontend, admin, and backend on Windows.

## Coding Style & Naming Conventions

Use Vue single-file components with TypeScript. Name components in PascalCase, composables as `useX.ts`, stores by domain, and API clients under `src/api/`. Keep Tailwind/CSS changes close to the component or shared `styles.css`.

Python code uses `snake_case`. Keep endpoints thin, move business logic to services, and keep shared request/response models in `backend/app/models/schemas.py` unless a local pattern is clearer.

## Testing Guidelines

No dedicated test suite is currently checked in. Validate with targeted builds and manual QA:

- Run `npm run build` in each affected SPA.
- For backend edits, run `python -m compileall backend/app` from the repo root or start the API and exercise the changed endpoint.
- Use `docs/MANUAL_QA_CHECKLIST.md` and `docs/API_CONTRACT.md` when changes affect public behavior.

Name future tests by behavior, for example `test_comments_login_flow.py` or `PostList.spec.ts`.

## Commit & Pull Request Guidelines

Use short, descriptive commit messages in English or Chinese, for example `Fix display refresh and backend-sorted nearby list` or `重构管理台导航结构并修复历史记录渲染`.

Pull requests should include:

- A concise summary of user-visible changes.
- The commands run for verification.
- Linked issues or context when available.
- Screenshots or screen recordings for UI changes.
- Notes about data migrations, config changes, or deployment impact.

## Security & Configuration Tips

Do not commit OAuth secrets, SMTP secrets, admin tokens, generated backups, or private uploads. Public settings endpoints should expose only non-sensitive status such as `configured: true`. Review `docs/SECURITY_NOTES.md` before changing auth, uploads, updates, or public API responses.
