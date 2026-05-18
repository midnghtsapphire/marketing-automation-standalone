# Deployment Guide — Marketing Automation Standalone

## Quick Deploy (5 minutes)

### Option 1: Docker (Recommended)

```bash
# Clone the repository
git clone https://github.com/midnghtsapphire/marketing-automation-standalone.git
cd marketing-automation-standalone

# Configure environment
cp .env.example .env
nano .env  # Add your credentials

# Build and run
docker-compose up -d

# Check health
curl http://localhost:5000/health

# Access dashboard
open http://localhost:5000
```

### Option 2: Local Python

```bash
# Prerequisites: Python 3.11+, Chrome browser

# Clone and setup
git clone https://github.com/midnghtsapphire/marketing-automation-standalone.git
cd marketing-automation-standalone

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
nano .env  # Add your credentials

# Run the app
python website_integration.py

# Access dashboard
open http://localhost:5000
```

## Production Deployment

### DigitalOcean Droplet (Recommended)

**1. Create a Droplet**
- Size: Basic ($6/month) or General Purpose ($18/month for heavier automation)
- Image: Docker on Ubuntu 24.04
- Region: Closest to your target audience

**2. SSH into your droplet**
```bash
ssh root@your-droplet-ip
```

**3. Deploy the app**
```bash
# Clone the repo
git clone https://github.com/midnghtsapphire/marketing-automation-standalone.git
cd marketing-automation-standalone

# Configure environment (IMPORTANT: Set strong SECRET_KEY)
cp .env.example .env
nano .env

# Update these critical values:
# SECRET_KEY=<generate-with-python-secrets>
# SELENIUM_HEADLESS=true
# Add social media credentials
# Add Amazon affiliate tag
# Add SMTP credentials

# Start the service
docker-compose up -d

# Verify it's running
docker ps
curl http://localhost:5000/health
```

**4. Configure firewall**
```bash
ufw allow 22     # SSH
ufw allow 5000   # App (or use nginx reverse proxy)
ufw enable
```

**5. Setup reverse proxy (optional but recommended)**

Install nginx:
```bash
apt update
apt install nginx
```

Create nginx config `/etc/nginx/sites-available/marketing-automation`:
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

Enable and restart:
```bash
ln -s /etc/nginx/sites-available/marketing-automation /etc/nginx/sites-enabled/
nginx -t
systemctl restart nginx
```

**6. SSL with Let's Encrypt**
```bash
apt install certbot python3-certbot-nginx
certbot --nginx -d your-domain.com
```

### DigitalOcean App Platform (PaaS)

**1. Connect your GitHub repo**
- Go to DigitalOcean App Platform
- Click "Create App" → Select GitHub repository

**2. Configure build**
- Build Command: (leave empty, Dockerfile detected automatically)
- HTTP Port: 5000
- Environment Variables: Add all from .env.example

**3. Deploy**
- Click "Deploy" — automatic HTTPS + CDN included
- Cost: ~$12/month for basic tier

### Environment Variables (Production Checklist)

Critical security settings:
- [ ] `SECRET_KEY` — Generate with `python -c "import secrets; print(secrets.token_hex(32))"`
- [ ] `SELENIUM_HEADLESS=true` — Must be true for server deployment
- [ ] Social media credentials encrypted (implement encryption in production)
- [ ] `FLASK_ENV=production`
- [ ] `FLASK_DEBUG=0`

## Monitoring

### Health Check
```bash
curl http://your-domain.com/health

# Expected response:
# {
#   "status": "healthy",
#   "service": "Marketing Automation Standalone",
#   "version": "1.0.0",
#   "timestamp": "2026-05-18T22:30:00"
# }
```

### Docker Logs
```bash
docker-compose logs -f marketing-automation
```

### Resource Usage
```bash
docker stats marketing-automation-standalone
```

## Scaling

### Horizontal Scaling
- Deploy multiple instances behind a load balancer
- Use external database (PostgreSQL on DigitalOcean Managed Databases)
- Share affiliate_links.db, marketing_automation.db, scheduler.db via volume mount

### Vertical Scaling
- Start: $6/month (1GB RAM, 1 vCPU) — handles ~500 posts/day
- Growth: $18/month (4GB RAM, 2 vCPU) — handles ~2,000 posts/day
- Scale: $48/month (8GB RAM, 4 vCPU) — handles ~10,000 posts/day

## Backup

### Database Backup Script
```bash
#!/bin/bash
# backup.sh

BACKUP_DIR="/root/backups"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR

docker exec marketing-automation-standalone tar czf - \
  /app/data/*.db \
  > $BACKUP_DIR/marketing-automation-$DATE.tar.gz

# Retain last 30 days
find $BACKUP_DIR -name "marketing-automation-*.tar.gz" -mtime +30 -delete
```

Add to crontab:
```bash
crontab -e
# Add: 0 2 * * * /root/backup.sh
```

## Troubleshooting

### Chrome/Selenium Issues
```bash
# If Chrome fails to start in Docker
docker-compose exec marketing-automation google-chrome --version
docker-compose exec marketing-automation chromedriver --version

# Rebuild with no cache if issues persist
docker-compose build --no-cache
```

### Permission Issues
```bash
# Fix database permissions
docker-compose exec marketing-automation chown -R nobody:nogroup /app/data
```

### Memory Issues
```bash
# Check container memory
docker stats

# Increase Docker memory limit in docker-compose.yml:
services:
  marketing-automation:
    mem_limit: 2g
    memswap_limit: 2g
```

## Security Hardening

1. **Firewall**: Only allow ports 22 (SSH), 80 (HTTP), 443 (HTTPS)
2. **SSH**: Use key-based auth, disable password login
3. **Updates**: Set up unattended-upgrades for security patches
4. **Monitoring**: Install fail2ban to prevent brute force attacks
5. **Secrets**: Never commit .env files, use environment variables
6. **SSL**: Always use HTTPS in production
7. **Rate Limiting**: Implement rate limiting on social posts to avoid bans

## Cost Estimate

| Component | Monthly Cost |
|-----------|--------------|
| DigitalOcean Droplet (Basic) | $6 |
| DigitalOcean Droplet (General Purpose) | $18 |
| DigitalOcean App Platform | $12+ |
| Domain Name | $1-2/month |
| **Total (Self-Hosted)** | **$7-20/month** |

Compare to competitors:
- HubSpot: $890/month
- ActiveCampaign: $49-79/month
- Buffer: $12-120/month
- **Marketing Automation Standalone: $7-20/month (self-hosted)**

## Support

- GitHub Issues: https://github.com/midnghtsapphire/marketing-automation-standalone/issues
- Documentation: README.md, AUTOMATION_WORKFLOW_GUIDE.md
- Email: [Contact through GitHub]

---

**Ship it. Own your automation. Pay $7/month instead of $890/month.**
