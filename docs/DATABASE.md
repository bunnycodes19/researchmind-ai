# Database Design — ResearchMind AI

## ER Diagram (Textual)

```
users ─────────────┬──────────────── papers
    │              │                    │
    │              │                    ├── chunks ── embeddings (faiss_id)
    │              │                    │
    ├── chat_sessions ── messages      │
    │              │                    │
    ├── summaries (paper_id)           │
    ├── study_notes                    │
    ├── flashcards                     │
    ├── literature_reviews             │
    └── evaluations (message_id)       │
                                       │
refresh_tokens (user_id)               │
activity_logs (user_id, optional paper_id)
```

## Tables

### users
| Column | Type | Notes |
|--------|------|-------|
| id | UUID PK | |
| email | VARCHAR UNIQUE | |
| hashed_password | VARCHAR | bcrypt |
| full_name | VARCHAR | |
| is_active | BOOLEAN | default true |
| created_at | TIMESTAMPTZ | |
| updated_at | TIMESTAMPTZ | |

### refresh_tokens
| Column | Type | Notes |
|--------|------|-------|
| id | UUID PK | |
| user_id | UUID FK | |
| token_hash | VARCHAR | |
| expires_at | TIMESTAMPTZ | |
| revoked | BOOLEAN | |

### papers
| Column | Type | Notes |
|--------|------|-------|
| id | UUID PK | |
| user_id | UUID FK | |
| title | VARCHAR | |
| filename | VARCHAR | |
| file_path | VARCHAR | |
| file_size_bytes | BIGINT | |
| page_count | INT | |
| status | ENUM | pending, processing, ready, failed |
| processing_error | TEXT nullable | |
| metadata_json | JSONB | authors, models, datasets, etc. |
| created_at | TIMESTAMPTZ | |

### chunks
| Column | Type | Notes |
|--------|------|-------|
| id | UUID PK | |
| paper_id | UUID FK | |
| chunk_index | INT | |
| content | TEXT | |
| page_number | INT | |
| section_name | VARCHAR | |
| char_start | INT | |
| char_end | INT | |

### embeddings
| Column | Type | Notes |
|--------|------|-------|
| id | UUID PK | |
| chunk_id | UUID FK UNIQUE | |
| faiss_index | INT | position in user FAISS |
| dimension | INT | |

### chat_sessions
| Column | Type | Notes |
|--------|------|-------|
| id | UUID PK | |
| user_id | UUID FK | |
| title | VARCHAR | |
| paper_ids | UUID[] | scope |
| created_at | TIMESTAMPTZ | |

### messages
| Column | Type | Notes |
|--------|------|-------|
| id | UUID PK | |
| session_id | UUID FK | |
| role | VARCHAR | user, assistant, system |
| content | TEXT | |
| citations | JSONB | [{chunk_id, page, excerpt}] |
| confidence | FLOAT nullable | |
| mode | VARCHAR nullable | simple, intermediate, expert |
| created_at | TIMESTAMPTZ | |

### summaries, study_notes, flashcards, literature_reviews
Each has: id, user_id, paper_id(s), content JSONB, created_at.

### evaluations
| Column | Type | Notes |
|--------|------|-------|
| id | UUID PK | |
| message_id | UUID FK | |
| relevance | FLOAT | RAGAS |
| faithfulness | FLOAT | |
| context_precision | FLOAT | |
| context_recall | FLOAT | |
| created_at | TIMESTAMPTZ | |

### activity_logs
| Column | Type | Notes |
|--------|------|-------|
| id | UUID PK | |
| user_id | UUID FK | |
| action | VARCHAR | |
| metadata | JSONB | |
| created_at | TIMESTAMPTZ | |
