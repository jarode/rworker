# 🚀 DEPLOYMENT OPTIONS - PYTHON WEBHOOK

## 🎯 **PROBLEM:**
Webhook Python działa lokalnie (`http://localhost:5000`), ale n8n potrzebuje publicznego URL.

---

## 📊 **OPCJE DEPLOYMENT:**

### **1. 🌐 CHMURA (RECOMMENDED)**

#### **A) Railway.app (Najłatwiejsze)**
```bash
# Pros:
✅ Zero-config deployment
✅ Automatic HTTPS
✅ Free tier (500h/month)
✅ Docker support
✅ Custom domains

# Steps:
1. Push kod do GitHub
2. Connect Railway to repo
3. Deploy automatically
4. Get public URL: https://spa-webhook.railway.app
```

#### **B) Render.com**
```bash
# Pros:
✅ Free tier (750h/month)
✅ Docker support
✅ Automatic deployments
✅ HTTPS included

# Steps:
1. Connect GitHub repo
2. Deploy as Docker service
3. Get URL: https://spa-webhook.onrender.com
```

#### **C) Fly.io**
```bash
# Pros:
✅ Global deployment
✅ Free tier (3 apps)
✅ Docker support
✅ Custom domains

# Steps:
1. Install flyctl
2. fly launch
3. fly deploy
4. Get URL: https://spa-webhook.fly.dev
```

### **2. 🖥️ VPS/SERVER**

#### **A) DigitalOcean Droplet**
```bash
# Pros:
✅ Full control
✅ Predictable pricing ($5/month)
✅ Custom domain
✅ SSH access

# Steps:
1. Create Ubuntu droplet
2. Install Docker
3. Deploy app
4. Configure nginx + SSL
```

#### **B) AWS EC2**
```bash
# Pros:
✅ Enterprise grade
✅ Free tier (1 year)
✅ Auto-scaling
✅ Load balancing

# Steps:
1. Launch EC2 instance
2. Configure security groups
3. Deploy with Docker
4. Setup ALB + Route 53
```

### **3. 🔧 SELF-HOSTED**

#### **A) Home Server + ngrok**
```bash
# Pros:
✅ Keep local development
✅ Temporary public access
✅ Free for testing

# Steps:
1. Install ngrok
2. ngrok http 5000
3. Get public URL
4. Update n8n workflow
```

#### **B) VPS + Reverse Proxy**
```bash
# Pros:
✅ Full control
✅ Custom domain
✅ SSL certificates
✅ Multiple apps

# Steps:
1. Rent VPS
2. Install Docker + nginx
3. Deploy webhook
4. Configure SSL
```

---

## 🏆 **RECOMMENDED: RAILWAY.APP**

### **Dlaczego Railway?**
- ✅ **Najłatwiejsze** - zero configuration
- ✅ **Free tier** - 500h/month (wystarczy)
- ✅ **Automatic HTTPS** - SSL out of the box
- ✅ **GitHub integration** - auto-deploy on push
- ✅ **Docker support** - używa naszego Dockerfile
- ✅ **Monitoring** - built-in logs
- ✅ **Custom domains** - można dodać własną domenę

### **Deployment Steps:**

#### **1. Przygotuj kod:**
```bash
# Dodaj railway.json (opcjonalnie)
{
  "build": {
    "builder": "DOCKERFILE"
  },
  "deploy": {
    "startCommand": "python src/webhook.py",
    "healthcheckPath": "/health"
  }
}
```

#### **2. Push do GitHub:**
```bash
git add .
git commit -m "Add Railway deployment config"
git push origin main
```

#### **3. Deploy na Railway:**
```bash
# W Railway dashboard:
1. New Project → Deploy from GitHub
2. Select repository
3. Deploy automatically
4. Get public URL
```

#### **4. Update n8n workflow:**
```json
// Zmień URL w workflow
"url": "https://spa-webhook-production.railway.app/webhook/spa/{{ $json.id }}"
```

