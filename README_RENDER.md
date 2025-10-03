# 🚀 DEPLOYMENT NA RENDER.COM

## 🎯 **DARMOWA ALTERNATYWA DLA RAILWAY**

### **Render.com Specs:**
- ✅ **750h/month FREE** (wystarczy dla webhook)
- ✅ **Docker support** (używa naszego Dockerfile)
- ✅ **Automatic deployments** (z GitHub)
- ✅ **HTTPS** (SSL out of the box)
- ✅ **No credit card** (prawdziwie darmowe)
- ✅ **Custom domains** (można dodać własną domenę)

### **Limits:**
- ⚠️ **Sleeps** - budzi się przy request (OK dla webhook)
- ⚠️ **512MB RAM** - wystarczy dla Python webhook
- ⚠️ **0.1 CPU** - OK dla prostego webhook

---

## 📋 **PRZYGOTOWANE PLIKI:**

### **1. render.yaml** - Konfiguracja Render
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

### **2. Dockerfile** - Zaktualizowany (port 10000)
```dockerfile
# Expose port (Render uses port 10000)
EXPOSE 10000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:10000/health || exit 1

# Run the webhook application
CMD ["python", "src/webhook.py"]
```

### **3. webhook.py** - Port support
```python
if __name__ == '__main__':
    port = int(os.getenv('FLASK_PORT', 5000))
    debug = os.getenv('FLASK_DEBUG', '0') == '1'
    app.run(host='0.0.0.0', port=port, debug=debug)
```

---

## 🚀 **KROKI DEPLOYMENT:**

### **1. Push do GitHub:**
```bash
cd /home/jarek/ralengroup/newsolution/spa_automation
git add .
git commit -m "Add Render.com deployment configuration"
git push origin main
```

### **2. Render Dashboard:**
1. Idź do [render.com](https://render.com)
2. **Sign up** (użyj GitHub)
3. **New +** → **Web Service**
4. **Connect GitHub** → Wybierz `jarode/rworker`
5. **Configure:**
   - **Name:** `spa-webhook`
   - **Environment:** `Docker`
   - **Dockerfile Path:** `./Dockerfile`
   - **Plan:** `Free`

### **3. Environment Variables:**
W Render dashboard → **Environment**:
```
BITRIX_DOMAIN = ralengroup.bitrix24.pl
BITRIX_USER_ID = 25031
BITRIX_WEBHOOK_KEY = 6cg9uncuyvbxtiq3
LOG_LEVEL = INFO
FLASK_ENV = production
FLASK_PORT = 10000
```

### **4. Deploy:**
- Kliknij **Create Web Service**
- Render automatycznie zbuduje i wdroży
- Czas: ~3-5 minut
- URL: `https://spa-webhook.onrender.com`

---

## 🧪 **TESTING DEPLOYMENT:**

### **1. Health Check:**
```bash
curl https://spa-webhook.onrender.com/health
```

**Expected Response:**
```json
{
  "service": "SPA Automation",
  "status": "healthy",
  "timestamp": "2025-10-03T08:30:00.000Z",
  "version": "2.0.0-python"
}
```

### **2. Webhook Test:**
```bash
curl https://spa-webhook.onrender.com/webhook/spa/79/dry-run
```

### **3. Production Test:**
```bash
curl https://spa-webhook.onrender.com/webhook/spa/79
```

---

## 📊 **MONITORING:**

### **Render Dashboard:**
- **Logs** - live logs z aplikacji
- **Metrics** - CPU, RAM, Network
- **Deployments** - historia wdrożeń
- **Environment** - environment variables

### **Health Monitoring:**
- Render automatycznie sprawdza `/health`
- Restart przy błędach
- Uptime monitoring

---

## 🔧 **TROUBLESHOOTING:**

### **Common Issues:**

#### **1. Build Failed:**
```bash
# Sprawdź logs w Render dashboard
# Common fixes:
- Sprawdź Dockerfile syntax
- Sprawdź requirements.txt
- Sprawdź Python path
```

#### **2. Runtime Error:**
```bash
# Sprawdź environment variables
# Sprawdź logs w Render dashboard
# Test localnie: docker compose up
```

#### **3. Health Check Failed:**
```bash
# Sprawdź czy port 10000 jest exposed
# Sprawdź czy /health endpoint działa
# Sprawdź curl w kontenerze
```

### **Debug Commands:**
```bash
# Local test
docker build -t spa-webhook .
docker run -p 10000:10000 -e FLASK_PORT=10000 spa-webhook

# Check logs
docker logs <container_id>

# Test health
curl http://localhost:10000/health
```

---

## 📈 **PERFORMANCE:**

### **Render Free Specs:**
- **CPU:** 0.1 vCPU
- **RAM:** 512MB
- **Storage:** 1GB
- **Network:** 100GB/month
- **Uptime:** 99.9%

### **Expected Performance:**
- **Startup:** ~30 seconds
- **Response Time:** < 2 seconds
- **Memory Usage:** ~200MB
- **Concurrent Requests:** 10-20

---

## 🔄 **AUTOMATIC DEPLOYMENTS:**

### **GitHub Integration:**
- Push do `main` → automatyczny deploy
- Pull Request → preview deployment
- Rollback → jeden klik w dashboard

### **Deployment Process:**
1. **Build** - Docker build
2. **Test** - Health check
3. **Deploy** - Zero-downtime deployment
4. **Verify** - Health check
5. **Monitor** - Continuous monitoring

---

## 🎯 **NEXT STEPS:**

### **Po deployment:**
1. ✅ Test health endpoint
2. ✅ Test webhook endpoint
3. ✅ Update n8n workflow URL
4. ✅ Test end-to-end workflow
5. ✅ Monitor performance

### **Production Checklist:**
- [ ] Health check OK
- [ ] Webhook responds
- [ ] Environment variables set
- [ ] Logs visible
- [ ] n8n workflow updated
- [ ] End-to-end test passed

---

## 📞 **SUPPORT:**

### **Render Support:**
- **Docs:** [render.com/docs](https://render.com/docs)
- **Status:** [status.render.com](https://status.render.com)
- **Community:** [community.render.com](https://community.render.com)

### **Our Project:**
- **Repository:** `jarode/rworker`
- **Service:** `spa-webhook`
- **URL:** `https://spa-webhook.onrender.com`

---

**Gotowe do deployment na Render! 🚀**
