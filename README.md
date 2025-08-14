# Claude Code Dashboard

A comprehensive web application for managing and interacting with multiple Claude Code instances. This dashboard provides a modern, mobile-friendly interface for managing both local and Docker-containerized Claude Code instances, with secure remote access via Tailscale.

![Claude Code Dashboard](https://img.shields.io/badge/Status-Production%20Ready-brightgreen)
![Python](https://img.shields.io/badge/Python-3.11+-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green)
![React](https://img.shields.io/badge/React-18+-blue)
![Docker](https://img.shields.io/badge/Docker-Ready-blue)

## 🚀 Features

### Core Functionality
- **Multi-Instance Management**: Manage multiple Claude Code instances from a single dashboard
- **Real-time Chat Interface**: Interactive chat with individual Claude Code instances
- **Docker Integration**: Automatic discovery and management of Docker containers
- **Mobile-Friendly Design**: Responsive UI optimized for mobile devices
- **Remote Access**: Secure access via Tailscale for mobile management

### Instance Management
- ✅ Add, edit, and remove Claude Code instances
- ✅ Health monitoring and status indicators
- ✅ Support for both local and Docker instances
- ✅ Automatic Docker container discovery
- ✅ Container lifecycle management (start/stop)

### Chat Features
- ✅ Real-time messaging with Claude Code instances
- ✅ Chat history persistence and management
- ✅ Message search and export (JSON/TXT)
- ✅ Copy-to-clipboard functionality
- ✅ Error handling and retry mechanisms

### Security & Access
- ✅ Token-based authentication for remote access
- ✅ Configurable authentication (can be disabled for local development)
- ✅ CORS support for cross-origin requests
- ✅ Secure Docker socket access

## 📋 Requirements

### System Requirements
- **Python 3.11+** for the backend
- **Node.js 18+** for the frontend
- **Docker** (optional, for container management)
- **Modern web browser** with JavaScript support

### Network Requirements
- **Local Access**: Backend on port 8000, Frontend on port 3000
- **Remote Access**: Tailscale network for mobile/remote access
- **Claude Code Instances**: Accessible on configured ports (typically 8000, 8080, etc.)

## 🛠️ Installation & Setup

### Option 1: Local Development Setup

#### 1. Clone the Repository
```bash
git clone <repository-url>
cd claude-code-ui
```

#### 2. Backend Setup
```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Copy environment configuration
cp ../.env.example .env

# Edit .env file with your settings
# For development, you can set DISABLE_AUTH=true
```

#### 3. Frontend Setup
```bash
# Navigate to frontend directory
cd ../frontend

# Install dependencies
npm install

# Copy environment configuration (optional)
cp .env.example .env.local
```

#### 4. Start the Application
```bash
# Terminal 1 - Start Backend
cd backend
python main.py

# Terminal 2 - Start Frontend
cd frontend
npm run dev
```

#### 5. Access the Application
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

### Option 2: Docker Setup

#### 1. Using Docker Compose (Recommended)
```bash
# Clone repository
git clone <repository-url>
cd claude-code-ui

# Copy and configure environment
cp .env.example .env
# Edit .env file with your settings

# Start the application
docker-compose up -d

# View logs
docker-compose logs -f
```

#### 2. Manual Docker Build
```bash
# Build backend
cd backend
docker build -t claude-dashboard-backend .

# Build frontend
cd ../frontend
docker build -t claude-dashboard-frontend .

# Run containers
docker run -d -p 8000:8000 \
  --name dashboard-backend \
  -v /var/run/docker.sock:/var/run/docker.sock:ro \
  claude-dashboard-backend

docker run -d -p 3000:80 \
  --name dashboard-frontend \
  --link dashboard-backend \
  claude-dashboard-frontend
```

### Option 3: Production Deployment

#### Environment Configuration
```bash
# Copy environment template
cp .env.example .env

# Edit configuration for production
nano .env
```

**Important Production Settings:**
- Set `DISABLE_AUTH=false`
- Change `SECRET_KEY` to a strong random string
- Update `DASHBOARD_USERNAME` and `DASHBOARD_PASSWORD`
- Set appropriate `CORS_ORIGINS`
- Configure `VITE_API_URL` for your domain

#### Using Docker Compose (Production)
```bash
# Start in production mode
docker-compose -f docker-compose.yml up -d

# Or with custom environment
docker-compose --env-file .env.production up -d
```

## 🔧 Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `HOST` | `0.0.0.0` | Host to bind the backend server |
| `PORT` | `8000` | Port for the backend server |
| `DISABLE_AUTH` | `false` | Disable authentication (development only) |
| `SECRET_KEY` | `claude-code-dashboard-secret-key` | JWT secret key |
| `DASHBOARD_USERNAME` | `admin` | Default admin username |
| `DASHBOARD_PASSWORD` | `claude-dashboard` | Default admin password |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `1440` | Token expiration time (24 hours) |

### Authentication

The dashboard supports two authentication modes:

#### Development Mode (Authentication Disabled)
```bash
# In .env file
DISABLE_AUTH=true
```

#### Production Mode (Authentication Enabled)
```bash
# In .env file
DISABLE_AUTH=false
SECRET_KEY=your-strong-secret-key
DASHBOARD_USERNAME=your-username
DASHBOARD_PASSWORD=your-secure-password
```

### Tailscale Setup for Remote Access

1. **Install Tailscale** on your server and mobile devices
2. **Configure the backend** to bind to `0.0.0.0` (default)
3. **Access the dashboard** using your Tailscale IP: `http://tailscale-ip:3000`

## 📱 Usage Guide

### Adding Claude Code Instances

#### Manual Addition
1. Click **"Add Instance"** on the dashboard
2. Fill in the instance details:
   - **Name**: Descriptive name for the instance
   - **Type**: Local or Docker
   - **Host**: IP address or hostname
   - **Port**: Port number (usually 8000)
3. Click **"Create Instance"**

#### Docker Discovery
1. Click **"Discover Docker"** on the dashboard
2. The system will automatically find running Claude Code containers
3. New instances will be added automatically

### Using the Chat Interface

1. **Select an instance** from the dashboard
2. **Type your message** in the input field
3. **Press Enter** or click the send button
4. **View responses** in real-time
5. **Copy messages** by hovering and clicking the copy icon
6. **Export chat history** using the export buttons

### Managing Instances

- **Health Check**: Click the clock icon to check instance status
- **Edit**: Click the menu (⋮) and select "Edit"
- **Delete**: Click the menu (⋮) and select "Delete"
- **Direct Access**: Click "Open Direct" to access the instance directly

### Docker Container Management

For Docker instances, you can:
- **Start containers**: Click the play button
- **Stop containers**: Click the stop button
- **View container info**: Check the instance details panel

## 🔍 API Reference

The backend provides a comprehensive REST API. Access the interactive documentation at:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Key Endpoints

#### Instances
- `GET /api/instances` - List all instances
- `POST /api/instances` - Create new instance
- `GET /api/instances/{id}` - Get specific instance
- `PUT /api/instances/{id}` - Update instance
- `DELETE /api/instances/{id}` - Delete instance
- `POST /api/instances/{id}/health` - Health check

#### Chat
- `POST /api/chat/send` - Send message to instance
- `GET /api/chat/history/{instance_id}` - Get chat history
- `DELETE /api/chat/history/{instance_id}` - Clear chat history
- `GET /api/chat/export/{instance_id}` - Export chat history

#### Docker
- `GET /api/docker/status` - Docker daemon status
- `GET /api/docker/containers` - List containers
- `POST /api/docker/containers/{id}/start` - Start container
- `POST /api/docker/containers/{id}/stop` - Stop container

## 🛠️ Development

### Backend Development

```bash
cd backend

# Install development dependencies
pip install -r requirements.txt pytest pytest-asyncio

# Run tests
pytest

# Start with auto-reload
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Format code
black .
isort .
```

### Frontend Development

```bash
cd frontend

# Start development server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview

# Lint code
npm run lint
```

### Project Structure

```
claude-code-ui/
├── backend/                 # FastAPI backend
│   ├── main.py             # Main application
│   ├── auth.py             # Authentication system
│   ├── claude_client.py    # Claude Code API client
│   ├── docker_manager.py   # Docker integration
│   ├── models/             # Data models
│   ├── routers/            # API endpoints
│   └── services/           # Business logic
├── frontend/               # React frontend
│   ├── src/
│   │   ├── api/           # API client
│   │   ├── components/    # React components
│   │   ├── pages/         # Page components
│   │   └── styles/        # CSS styles
│   ├── package.json
│   └── vite.config.js
├── docker-compose.yml      # Docker orchestration
├── requirements.txt        # Python dependencies
└── README.md              # This file
```

## 🔒 Security Considerations

### Production Security
- **Change default credentials** immediately
- **Use strong SECRET_KEY** for JWT tokens
- **Enable authentication** (`DISABLE_AUTH=false`)
- **Use HTTPS** in production environments
- **Restrict CORS origins** to your domain
- **Keep dependencies updated**

### Docker Security
- **Read-only Docker socket** mount for container discovery
- **Non-root user** in Docker containers
- **Network isolation** using Docker networks
- **Regular security updates** for base images

### Access Control
- **Authentication required** for remote access
- **JWT tokens** with expiration
- **Rate limiting** on API endpoints (recommended)
- **Input validation** on all endpoints

## 🐛 Troubleshooting

### Common Issues

#### Backend Won't Start
```bash
# Check Python version
python --version  # Should be 3.11+

# Check dependencies
pip install -r requirements.txt

# Check port availability
netstat -an | grep 8000
```

#### Frontend Build Fails
```bash
# Clear cache and reinstall
rm -rf node_modules package-lock.json
npm install

# Check Node version
node --version  # Should be 18+
```

#### Docker Discovery Not Working
```bash
# Check Docker daemon
docker info

# Check socket permissions
ls -la /var/run/docker.sock

# On Windows/macOS, ensure Docker Desktop is running
```

#### Can't Connect to Claude Code Instances
1. **Check instance status** in the dashboard
2. **Verify host/port** configuration
3. **Test direct connection**: `curl http://host:port/health`
4. **Check firewall settings**
5. **Verify Claude Code is running**

### Logging

Check application logs for detailed error information:

```bash
# Backend logs
tail -f claude_dashboard.log

# Docker logs
docker-compose logs -f dashboard-backend
docker-compose logs -f dashboard-frontend

# Browser console
# Open browser dev tools (F12) and check Console tab
```

## 🤝 Contributing

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature-name`
3. **Make your changes** with proper tests
4. **Run tests**: `pytest` (backend), `npm test` (frontend)
5. **Submit a pull request**

### Development Guidelines
- Follow **PEP 8** for Python code
- Use **TypeScript** for new frontend components
- Add **tests** for new features
- Update **documentation** for API changes
- Follow **conventional commits** format

## 📄 License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **FastAPI** for the excellent async web framework
- **React** for the powerful frontend library
- **Docker** for containerization support
- **Tailwind CSS** for the utility-first CSS framework
- **Lucide React** for the beautiful icons

## 📞 Support

For issues, questions, or contributions:
- **GitHub Issues**: [Create an issue](issues)
- **Documentation**: See this README and API docs
- **Community**: Join our discussions

---

**Built with ❤️ for the Claude Code community**