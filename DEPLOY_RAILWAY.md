# Hướng Dẫn Deploy Lên Railway.app

## Bước 1: Chuẩn Bị Git Repository

```bash
# Mở PowerShell tại thư mục C:\backend

# 1. Khởi tạo git (nếu chưa có)
git init

# 2. Add tất cả file
git add .

# 3. Commit
git commit -m "Ready for deployment"

# 4. Tạo repo trên GitHub và push
# Vào https://github.com/new tạo repo mới
# Sau đó:
git remote add origin https://github.com/yourusername/amitruyen.git
git branch -M main
git push -u origin main
```

## Bước 2: Deploy Lên Railway

### 2.1. Đăng Ký Railway

1. Vào https://railway.app
2. Sign up with GitHub
3. Authorize Railway

### 2.2. Tạo Project

1. Click "New Project"
2. Chọn "Deploy from GitHub repo"
3. Chọn repo `amitruyen` của bạn
4. Railway sẽ tự động detect Flask app

### 2.3. Add Database

1. Click "New" → "Database" → "Add PostgreSQL"
2. Railway tự động tạo DATABASE_URL

### 2.4. Set Environment Variables

Click vào service → Variables → Add:

```
SECRET_KEY=your-random-secret-key-here
JWT_SECRET_KEY=your-jwt-secret-key-here
FLASK_ENV=production
UPLOAD_FOLDER=uploads
PROGRESSION_ENABLED=True
RANK_TITLES_ENABLED=True
```

### 2.5. Deploy

Railway tự động deploy. Đợi 2-3 phút.

### 2.6. Initialize Database

1. Click vào service → Settings → Copy domain
2. Mở terminal local:

```bash
# Install Railway CLI
npm i -g @railway/cli

# Login
railway login

# Link to project
railway link

# Run init script
railway run python init_production.py
```

### 2.7. Add Custom Domain

1. Click service → Settings → Domains
2. Click "Custom Domain"
3. Nhập: amitruyen.id.vn
4. Railway sẽ cho bạn CNAME record

## Bước 3: Cấu Hình DNS

Vào nhà cung cấp tên miền (nơi bạn mua amitruyen.id.vn):

```
Type: CNAME
Name: @
Value: <railway-domain-từ-bước-2.7>
TTL: 300
```

Đợi 5-30 phút để DNS propagate.

## ✅ Xong!

Website của bạn sẽ online tại:

- https://amitruyen.id.vn (custom domain)
- https://your-project.railway.app (Railway domain)

## 🔧 Maintenance

### Update Code

```bash
git add .
git commit -m "Update features"
git push
# Railway tự động deploy
```

### View Logs

```bash
railway logs
```

### Connect to Database

```bash
railway connect postgres
```

---

## Phương Án 2: Google Cloud (Nếu Muốn Học VPS Thật)

Xem file DEPLOY_GCP.md

## Phương Án 3: Oracle Cloud (Free Forever Nhưng Khó)

Xem file DEPLOY_ORACLE.md
