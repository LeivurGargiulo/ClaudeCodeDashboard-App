# Contributing to Claude Code Dashboard

Thank you for your interest in contributing to the Claude Code Dashboard! This document provides guidelines and information for contributors.

## 🚀 Getting Started

### Prerequisites

- Python 3.11 or higher
- Node.js 18 or higher
- npm (comes with Node.js)
- Docker (optional, for container management features)

### Development Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd claude-code-dashboard
   ```

2. **Quick start**
   ```bash
   python start.py
   ```

3. **Manual setup** (if you prefer)
   ```bash
   # Backend
   cd backend
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   python main.py

   # Frontend (new terminal)
   cd frontend
   npm install
   npm run dev
   ```

## 🧪 Running Tests

### Backend Tests
```bash
cd backend
pytest
```

### Frontend Tests
```bash
cd frontend
npm test
```

## 🏗️ Project Structure

```
claude-code-dashboard/
├── backend/                 # FastAPI backend
│   ├── main.py             # Main application
│   ├── models/             # Data models
│   ├── routers/            # API endpoints
│   ├── services/           # Business logic
│   └── tests/              # Backend tests
├── frontend/               # React frontend
│   ├── src/
│   │   ├── components/     # Reusable components
│   │   ├── pages/          # Page components
│   │   ├── api/            # API client
│   │   └── utils/          # Utilities
│   └── tests/              # Frontend tests
└── docs/                   # Documentation
```

## 🎯 How to Contribute

### 1. Issues

- **Bug Reports**: Use the bug report template
- **Feature Requests**: Use the feature request template
- **Questions**: Use the question template

### 2. Pull Requests

1. **Fork the repository**
2. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```
3. **Make your changes**
4. **Write tests** for new functionality
5. **Run the test suite**
6. **Commit your changes**
   ```bash
   git commit -m "Add: brief description of changes"
   ```
7. **Push to your fork**
   ```bash
   git push origin feature/your-feature-name
   ```
8. **Create a Pull Request**

### 3. Commit Message Format

Use conventional commits format:

```
type(scope): description

[optional body]

[optional footer]
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

**Examples:**
```
feat(chat): add message export functionality
fix(docker): resolve Windows Docker Desktop connection issue
docs: update installation instructions
```

## 📋 Code Style Guidelines

### Python (Backend)

- Follow **PEP 8** style guide
- Use **type hints** for function parameters and return values
- Write **docstrings** for all functions and classes
- Use **meaningful variable names**
- Maximum line length: **88 characters** (Black formatter)

**Format your code:**
```bash
black .
isort .
flake8 .
```

### JavaScript/React (Frontend)

- Use **ES6+** features
- Follow **React best practices**
- Use **functional components** with hooks
- Use **meaningful component and variable names**
- Use **JSDoc** comments for complex functions

**Format your code:**
```bash
npm run lint
npm run format
```

## 🐛 Bug Reports

When reporting bugs, please include:

1. **Steps to reproduce**
2. **Expected behavior**
3. **Actual behavior**
4. **Environment details** (OS, Python version, Node.js version)
5. **Error messages** (if any)
6. **Screenshots** (if applicable)

## 💡 Feature Requests

When requesting features, please include:

1. **Use case** - Why is this feature needed?
2. **Proposed solution** - How should it work?
3. **Alternatives** - What other solutions did you consider?
4. **Additional context** - Any other relevant information

## 🔍 Code Review Process

1. **All PRs** require at least one review
2. **Automated checks** must pass (tests, linting)
3. **Documentation** must be updated for new features
4. **Breaking changes** require discussion

## 📚 Documentation

- Keep **README.md** up to date
- Document **new API endpoints** in code
- Update **configuration examples** when needed
- Add **inline comments** for complex logic

## 🛡️ Security

- **Never commit** sensitive information (API keys, passwords)
- **Use environment variables** for configuration
- **Report security issues** privately to maintainers
- **Follow secure coding practices**

## 🚀 Release Process

1. **Version bumping** follows semantic versioning
2. **Changelog** is updated for each release
3. **Tags** are created for releases
4. **Docker images** are built and published

## 📞 Getting Help

- **GitHub Issues**: For bugs and feature requests
- **Discussions**: For questions and general discussion
- **Discord/Slack**: Real-time community chat (if available)

## 🏆 Recognition

Contributors will be recognized in:
- **CONTRIBUTORS.md** file
- **Release notes**
- **README.md** acknowledgments

## 📄 License

By contributing to this project, you agree that your contributions will be licensed under the same license as the project (MIT License).

---

Thank you for contributing! 🎉