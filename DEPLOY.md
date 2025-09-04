# Softball Stats App — Production Deployment Guide

## Goals

*   Single docker-compose for production (no Vite dev server)
*   Web (Vue build) served by Nginx, proxying `/api` → FastAPI
*   API served by Gunicorn + Uvicorn workers
*   MySQL with persistent volume
*   Separate `.env.prod` for production settings
*   Simple MySQL backup plan

- - -

## 1) API base URL in frontend

_web/src/api.ts_:

```ts
import axios from "axios";

// In prod we’ll set VITE_API_BASE to "/api" (Nginx proxy).
// In dev it’ll fall back to http://localhost:8000.
const BASE = import.meta.env.VITE_API_BASE || "http://localhost:8000";

export const api = axios.create({
  baseURL: BASE,
  timeout: 8000,
});
```

Create Vite env files:

_web/.env.development_

```
VITE_API_BASE=http://localhost:8000
```

_web/.env.production_

```
VITE_API_BASE=/api
```

- - -

## 2) Production Dockerfile for web

_web/Dockerfile.prod_

```dockerfile
FROM node:20-alpine AS build
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM nginx:1.27-alpine
COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=build /app/dist /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

_web/nginx.conf_

```nginx
server {
  listen 80;
  server_name _;
  root /usr/share/nginx/html;
  index index.html;

  # Proxy API calls to FastAPI service
  location /api/ {
    proxy_pass         http://api:8000/;
    proxy_http_version 1.1;
    proxy_set_header   Upgrade $http_upgrade;
    proxy_set_header   Connection "upgrade";
    proxy_set_header   Host $host;
    proxy_set_header   X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header   X-Forwarded-Proto $scheme;
  }

  # History API fallback for SPA routes
  location / {
    try_files $uri $uri/ /index.html;
  }
}
```

- - -

## 3) Gunicorn for API

Command:

```
gunicorn app.main:app -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8000 --workers 2 --threads 4 --timeout 60
```

- - -

## 4) docker-compose.prod.yml

```yaml
version: "3.9"

services:
  db:
    image: mysql:8.0
    container_name: softball_db
    env_file: .env.prod
    environment:
      - MYSQL_DATABASE
      - MYSQL_USER
      - MYSQL_PASSWORD
      - MYSQL_ROOT_PASSWORD
    volumes:
      - db_data:/var/lib/mysql
    command: --default-authentication-plugin=mysql_native_password
    healthcheck:
      test: ["CMD", "mysqladmin", "ping", "-h", "localhost", "-p${MYSQL_ROOT_PASSWORD}"]
      interval: 5s
      timeout: 5s
      retries: 20
    restart: unless-stopped

  api:
    build:
      context: ./api
      dockerfile: Dockerfile
    container_name: softball_api
    env_file: .env.prod
    environment:
      DATABASE_URL: "mysql+pymysql://${MYSQL_USER}:${MYSQL_PASSWORD}@${MYSQL_HOST:-db}:${MYSQL_PORT:-3306}/${MYSQL_DATABASE}"
      ADMIN_TOKEN: ${ADMIN_TOKEN}
      API_CORS_ORIGINS: ${API_CORS_ORIGINS}
    command: >
      sh -lc 'gunicorn app.main:app -k uvicorn.workers.UvicornWorker
              -b 0.0.0.0:8000 --workers 2 --threads 4 --timeout 60'
    depends_on:
      db:
        condition: service_healthy
    expose:
      - "8000"
    restart: unless-stopped

  web:
    build:
      context: ./web
      dockerfile: Dockerfile.prod
    container_name: softball_web
    env_file: .env.prod
    ports:
      - "${WEB_PORT:-80}:80"
    depends_on:
      - api
    restart: unless-stopped

volumes:
  db_data:
```

- - -

## 5) .env.prod

```
MYSQL_HOST=db
MYSQL_PORT=3306
MYSQL_DATABASE=softball
MYSQL_USER=softball
MYSQL_PASSWORD=softballpw
MYSQL_ROOT_PASSWORD=change-me-root

API_CORS_ORIGINS=https://stats.example.com
ADMIN_TOKEN=change-me-admin

WEB_PORT=8080
```

- - -

## 6) Build & Run

```
docker compose -f docker-compose.prod.yml --env-file .env.prod up -d --build
```

*   Web: `http://localhost:8080`
*   API proxied via `/api`

- - -

## 7) HTTPS

Put Caddy, Traefik, or Nginx in front to terminate TLS.

Example Caddyfile:

```
stats.example.com {
  reverse_proxy 127.0.0.1:8080
}
```

- - -

## 8) Backups

**Manual dump:**

```
docker compose -f docker-compose.prod.yml exec db \
  sh -lc 'mysqldump -u root -p"$MYSQL_ROOT_PASSWORD" --databases "$MYSQL_DATABASE"' \
  > softball-$(date +%F).sql
```

**Restore:**

```
docker compose -f docker-compose.prod.yml exec -T db \
  sh -lc 'mysql -u root -p"$MYSQL_ROOT_PASSWORD"' \
  < softball-2025-08-27.sql
```

**Cron (daily 2:05 AM):**

```
5 2 * * * cd /path/to/softball-stats && docker compose -f docker-compose.prod.yml exec -T db sh -lc 'mysqldump -u root -p"$MYSQL_ROOT_PASSWORD" --databases "$MYSQL_DATABASE"' > /path/to/backups/softball-$(date +\%F).sql
```

- - -

## 9) Checklist

*   SPA loads at `http://localhost:8080`
*   API reachable via `/api` proxy
*   Login with `ADMIN_TOKEN` works
*   DB backups tested
*   If TLS fronted, site runs at `https://stats.example.com`