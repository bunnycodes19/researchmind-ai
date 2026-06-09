# ResearchMind AI — Frontend

## Structure

```
src/
  app/                    # Next.js App Router pages
    (auth)/               # login, signup
    (dashboard)/          # protected app shell
  components/
    ui/                   # shadcn-style primitives
    layout/               # sidebar, shell
    papers/               # upload zone
    chat/                 # RAG chat panel
  lib/                    # api client, utils
  stores/                 # Zustand (auth, UI)
```

## Pages

| Route | Purpose |
|-------|---------|
| `/` | Landing |
| `/login`, `/signup` | Auth |
| `/dashboard` | Stats & activity |
| `/papers` | Upload & library |
| `/workspace` | RAG chat (ELI5 modes) |
| `/compare` | Multi-paper analysis |
| `/study` | Summaries, flashcards, lit review |
| `/evaluation` | RAGAS docs |
| `/settings` | Profile |

## Run

```bash
npm install
NEXT_PUBLIC_API_URL=http://localhost:8000 npm run dev
```