---

## 🔧 **ALTERNATIVE: RENDER.COM**

### **Deployment Steps:**

#### **1. Przygotuj render.yaml:**
```yaml
services:
  - type: web
    name: spa-webhook
    env: docker
    dockerfilePath: ./Dockerfile
    plan: free
    envVars:
      - key: BITRIX_DOMAIN
        value: ralengroup.bitrix24.pl
      - key: BITRIX_USER_ID
        value: 25031
      - key: BITRIX_WEBHOOK_KEY
        value: 6cg9uncuyvbxtiq3
      - key: LOG_LEVEL
        value: INFO
```

#### **2. Deploy:**
```bash
# W Render dashboard:
1. New Web Service
2. Connect GitHub
3. Select repo
4. Deploy
```

---

## 🖥️ **ALTERNATIVE: VPS DEPLOYMENT**

### **DigitalOcean Droplet ($5/month):**

#### **1. Create Droplet:**
```bash
# Ubuntu 22.04 LTS
# Basic plan: $5/month
# 1GB RAM, 1 vCPU, 25GB SSD
```

#### **2. Setup Server:**
```bash
# SSH to server
ssh root@your-server-ip

# Update system
apt update && apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# Install Docker Compose
apt install docker-compose-plugin -y
```

#### **3. Deploy App:**
```bash
# Clone repo
git clone https://github.com/your-repo/spa-automation.git
cd spa-automation

# Create .env
cat > .env << EOF
BITRIX_DOMAIN=ralengroup.bitrix24.pl
BITRIX_USER_ID=25031
BITRIX_WEBHOOK_KEY=6cg9uncuyvbxtiq3
LOG_LEVEL=INFO
EOF

# Deploy
docker compose -f docker-compose.prod.yml up -d
```

#### **4. Setup Nginx + SSL:**
```bash
# Install nginx
apt install nginx -y

# Configure nginx
cat > /etc/nginx/sites-available/spa-webhook << EOF
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:5000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
    }
}
EOF

# Enable site
ln -s /etc/nginx/sites-available/spa-webhook /etc/nginx/sites-enabled/
nginx -t
systemctl reload nginx

# SSL with Let's Encrypt
apt install certbot python3-certbot-nginx -y
certbot --nginx -d your-domain.com
```

---

## 🧪 **TESTING DEPLOYMENT**

### **Health Check:**
```bash
# Test local
curl http://localhost:5000/health

# Test production
curl https://your-domain.com/health
```

### **Webhook Test:**
```bash
# Test webhook
curl https://your-domain.com/webhook/spa/79/dry-run
```

---

## 📊 **COST COMPARISON**

| Option | Cost | Setup Time | Maintenance | Recommended |
|--------|------|------------|-------------|-------------|
| Railway | Free | 5 min | Low | ⭐⭐⭐⭐⭐ |
| Render | Free | 10 min | Low | ⭐⭐⭐⭐ |
| Fly.io | Free | 15 min | Medium | ⭐⭐⭐ |
| DigitalOcean | $5/mo | 30 min | Medium | ⭐⭐⭐ |
| AWS EC2 | Free/Paid | 45 min | High | ⭐⭐ |
| ngrok | Free | 2 min | High | ⭐ |

---

## 🎯 **RECOMMENDATION**

### **For Production: Railway.app**
- ✅ Free tier wystarczy
- ✅ Zero maintenance
- ✅ Automatic deployments
- ✅ Built-in monitoring

### **For Development: ngrok**
- ✅ Instant public URL
- ✅ Free for testing
- ✅ No server setup

---

## 🚀 **NEXT STEPS**

1. **Choose deployment option** (Railway recommended)
2. **Deploy webhook** to public URL
3. **Update n8n workflow** with new URL
4. **Test end-to-end** workflow
5. **Monitor** and optimize

---

**Którą opcję wybierasz? Railway.app jest najłatwiejsza i darmowa! 🎯**
