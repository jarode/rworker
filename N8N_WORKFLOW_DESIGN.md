# 🔄 N8N WORKFLOW - SPA AUTOMATION

## 📋 **OPIS WORKFLOW**

### **Cel:**
Automatyczne uruchamianie webhook Python SPA co 5 minut dla wszystkich SPA "W trakcie" z wolnymi miejscami > 0.

---

## 🏗️ **STRUKTURA WORKFLOW**

### **1. TRIGGER - Schedule Trigger**
```
Node: "Schedule SPA Processing"
Type: Schedule Trigger
Settings:
  - Interval: 5 minutes
  - Timezone: Europe/Warsaw
```

### **2. GET SPA LIST - HTTP Request**
```
Node: "Get Active SPA List"
Type: HTTP Request
Settings:
  - URL: https://ralengroup.bitrix24.pl/rest/25031/6cg9uncuyvbxtiq3/crm.item.list
  - Method: POST
  - Body (JSON):
    {
      "entityTypeId": 1032,
      "filter": {
        "STAGE_ID": "DT1032_17:UC_CU0OTZ"
      },
      "select": [
        "ID", 
        "TITLE", 
        "ufCrm9_1740930205",
        "ufCrm9_1747740109"
      ]
    }
```

### **3. FILTER SPA - IF Node**
```
Node: "Filter SPA with Free Slots"
Type: IF
Condition:
  - {{ $json.ufCrm9_1740930205 }} > 0
  - AND {{ $json.ufCrm9_1740930205 }} != null
```

### **4. SPLIT SPA - Split In Batches**
```
Node: "Split SPA for Processing"
Type: Split In Batches
Settings:
  - Batch Size: 1
  - Options: 
    - Reset: false
    - Wait: true
```

### **5. DELAY BETWEEN REQUESTS - Wait**
```
Node: "Wait 1 Minute"
Type: Wait
Settings:
  - Wait Time: 1 minute
  - Resume: On Webhook
```

### **6. CALL PYTHON WEBHOOK - HTTP Request**
```
Node: "Process SPA Webhook"
Type: HTTP Request
Settings:
  - URL: http://localhost:5000/webhook/spa/{{ $json.id }}
  - Method: GET
  - Timeout: 30 seconds
  - Retry: 3 attempts
```

### **7. LOG RESULTS - Set Node**
```
Node: "Log Processing Results"
Type: Set
Settings:
  - Keep Only Set: true
  - Values:
    - spa_id: {{ $json.id }}
    - spa_title: {{ $json.title }}
    - timestamp: {{ new Date().toISOString() }}
    - webhook_response: {{ $('Process SPA Webhook').item.json }}
```

---

## 🔄 **FLOW LOGIC**

### **Krok po kroku:**

1. **Co 5 minut** → Trigger startuje workflow
2. **Pobierz SPA** → Lista wszystkich SPA "W trakcie"
3. **Filtruj** → Tylko SPA z wolnymi miejscami > 0
4. **Dla każdego SPA:**
   - Czekaj 1 minutę (opcjonalnie)
   - Wywołaj webhook Python
   - Zapisz wynik
5. **Koniec** → Czekaj na następny trigger

---

## ⚙️ **KONFIGURACJA N8N**

### **Environment Variables:**
```bash
# W ustawieniach n8n
BITRIX_DOMAIN=ralengroup.bitrix24.pl
BITRIX_USER_ID=25031
BITRIX_WEBHOOK_KEY=6cg9uncuyvbxtiq3
PYTHON_WEBHOOK_URL=http://localhost:5000
```

### **Error Handling:**
- **Retry:** 3 próby dla każdego webhook
- **Timeout:** 30 sekund na request
- **Continue on Error:** Tak (nie zatrzymuj całego workflow)

---

## 📊 **MONITORING & LOGGING**

### **Co logować:**
- Timestamp uruchomienia
- Lista przetworzonych SPA
- Wyniki każdego webhook (success/error)
- Liczba awansowanych dealów
- Błędy i timeouty

### **Alerty:**
- Email/Slack gdy webhook zwróci błąd
- Dashboard z statystykami

---

## 🎯 **ADVANCED FEATURES**

### **1. Conditional Processing:**
```
Dodaj warunek:
- Tylko w godzinach pracy (8:00-18:00)
- Pomijaj weekendy
- Rate limiting (max 10 SPA na raz)
```

### **2. Webhook Response Processing:**
```
Sprawdź response:
- Jeśli promoted > 0 → wyślij notyfikację
- Jeśli error → retry po 5 minutach
- Loguj szczegóły do bazy danych
```

### **3. Integration z Bitrix24:**
```
Dodatkowe webhook:
- Aktualizuj pole "Ostatnie przetworzenie" w SPA
- Twórz komentarz w dealach które zostały awansowane
```

---

## 🚀 **DEPLOYMENT**

### **1. Import do n8n:**
```bash
# Skopiuj JSON workflow do n8n
# Aktywuj workflow
# Ustaw credentials
```

### **2. Test:**
```bash
# Uruchom manualnie
# Sprawdź logi
# Zweryfikuj wyniki w Bitrix24
```

### **3. Production:**
```bash
# Aktywuj schedule
# Monitoruj przez pierwsze godziny
# Skonfiguruj alerty
```

---

## 📈 **EXPECTED RESULTS**

### **Typowe wykonanie:**
```
Trigger: Co 5 minut
Duration: ~2-5 minut (zależnie od liczby SPA)
SPA processed: 0-6 (zależnie od dostępności)
Deals promoted: 0-20 (zależnie od kwalifikacji)
Errors: < 1% (przy stabilnym systemie)
```

### **Monitoring:**
- **Success Rate:** > 95%
- **Response Time:** < 30s per SPA
- **Uptime:** 24/7 (z wyjątkami maintenance)

---

## 🔧 **TROUBLESHOOTING**

### **Common Issues:**
1. **Python webhook nie odpowiada**
   - Sprawdź czy Docker container działa
   - Sprawdź logi: `docker compose logs spa-webhook`

2. **Bitrix24 API timeout**
   - Zwiększ timeout w HTTP Request
   - Dodaj retry logic

3. **Zbyt wiele requestów**
   - Zwiększ delay między requestami
   - Dodaj rate limiting

### **Debug Mode:**
```
Temporary settings:
- Interval: 1 minute (dla testów)
- Batch Size: 1
- Detailed logging: ON
```

---

## 📋 **CHECKLIST PRZED DEPLOYMENT**

- [ ] Python webhook działa i odpowiada
- [ ] Bitrix24 credentials są poprawne
- [ ] n8n ma dostęp do localhost:5000
- [ ] Workflow został przetestowany manualnie
- [ ] Error handling jest skonfigurowany
- [ ] Monitoring/alerty są ustawione
- [ ] Backup plan (manual processing) jest gotowy

---

**Ten workflow zapewni pełną automatyzację procesu SPA! 🎯**
