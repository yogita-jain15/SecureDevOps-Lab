# WAF + Brute-Force Protection

## ModSecurity WAF (Kubernetes Ingress)
- Enabled OWASP Core Rule Set
- Added custom rule to block SQLi attempts
- Tested: SQL injection attempt blocked with 403

## Fail2Ban (Ubuntu)
- Protects SSH from brute-force attacks
- Config: 3 failed attempts → ban for 10 minutes
- Tested: IP banned after multiple failed login attempts
