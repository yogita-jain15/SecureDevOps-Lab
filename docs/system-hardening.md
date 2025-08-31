# Linux System Hardening

## Firewall (UFW)
- Allowed only SSH (22), HTTP (80), HTTPS (443)
- Denied all other incoming connections

## SSH Hardening
- Disabled root login
- Disabled password authentication (key-based only)
- Restricted to non-root sudo user (yogita)
- MaxAuthTries = 3

## File Permissions
- Logs restricted to root group
- Config files (env) restricted to owner (600)

## Monitoring
- Enabled auditd for login monitoring
- Logs reviewed in /var/log/auth.log
