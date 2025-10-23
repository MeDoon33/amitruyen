# Hướng Dẫn Deploy Lên Google Cloud Platform (GCP)

## ✅ Ưu Điểm

- $300 credit miễn phí 90 ngày
- VM e2-micro free forever (US regions)
- Học được cách quản lý VPS thật

## Bước 1: Đăng Ký GCP

1. Vào https://cloud.google.com
2. Sign up (cần thẻ Visa/Mastercard để verify - không trừ tiền)
3. Nhận $300 credit

## Bước 2: Tạo VM Instance

1. Vào Console → Compute Engine → VM instances
2. Click "Create Instance"
3. Cấu hình:
   ```
   Name: amitruyen-server
   Region: us-west1 (Oregon) - Free tier
   Machine type: e2-micro (0.25-2 vCPU, 1GB RAM)
   Boot disk: Ubuntu 22.04 LTS, 30GB
   Firewall: ✅ Allow HTTP, ✅ Allow HTTPS
   ```
4. Click "Create"

## Bước 3: SSH Vào Server

Click "SSH" button trên console (mở browser SSH)

## Bước 4: Setup Server

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python và dependencies
sudo apt install -y python3 python3-pip python3-venv nginx postgresql postgresql-contrib supervisor git

# Tạo user cho app
sudo adduser --disabled-password --gecos "" appuser

# Switch to appuser
sudo su - appuser

# Clone code (thay YOUR_GITHUB_USERNAME)
cd /home/appuser
git clone https://github.com/YOUR_GITHUB_USERNAME/amitruyen.git
cd amitruyen

# Tạo virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
pip install gunicorn psycopg2-binary

# Setup .env
nano .env
# Paste nội dung từ .env.example và sửa lại
```

## Bước 5: Setup PostgreSQL

```bash
# Tạo database
sudo -u postgres psql

# Trong PostgreSQL shell:
CREATE DATABASE amitruyen;
CREATE USER amitruyen_user WITH PASSWORD 'your_strong_password';
GRANT ALL PRIVILEGES ON DATABASE amitruyen TO amitruyen_user;
\q

# Update DATABASE_URL trong .env:
# DATABASE_URL=postgresql://amitruyen_user:your_strong_password@localhost/amitruyen
```

## Bước 6: Initialize Database

```bash
source venv/bin/activate
python init_production.py
```

## Bước 7: Setup Gunicorn + Supervisor

```bash
# Thoát appuser
exit

# Tạo supervisor config
sudo nano /etc/supervisor/conf.d/amitruyen.conf
```

Paste nội dung:

```ini
[program:amitruyen]
directory=/home/appuser/amitruyen
command=/home/appuser/amitruyen/venv/bin/gunicorn -w 4 -b 127.0.0.1:8000 wsgi:app
user=appuser
autostart=true
autorestart=true
stopasgroup=true
killasgroup=true
stderr_logfile=/var/log/amitruyen/amitruyen.err.log
stdout_logfile=/var/log/amitruyen/amitruyen.out.log
```

```bash
# Tạo log directory
sudo mkdir -p /var/log/amitruyen
sudo chown appuser:appuser /var/log/amitruyen

# Start supervisor
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start amitruyen
```

## Bước 8: Setup Nginx

```bash
sudo nano /etc/nginx/sites-available/amitruyen
```

Paste:

```nginx
server {
    listen 80;
    server_name amitruyen.id.vn www.amitruyen.id.vn;

    client_max_body_size 100M;

    location /static {
        alias /home/appuser/amitruyen/app/static;
        expires 30d;
    }

    location /uploads {
        alias /home/appuser/amitruyen/uploads;
        expires 30d;
    }

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

```bash
# Enable site
sudo ln -s /etc/nginx/sites-available/amitruyen /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

## Bước 9: Cấu Hình Firewall

```bash
# Allow HTTP/HTTPS
sudo ufw allow 'Nginx Full'
sudo ufw allow OpenSSH
sudo ufw enable
```

## Bước 10: Setup SSL (HTTPS)

```bash
# Install certbot
sudo apt install certbot python3-certbot-nginx

# Get certificate (chỉ chạy SAU KHI đã trỏ DNS)
sudo certbot --nginx -d amitruyen.id.vn -d www.amitruyen.id.vn
```

## Bước 11: Trỏ DNS

Vào nhà cung cấp domain, add:

```
Type: A
Name: @
Value: <IP-của-GCP-VM>  (xem trong GCP Console)
TTL: 300

Type: A
Name: www
Value: <IP-của-GCP-VM>
TTL: 300
```

Đợi 5-30 phút.

## ✅ Xong!

Truy cập https://amitruyen.id.vn

## 🔧 Maintenance Commands

```bash
# View logs
sudo tail -f /var/log/amitruyen/amitruyen.err.log

# Restart app
sudo supervisorctl restart amitruyen

# Update code
sudo su - appuser
cd amitruyen
git pull
source venv/bin/activate
pip install -r requirements.txt
exit
sudo supervisorctl restart amitruyen

# Database backup
sudo -u postgres pg_dump amitruyen > backup_$(date +%Y%m%d).sql
```

## 💰 Chi Phí

- 90 ngày đầu: FREE ($300 credit)
- Sau 90 ngày: FREE (nếu dùng e2-micro ở US regions)
- Nếu vượt free tier: ~$5-10/tháng
