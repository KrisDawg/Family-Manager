# Operations & Deployment Guide

## Production Deployment Strategy

This guide covers deploying the Family Household Manager system to production for real-world use by families.

## Pre-Deployment Checklist

### Code Quality
- [ ] All tests passing: `python3 -m pytest tests/`
- [ ] No syntax errors: `python3 -m py_compile family_manager/*.py`
- [ ] Codacy score acceptable (B grade or better)
- [ ] No hardcoded API keys or secrets
- [ ] All dependencies documented in requirements.txt

### Security
- [ ] Authentication implemented (token-based auth)
- [ ] CORS configured (whitelist allowed domains)
- [ ] SQL injection prevention verified (parameterized queries)
- [ ] Rate limiting enabled on API endpoints
- [ ] SSL/TLS configured for production
- [ ] Database credentials not in code
- [ ] API keys stored in environment variables
- [ ] HTTPS enforced for all requests

### Performance
- [ ] Database indexes optimized (run PRAGMA analyze)
- [ ] API response times <100ms for 95th percentile
- [ ] Mobile app startup <3 seconds
- [ ] Cache strategy configured and tested
- [ ] Load testing completed with expected user concurrency

### Testing
- [ ] Unit tests passing (>80% coverage)
- [ ] Integration tests passing
- [ ] Manual testing on target devices
- [ ] Offline sync tested end-to-end
- [ ] Error scenarios tested (network failure, database error)
- [ ] Backup/restore procedure tested

### Documentation
- [ ] User guide written and reviewed
- [ ] Admin guide for server maintenance
- [ ] Troubleshooting guide published
- [ ] API documentation complete
- [ ] Database schema documented
- [ ] Deployment procedure documented (this guide)

## Server Deployment

### Hosting Options

#### Option 1: Cloud Platform (Recommended)

**AWS:**
```bash
# Use EC2 for application server
# RDS for managed PostgreSQL (optional, if migrating from SQLite)
# S3 for backups
# CloudFront for CDN (if adding web dashboard)

# Estimated costs:
# - t2.micro (1 year free tier): $0/month
# - Small instance (t3.small): $20-30/month
# - RDS PostgreSQL: $15-30/month
# - Total: $35-60/month
```

**Azure:**
```bash
# Use App Service for Python app
# Azure SQL Database (optional)
# Azure Storage for backups

# Estimated costs:
# - App Service B1 (shared): $10/month
# - Application Insights: $0 (included)
# - Total: $10-20/month
```

**DigitalOcean (Simplest):**
```bash
# Use Droplets with Ubuntu 22.04 LTS
# $5-6/month for basic setup

# Steps:
# 1. Create Droplet (1GB RAM, 25GB SSD)
# 2. SSH into server
# 3. Run deployment script below
```

#### Option 2: On-Premises (Home Server)

**Hardware Requirements:**
- Minimal: 2GB RAM, 10GB storage
- Recommended: 4GB RAM, 50GB storage (for database growth)
- Network: Stable, port forwarding enabled

**Power Considerations:**
- Small fanless PC: 10-20W continuous
- Raspberry Pi 4: 3-5W continuous
- Cost: $100-300 hardware + electricity

## Deployment Script

### DigitalOcean / Ubuntu 22.04

