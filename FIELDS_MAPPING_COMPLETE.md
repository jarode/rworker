# 📋 KOMPLETNE MAPOWANIE PÓL - SPA I DEAL

**Status:** ✅ Potwierdzone przez API  
**Data:** 2025-10-02  
**Źródło:** b24pysdk API + dokumentacja

---

## 📦 **POLA DEAL (Kandydat)**

**Entity:** Rekrutacja NEW (categoryId=25)

### **Podstawowe pola**
| Kod techniczny | Nazwa UI | Typ | Wartości enum | Notatki |
|----------------|----------|-----|---------------|---------|
| `ID` | ID | string | - | Unikalny identyfikator |
| `TITLE` | Tytuł | string | - | Imię i nazwisko |
| `STAGE_ID` | Etap | string | C25:UC_* | Status deala |

### **Przypisanie do SPA**
| Kod techniczny | Nazwa UI | Typ | Notatki |
|----------------|----------|-----|---------|
| `PARENT_ID_1032` | - | string | Relacja do SPA (preferowane) |
| `UF_CRM_1740931330` | ID Zamówienie SPA | string | Backup field |

### **Dane kandydata**
| Kod techniczny | Nazwa UI | Typ | Wartości enum |
|----------------|----------|-----|---------------|
| **`UF_CRM_1669643033481`** | **Wiek** | double | - |
| `UF_CRM_1740931256` | Data przyjazdu | date | - |
| `UF_CRM_1740931105` | Płeć | enumeration | 1907=K, 1909=M, 1911=PARA |
| `UF_CRM_1740931164` | Mieszkanie | enumeration | 1917=Własne, 1919=Nasze |

### **Priorytetyzacja**
| Kod techniczny | Nazwa UI | Typ | Wartości enum |
|----------------|----------|-----|---------------|
| `UF_CRM_1743329864` | Priorytet SPA | enumeration | 1951=P1, 1953=P2, 1955=P3, 1957=P4 |
| `UF_CRM_1741856527` | Czas dodania - sortowanie | datetime | - |
| `UF_CRM_1740931132` | Sanepid | enumeration | 1913=Tak, 1915=Nie |
| `UF_CRM_1740931312` | Polecenie pracy | enumeration | 1925=Tak, 1927=Nie |
| `UF_CRM_1740931210` | Pośrednik | enumeration | 1921=Tak, 1923=Nie |
| `UF_CRM_1748981275` | Powrót | enumeration | 1999=Tak, 2001=Nie |
| `UF_CRM_1748981302` | Doświadczenie | enumeration | 2003=Tak, 2005=Nie |
| `UF_CRM_1748981451` | Koordynator | enumeration | 2007=Tak, 2009=Nie |

---

## 📦 **POLA SPA (Smart Process Automation)**

**Entity:** Smart Process (entityTypeId=1032)

### **Limity miejsc (wolne)**
| Kod techniczny | Nazwa UI (przypuszczalna) | Wartość przykład | Notatki |
|----------------|---------------------------|------------------|---------|
| `ufCrm9_1740930205` | Wolne wszystkie | -134 | ⚠️ Może być ujemne! |
| `ufCrm9_1740930322` | Wolne M nasze | 1 | - |
| `ufCrm9_1740930346` | Wolne K nasze | 0 | - |
| `ufCrm9_1740930371` | Wolne PARY nasze | -1 | - |
| `ufCrm9_1740930392` | Wolne M własne | -1 | - |
| `ufCrm9_1740930427` | Wolne K własne | -2 | - |
| `ufCrm9_1740930439` | Wolne PARY własne | 0 | - |

### **Limity miejsc (całkowite)**
| Kod techniczny | Nazwa UI (przypuszczalna) | Wartość przykład |
|----------------|---------------------------|------------------|
| `ufCrm9_1740930456` | Liczba miejsc | 3 |
| `ufCrm9_1740930468` | Mężczyźni | 2 |
| `ufCrm9_1740930480` | Kobiety | 1 |
| `ufCrm9_1740930495` | Pary | 0 |

### **Warunki kwalifikacji**
| Kod techniczny | Nazwa UI | Typ | Wartość przykład | Użycie |
|----------------|----------|-----|------------------|--------|
| **`ufCrm9_1740930520`** | **Wiek (limit)** | int | 55 | **Wiek <= limit** |
| **`ufCrm9_1740930537`** | **Data szkolenia** | datetime | 2026-01-30 | Przyjazd < szkolenie |
| **`ufCrm9_1740931899`** | **Przyjazd OD** | datetime | 2026-04-30 | **Przyjazd >= OD** |
| **`ufCrm9_1740931913`** | **Przyjazd DO** | datetime | NULL | **Przyjazd <= DO** |

