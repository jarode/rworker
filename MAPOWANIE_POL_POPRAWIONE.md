# ✅ MAPOWANIE PÓL - POPRAWIONE I POTWIERDZONE

## 🎯 **AKTUALIZOWANE WYMAGANIA**

### **1. DATA PRZYJAZDU - ZAKRES OD-DO**

**Stara logika (webhook6.php):**
```php
// ❌ Tylko sprawdza czy przed szkoleniem
if ($dealArrivalDate < $spaTrainingDate) {
    return true;
}
```

**Nowa logika (poprawiona):**
```python
# ✅ Sprawdza zakres OD-DO + przed szkoleniem

# Warunek:
deal.arrival_date >= spa.arrival_from  # Nie wcześniej niż OD
AND
deal.arrival_date <= spa.arrival_to    # Nie później niż DO  
AND
deal.arrival_date < spa.training_date  # Przed szkoleniem
```

**Pola SPA:**
| Kod techniczny | Nazwa UI | Wartość przykładowa | Opis |
|----------------|----------|---------------------|------|
| `ufCrm9_1740931899` | **Przyjazd OD** | 2026-04-30 | Początek zakresu przyjazdów |
| `ufCrm9_1740931913` | **Przyjazd DO** | 2026-05-15 | Koniec zakresu przyjazdów |
| `ufCrm9_1740930537` | **Data szkolenia** | 2026-01-30 | Data szkolenia (musi być po przyjazdach) |

**Pole Deala:**
| Kod techniczny | Nazwa UI | Wartość przykładowa | Opis |
|----------------|----------|---------------------|------|
| `UF_CRM_1740931256` | **Data przyjazdu** | 2026-05-10 | Planowana data przyjazdu kandydata |

---

### **2. WIEK - RÓWNY LUB NIŻSZY**

**Stara logika (webhook6.php):**
```php
// ❌ Wiek musi być MNIEJSZY (nie równy)
if ($dealAge >= $spaAgeLimit) {
    return false;  // Za stary
}
```

**Nowa logika (poprawiona):**
```python
# ✅ Wiek może być RÓWNY lub MNIEJSZY

# Warunek:
deal.age <= spa.age_limit  # <= zamiast <
```

**Pole SPA:**
| Kod techniczny | Nazwa UI | Wartość przykładowa | Opis |
|----------------|----------|---------------------|------|
| `ufCrm9_1740930520` | **Wiek** | 55 | Maksymalny wiek (włącznie) |

**Pole Deala:**
| Kod techniczny | Nazwa UI | Wartość przykładowa | Opis |
|----------------|----------|---------------------|------|
| `UF_CRM_1740930520` | **Wiek** | 35 | Wiek kandydata |

---

## 📊 **KOMPLETNE MAPOWANIE - WSZYSTKIE POLA**

### **POLA SPA (Smart Process, entityTypeId=1032)**

| Kod techniczny | Nazwa UI | Typ | Opis | Użycie |
|----------------|----------|-----|------|--------|
| `ufCrm9_1740930205` | **Wolne wszystkie** | int | Wolne miejsca ogółem | Główny limit awansu |
| `ufCrm9_1740930322` | **Wolne M nasze** | int | Wolne M + nasze | Limit kategorii |
| `ufCrm9_1740930346` | **Wolne K nasze** | int | Wolne K + nasze | Limit kategorii |
| `ufCrm9_1740930371` | **Wolne PARY nasze** | int | Wolne PARA + nasze | Limit kategorii |
| `ufCrm9_1740930392` | **Wolne M własne** | int | Wolne M + własne | Limit kategorii |
| `ufCrm9_1740930427` | **Wolne K własne** | int | Wolne K + własne | Limit kategorii |
| `ufCrm9_1740930439` | **Wolne PARY własne** | int | Wolne PARA + własne | Limit kategorii |
| `ufCrm9_1740930520` | **Wiek** | int | Limit wieku (<=) | **ZMIENIONE: <= zamiast <** |
| `ufCrm9_1740930537` | **Data szkolenia** | datetime | Data szkolenia | Walidacja < |
| **`ufCrm9_1740931899`** | **Przyjazd OD** | datetime | Początek zakresu | **NOWE: >= (od)** |
| **`ufCrm9_1740931913`** | **Przyjazd DO** | datetime | Koniec zakresu | **NOWE: <= (do)** |
| `ufCrm9_1740930561` | **Priority 1** | enum | Priorytet 1 | Dynamiczne sortowanie |
| `ufCrm9_1740930829` | **Priority 2** | enum | Priorytet 2 | Dynamiczne sortowanie |
| `ufCrm9_1740930917` | **Priority 3** | enum | Priorytet 3 | Dynamiczne sortowanie |
| `ufCrm9_1747740109` | **Bezpłciowe?** | enum | 1991=Tak, 1993=Nie | Typ zamówienia |

### **POLA DEALA (Deal, categoryId=25)**

| Kod techniczny | Nazwa UI | Typ | Opis |
|----------------|----------|-----|------|
| `UF_CRM_1740931256` | **Data przyjazdu** | datetime | Planowana data przyjazdu |
| `UF_CRM_1740930520` | **Wiek** | int | Wiek kandydata |
| `UF_CRM_1740931105` | **Płeć** | enum | 1907=K, 1909=M, 1911=PARA |
| `UF_CRM_1740931164` | **Mieszkanie** | enum | 1917=Własne, 1919=Nasze |
| `UF_CRM_1743329864` | **Priorytet SPA** | enum | 1951=P1, 1953=P2, 1955=P3, 1957=P4 |
| `UF_CRM_1741856527` | **Data EXECUTING** | datetime | Czas dodania do sortowania |
| `UF_CRM_1740931330` | **ID Zamówienie SPA** | string | ID SPA (przypisanie) |

---

## 🔄 **ZMIANY W WALIDACJI**

### **Zmiana 1: Data przyjazdu (ZAKRES)**

**PRZED:**
```python
def check_arrival_date(deal, spa):
    return deal.arrival_date < spa.training_date
```

**PO:**
```python
def check_arrival_date(deal, spa):
    # Sprawdź zakres OD-DO
    if spa.arrival_from and deal.arrival_date:
        if deal.arrival_date < spa.arrival_from:
            return False  # Za wcześnie
    
    if spa.arrival_to and deal.arrival_date:
        if deal.arrival_date > spa.arrival_to:
            return False  # Za późno
    
    # Sprawdź przed szkoleniem
    if spa.training_date and deal.arrival_date:
        if deal.arrival_date >= spa.training_date:
            return False  # Po szkoleniu
    
    return True
```

### **Zmiana 2: Wiek (RÓWNY LUB MNIEJSZY)**

**PRZED:**
```python
def check_age(deal, spa):
    return deal.age < spa.age_limit  # Tylko <
```

**PO:**
```python
def check_age(deal, spa):
    return deal.age <= spa.age_limit  # <= (włącznie)
```

---

## ✅ **DO AKTUALIZACJI W KODZIE**

### **1. Model SPA (src/models/spa.py)**
```python
# Dodać nowe pola:
arrival_from: Optional[datetime] = Field(default=None, alias="ufCrm9_1740931899")
arrival_to: Optional[datetime] = Field(default=None, alias="ufCrm9_1740931913")
```

### **2. Validator (src/business_logic/validators.py)**
```python
# Zaktualizować check_arrival_date()
# Zaktualizować check_age() (< na <=)
```

### **3. Testy (tests/unit/test_validators.py)**
```python
# Dodać testy dla zakresu dat
# Zaktualizować test wieku (równy = PASS)
```

---

**Gotowy do aktualizacji kodu?** 🚀