```bash
#!/bin/bash
# Deploy Family Household Manager to Ubuntu server

# 1. Update system
sudo apt-get update
sudo apt-get upgrade -y
sudo apt-get install -y python3-pip python3-venv git wget curl

# 2. Create application directory
sudo mkdir -p /opt/family-manager
cd /opt/family-manager

# 3. Clone repository (or upload files)
sudo git clone https://github.com/yourname/meal-plan-inventory.git .
# OR upload folder: scp -r . user@server:/opt/family-manager/

# 4. Create virtual environment
python3 -m venv venv
source venv/bin/activate

# 5. Install dependencies
cd family_manager/
pip install -r requirements.txt

# 6. Initialize database
python3 db_setup.py

# 7. Set environment variables
cat > ../.env << EOF
FLASK_ENV=production
FLASK_DEBUG=0
SERVER_PORT=5000
GEMINI_API_KEY=your_key_here
EOF

# 8. Create systemd service
sudo tee /etc/systemd/system/family-manager.service > /dev/null << EOF
[Unit]
Description=Family Household Manager API
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/opt/family-manager/family_manager
Environment="PATH=/opt/family-manager/venv/bin"
EnvironmentFile=/opt/family-manager/.env
ExecStart=/opt/family-manager/venv/bin/python3 main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# 9. Enable and start service
sudo systemctl daemon-reload
sudo systemctl enable family-manager
sudo systemctl start family-manager

# 10. Verify service running
sudo systemctl status family-manager
curl http://localhost:5000/api/inventory

# 11. Setup Nginx reverse proxy
sudo apt-get install -y nginx
sudo tee /etc/nginx/sites-available/family-manager > /dev/null << EOF
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:5000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
    }
}
EOF

sudo ln -s /etc/nginx/sites-available/family-manager /etc/nginx/sites-enabled/
sudo systemctl restart nginx

# 12. Setup SSL with Let's Encrypt
sudo apt-get install -y certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com

# 13. Setup backup cron job
cat > /opt/family-manager/backup.sh << 'EOF'
#!/bin/bash
BACKUP_DIR="/opt/family-manager/backups"
mkdir -p $BACKUP_DIR
cp family_manager/family_manager.db $BACKUP_DIR/family_manager.db.$(date +%Y%m%d_%H%M%S)
# Keep only last 7 days
find $BACKUP_DIR -name "*.db" -mtime +7 -delete
EOF

chmod +x /opt/family-manager/backup.sh
(crontab -l 2>/dev/null; echo "0 2 * * * /opt/family-manager/backup.sh") | crontab -

echo "Deployment complete!"
echo "Server running at: http://your-domain.com"
echo "API endpoint: http://your-domain.com/api/inventory"
```

## Configuration Management

### Environment Variables

Create `.env` file on server:
```bash
# .env
FLASK_ENV=production
FLASK_DEBUG=False
SERVER_PORT=5000
GEMINI_API_KEY=your_key_here
OPENAI_API_KEY=your_key_here
SPOONACULAR_API_KEY=your_key_here
DATABASE_PATH=/opt/family-manager/family_manager/family_manager.db
LOG_LEVEL=INFO
LOG_FILE=/var/log/family-manager/app.log
```

Load in Python:
```python
import os
from dotenv import load_dotenv

load_dotenv()

GEMINI_KEY = os.getenv('GEMINI_API_KEY', '')
DATABASE_PATH = os.getenv('DATABASE_PATH', 'family_manager.db')
```

### Configuration File

Alternatively, create `config.json`:
```json
{
  "server": {
    "host": "0.0.0.0",
    "port": 5000,
    "debug": false,
    "ssl": {
      "enabled": true,
      "cert_file": "/etc/ssl/certs/family-manager.crt",
      "key_file": "/etc/ssl/private/family-manager.key"
    }
  },
  "database": {
    "path": "/opt/family-manager/family_manager.db",
    "backup_enabled": true,
    "backup_dir": "/opt/family-manager/backups",
    "backup_interval_hours": 24
  },
  "api": {
    "timeout_seconds": 5,
    "rate_limit": "100/hour",
    "cors_origins": ["http://localhost:3000", "https://your-domain.com"]
  },
  "cache": {
    "ttl_minutes": 60,
    "max_size_mb": 100
  },
  "logging": {
    "level": "INFO",
    "file": "/var/log/family-manager/app.log",
    "max_size_mb": 100,
    "backup_count": 5
  }
}
```

## Database Maintenance

### Regular Backups

#### Daily Backup Script
```bash
#!/bin/bash
# /usr/local/bin/backup-family-manager.sh

BACKUP_DIR="/opt/family-manager/backups"
DB_PATH="/opt/family-manager/family_manager/family_manager.db"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

# Create backup directory
mkdir -p $BACKUP_DIR

# Backup database
cp $DB_PATH $BACKUP_DIR/family_manager_$TIMESTAMP.db

# Compress older backups
find $BACKUP_DIR -name "*.db" -mtime +1 -exec gzip {} \;

# Remove backups older than 30 days
find $BACKUP_DIR -name "*.gz" -mtime +30 -delete

# Log backup
echo "$(date): Backup completed to $BACKUP_DIR/family_manager_$TIMESTAMP.db" >> /var/log/family-manager/backup.log
```

Cron job:
```bash
# Run daily at 2 AM
0 2 * * * /usr/local/bin/backup-family-manager.sh
```

#### Off-Site Backup
```bash
#!/bin/bash
# Upload backups to cloud storage (AWS S3)

BACKUP_DIR="/opt/family-manager/backups"
S3_BUCKET="s3://family-manager-backups"

# Upload latest backup
aws s3 cp $BACKUP_DIR/family_manager_*.db $S3_BUCKET/ \
  --sse AES256 \
  --metadata "server=production"

# Or use other cloud storage
# gsutil cp $BACKUP_DIR/family_manager_*.db gs://family-manager-backups/
```

