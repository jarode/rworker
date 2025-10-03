# 🚀 DEPLOYMENT NA RAILWAY.APP

## 📋 **PRZYGOTOWANIE**

### **1. Utworzone pliki:**
- ✅ `railway.json` - konfiguracja Railway
- ✅ `.railwayignore` - pliki do ignorowania
- ✅ `Dockerfile` - zaktualizowany (curl + health check)
- ✅ `requirements.txt` - zależności Python

### **2. Zmienne środowiskowe:**
```bash
BITRIX_DOMAIN=ralengroup.bitrix24.pl
BITRIX_USER_ID=25031
BITRIX_WEBHOOK_KEY=6cg9uncuyvbxtiq3
LOG_LEVEL=INFO
```

---

## 🚀 **KROKI DEPLOYMENT**

### **1. Push do GitHub:**
```bash
cd /home/jarek/ralengroup/newsolution/spa_automation
git init
git add .
git commit -m "Add Railway deployment configuration"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/spa-automation.git
git push -u origin main
```

### **2. Railway Dashboard:**
1. Idź do [railway.app](https://railway.app)
2. Zaloguj się przez GitHub
3. **New Project** → **Deploy from GitHub repo**
4. Wybierz repository: `spa-automation`
5. Railway automatycznie wykryje `Dockerfile`

### **3. Konfiguracja Environment Variables:**
W Railway dashboard → **Variables**:
```
BITRIX_DOMAIN = ralengroup.bitrix24.pl
BITRIX_USER_ID = 25031
BITRIX_WEBHOOK_KEY = 6cg9uncuyvbxtiq3
LOG_LEVEL = INFO
```

### **4. Deploy:**
- Railway automatycznie zbuduje i wdroży
- Czas: ~2-3 minuty
- URL: `https://spa-automation-production.railway.app`

---

## 🧪 **TESTING DEPLOYMENT**

### **1. Health Check:**
```bash
curl https://spa-automation-production.railway.app/health
```

**Expected Response:**
```json
{
  "service": "SPA Automation",
  "status": "healthy",
  "timestamp": "2025-10-02T22:30:00.000Z",
  "version": "2.0.0-python"
}
```

### **2. Webhook Test:**
```bash
curl https://spa-automation-production.railway.app/webhook/spa/79/dry-run
```

### **3. Production Test:**
```bash
curl https://spa-automation-production.railway.app/webhook/spa/79
```

---

## 📊 **MONITORING**

### **Railway Dashboard:**
- **Logs** - live logs z aplikacji
- **Metrics** - CPU, RAM, Network
- **Deployments** - historia wdrożeń
- **Variables** - environment variables

### **Health Monitoring:**
- Railway automatycznie sprawdza `/health`
- Restart przy błędach
- Uptime monitoring

---

## 🔧 **TROUBLESHOOTING**

### **Common Issues:**

#### **1. Build Failed:**
```bash
# Sprawdź logs w Railway dashboard
# Common fixes:
- Sprawdź Dockerfile syntax
- Sprawdź requirements.txt
- Sprawdź Python path
```

#### **2. Runtime Error:**
```bash
# Sprawdź environment variables
# Sprawdź logs w Railway dashboard
# Test localnie: docker compose up
```

#### **3. Health Check Failed:**
```bash
# Sprawdź czy port 5000 jest exposed
# Sprawdź czy /health endpoint działa
# Sprawdź curl w kontenerze
```

### **Debug Commands:**
```bash
# Local test
docker build -t spa-automation .
docker run -p 5000:5000 spa-automation

# Check logs
docker logs <container_id>

# Test health
curl http://localhost:5000/health
```

---

## 📈 **PERFORMANCE**

### **Railway Specs:**
- **CPU:** 1 vCPU
- **RAM:** 1GB
- **Storage:** 1GB
- **Network:** 100GB/month
- **Uptime:** 99.9%

### **Expected Performance:**
- **Startup:** ~30 seconds
- **Response Time:** < 2 seconds
- **Memory Usage:** ~200MB
- **Concurrent Requests:** 10-20

---

## 🔄 **AUTOMATIC DEPLOYMENTS**

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

## 🎯 **NEXT STEPS**

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

## 📞 **SUPPORT**

### **Railway Support:**
- **Docs:** [docs.railway.app](https://docs.railway.app)
- **Discord:** [discord.gg/railway](https://discord.gg/railway)
- **GitHub:** [github.com/railwayapp](https://github.com/railwayapp)

### **Our Project:**
- **Repository:** `spa-automation`
- **Service:** `spa-webhook`
- **URL:** `https://spa-automation-production.railway.app`

---

**Gotowe do deployment na Railway! 🚀**
