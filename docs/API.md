# API Reference — ResearchMind AI

Base URL: `http://localhost:8000/api/v1`

## Auth

| Method | Path | Body | Response |
|--------|------|------|----------|
| POST | `/auth/signup` | `{email, password, full_name}` | `TokenResponse` 201 |
| POST | `/auth/login` | `{email, password}` | `TokenResponse` |
| POST | `/auth/refresh` | `{refresh_token}` | `TokenResponse` |
| POST | `/auth/logout` | Bearer | 204 |
| GET | `/auth/me` | Bearer | `UserResponse` |
| PATCH | `/auth/me` | `{full_name?}` | `UserResponse` |

## Papers

| Method | Path | Notes |
|--------|------|-------|
| GET | `/papers` | List user papers |
| GET | `/papers/{id}` | Paper detail |
| POST | `/papers/upload` | multipart `files[]` |
| DELETE | `/papers/{id}` | Delete paper + vectors |
| POST | `/papers/compare` | `{paper_ids[], question?}` |

## Chat

| Method | Path | Notes |
|--------|------|-------|
| GET | `/chat/sessions` | List sessions |
| POST | `/chat/sessions` | Create `{title?, paper_ids?}` |
| GET | `/chat/sessions/{id}/messages` | Message history |
| POST | `/chat/sessions/{id}/messages` | `{content, mode?, paper_ids?}` → RAG answer |

## Study

| POST | `/study/summary` | `{paper_id}` |
| POST | `/study/generate` | `{paper_id, artifact_type}` |
| POST | `/study/literature-review` | `{paper_ids[]}` |

## Dashboard

| GET | `/dashboard/stats` | Usage metrics |
| GET | `/dashboard/evaluations/{message_id}` | RAGAS scores |

## Health

| GET | `/health` | Liveness |
| GET | `/ready` | Readiness |

All protected routes require `Authorization: Bearer <access_token>`.

Errors: `{ "detail": string, "code"?: string }` with 4xx/5xx status codes.