### Database Optimization

Run regularly (weekly):
```bash
#!/bin/bash
# src/optimize_database.sh

sqlite3 family_manager/family_manager.db << EOF
-- Analyze for query optimization
ANALYZE;

-- Rebuild indexes
REINDEX;

-- Cleanup free space
VACUUM;

-- Check integrity
PRAGMA integrity_check;

-- Get stats
PRAGMA database_list;
.tables
EOF
```

### Database Monitoring

```bash
#!/bin/bash
# Monitor database size and table statistics

sqlite3 family_manager/family_manager.db << EOF
-- Database size
SELECT page_count * page_size as size, page_count as pages FROM pragma_page_count(), pragma_page_size();

-- Table sizes
SELECT name, COUNT(*) as rows FROM (
  SELECT 'inventory' as name FROM inventory
  UNION ALL SELECT 'meals' FROM meals
  UNION ALL SELECT 'shopping_list' FROM shopping_list
  UNION ALL SELECT 'chores' FROM chores
  UNION ALL SELECT 'tasks' FROM tasks
  UNION ALL SELECT 'bills' FROM bills
  UNION ALL SELECT 'notifications' FROM notifications
) GROUP BY name ORDER BY rows DESC;

-- Largest tables by disk usage
SELECT name, COUNT(*) as rows FROM sqlite_master WHERE type='table';
EOF
```

## Monitoring & Logging

### Application Logging

Configure in `main.py`:
```python
import logging
from logging.handlers import RotatingFileHandler

# Setup logging
log_dir = '/var/log/family-manager'
os.makedirs(log_dir, exist_ok=True)

log_file = os.path.join(log_dir, 'app.log')
handler = RotatingFileHandler(
    log_file,
    maxBytes=100*1024*1024,  # 100MB
    backupCount=5
)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[handler]
)

logger = logging.getLogger(__name__)

# Log important events
logger.info("Server started")
logger.warning("API rate limit exceeded")
logger.error("Database connection failed")
```

### Health Checks

Implement health endpoint:
```python
@app.route('/health', methods=['GET'])
def health_check():
    """Check if server is healthy."""
    try:
        # Check database
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        conn.close()
        
        return {
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'database': 'connected'
        }, 200
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            'status': 'unhealthy',
            'error': str(e)
        }, 500
```

Monitor with:
```bash
# Check health every 5 minutes
while true; do
    curl http://localhost:5000/health
    sleep 300
done
```

### Server Resource Monitoring

```bash
#!/bin/bash
# Monitor CPU, memory, disk

watch -n 5 'free -h && echo "---" && df -h | grep opt && echo "---" && ps aux | grep family-manager | head -3'
```

Setup alerts:
```bash
#!/bin/bash
# Alert if disk usage >80%
USAGE=$(df /opt/family-manager | awk 'NR==2 {print $5}' | sed 's/%//')

if [ $USAGE -gt 80 ]; then
    echo "Disk usage at $USAGE%" | mail -s "Server Alert" admin@example.com
fi
```

## Updating the Application

### Zero-Downtime Updates

```bash
#!/bin/bash
# Deploy new version without downtime

# 1. Stop accepting new requests (optional, if using load balancer)
# Update load balancer health check endpoint

# 2. Update code
cd /opt/family-manager
git fetch origin
git checkout main
git pull origin main

# 3. Update dependencies if needed
source venv/bin/activate
pip install -r family_manager/requirements.txt

# 4. Backup database
cp family_manager/family_manager.db family_manager/family_manager.db.backup

# 5. Run migrations if needed
# python3 family_manager/db_setup.py (only if schema changed)

# 6. Restart service
sudo systemctl restart family-manager

# 7. Verify health
sleep 5
curl http://localhost:5000/health

# 8. Run smoke tests
python3 -m pytest tests/integration/test_api.py -q

echo "Update complete!"
```

## Disaster Recovery

### Complete Failure Recovery

```bash
#!/bin/bash
# Restore from backup if system fails

# 1. Setup clean server (follow deployment script)

# 2. Get latest backup (from S3, NAS, or local)
aws s3 cp s3://family-manager-backups/family_manager_TIMESTAMP.db .

# 3. Restore database
rm family_manager/family_manager.db
cp family_manager_TIMESTAMP.db family_manager/family_manager.db

# 4. Verify integrity
sqlite3 family_manager/family_manager.db "PRAGMA integrity_check;"

# 5. Start services
sudo systemctl start family-manager
curl http://localhost:5000/health

echo "System restored from backup"
```

