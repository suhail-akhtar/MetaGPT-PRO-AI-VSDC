# MetaGPT-PRO Docker Deployment Guide

## Deployment Options

MetaGPT-PRO provides flexible Docker deployment options:

### Option 1: Full-Stack Single Container (Simple)

Run both backend and frontend in a single container:

```bash
# Build the full-stack image
docker build -f Dockerfile.fullstack -t metagpt-pro:latest .

# Run the container
docker run -d \
  -p 3000:3000 \
  -p 8080:8080 \
  -v $(pwd)/workspace:/app/metagpt/workspace \
  --name metagpt-pro \
  metagpt-pro:latest
```

**Access:**
- Frontend: http://localhost:3000
- Backend API: http://localhost:8080/v1

---

### Option 2: Docker Compose (Production)

Run frontend and backend as separate containers with automatic networking:

```bash
# Build and start all services
docker-compose up -d --build

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

**Access:**
- Frontend: http://localhost:3000
- Backend API: http://localhost:8080/v1

---

### Option 3: Frontend Only

If you have an existing backend, build just the frontend:

```bash
cd frontend

# Build with custom API URL
docker build \
  --build-arg NEXT_PUBLIC_API_URL=http://your-api-server:8080/v1 \
  --build-arg NEXT_PUBLIC_WS_URL=ws://your-api-server:8080/v1 \
  -t metagpt-frontend:latest .

# Run frontend
docker run -d \
  -p 3000:3000 \
  --name metagpt-frontend \
  metagpt-frontend:latest
```

---

### Option 4: Backend Only

Run just the backend API:

```bash
# Build backend image
docker build -f Dockerfile.backend -t metagpt-backend:latest .

# Run backend
docker run -d \
  -p 8080:8080 \
  -v $(pwd)/workspace:/app/metagpt/workspace \
  --name metagpt-backend \
  metagpt-backend:latest
```

---

## Environment Variables

### Frontend
| Variable | Default | Description |
|----------|---------|-------------|
| `NEXT_PUBLIC_API_URL` | `http://localhost:8080/v1` | Backend API URL |
| `NEXT_PUBLIC_WS_URL` | `ws://localhost:8080/v1` | WebSocket URL |
| `NEXT_PUBLIC_ENABLE_MOCK` | `false` | Enable mock data |

### Backend
| Variable | Default | Description |
|----------|---------|-------------|
| `METAGPT_LOG_LEVEL` | `INFO` | Log level |
| `PYTHONUNBUFFERED` | `1` | Python output buffering |

---

## Health Checks

**Backend:**
```bash
curl http://localhost:8080/v1/health
```

**Frontend:**
```bash
curl http://localhost:3000
```

---

## Volume Mounts

| Path | Description |
|------|-------------|
| `/app/metagpt/workspace` | Project files and generated code |
| `/app/metagpt/config` | Configuration files (read-only) |

---

## Troubleshooting

### Container won't start
```bash
# Check logs
docker logs metagpt-pro

# Check container status
docker ps -a
```

### Frontend can't connect to backend
1. Verify backend is running: `curl http://localhost:8080/v1/health`
2. Check environment variables are set correctly
3. In docker-compose, use service names (e.g., `http://backend:8080`)

### Build fails
```bash
# Clean build cache
docker builder prune -f

# Rebuild without cache
docker-compose build --no-cache
```
