# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a **Claude Code Dashboard** - a full-stack web application for managing and interacting with multiple Claude Code instances. It consists of a FastAPI backend with React frontend, designed for both local development and production deployment with Docker support.

**Architecture**: The application provides a unified interface to manage multiple Claude Code instances (both local processes and Docker containers), with real-time chat capabilities, Docker integration, and mobile-friendly remote access via Tailscale.

## Essential Commands

### Quick Start
```bash
# One-command startup (recommended)
python start.py

# Manual backend startup (development)
cd backend && python -m venv venv && source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
python main.py

# Manual frontend startup (development)
cd frontend && npm install && npm run dev

# Docker deployment
docker-compose up -d
```

### Development Commands
```bash
# Backend development
cd backend
python main.py                    # Start with auto-reload
pytest                           # Run backend tests
uvicorn main:app --reload        # Alternative startup with uvicorn

# Frontend development
cd frontend
npm run dev                      # Start development server
npm run build                    # Build for production
npm run preview                  # Preview production build
npm run lint                     # Lint code

# Docker operations
docker-compose up dashboard-backend dashboard-frontend  # Start only dashboard
docker-compose --profile example up                     # Include example Claude instance
docker-compose logs -f dashboard-backend                # View backend logs
```

### Testing & Quality
```bash
# Backend testing
cd backend && python -m pytest tests/ -v            # Run all tests
cd backend && python -m pytest tests/test_main.py   # Run specific test file
cd backend && python -m pytest --cov=. --cov-report=term-missing  # With coverage

# Frontend testing
cd frontend && npm run test                    # Run all tests
cd frontend && npm run test:watch              # Watch mode for development
cd frontend && npm run coverage                # With coverage

# Linting
cd backend && flake8 .                         # Python linting
cd frontend && npm run lint                    # JavaScript/React linting

# Production readiness
docker-compose -f docker-compose.simple.yml up     # Test CI Docker setup
docker-compose -f docker-compose.yml up             # Test production Docker setup
```

## Architecture Deep Dive

### Core Components Architecture

**Backend (FastAPI)**:
- `main.py` - Application entry point with lifespan management and CORS
- `auth.py` - JWT-based authentication system (configurable, disabled in dev)
- `models/` - Pydantic data models (Instance, Chat, Docker responses)
- `routers/` - API endpoints organized by domain (instances, chat, docker)
- `services/` - Business logic layer (InstanceService, ChatService)
- `docker_manager.py` - Multi-platform Docker integration with fallback connections

**Frontend (React + Vite)**:
- `src/pages/` - Main application views (Dashboard, InstanceDetails, Settings)
- `src/components/` - Reusable UI components (InstanceCard, ChatInterface, StatusIndicator)
- `src/api/client.js` - Centralized API communication with error handling
- Mobile-first responsive design using Tailwind CSS

### Key Architectural Patterns

**Instance Management Flow**:
1. `InstanceService` manages instance lifecycle and persistence
2. Docker auto-discovery runs on startup via `docker_manager.py`
3. Health checks performed via `claude_client.py` HTTP client
4. Real-time status updates through polling and WebSocket readiness

**Chat System Architecture**:
1. Messages sent via HTTP to `/api/chat/send`
2. Chat history persisted in `backend/chat_history/` JSON files
3. Frontend polls for message updates (WebSocket-ready architecture)
4. Export functionality supports JSON/TXT formats

**Docker Integration**:
- Multi-platform connection handling (Windows Docker Desktop named pipes, Linux sockets)
- Container lifecycle management (start/stop/discover)
- Read-only Docker socket mounting for security
- Automatic Claude Code container detection by port patterns

### Cross-Platform Compatibility

**Windows Specific**:
- Docker connection via named pipes (`npipe:////./pipe/docker_engine`)
- Virtual environment activation scripts (`venv\Scripts\activate`)
- Shell command execution with `shell=True` parameter

**Universal Launcher** (`start.py`):
- Cross-platform dependency checking (Python 3.11+, Node.js 18+)
- Automatic virtual environment setup and dependency installation
- Parallel server startup with health monitoring
- Browser auto-launch with development credentials

### Authentication Architecture

**Development Mode**: Authentication disabled (`DISABLE_AUTH=true`)
**Production Mode**: JWT tokens with bcrypt password hashing
- Token expiration: 24 hours (configurable)
- Middleware-based protection for all API routes
- Frontend token storage and automatic renewal

### Environment Configuration

**Key Environment Variables**:
- `DISABLE_AUTH` - Toggle authentication (true for dev, false for prod)
- `HOST=0.0.0.0` - Required for Tailscale remote access
- `SECRET_KEY` - JWT signing key (must be changed in production)
- `CORS_ORIGINS` - Comma-separated allowed origins

**Configuration Hierarchy**:
1. `.env` files in backend directory
2. Environment variables from system/Docker
3. Default values in code

### Data Persistence Strategy

**Instance Configuration**: JSON files in `backend/data/instances.json`
**Chat History**: Individual JSON files per instance in `backend/chat_history/`
**No Database**: File-based storage for simplicity and portability

## Development Workflow Notes

### Common Patterns in Codebase

**Error Handling**: Comprehensive try-catch with structured logging using `structlog`
**API Responses**: Consistent JSON response format with success/error patterns
**Component Structure**: React functional components with hooks, form validation via `react-hook-form` + `zod`
**Docker Patterns**: Health checks, restart policies, and network isolation

### When Modifying Core Components

**Adding New Instance Types**: Extend `InstanceType` enum and update discovery logic
**New Chat Features**: Modify `ChatService` and ensure message persistence
**Docker Features**: Update `DockerManager` with proper error handling for connection failures
**Frontend Components**: Follow existing component patterns with proper prop validation

### Production Deployment Considerations

**Security**: Authentication must be enabled, default credentials changed
**Docker**: Mount Docker socket read-only, use proper network isolation
**Performance**: Frontend build optimization, backend async patterns throughout
**Monitoring**: Structured logging ready for aggregation, health endpoints available

## Important Implementation Details

**Docker Connection Resilience**: The Docker manager tries multiple connection methods to handle Windows Docker Desktop, WSL, and Linux environments automatically.

**Chat Message Flow**: Messages are sent via HTTP POST, stored locally, and retrieved via polling. The architecture is WebSocket-ready but currently uses HTTP for simplicity.

**Instance Discovery**: On startup, the system automatically scans for running Docker containers that appear to be Claude Code instances based on port patterns and container metadata.

**Mobile Responsiveness**: The frontend is mobile-first designed with Tailwind CSS breakpoints, specifically optimized for Tailscale remote access from mobile devices.