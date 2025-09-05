# Softball Stats App

A small web application for tracking softball team hitting stats.  
Built with **Vue 3 + TailwindCSS** (frontend), **FastAPI** (backend), and **MySQL** (database).  
Everything runs in **Docker containers**, deployed on an **AWS Lightsail** instance with a **Caddy reverse proxy** for HTTPS.

## Features

*   Track per-game stats:
    *   at\_bats, hits, singles, doubles, triples, home\_runs, rbis, walks, strikeouts, sac\_flies, hit\_by\_pitches, errors
*   View season totals and calculated metrics (average, slugging, OBP, OPS)
*   Filter by player or game
*   Mobile-friendly UI (Vue + Tailwind)
*   Admin-only endpoints protected with a token
*   Live on [https://softball-stats.casad.net](https://softball-stats.casad.net)

## Architecture

Browser
   ↓
stats.casad.net
   ↓ (HTTPS, auto-certificates via Caddy)
Caddy reverse proxy
   ↓
Nginx (serves Vue build, proxies /api/\*)
   ↓
FastAPI backend (uvicorn workers)
   ↓
External MySQL database
  

*   **Frontend**: Vue 3 + Tailwind, built into static assets and served by Nginx.
*   **Backend**: FastAPI (Python 3.11), with SQLAlchemy ORM.
*   **Database**: External MySQL instance (tables auto-created on first run).
*   **Proxy**: Caddy handles HTTPS certificates and reverse-proxies traffic.
*   **Container orchestration**: Docker Compose.
*   **Hosting**: AWS Lightsail (Ubuntu 22.04).
*   **Auto-restart**: systemd units restart containers on reboot.

## Deployment workflow

1.  Code is stored in GitHub.
2.  Deployment is manual (or via CI/CD later):
    
    ```
    ssh ubuntu@<lightsail-ip>
    cd ~/stacks/softball-stats
    git pull
    docker compose -f docker-compose.prod.yml --env-file .env.prod up -d --build
    ```
    
3.  Caddy auto-renews TLS certs for the domain.
4.  On reboot, systemd units automatically bring stacks back up.

## Development setup

*   Frontend dev server runs on Vite (`localhost:5173`)
*   Backend runs on FastAPI with uvicorn (`localhost:8000`)
*   MySQL via local Docker or an external instance
