# 🐍 SPA Automation - Python + b24pysdk

Automatyzacja procesu rekrutacji SPA z wykorzystaniem oficjalnego **Bitrix24 Python SDK**.

## 🐳 **Docker-only Development**

Zgodnie z oficjalnym podejściem [b24pysdk](https://github.com/bitrix24/b24pysdk):
- **Wszystko działa w Docker** - brak lokalnych instalacji Python
- **Dev image** - szybka iteracja z mounted volumes
- **Test image** - dedykowany do testów
- **Webhook image** - deployment produkcyjny

## 🚀 **Quick Start**

### 1. **Konfiguracja**
```bash
# Skopiuj przykładową konfigurację
cp .env.example .env

# Edytuj .env z właściwymi credentials
nano .env
```

### 2. **Build Docker image**
```bash
# Zbuduj dev image (tylko raz)
make build-dev

# Lub wszystkie images
make build
```

### 3. **Uruchom testy**
```bash
# Wszystkie testy
make test

# Tylko unit testy
make test-unit

# Tylko integration testy
make test-integration
```

### 4. **Development**
```bash
# Otwórz shell w dev container
make shell

# Lub uruchom dev container interaktywnie
make run-dev
```

### 5. **Uruchom webhook**
```bash
# Start webhook service (port 5000)
make up

# Zatrzymaj
make down

# Restart
make restart

# Logi
make logs
```

## 📁 **Struktura projektu**

```
spa_automation/
├── Dockerfile              # Docker image definition
├── docker-compose.yml      # Services: dev, webhook, test
├── Makefile               # Commands (make help)
├── requirements.txt       # Python dependencies
├── .env.example          # Example configuration
├── .env                  # Your configuration (gitignored)
│
├── src/
│   ├── __init__.py
│   ├── config.py         # Bitrix24 client setup
│   ├── models/           # Pydantic models
│   ├── services/         # Business logic
│   ├── business_logic/   # Validators, prioritizers
│   └── webhook.py        # Flask endpoint
│
└── tests/
    ├── unit/             # Unit tests
    ├── integration/      # Integration tests
    └── e2e/              # End-to-end tests
```

## 🛠️ **Dostępne komendy (Makefile)**

```bash
make help              # Pokaż wszystkie komendy
make build-dev         # Zbuduj dev image
make build             # Zbuduj wszystkie images
make test              # Uruchom testy
make test-unit         # Tylko unit testy
make test-integration  # Tylko integration testy
make lint              # Lintery (flake8, mypy)
make format            # Format kodu (black, isort)
make run-webhook       # Uruchom webhook service
make shell             # Otwórz bash w container
make clean             # Wyczyść cache
make logs              # Pokaż logi webhook
make ps                # Status containers
make up                # Start webhook
make down              # Stop wszystko
make restart           # Restart webhook
```

## 🧪 **Workflow TDD**

### 1. **Napisz test**
```python
# tests/unit/test_validators.py
def test_arrival_date_validation():
    # Given
    spa = SPA(training_date="2025-10-15")
    deal = Deal(arrival_date="2025-10-10")
    
    # When
    validator = QualificationValidator()
    result = validator.check_arrival_date(deal, spa)
    
    # Then
    assert result == True
```

### 2. **Uruchom test (Red)**
```bash
make test-unit
# FAILED - brak implementacji
```

### 3. **Implementuj kod**
```python
# src/business_logic/validators.py
class QualificationValidator:
    def check_arrival_date(self, deal, spa):
        return deal.arrival_date < spa.training_date
```

### 4. **Uruchom test (Green)**
```bash
make test-unit
# PASSED ✅
```

### 5. **Refactor (optional)**
```bash
make format  # Auto-format
make lint    # Check code quality
```

## 🔧 **Konfiguracja (.env)**

```env
# Bitrix24
BITRIX_DOMAIN=ralengroup.bitrix24.pl
BITRIX_USER_ID=25031
BITRIX_WEBHOOK_KEY=your_webhook_key

# Flask
FLASK_ENV=development
FLASK_DEBUG=1
FLASK_PORT=5000
```

## 📊 **Użycie b24pysdk**

### Podstawowe operacje:
```python
from src.config import get_bitrix_client

client = get_bitrix_client()

# Pobierz SPA
spa = client.crm.item.get(entityTypeId=1032, id=112)

# Lista dealów (z auto-pagination)
deals = client.crm.deal.list(
    filter={"STAGE_ID": "C25:UC_5I8UBF"}
).as_list_fast().result

# Batch update (do 50 naraz)
requests = {
    f"deal_{id}": client.crm.deal.update(
        bitrix_id=id,
        fields={"STAGE_ID": "C25:UC_0LRPVJ"}
    )
    for id in deal_ids
}
results = client.call_batch(requests)
```

## 🎯 **Deployment**

### Lokalny development:
```bash
make run-dev
```

### Produkcja (Docker):
```bash
make up
# Webhook dostępny na http://localhost:5000
```

### n8n integration:
```
Webhook URL: http://your-server:5000/webhook/spa/<spa_id>
Method: POST/GET
```

## 📚 **Dokumentacja**

- [b24pysdk GitHub](https://github.com/bitrix24/b24pysdk)
- [Bitrix24 REST API](https://dev.1c-bitrix24.com/rest_help/)
- Dokumentacja biznesowa: `../LOGIKA_AWANSU.md`, `../SPA_RULES.md`

## 🐛 **Troubleshooting**

### Container nie startuje:
```bash
make clean
make build
```

### Testy failują:
```bash
# Sprawdź logi
docker-compose logs spa-test

# Uruchom shell i debug
make shell
pytest tests/ -v --pdb
```

### Problemy z permissions:
```bash
# Fix ownership
sudo chown -R $USER:$USER .
```

---

**Status:** 🟢 Ready for development  
**Stack:** Python 3.12 + b24pysdk + Docker + pytest  
**Pattern:** TDD + Clean Architecture


