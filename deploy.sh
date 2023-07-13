#!/bin/bash

# 变量定义
APP_DIRECTORY="/path/to/your/app"
BACKUP_DIRECTORY="/path/to/your/backup/directory"
NGINX_AVAILABLE="/etc/nginx/sites-available"
NGINX_ENABLED="/etc/nginx/sites-enabled"
NGINX_CONFIG="auth_app"
DOMAIN_OR_IP="your_domain_or_ip"
CERTIFICATE_PATH="/etc/letsencrypt/live/liwenlong.site/fullchain.pem"
CERTIFICATE_KEY_PATH="/etc/letsencrypt/live/liwenlong.site/privkey.pem"

# 创建数据库备份的定时任务
(crontab -l 2>/dev/null; echo "0 0 * * * sqlite3 $APP_DIRECTORY/test.db \".backup $BACKUP_DIRECTORY/db_\$(date +\%Y\%m\%d).db\"") | crontab -

# 创建 Nginx 配置文件
echo "server {
    listen 80;
    server_name $DOMAIN_OR_IP;
    return 301 https://\$host\$request_uri;
}

server {
    listen 443 ssl;
    server_name $DOMAIN_OR_IP;
    
    ssl_certificate $CERTIFICATE_PATH;
    ssl_certificate_key $CERTIFICATE_KEY_PATH;

    location /auth/ {
        proxy_pass http://localhost:8000/;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
    }
}" > $NGINX_AVAILABLE/$NGINX_CONFIG

# 启用 Nginx 配置
ln -s $NGINX_AVAILABLE/$NGINX_CONFIG $NGINX_ENABLED/

# 重启 Nginx
service nginx restart
