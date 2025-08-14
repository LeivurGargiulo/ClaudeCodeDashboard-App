# Security Policy

## Supported Versions

We actively support the following versions with security updates:

| Version | Supported          |
| ------- | ------------------ |
| 1.x.x   | :white_check_mark: |
| < 1.0   | :x:                |

## Reporting a Vulnerability

We take security vulnerabilities seriously. If you discover a security vulnerability, please follow these steps:

### Private Reporting

**Please do NOT create a public GitHub issue for security vulnerabilities.**

Instead, please report security vulnerabilities by:

1. **Email**: Send details to [security@your-domain.com] (replace with actual email)
2. **GitHub Security Advisories**: Use the "Security" tab in the repository
3. **Encrypted Communication**: Use our PGP key if available

### What to Include

When reporting a vulnerability, please include:

- **Description** of the vulnerability
- **Steps to reproduce** the issue
- **Potential impact** of the vulnerability
- **Suggested fix** (if you have one)
- **Your contact information** for follow-up

### Response Timeline

- **Initial Response**: Within 48 hours
- **Status Update**: Within 1 week
- **Fix Timeline**: Depends on severity
  - Critical: Within 24-48 hours
  - High: Within 1 week
  - Medium: Within 2 weeks
  - Low: Next regular release

## Security Considerations

### Authentication

- Default authentication is **disabled** in development mode
- **Enable authentication** for production deployments
- **Change default credentials** immediately
- Use **strong, unique passwords**
- Consider implementing **2FA** for production

### Network Security

- **Bind to specific interfaces** in production (not 0.0.0.0)
- Use **HTTPS** in production environments
- Implement **proper firewall rules**
- Consider using **VPN or Tailscale** for remote access

### Docker Security

- **Read-only Docker socket** mount when possible
- **Run containers as non-root** users
- **Keep Docker images updated**
- **Scan images** for vulnerabilities

### Configuration Security

- **Never commit** `.env` files or secrets
- Use **environment variables** for sensitive configuration
- **Rotate secrets** regularly
- **Validate all inputs** from external sources

### Dependencies

- **Keep dependencies updated**
- **Monitor for security advisories**
- **Use dependency scanning tools**
- **Pin dependency versions** in production

## Secure Development Practices

### Code Review

- **All changes** require review
- **Security-focused reviews** for authentication/authorization changes
- **Automated security scanning** in CI/CD

### Testing

- **Security tests** included in test suite
- **Input validation testing**
- **Authentication bypass testing**
- **SQL injection prevention** (if applicable)

### Deployment

- **Environment separation** (dev/staging/prod)
- **Secure secrets management**
- **Regular security updates**
- **Monitoring and alerting**

## Known Security Considerations

### Current Limitations

1. **Authentication is optional** - Enable for production use
2. **Docker socket access** - Required for container management
3. **Local file storage** - Chat history stored locally
4. **No rate limiting** - Implement in production if needed

### Recommended Production Setup

1. **Enable authentication**
   ```env
   DISABLE_AUTH=false
   SECRET_KEY=your-strong-secret-key
   ```

2. **Use HTTPS**
   - Configure reverse proxy (nginx, Apache)
   - Obtain SSL certificates
   - Redirect HTTP to HTTPS

3. **Secure Docker**
   ```yaml
   volumes:
     - /var/run/docker.sock:/var/run/docker.sock:ro
   ```

4. **Network Security**
   ```env
   HOST=127.0.0.1  # or specific interface
   CORS_ORIGINS=https://your-domain.com
   ```

## Security Audit

This project has not yet undergone a formal security audit. We welcome:

- **Community security reviews**
- **Penetration testing reports**
- **Vulnerability assessments**
- **Security recommendations**

## Contact

For security-related questions or concerns:

- **General Security**: Create a GitHub issue with `security` label
- **Vulnerabilities**: Follow private reporting process above
- **Security Enhancements**: Submit feature requests

## Acknowledgments

We appreciate security researchers and community members who help improve the security of this project. Contributors who report valid security issues will be acknowledged in our security advisories (with permission).

---

**Last Updated**: 2024-08-14