### Rollback Procedure

```bash
#!/bin/bash
# Rollback to previous version if update fails

# 1. Check current version
git log --oneline -5

# 2. Backup current database
cp family_manager/family_manager.db family_manager/family_manager.db.failed

# 3. Restore previous version
git checkout <previous-commit-hash>

# 4. Restore previous database backup (if schema changed)
# (usually database is forward-compatible)

# 5. Restart service
sudo systemctl restart family-manager

# 6. Verify
curl http://localhost:5000/health

echo "Rolled back to previous version"
```

## Performance Tuning

### Nginx Configuration

Optimize for production:
```nginx
# /etc/nginx/nginx.conf

http {
    # Compression
    gzip on;
    gzip_types application/json text/plain;
    gzip_min_length 1000;
    
    # Caching
    proxy_cache_path /var/cache/nginx levels=1:2 keys_zone=api_cache:10m;
    
    # Upstream (if multiple servers)
    upstream family_manager_backend {
        server localhost:5000;
        server localhost:5001;  # Load balance
    }
    
    # Limits
    limit_req_zone $binary_remote_addr zone=general:10m rate=100r/s;
}
```

### Database Query Optimization

Profile slow queries:
```bash
sqlite3 family_manager/family_manager.db << EOF
.mode line
.timer ON
EXPLAIN QUERY PLAN SELECT * FROM inventory WHERE category='Dairy';
EOF
```

## Security Hardening

### SSL/TLS Certificate Management

```bash
#!/bin/bash
# Auto-renew SSL certificates

# Install certbot
sudo apt-get install -y certbot python3-certbot-nginx

# Get certificate
sudo certbot certonly --nginx -d your-domain.com

# Auto-renewal
sudo certbot renew --dry-run  # Test
sudo certbot renew  # Actual

# Cron job to auto-renew
0 0 1 * * /usr/bin/certbot renew --quiet
```

### Firewall Configuration

```bash
#!/bin/bash
# UFW firewall setup

sudo ufw default deny incoming
sudo ufw default allow outgoing

# Allow SSH (change port if not 22)
sudo ufw allow 22/tcp

# Allow HTTP/HTTPS
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# Deny internal API port
sudo ufw deny 5000/tcp

# Enable firewall
sudo ufw enable
sudo ufw status
```

### API Security

Rate limiting already added in code:
```python
from flask_limiter import Limiter

limiter = Limiter(app, key_func=lambda: request.remote_addr)

@app.route('/api/inventory')
@limiter.limit("100/hour")
def get_inventory():
    pass
```

## Monitoring Services

### Uptime Monitoring

Use external service:
```bash
# UptimeRobot, Datadog, Pingdom, or similar

# OR simple script
#!/bin/bash
while true; do
    response=$(curl -s -o /dev/null -w "%{http_code}" http://your-domain.com/health)
    
    if [ $response != "200" ]; then
        echo "Server down! Status: $response" | mail -s "Alert" admin@example.com
    fi
    
    sleep 300
done
```

### Log Aggregation

Use centralized logging (optional):
```bash
# ELK Stack, Splunk, Datadog, or papertrail

# Or simple log viewing
tail -f /var/log/family-manager/app.log
```

## Production Checklists

### Daily
- [ ] Check service status: `sudo systemctl status family-manager`
- [ ] Monitor error logs: `tail -20 /var/log/family-manager/app.log`
- [ ] Verify backup completed: `ls -lt /opt/family-manager/backups | head -1`

### Weekly
- [ ] Review database size: `du -h family_manager/family_manager.db`
- [ ] Optimize database: Run VACUUM and ANALYZE
- [ ] Check storage usage: `df -h /opt/family-manager`

### Monthly
- [ ] Security updates: `sudo apt-get update && upgrade`
- [ ] Update dependencies: `pip list --outdated`
- [ ] Test restore procedure
- [ ] Review error logs for patterns

### Quarterly
- [ ] Full system backup test
- [ ] Performance baseline measurement
- [ ] Security audit
- [ ] User feedback review

## Support & Communication

### User Support
- Document common issues: See TROUBLESHOOTING.md
- Setup help email: support@your-domain.com
- Consider message board or Discord community

### Incident Response
- Have runbook for common failures
- Communicate status to users
- Post-incident review

### Documentation
- Keep API documentation updated
- Document any custom changes
- Version control everything
