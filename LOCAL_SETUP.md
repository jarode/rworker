# 🐍 Lokalne środowisko (bez Dockera)

## Tylko do development/testowania lokalnego

### 1. Utwórz virtualenv
```bash
cd /home/jarek/ralengroup/newsolution/spa_automation

# Python venv
python3 -m venv venv
source venv/bin/activate
```

### 2. Zainstaluj dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 3. Skonfiguruj .env
```bash
cp .env.example .env
# Edytuj .env z właściwymi credentials
```

### 4. Uruchom testy lokalnie
```bash
# Aktywuj venv
source venv/bin/activate

# Uruchom testy
pytest tests/ -v

# Lub konkretny test
pytest tests/unit/test_validators.py -v
```

### 5. Uruchom webhook lokalnie
```bash
source venv/bin/activate
python src/webhook.py
```

---

## ⚠️ Ważne

To podejście działa **TYLKO lokalnie** dla development.

Dla **produkcji** i **CI/CD** nadal używamy **Dockera** (zgodnie z oficjalnym b24pysdk).

Gdy naprawisz Docker Desktop, wróć do:
```bash
make build-dev
make test
```


