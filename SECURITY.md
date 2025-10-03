# 🔒 SECURITY - SPA AUTOMATION

## ⚠️ **WAŻNE: NIE UDOSTĘPNIAJ WEBHOOK KEY!**

### **Co NIE robić:**
- ❌ Nie commituj pliku `.env` do Git
- ❌ Nie udostępniaj `BITRIX_WEBHOOK_KEY` publicznie
- ❌ Nie wklejaj webhook key w dokumentacji
- ❌ Nie zostawiaj webhook key w logach

### **Co robić:**
- ✅ Używaj `.env.example` jako template
- ✅ Ustaw webhook key jako environment variable
- ✅ Użyj `.gitignore` żeby wykluczyć `.env`
- ✅ W Railway ustaw environment variables w dashboard

---

## 🔧 **KONFIGURACJA BEZPIECZEŃSTWA**

### **1. Environment Variables:**
```bash
# Lokalnie - stwórz .env (nie commituj!)
cp .env.example .env
# Edytuj .env i ustaw prawdziwe wartości

# Railway - ustaw w dashboard:
BITRIX_DOMAIN=ralengroup.bitrix24.pl
BITRIX_USER_ID=25031
BITRIX_WEBHOOK_KEY=6cg9uncuyvbxtiq3
LOG_LEVEL=INFO
```

### **2. Git Security:**
```bash
# Sprawdź czy .env jest w .gitignore
grep -q "\.env" .gitignore && echo "✅ .env jest ignorowany" || echo "❌ Dodaj .env do .gitignore"

# Sprawdź co jest commitowane
git status
```

### **3. Railway Security:**
- Environment variables są szyfrowane
- Nie są widoczne w logach
- Dostęp tylko dla właściciela projektu

---

## 🚨 **JEŚLI WEBHOOK KEY ZOSTAŁ UDOSTĘPNIONY:**

### **Natychmiastowe działania:**
1. **Wygeneruj nowy webhook key** w Bitrix24
2. **Zaktualizuj environment variables** w Railway
3. **Usuń stary key** z Bitrix24
4. **Sprawdź logi** czy nie było nieautoryzowanych requestów

### **W Bitrix24:**
1. Idź do **Settings** → **Development** → **Webhooks**
2. **Usuń stary webhook**
3. **Utwórz nowy webhook** z nowym key
4. **Zaktualizuj environment variables** wszędzie

---

## 🔍 **SPRAWDZENIE BEZPIECZEŃSTWA**

### **Przed commitem:**
```bash
# Sprawdź czy .env jest ignorowany
git check-ignore .env && echo "✅ .env jest bezpieczny" || echo "❌ .env może być commitowany!"

# Sprawdź co będzie commitowane
git add -n .
```

### **Po commicie:**
```bash
# Sprawdź historię commitów
git log --oneline -10

# Sprawdź czy webhook key jest w historii
git log -p | grep -i "6cg9uncuyvbxtiq3" && echo "❌ WEBHOOK KEY W HISTORII!" || echo "✅ Webhook key nie jest w historii"
```

---

## 📋 **CHECKLIST BEZPIECZEŃSTWA**

### **Przed push do GitHub:**
- [ ] ✅ `.env` jest w `.gitignore`
- [ ] ✅ `.env.example` ma placeholder values
- [ ] ✅ Webhook key nie jest w kodzie
- [ ] ✅ Webhook key nie jest w dokumentacji
- [ ] ✅ `git status` nie pokazuje `.env`

### **Po deployment na Railway:**
- [ ] ✅ Environment variables ustawione w Railway
- [ ] ✅ Webhook key ustawiony jako environment variable
- [ ] ✅ `.env` nie jest w repozytorium
- [ ] ✅ Test webhook działa z Railway

---

## 🎯 **BEST PRACTICES**

### **Development:**
```bash
# Zawsze używaj .env.example
cp .env.example .env
# Edytuj .env lokalnie (nie commituj!)

# Sprawdź przed commitem
git status
git check-ignore .env
```

### **Production:**
```bash
# Railway dashboard → Variables
BITRIX_DOMAIN=ralengroup.bitrix24.pl
BITRIX_USER_ID=25031
BITRIX_WEBHOOK_KEY=6cg9uncuyvbxtiq3
LOG_LEVEL=INFO
```

### **Documentation:**
```bash
# Zawsze używaj placeholder values
BITRIX_WEBHOOK_KEY=your_webhook_key_here
# NIGDY nie używaj prawdziwych wartości w dokumentacji
```

---

## 🔐 **DODATKOWE ZABEZPIECZENIA**

### **1. Rate Limiting:**
- Webhook ma wbudowane rate limiting
- Maksymalnie 1 request na minutę per SPA
- Timeout 30 sekund

### **2. Input Validation:**
- Wszystkie inputy są walidowane
- Pydantic models zapewniają type safety
- SQL injection protection (nie używamy SQL)

### **3. Error Handling:**
- Błędy nie ujawniają wrażliwych danych
- Logi nie zawierają webhook key
- Graceful degradation

---

## 📞 **SUPPORT**

### **Jeśli masz problemy z bezpieczeństwem:**
1. **Natychmiast** wygeneruj nowy webhook key
2. **Zaktualizuj** environment variables
3. **Sprawdź** logi Bitrix24
4. **Skontaktuj się** z administratorem

### **Kontakt:**
- **Bitrix24 Support:** [support.bitrix24.com](https://support.bitrix24.com)
- **Railway Support:** [docs.railway.app](https://docs.railway.app)

---

**BEZPIECZEŃSTWO TO PRIORYTET! 🔒**
