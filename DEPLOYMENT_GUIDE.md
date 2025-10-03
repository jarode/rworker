# 🚀 INSTRUKCJA WDROŻENIA - SPA Automation Python

**Wersja:** 2.0.0  
**Data:** 2025-10-02  
**Status:** ✅ Ready for deployment

---

## 🎯 **STRATEGIA WDROŻENIA**

### **FAZA 1: Dual-Run (Równoległe uruchomienie)**

```
┌─────────────────────────────────┐
│ PHP webhook6.php (stary)        │ ← Produkcja (100% ruchu)
│ http://server/webhook6.php      │
└─────────────────────────────────┘

┌─────────────────────────────────┐
│ Python webhook (nowy)           │ ← Test (0% ruchu, tylko obserwacja)
│ http://server:5000/webhook/spa  │
└─────────────────────────────────┘

CEL: Porównać wyniki bez ryzyka
CZAS: 1-2 tygodnie
```

### **FAZA 2: Canary Deployment**

```
10% ruchu → Python
90% ruchu → PHP

CEL: Testowanie na małym % ruchu
CZAS: 1 tydzień
```

### **FAZA 3: Full Migration**

```
100% ruchu → Python
PHP → backup (na wypadek rollback)
```

---

## 📋 **KROK PO KROKU - WDROŻENIE**

### **KROK 1: Przygotowanie serwera**

```bash
# Połącz się z serwerem
ssh user@your-server

# Utwórz katalog
cd /var/www
sudo mkdir spa_automation
sudo chown $USER:$USER spa_automation
cd spa_automation

# Sklonuj projekt (lub skopiuj przez scp)
# Opcja A: Git
git clone <your-repo> .

# Opcja B: SCP z lokalnego
# (z lokalnej maszyny)
cd /home/jarek/ralengroup/newsolution/spa_automation
scp -r . user@server:/var/www/spa_automation/
```

### **KROK 2: Konfiguracja .env**

```bash
cd /var/www/spa_automation

# Utwórz .env z production credentials
cat > .env << 'EOF'
# Bitrix24
BITRIX_DOMAIN=ralengroup.bitrix24.pl
BITRIX_USER_ID=25031
BITRIX_WEBHOOK_KEY=6cg9uncuyvbxtiq3

# Flask
FLASK_ENV=production
FLASK_DEBUG=0
FLASK_PORT=5000
EOF

chmod 600 .env  # Bezpieczeństwo
```

### **KROK 3: Build Docker image**

```bash
# Zbuduj production image
docker compose build spa-webhook

# Sprawdź czy zbudowany
docker images | grep spa_automation
```

### **KROK 4: Uruchom webhook**

```bash
# Start webhook service
docker compose up -d spa-webhook

# Sprawdź status
docker compose ps

# Sprawdź logi
docker compose logs -f spa-webhook
```

### **KROK 5: Test health check**

```bash
# Sprawdź czy działa
curl http://localhost:5000/health

# Powinno zwrócić:
# {
#   "status": "healthy",
#   "service": "SPA Automation",
#   "version": "2.0.0-python"
# }
```

### **KROK 6: Test dry-run (BEZ zmian w Bitrix24)**

```bash
# Wybierz SPA ID do testu (np. 112)
curl http://localhost:5000/webhook/spa/112/dry-run | python3 -m json.tool

# Sprawdź wyniki:
# - status: "dry-run"
# - stats: {...}
# - would_promote: [...]
# - note: "Żadne dane nie zostały zmienione"
```

### **KROK 7: Test produkcyjny (z aktualizacją)**

⚠️ **UWAGA:** To zaktualizuje dane w Bitrix24!

```bash
# Wykonaj na testowym SPA najpierw!
curl http://localhost:5000/webhook/spa/112 | python3 -m json.tool

# Sprawdź w Bitrix24 czy deale zostały przeniesione
```

---

## 🔧 **KONFIGURACJA n8n**

### **Node 1: Schedule Trigger**
```
Cron: */5 * * * *  (co 5 minut)
```

### **Node 2: HTTP Request - Pobierz SPA**
```
URL: https://ralengroup.bitrix24.pl/rest/25031/6cg9uncuyvbxtiq3/crm.item.list
Method: POST
Body:
{
  "entityTypeId": 1032,
  "filter": {
    "STAGE_ID": "DT1032_17:UC_CU0OTZ",
    "ufCrm9_1740930205": ">0"
  },
  "select": ["ID", "TITLE", "ufCrm9_1740930205"]
}
```

### **Node 3: Split SPA Items**
```
Batch size: 1
```

### **Node 4: Wait 1 minute**
```
Wait: 60 seconds
```

### **Node 5: HTTP Request - Wywołaj webhook**
```
URL: http://your-server:5000/webhook/spa/{{ $json.ID }}
Method: GET
```

---

## 📊 **MONITORING**

### **Logi webhook:**
```bash
# Real-time logs
docker compose logs -f spa-webhook

# Ostatnie 100 linii
docker compose logs --tail=100 spa-webhook

# Szukaj błędów
docker compose logs spa-webhook | grep -i error
```

### **Metryki:**
```bash
# Status kontenera
docker compose ps

# Zużycie zasobów
docker stats spa_automation-spa-webhook
```

### **Health check (automated):**
```bash
# Dodaj do crontab na serwerze
*/5 * * * * curl -f http://localhost:5000/health || echo "Webhook down!" | mail -s "ALERT" admin@example.com
```

---

## 🔄 **ROLLBACK (w razie problemów)**

### **Szybki rollback:**
```bash
# Zatrzymaj Python webhook
docker compose down spa-webhook

# Wróć do PHP webhook6.php (jest już działający)
# Żadnych zmian nie trzeba - PHP nadal działa
```

### **Pełny rollback:**
```bash
# Usuń wszystko
docker compose down
docker rmi spa_automation-spa-webhook

# PHP webhook6.php nadal działa bez zmian
```

---

## 🧪 **CHECKLIST PRZED WDROŻENIEM**

- [ ] Testy lokalne przeszły (47/47) ✅
- [ ] Docker image zbudowany ✅
- [ ] .env skonfigurowany z production credentials
- [ ] Health check działa
- [ ] Dry-run test wykonany i sprawdzony
- [ ] Backup PHP webhook6.php istnieje
- [ ] Monitoring skonfigurowany
- [ ] Plan rollback przygotowany
- [ ] Dokumentacja aktualna
- [ ] Team poinformowany

---

## 📞 **WSPARCIE**

### **Logi i debugging:**
```bash
# Wejdź do kontenera
docker compose exec spa-webhook bash

# Python shell (debug)
docker compose run --rm spa-dev python

# Uruchom konkretny test
docker compose run --rm spa-test pytest tests/e2e/ -v -s
```

### **Restart webhook:**
```bash
make restart
```

---

**Gotowy do wdrożenia! Powodzenia! 🚀**

