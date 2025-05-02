# Deployment Guide

## Prerequisites
- Python 3.8 or higher
- MySQL 5.7 or higher
- Node.js 14 or higher
- Nginx or Apache web server
- SSL certificate (for production)

## Environment Setup

### 1. Clone the Repository
```bash
git clone https://github.com/your-username/student-portfolio.git
cd student-portfolio
```

### 2. Create Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Python Dependencies
```bash
pip install -r requirements.txt
```

### 4. Install Node.js Dependencies
```bash
npm install
```

### 5. Configure Environment Variables
Create a `.env` file in the project root:
```env
DEBUG=False
SECRET_KEY=your-secret-key
ALLOWED_HOSTS=your-domain.com,www.your-domain.com

# Database Configuration
DB_NAME=student_portfolio
DB_USER=your_db_user
DB_PASSWORD=your_db_password
DB_HOST=localhost
DB_PORT=3306

# Email Configuration
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
EMAIL_USE_TLS=True

# File Storage
MEDIA_ROOT=/path/to/media
STATIC_ROOT=/path/to/static

# AWS S3 Configuration (Optional)
AWS_ACCESS_KEY_ID=your-access-key
AWS_SECRET_ACCESS_KEY=your-secret-key
AWS_STORAGE_BUCKET_NAME=your-bucket-name
AWS_S3_REGION_NAME=your-region
```

## Database Setup

### 1. Create MySQL Database
```sql
CREATE DATABASE student_portfolio CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

### 2. Run Migrations
```bash
python manage.py migrate
```

### 3. Create Superuser
```bash
python manage.py createsuperuser
```

### 4. Load Initial Data
```bash
python manage.py seed_data
```

## Web Server Configuration

### Nginx Configuration
```nginx
server {
    listen 80;
    server_name your-domain.com www.your-domain.com;
    
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
    
    location /static/ {
        alias /path/to/static/;
    }
    
    location /media/ {
        alias /path/to/media/;
    }
}
```

### Apache Configuration
```apache
<VirtualHost *:80>
    ServerName your-domain.com
    ServerAlias www.your-domain.com
    
    Alias /static/ /path/to/static/
    Alias /media/ /path/to/media/
    
    <Directory /path/to/static>
        Require all granted
    </Directory>
    
    <Directory /path/to/media>
        Require all granted
    </Directory>
    
    WSGIDaemonProcess student_portfolio python-path=/path/to/project
    WSGIProcessGroup student_portfolio
    WSGIScriptAlias / /path/to/project/wsgi.py
    
    <Directory /path/to/project>
        <Files wsgi.py>
            Require all granted
        </Files>
    </Directory>
</VirtualHost>
```

## SSL Configuration

### 1. Install Certbot
```bash
sudo apt-get install certbot python3-certbot-nginx
```

### 2. Obtain SSL Certificate
```bash
sudo certbot --nginx -d your-domain.com -d www.your-domain.com
```

## Production Deployment

### 1. Collect Static Files
```bash
python manage.py collectstatic
```

### 2. Configure Gunicorn
Create `gunicorn_config.py`:
```python
bind = "127.0.0.1:8000"
workers = 4
worker_class = "gthread"
threads = 2
timeout = 120
```

### 3. Start Gunicorn
```bash
gunicorn -c gunicorn_config.py student_portfolio.wsgi:application
```

### 4. Configure Supervisor
Create `/etc/supervisor/conf.d/student_portfolio.conf`:
```ini
[program:student_portfolio]
command=/path/to/venv/bin/gunicorn -c /path/to/gunicorn_config.py student_portfolio.wsgi:application
directory=/path/to/project
user=www-data
autostart=true
autorestart=true
stderr_logfile=/var/log/student_portfolio.err.log
stdout_logfile=/var/log/student_portfolio.out.log
```

### 5. Start Supervisor
```bash
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start student_portfolio
```

## Monitoring and Maintenance

### 1. Log Rotation
Configure log rotation in `/etc/logrotate.d/student_portfolio`:
```conf
/var/log/student_portfolio.*.log {
    daily
    missingok
    rotate 14
    compress
    delaycompress
    notifempty
    create 0640 www-data www-data
    sharedscripts
    postrotate
        supervisorctl restart student_portfolio
    endscript
}
```

### 2. Backup Strategy
Create a backup script:
```bash
#!/bin/bash
BACKUP_DIR="/path/to/backups"
DATE=$(date +%Y%m%d_%H%M%S)

# Backup database
mysqldump -u your_db_user -p your_db_password student_portfolio > $BACKUP_DIR/db_$DATE.sql

# Backup media files
tar -czf $BACKUP_DIR/media_$DATE.tar.gz /path/to/media

# Keep only last 7 backups
find $BACKUP_DIR -type f -mtime +7 -delete
```

### 3. Security Checklist
- [ ] Enable HTTPS
- [ ] Set secure cookie settings
- [ ] Configure CORS properly
- [ ] Set up rate limiting
- [ ] Enable CSRF protection
- [ ] Configure secure headers
- [ ] Set up regular security updates
- [ ] Enable automatic backups
- [ ] Configure firewall rules

## Troubleshooting

### Common Issues
1. **Static Files Not Loading**
   - Check file permissions
   - Verify Nginx/Apache configuration
   - Run collectstatic again

2. **Database Connection Issues**
   - Verify database credentials
   - Check database server status
   - Ensure proper network access

3. **Email Not Working**
   - Check SMTP settings
   - Verify email credentials
   - Test email configuration

4. **Performance Issues**
   - Check server resources
   - Optimize database queries
   - Enable caching
   - Review web server configuration

### Support
For deployment assistance:
- Email: devops@studentportfolio.com
- Documentation: https://docs.studentportfolio.com
- GitHub Issues: https://github.com/your-username/student-portfolio/issues 