# GrantBotAI — Local RAG-Driven Grant Application Generator (local MVP version)

## Table of Contents

- [Tech Stack and Tools](#tech-stack-and-tools)
- [Repository Structure](#repository-structure)
- [Local Development & Running Containers](#local-development--running-containers)
- [Key Decisions & Rationale](#key-decisions--rationale)
- [Assumptions](#assumptions)
- [Next Steps & Roadmap](#next-steps--roadmap)


---

## Tech Stack and Tools

- **Python 3.12**
- **FastAPI** — RESTful API
- **MongoDB** — Document data store, seeded with context documents
- **Docker** & **Docker Compose** — Local container orchestration
- **Poetry** — Dependency management
- **OpenRouter** — LLM API (compatible with OpenAI SDK)
- **scikit-learn** — TF-IDF vectorizer, cosine similarity for document ranking
- **Python logging**

---

## Repository Structure

```

├── app/ # Main Python source code
│ ├── init.py
│ ├── config.py # Configuration (env vars, keys)
│ ├── db.py # MongoDB connector
│ ├── logger.py # Project-wide logger setup
│ ├── llm.py # All RAG + LLM logic (OpenRouterLLM class)
│ ├── main.py # FastAPI app entrypoint
│ ├── models.py # Pydantic models for API
│ └── routers/ # API endpoint routers
├── docker/
│ ├── Dockerfile.api # API service Dockerfile
│ ├── Dockerfile.mongo # MongoDB + seeding Dockerfile
│ ├── docker-compose.yml # Orchestration for local containers
│ └── mongo-init/
│ ├── startup.sh # Script for seeding MongoDB with JSONL
│ └── data.jsonl # Seed data (context docs)
├── tests/ # Unit tests for codebase
├── pyproject.toml # Poetry dependency and project config
├── README.md

```

---


---

## Local Development & Running Containers

### Prerequisites

- Docker & Docker Compose
- Python 3.10+
- Poetry (recommended)
- OpenRouter API key

### Quickstart

#### How to Obtain an OpenRouter API Key

1. **Create an Account**
   - Go to [https://openrouter.ai](https://openrouter.ai) and sign up or log in (you can use your email, Google, or MetaMask).

2. **Generate an API Key**
   - After logging in, click on your avatar (top right) and select **Keys** from the menu, or visit [https://openrouter.ai/keys](https://openrouter.ai/keys).
   - Click **Create New Key**.
   - Enter a descriptive name (e.g. `GrantBotDev`), set a limit if you want, and confirm.
   - Copy your new API key now—it won’t be shown again.

3. **Add Your Key to the .env File**
   - Open your project’s `.env` file.
   - Add:
     ```
     OPENROUTER_KEY=sk-...  # Paste your API key here
     OPENROUTER_API_BASE=https://openrouter.ai/api/v1
     ```
   - Never commit keys to public repositories!
   - For this MVP, there is no need to worry about costs, since we are using the free LLM model

## Quick Start

Get GrantBotAI running locally:

1. **Set up your OpenRouter API key**
- Follow the instructions above and configure your `.env` file.

3. **Create your `.env` file**

    ```cp .env.example .env```
    - Edit .env by adding your API key generated in section 1. For this local MVP, **don't change anything else from the env.example**

4. **Build and launch services**

    ```
    make run-local
    ```


---

## Key Decisions & Rationale

| Decision                   | Rationale                                   | Alternatives Considered                      |
|----------------------------|---------------------------------------------|----------------------------------------------|
| MongoDB for context        | Flexible schema, MVP speed                  | SQL, file-based stores                       |
| RAG (TF-IDF)               | No outside embedding, fast on small corpus  | Neural vector DB, slower, more setup, more latency          |
| OpenRouter API             | Free tier, OpenAI-compatible API            | Local HF models, OpenAI (more expensive)     |
| Encapsulation in `llm.py`  | Easier to test, deploy                      | More modules              |
| Docker Compose             | Quick local dev, reproducible               | Manual setup, one Dockerfile                                 |

---

## Assumptions

- Seed docs include `company_id`, `section_type`, and `text`.
- All context selection is per company, ranked by input similarity; section type matches user request.
- LLM model must be available/enabled on your OpenRouter account.
- Secrets/keys always loaded from `.env` and we always use the free LLM model provided by OpenRouter.

---

## Next Steps & Roadmap

- Replace TF-IDF with neural retrieval/vector DB for better ranking.
- Support local LLMs as backend alternative (e.g. HuggingFace).
- Add CI, production deploy scripts, and cloud hosting.
- **Caching:**  
  To speed up frequent or repeated requests, caching can be implemented:
  - Results of document retrieval (top-k contexts) can be cached keyed by `(company_id, section_type, input_text_hash)`.
  - Generated LLM outputs can be cached similarly for repeated prompts.
  - Recommended caching backends include Redis or in-memory caches with TTL expiration.
- **Async Endpoints & IO:**  
  While the MVP uses synchronous endpoints for simplicity and compatibility with mongodb library, **async endpoints** are the industry standard for FastAPI deployments. Migrating to async (using uvicorn w/ async MongoDB drivers like Motor, async HTTP clients for LLM APIs, and async-aware internal logic) enables higher concurrency and lower latency.

---
