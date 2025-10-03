# 🆓 DARMOWE ALTERNATYWY DLA RAILWAY

## 🎯 **PROBLEM:**
Railway ma tylko 30-dniowy okres próbny, potrzebujemy darmowej alternatywy.

---

## 🆓 **DARMOWE OPCJE DEPLOYMENT:**

### **1. 🌟 RENDER.COM (NAJLEPSZE)**
```bash
# Pros:
✅ 750h/month FREE (wystarczy)
✅ Automatic deployments
✅ Docker support
✅ HTTPS included
✅ No credit card required
✅ Custom domains

# Limits:
⚠️ Sleeps after 15min inactivity
⚠️ 512MB RAM limit
⚠️ 0.1 CPU limit
```

### **2. 🚀 FLY.IO**
```bash
# Pros:
✅ 3 apps FREE forever
✅ Global deployment
✅ Docker support
✅ Custom domains
✅ No sleep (always on)

# Limits:
⚠️ 256MB RAM per app
⚠️ Shared CPU
⚠️ 3GB storage
```

### **3. 🐳 HEROKU**
```bash
# Pros:
✅ 550-1000 dyno hours FREE
✅ Easy deployment
✅ Add-ons ecosystem
✅ Custom domains

# Limits:
⚠️ Sleeps after 30min
⚠️ Requires credit card
⚠️ 512MB RAM
```

### **4. 🌐 VERCEL**
```bash
# Pros:
✅ Unlimited deployments
✅ Serverless functions
✅ Edge network
✅ Automatic HTTPS

# Limits:
⚠️ 10s execution limit
⚠️ 100GB bandwidth
⚠️ No persistent storage
```

---

## 🏆 **REKOMENDACJA: RENDER.COM**

### **Dlaczego Render:**
- ✅ **750h/month** - wystarczy dla webhook
- ✅ **Docker support** - używa naszego Dockerfile
- ✅ **Automatic deployments** - z GitHub
- ✅ **HTTPS** - SSL out of the box
- ✅ **No credit card** - prawdziwie darmowe
- ✅ **Custom domains** - można dodać własną domenę

### **Limits:**
- ⚠️ **Sleeps** - budzi się przy request (OK dla webhook)
- ⚠️ **512MB RAM** - wystarczy dla Python webhook
- ⚠️ **0.1 CPU** - OK dla prostego webhook

---

## 🚀 **DEPLOYMENT NA RENDER.COM**

### **1. Przygotuj render.yaml:**
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
      - key: FLASK_ENV
        value: production
      - key: FLASK_PORT
        value: 10000
```

### **2. Update Dockerfile dla Render:**
```dockerfile
# Dodaj port 10000 (Render requirement)
EXPOSE 10000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:10000/health || exit 1

# Run webhook
CMD ["python", "src/webhook.py"]
```

### **3. Update webhook.py:**
```python
# Dodaj port 10000 support
if __name__ == '__main__':
    port = int(os.getenv('FLASK_PORT', 5000))
    app.run(host='0.0.0.0', port=port)
```

---

## 🔧 **ALTERNATYWA: FLY.IO**

### **1. Install flyctl:**
```bash
curl -L https://fly.io/install.sh | sh
```

### **2. Create fly.toml:**
```toml
app = "spa-webhook"
primary_region = "fra"

[build]

[env]
  BITRIX_DOMAIN = "ralengroup.bitrix24.pl"
  BITRIX_USER_ID = "25031"
  BITRIX_WEBHOOK_KEY = "6cg9uncuyvbxtiq3"
  LOG_LEVEL = "INFO"

[http_service]
  internal_port = 5000
  force_https = true
  auto_stop_machines = true
  auto_start_machines = true
  min_machines_running = 0

[[vm]]
  memory = "256mb"
  cpu_kind = "shared"
  cpus = 1
```

### **3. Deploy:**
```bash
fly launch
fly deploy
```

---

## 📊 **PORÓWNANIE DARMOWYCH OPCJI:**

| Platform | Free Hours | RAM | CPU | Sleep | Credit Card | Custom Domain |
|----------|------------|-----|-----|-------|-------------|---------------|
| **Render** | 750h/mo | 512MB | 0.1 | 15min | ❌ | ✅ |
| **Fly.io** | Unlimited | 256MB | Shared | ❌ | ❌ | ✅ |
| **Heroku** | 550h/mo | 512MB | Shared | 30min | ✅ | ✅ |
| **Vercel** | Unlimited | 1GB | 0.1 | ❌ | ❌ | ✅ |

---

## 🎯 **REKOMENDACJA: RENDER.COM**

### **Dlaczego Render:**
1. **750h/month** - wystarczy dla webhook (webhook działa ~2-5min co 5min = 24-60h/mo)
2. **Docker support** - używa naszego Dockerfile
3. **Automatic deployments** - z GitHub
4. **No credit card** - prawdziwie darmowe
5. **HTTPS** - SSL out of the box
6. **Custom domains** - można dodać własną domenę

### **Limits (OK dla webhook):**
- **Sleeps** - budzi się przy request (OK dla webhook)
- **512MB RAM** - wystarczy dla Python webhook
- **0.1 CPU** - OK dla prostego webhook

---

## 🚀 **NEXT STEPS:**

### **Opcja A: Render.com (Rekomendowane)**
1. Utwórz `render.yaml`
2. Update `Dockerfile` (port 10000)
3. Update `webhook.py` (port support)
4. Deploy na Render
5. Test webhook

### **Opcja B: Fly.io**
1. Install `flyctl`
2. Utwórz `fly.toml`
3. Deploy: `fly launch && fly deploy`
4. Test webhook

### **Opcja C: Heroku**
1. Install Heroku CLI
2. Utwórz `Procfile`
3. Deploy: `git push heroku main`
4. Test webhook

---

## 📋 **CHECKLIST:**

- [ ] Wybierz platformę (Render recommended)
- [ ] Przygotuj konfigurację
- [ ] Update kod dla platformy
- [ ] Deploy
- [ ] Test webhook
- [ ] Update n8n workflow

---

**Którą platformę wybierasz? Render.com jest najlepsze dla webhook! 🎯**
