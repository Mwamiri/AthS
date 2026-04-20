# Security Guidelines for AthS v3.0.0

## Critical Security Requirements

### 1. Environment Variables

**NEVER** commit `.env` files to version control. The following variables MUST be set in production:

- `SECRET_KEY`: Minimum 32 characters, cryptographically random
- `JWT_SECRET_KEY`: Minimum 32 characters, cryptographically random
- `DATABASE_URL`: Use strong passwords (minimum 16 characters)
- `REDIS_URL`: Restrict access to internal network only

Generate secure keys:
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

### 2. HTTPS Enforcement

In production, always enable HTTPS:
```env
TALISMAN_ENABLED=true
FORCE_HTTPS=true
```

Configure proper SSL certificates on your reverse proxy (Nginx).

### 3. Database Security

- Use dedicated database users with minimal privileges
- Enable PostgreSQL SSL connections in production
- Regularly backup and encrypt database dumps
- Keep PostgreSQL updated to latest security patches

### 4. Redis Security

- Redis should ONLY be accessible from the internal Docker network
- Use Redis AUTH password in production
- Disable dangerous commands if not needed
- Monitor Redis memory usage

### 5. API Security

- Rate limiting is enabled by default (100 requests/hour)
- JWT tokens expire after 1 hour (access) and 7 days (refresh)
- All inputs are validated using Pydantic models
- CORS is restricted to trusted origins only

### 6. Authentication

- Passwords must be hashed using bcrypt or argon2
- Implement account lockout after failed attempts
- Use secure password requirements (min 12 chars, complexity)
- Enable multi-factor authentication for admin accounts

### 7. Logging & Monitoring

- Structured JSON logs are enabled
- Audit logs track all authentication and admin actions
- Monitor for unusual patterns (brute force, SQL injection attempts)
- Set up alerts for security events

### 8. Container Security

- Containers run as non-root users
- Minimal base images used (Alpine, Slim)
- Health checks detect compromised services
- Network segmentation between services

### 9. Dependency Management

- Dependabot automatically checks for vulnerabilities
- Review and apply security updates promptly
- Pin exact versions in requirements.txt and package.json
- Run `pip audit` and `npm audit` regularly

### 10. Production Checklist

Before deploying to production:

- [ ] Change all default secrets and passwords
- [ ] Enable HTTPS with valid certificates
- [ ] Configure firewall rules
- [ ] Enable database encryption at rest
- [ ] Set up regular backups
- [ ] Configure log aggregation
- [ ] Enable monitoring and alerting
- [ ] Review CORS settings
- [ ] Test rate limiting
- [ ] Verify health checks
- [ ] Conduct penetration testing

## Incident Response

If a security incident is suspected:

1. Isolate affected services immediately
2. Preserve logs for forensic analysis
3. Rotate all secrets and credentials
4. Review audit logs for unauthorized access
5. Notify affected users if data breach occurred
6. Document incident and remediation steps

## Compliance

This system is designed to support compliance with:
- GDPR (data protection)
- OWASP Top 10 (web security)
- SOC 2 (security controls)

Consult with security professionals for formal compliance certification.

## Contact

Report security vulnerabilities responsibly via GitHub Security Advisories.
