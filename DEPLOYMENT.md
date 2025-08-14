# Deployment Guide

This guide covers deploying the Claude Code Dashboard to production environments.

## 🚀 Quick Deploy Options

### Option 1: Docker Compose (Recommended)

```bash
# Clone the repository
git clone <repository-url>
cd claude-code-dashboard

# Copy and configure environment
cp .env.example .env
# Edit .env with your production settings

# Start with Docker Compose
docker-compose up -d

# Check status
docker-compose ps
docker-compose logs -f
```

### Option 2: Manual Deployment

```bash
# Clone and setup
git clone <repository-url>
cd claude-code-dashboard

# Run the deployment script
python start.py
```

## 🔧 Production Configuration

### Environment Variables

Create a `.env` file with production settings:

```env
# Server Configuration
HOST=0.0.0.0
PORT=8000

# Security (IMPORTANT!)
DISABLE_AUTH=false
SECRET_KEY=your-super-secure-secret-key-change-this
DASHBOARD_USERNAME=your-admin-username
DASHBOARD_PASSWORD=your-secure-password

# Logging
LOG_LEVEL=INFO

# CORS (specify your domain)
CORS_ORIGINS=https://your-domain.com,https://api.your-domain.com

# Optional: Database URL (if implemented)
# DATABASE_URL=postgresql://user:pass@localhost/claude_dashboard
```

### Security Checklist

- [ ] ✅ **Change default credentials**
- [ ] ✅ **Use strong SECRET_KEY** (generate with `python -c "import secrets; print(secrets.token_urlsafe(32))"`)
- [ ] ✅ **Enable authentication** (`DISABLE_AUTH=false`)
- [ ] ✅ **Configure CORS** with your domain
- [ ] ✅ **Use HTTPS** in production
- [ ] ✅ **Regular security updates**

## 🐳 Docker Deployment

### Production Docker Compose

```yaml
version: '3.8'

services:
  dashboard-backend:
    image: claude-dashboard-backend:latest
    ports:
      - "8000:8000"
    environment:
      - HOST=0.0.0.0
      - PORT=8000
      - DISABLE_AUTH=false
      - SECRET_KEY=${SECRET_KEY}
      - DASHBOARD_USERNAME=${DASHBOARD_USERNAME}
      - DASHBOARD_PASSWORD=${DASHBOARD_PASSWORD}
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock:ro
      - ./data:/app/data
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/api/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  dashboard-frontend:
    image: claude-dashboard-frontend:latest
    ports:
      - "3000:80"
    environment:
      - VITE_API_URL=https://api.your-domain.com
    depends_on:
      - dashboard-backend
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost/"]
      interval: 30s
      timeout: 10s
      retries: 3

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - dashboard-frontend
      - dashboard-backend
    restart: unless-stopped
```

### Build Images

```bash
# Build backend
docker build -t claude-dashboard-backend:latest ./backend

# Build frontend
docker build -t claude-dashboard-frontend:latest ./frontend
```

## 🌐 Reverse Proxy Setup

### Nginx Configuration

```nginx
server {
    listen 80;
    server_name your-domain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name your-domain.com;

    ssl_certificate /etc/nginx/ssl/cert.pem;
    ssl_certificate_key /etc/nginx/ssl/key.pem;

    # Frontend
    location / {
        proxy_pass http://dashboard-frontend:80;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Backend API
    location /api/ {
        proxy_pass http://dashboard-backend:8000/api/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # WebSocket support (if needed)
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

## ☁️ Cloud Deployment

### AWS ECS

1. **Create ECR repositories**
2. **Push Docker images to ECR**
3. **Create ECS task definitions**
4. **Deploy to ECS service**

### Google Cloud Run

```bash
# Build and deploy backend
gcloud run deploy claude-dashboard-backend \
  --image gcr.io/PROJECT-ID/claude-dashboard-backend \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated

# Build and deploy frontend
gcloud run deploy claude-dashboard-frontend \
  --image gcr.io/PROJECT-ID/claude-dashboard-frontend \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

### DigitalOcean App Platform

Create `app.yaml`:

```yaml
name: claude-dashboard
services:
- name: backend
  source_dir: backend
  github:
    repo: your-username/claude-dashboard
    branch: main
  run_command: python main.py
  environment_slug: python
  instance_count: 1
  instance_size_slug: basic-xxs
  envs:
  - key: DISABLE_AUTH
    value: "false"
  - key: SECRET_KEY
    value: ${SECRET_KEY}

- name: frontend
  source_dir: frontend
  github:
    repo: your-username/claude-dashboard
    branch: main
  build_command: npm run build
  run_command: npx serve -s build
  environment_slug: node-js
  instance_count: 1
  instance_size_slug: basic-xxs
```

## 📊 Monitoring & Logging

### Health Checks

- **Backend**: `GET /api/health`
- **Frontend**: `GET /`
- **Docker**: Built-in health checks

### Logging

```bash
# View logs
docker-compose logs -f

# Backend logs
docker-compose logs backend

# Frontend logs
docker-compose logs frontend
```

### Monitoring

Recommended monitoring tools:
- **Prometheus + Grafana**
- **ELK Stack** (Elasticsearch, Logstash, Kibana)
- **Cloud provider monitoring** (CloudWatch, Stackdriver)

## 🔄 Updates & Maintenance

### Update Process

```bash
# Pull latest code
git pull origin main

# Rebuild and restart
docker-compose down
docker-compose build
docker-compose up -d
```

### Backup

```bash
# Backup data directory
tar -czf backup-$(date +%Y%m%d).tar.gz data/

# Backup database (if applicable)
# pg_dump claude_dashboard > backup-db-$(date +%Y%m%d).sql
```

### Database Migrations

```bash
# If using database (future feature)
# python manage.py migrate
```

## 🛠️ Troubleshooting

### Common Issues

1. **Docker socket permission denied**
   ```bash
   sudo usermod -aG docker $USER
   # Then logout and login
   ```

2. **Port already in use**
   ```bash
   # Change ports in docker-compose.yml
   ports:
     - "8001:8000"  # Use different host port
   ```

3. **Authentication not working**
   - Check `DISABLE_AUTH=false`
   - Verify `SECRET_KEY` is set
   - Check credentials

4. **CORS errors**
   - Update `CORS_ORIGINS` environment variable
   - Include your domain in the list

### Logs

```bash
# Application logs
docker-compose logs -f dashboard-backend

# System logs
journalctl -u docker
```

## 📞 Support

- **Documentation**: Check README.md
- **Issues**: GitHub Issues
- **Security**: See SECURITY.md
- **Contributing**: See CONTRIBUTING.md

---

**Happy Deploying!** 🚀