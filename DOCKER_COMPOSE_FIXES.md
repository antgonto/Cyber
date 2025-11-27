# Docker Compose Issues Fixed for PyCharm

## 🔧 Issues Found & Fixed

### 1. **Missing `version` Field**
**Issue**: Modern Docker Compose files should specify a version for compatibility with PyCharm's Docker integration.

**Fixed**: Added `version: '3.8'` at the top of the file.

### 2. **Healthcheck Syntax Error**
**Issue**: The healthcheck command was using shell syntax that PyCharm's validator might flag.
```yaml
# Before (problematic)
test: curl --fail http://django:8000/app/v1/cyber/docs || exit 1

# After (fixed)
test: ["CMD", "curl", "--fail", "http://localhost:8000/app/v1/cyber/docs"]
interval: 30s
timeout: 10s
retries: 3
start_period: 40s
```

### 3. **Environment Variable Conflicts**
**Issue**: Redis was using both `environment` and `env_file`, with `${REDIS_PASSWORD}` not being escaped properly in the command.

**Fixed**: 
- Removed duplicate `environment` section
- Escaped variable in command: `$${REDIS_PASSWORD}`
- Now only uses `env_file: - ./.env`

### 4. **Missing Volume Mounts for Cyber IDS**
**Issue**: The Cyber IDS module needs access to `data/` and `artifacts/` directories for training and model storage.

**Fixed**: Added volume mounts to both `entrypoint` and `django` services:
```yaml
volumes:
  - .:/code
  - ./data:/code/data
  - ./artifacts:/code/artifacts
```

### 5. **Wrong Frontend API URL**
**Issue**: Frontend was pointing to `/api` instead of the correct Cyber IDS endpoint `/app/v1/cyber`.

**Fixed**:
```yaml
# Before
- REACT_APP_API_URL=http://django:8000/api

# After
- REACT_APP_API_BASE_URL=http://django:8000/app/v1/cyber
```

---

## ✅ How to Run in PyCharm

### Method 1: Using PyCharm's Docker Integration (Recommended)

1. **Open Docker Compose File**
   - In PyCharm, navigate to `docker-compose.yml`
   - You should see green play buttons in the gutter

2. **Run All Services**
   - Click the green play button next to `services:`
   - Or right-click `docker-compose.yml` → **Run 'docker-compose.yml'**

3. **Run Individual Service**
   - Click the green play button next to a specific service (e.g., `django:`)
   - Useful for testing one service at a time

4. **View Logs**
   - After starting, PyCharm's **Services** panel opens automatically
   - Expand **Docker Compose** → **cyber** → service name to view logs

### Method 2: Using PyCharm Terminal

```bash
# From project root in PyCharm terminal
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### Method 3: Using Run Configuration

1. **Create Run Configuration**
   - Run → Edit Configurations
   - Click `+` → Docker → Docker-compose
   - Service: Select `all` or specific service
   - Compose files: Browse to `docker-compose.yml`
   - Click OK

2. **Run**
   - Select the configuration from dropdown
   - Click green play button in toolbar

---

## 🚀 Quick Start Commands

### Start All Services
```bash
docker-compose up -d
```

### View Logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f django
```

### Check Status
```bash
docker-compose ps
```

### Stop Services
```bash
docker-compose down
```

### Rebuild After Code Changes
```bash
docker-compose up -d --build
```

---

## 🔍 Verify Services Are Running

### 1. Check Containers
```bash
docker ps
```

Expected output:
```
CONTAINER ID   IMAGE              STATUS    PORTS
...            cyber_django       Up        0.0.0.0:8000->8000/tcp
...            cyber_frontend     Up        0.0.0.0:3000->80/tcp
...            postgres:17.4      Up        0.0.0.0:5432->5432/tcp
...            redis:8.0          Up
```

### 2. Test Backend API
```bash
# Health check
curl http://localhost:8000/app/v1/cyber/ml/health

# Swagger docs
open http://localhost:8000/app/v1/cyber/docs
```

### 3. Test Frontend
```bash
open http://localhost:3000
```

---

## 🐛 Troubleshooting

### Issue: "Cannot connect to Docker daemon"
**Solution**: 
1. Start Docker Desktop
2. Wait for it to fully start (green icon in system tray)
3. Try again in PyCharm

### Issue: "Port already in use"
**Solution**:
```bash
# Find what's using the port
netstat -ano | findstr :8000

# Stop conflicting process or change port in docker-compose.yml
```

### Issue: "Build failed"
**Solution**:
```bash
# Clean rebuild
docker-compose down -v
docker-compose build --no-cache
docker-compose up -d
```

### Issue: ".env file not found"
**Solution**:
Create `.env` file in project root with:
```env
POSTGRES_USERNAME=cyber_user
POSTGRES_PASSWORD=your_password
POSTGRES_DATABASE=cyber_db
POSTGRES_HOST=cyber_db
POSTGRES_PORT=5432
REDIS_PASSWORD=your_redis_password
REDIS_PORT=6379
```

### Issue: PyCharm doesn't recognize docker-compose.yml
**Solution**:
1. Install **Docker** plugin in PyCharm
   - File → Settings → Plugins
   - Search "Docker"
   - Install and restart
2. Configure Docker connection
   - File → Settings → Build, Execution, Deployment → Docker
   - Click `+` → Docker for Windows/Mac
   - Test connection

---

## 📊 Service Dependencies

```
cyber_db (PostgreSQL)
    ↓
redis
    ↓
entrypoint (runs migrations/setup)
    ↓
django (backend API)
    ↓
frontend (React UI)
```

Services start in this order automatically via `depends_on`.

---

## 🎯 What Changed in docker-compose.yml

| Change | Reason | Impact |
|--------|--------|--------|
| Added `version: '3.8'` | PyCharm compatibility | Better IDE integration |
| Fixed healthcheck syntax | Proper Docker format | Reliable health checks |
| Added volume mounts | Cyber IDS needs data/artifacts | Training and models work |
| Fixed Redis env vars | Avoid conflicts | Redis starts properly |
| Fixed frontend API URL | Match Cyber IDS endpoints | Frontend connects correctly |
| Improved healthcheck params | More reliable checks | Better startup detection |

---

## ✅ Success Checklist

After running `docker-compose up -d`:

- [ ] All containers show as "Up" in `docker ps`
- [ ] Backend health check passes: `curl localhost:8000/app/v1/cyber/ml/health`
- [ ] Swagger docs load: http://localhost:8000/app/v1/cyber/docs
- [ ] Frontend loads: http://localhost:3000
- [ ] Database is accessible (check Django logs)
- [ ] No error messages in `docker-compose logs`

---

## 📞 Still Having Issues?

1. **Check PyCharm Docker Plugin**:
   - Settings → Plugins → search "Docker"
   - Ensure it's installed and enabled

2. **Check Docker Desktop**:
   - Ensure Docker Desktop is running
   - Check for updates

3. **Check .env file**:
   - Ensure all required variables are set
   - No syntax errors in .env

4. **Clean Start**:
   ```bash
   docker-compose down -v
   docker system prune -f
   docker-compose up -d --build
   ```

5. **View Detailed Logs**:
   ```bash
   docker-compose logs -f django
   ```

---

*Fixed: November 25, 2025*  
*Docker Compose v3.8 compatible*  
*Ready for PyCharm! ✅*