### **Priorytety dynamiczne**
| Kod techniczny | Nazwa UI | Typ | Wartość przykład | Notatki |
|----------------|----------|-----|------------------|---------|
| `ufCrm9_1740930561` | Priority 1 | enum_id | 1875 | Zobacz SPAPriorityType |
| `ufCrm9_1740930829` | Priority 2 | enum_id | 1879 | Zobacz SPAPriorityType |
| `ufCrm9_1740930917` | Priority 3 | enum_id | 1897 | Zobacz SPAPriorityType |

### **Specjalne flagi**
| Kod techniczny | Nazwa UI | Typ | Wartości | Notatki |
|----------------|----------|-----|----------|---------|
| `ufCrm9_1747740109` | Bezpłciowe? | enum_id | 1991=Tak, 1993=Nie | Typ zamówienia |

---

## ✅ **POPRAWIONE MAPOWANIE - KLUCZOWE ZMIANY**

### **ZMIANA 1: Pole wieku w DEAL**
```diff
- UF_CRM_1740930520  # ❌ NIE ISTNIEJE w Deal!
+ UF_CRM_1669643033481  # ✅ POPRAWNE pole wieku
```

### **ZMIANA 2: Zakres dat przyjazdu**
```diff
+ ufCrm9_1740931899  # Przyjazd OD (nowe!)
+ ufCrm9_1740931913  # Przyjazd DO (nowe!)
  ufCrm9_1740930537  # Data szkolenia (istniejące)
```

### **ZMIANA 3: Walidacja wieku**
```diff
- deal.age < spa.age_limit   # ❌ Tylko mniejszy
+ deal.age <= spa.age_limit  # ✅ Równy lub mniejszy
```

---

## 🎯 **NOWA LOGIKA WALIDACJI**

### **Warunek 1: Data przyjazdu (ZAKRES)**
```python
def check_arrival_date(deal: Deal, spa: SPA) -> bool:
    if not deal.arrival_date:
        return True  # Brak daty = PASS
    
    # 1. Sprawdź czy w zakresie OD-DO
    if spa.arrival_from:
        if deal.arrival_date < spa.arrival_from:
            return False  # Za wcześnie
    
    if spa.arrival_to:
        if deal.arrival_date > spa.arrival_to:
            return False  # Za późno
    
    # 2. Sprawdź przed szkoleniem
    if spa.training_date:
        if deal.arrival_date >= spa.training_date:
            return False  # Po szkoleniu
    
    return True
```

### **Warunek 2: Wiek (WŁĄCZNIE)**
```python
def check_age(deal: Deal, spa: SPA) -> bool:
    if not spa.age_limit or not deal.age:
        return True
    
    # <= zamiast <
    return deal.age <= spa.age_limit
```

---

## 📊 **PRZYKŁADY**

### **Przykład 1: Data przyjazdu (PASS)**
```
SPA:
  - Przyjazd OD: 2026-04-01
  - Przyjazd DO: 2026-04-30
  - Data szkolenia: 2026-05-15

Deal:
  - Data przyjazdu: 2026-04-15

Walidacja:
  ✅ 2026-04-15 >= 2026-04-01 (po OD)
  ✅ 2026-04-15 <= 2026-04-30 (przed DO)
  ✅ 2026-04-15 < 2026-05-15 (przed szkoleniem)
  
Wynik: PASS ✅
```

### **Przykład 2: Data przyjazdu (FAIL - za wcześnie)**
```
Deal: 2026-03-25

Walidacja:
  ❌ 2026-03-25 < 2026-04-01 (przed OD!)
  
Wynik: FAIL ❌
```

### **Przykład 3: Wiek (PASS - równy)**
```
SPA:
  - Limit wieku: 45

Deal:
  - Wiek: 45

Walidacja:
  ✅ 45 <= 45 (równy OK!)
  
Wynik: PASS ✅
```

### **Przykład 4: Wiek (FAIL - za stary)**
```
Deal:
  - Wiek: 46

Walidacja:
  ❌ 46 > 45
  
Wynik: FAIL ❌
```

---

## 🔄 **AKTUALIZACJE DO WYKONANIA**

### **1. Model SPA**
```python
# src/models/spa.py
arrival_from: Optional[datetime] = Field(default=None, alias="ufCrm9_1740931899")
arrival_to: Optional[datetime] = Field(default=None, alias="ufCrm9_1740931913")
```

### **2. Model Deal**
```python
# src/models/deal.py  
age: Optional[float] = Field(default=None, alias="UF_CRM_1669643033481")  # POPRAWIONE!
```

### **3. Validator**
```python
# src/business_logic/validators.py
# Zaktualizować check_arrival_date() - dodać zakres
# Zaktualizować check_age() - zmienić < na <=
```

### **4. Testy**
```python
# tests/unit/test_validators.py
# Dodać testy dla zakresu dat (OD-DO)
# Zaktualizować test wieku (równy = PASS)
```

---

**Gotowy do aktualizacji?** 🚀

