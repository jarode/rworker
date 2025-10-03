# 🔍 API Discovery - b24pysdk (0.1.0a1)

## ✅ **Potwierdzone działanie API**

### **1. Pobieranie SPA (Smart Process)**

```python
from src.config import get_bitrix_client

client = get_bitrix_client()

# Pobierz SPA
result = client.crm.item.get(
    bitrix_id=112,
    entity_type_id=1032  # SPA = 1032
)

# Struktura response
spa_data = result.result["item"]  # ⚠️ UWAGA: Wynik w kluczu "item"!

# Przykładowe dane:
{
  "id": 112,
  "title": "Jarek PHU MICHAŁ PIECHOCKI...",
  "stageId": "DT1032_17:UC_CU0OTZ",  # W trakcie
  "ufCrm9_1740930205": -134,  # Wolne wszystkie (może być ujemne!)
  "ufCrm9_1740930322": 1,     # Wolne M nasze
  "ufCrm9_1740930346": 0,     # Wolne K nasze
  "ufCrm9_1740930371": -1,    # Wolne PARY nasze
  "ufCrm9_1740930392": -1,    # Wolne M własne
  "ufCrm9_1740930427": -2,    # Wolne K własne
  "ufCrm9_1740930439": 0,     # Wolne PARY własne
  "ufCrm9_1740930520": 55,    # Limit wieku
  "ufCrm9_1740930537": "2026-01-30T03:00:00+03:00",  # Data szkolenia
  "ufCrm9_1740930561": 1875,  # Priority 1 (wartość: Data przyjazdu)
  "ufCrm9_1740930829": 1879,  # Priority 2 (wartość: Wiek)
  "ufCrm9_1740930917": 1897,  # Priority 3 (wartość: Mieszkanie nasze)
  "ufCrm9_1747740109": 1993,  # Czy bezpłciowe? (1991=Tak, 1993=Nie)
}
```

### **2. Lista dealów**

```python
# Podstawowa lista (max 50)
result = client.crm.deal.list(
    filter={
        "STAGE_ID": "C25:UC_5I8UBF",  # Rezerwa
        "UF_CRM_1740931330": "112"     # SPA ID
    },
    select=["ID", "TITLE", "STAGE_ID", "UF_CRM_1743329864"]
)

deals = result.result  # Lista dict, max 50 elementów

# Przykładowy deal:
{
  "ID": "10691",
  "TITLE": "Ірина",
  "STAGE_ID": "C25:UC_5I8UBF",
  "UF_CRM_1743329864": "1957",  # Priorytet 4
  "UF_CRM_1740931330": "105"    # SPA ID
}
```

### **3. Paginacja - wszystkie rekordy**

```python
# ✅ ZALECANE: as_list_fast() - generator (lazy loading)
result = client.crm.deal.list(
    filter={"STAGE_ID": "C25:UC_5I8UBF"}
)

deals_generator = result.as_list_fast().result

# Iteruj przez wszystkie (pobieranie na żądanie)
for deal in deals_generator:
    print(deal["ID"], deal["TITLE"])
    
# Lub zmień na listę (jeśli potrzebne)
deals_list = list(deals_generator)
```

```python
# Alternatywa: as_list() - zwraca pełną listę
deals = result.as_list().result  # List[dict]
```

### **4. Batch operations (do 50 requestów)**

```python
# Przygotuj wiele requestów
batch_requests = {
    "spa_112": client.crm.item.get(bitrix_id=112, entity_type_id=1032),
    "spa_113": client.crm.item.get(bitrix_id=113, entity_type_id=1032),
    "deal_1": client.crm.deal.get(bitrix_id=10691),
}

# Wykonaj wszystkie naraz
batch_result = client.call_batch(batch_requests)

# Wyniki
for key, data in batch_result.result.result.items():
    print(f"{key}: {data}")
```

### **5. Update deala**

```python
result = client.crm.deal.update(
    bitrix_id=10691,
    fields={
        "STAGE_ID": "C25:UC_0LRPVJ"  # Przenieś do Lista Główna
    }
)

success = result.result  # True/False
```

### **6. Metadane pól**

```python
# Pobierz definicje wszystkich pól dla Deal
result = client.crm.deal.fields()
fields = result.result

# Przykład: Pole "Priorytet SPA"
priorytet_field = fields["UF_CRM_1743329864"]
{
  "type": "enumeration",
  "formLabel": "Priorytet SPA",
  "items": [
    {"ID": "1951", "VALUE": "Priorytet 1"},
    {"ID": "1953", "VALUE": "Priorytet 2"},
    {"ID": "1955", "VALUE": "Priorytet 3"},
    {"ID": "1957", "VALUE": "Priorytet 4"}
  ]
}
```

---

## 🎯 **Kluczowe odkrycia**

### **1. Struktura response SPA**
⚠️ **WAŻNE:** SPA zwraca dane w `result.result["item"]`, NIE bezpośrednio w `result.result`!

```python
# ❌ ŹLE
spa_data = result.result
title = spa_data["title"]  # KeyError!

# ✅ DOBRZE
spa_data = result.result["item"]
title = spa_data["title"]  # Działa!
```

### **2. Struktura response Deal**
Deal zwraca listę dict bezpośrednio w `result.result`

```python
# ✅ OK
deals = result.result  # List[dict]
```

### **3. Wolne miejsca mogą być ujemne!**
```python
"ufCrm9_1740930205": -134  # Wolne wszystkie = -134 (przełożone!)
```
Musimy obsłużyć wartości ujemne w logice.

### **4. Priorytety dynamiczne (ID wartości)**

```python
"ufCrm9_1740930561": 1875,  # Priority 1 = 1875 (Data przyjazdu)
"ufCrm9_1740930829": 1879,  # Priority 2 = 1879 (Wiek)
"ufCrm9_1740930917": 1897,  # Priority 3 = 1897 (Mieszkanie nasze)
```

Mapowanie wartości priorytetów (z LOGIKA_AWANSU.md):
- 1867: Sanepid
- 1875: Data przyjazdu
- 1879: Wiek
- 1897: Mieszkanie nasze
- itd.

### **5. Pole bezpłciowe**
```python
"ufCrm9_1747740109": 1993  # 1991 = Tak, 1993 = Nie
```

---

## 📋 **Mapowanie pól (potwierdzone)**

### **SPA (entityTypeId=1032)**
| Pole biznesowe | Kod pola | Typ | Przykład |
|----------------|----------|-----|----------|
| ID | `id` | int | 112 |
| Tytuł | `title` | string | "Jarek PHU..." |
| Etap | `stageId` | string | "DT1032_17:UC_CU0OTZ" |
| Wolne wszystkie | `ufCrm9_1740930205` | int | -134 |
| Wolne M nasze | `ufCrm9_1740930322` | int | 1 |
| Wolne K nasze | `ufCrm9_1740930346` | int | 0 |
| Wolne PARY nasze | `ufCrm9_1740930371` | int | -1 |
| Wolne M własne | `ufCrm9_1740930392` | int | -1 |
| Wolne K własne | `ufCrm9_1740930427` | int | -2 |
| Wolne PARY własne | `ufCrm9_1740930439` | int | 0 |
| Limit wieku | `ufCrm9_1740930520` | int | 55 |
| Data szkolenia | `ufCrm9_1740930537` | datetime | "2026-01-30T03:00:00+03:00" |
| Priority 1 | `ufCrm9_1740930561` | int | 1875 |
| Priority 2 | `ufCrm9_1740930829` | int | 1879 |
| Priority 3 | `ufCrm9_1740930917` | int | 1897 |
| Bezpłciowe? | `ufCrm9_1747740109` | int | 1993 |

### **Deal (Kandydat)**
| Pole biznesowe | Kod pola | Typ | Przykład |
|----------------|----------|-----|----------|
| ID | `ID` | string | "10691" |
| Tytuł | `TITLE` | string | "Ірина" |
| Etap | `STAGE_ID` | string | "C25:UC_5I8UBF" |
| SPA ID | `PARENT_ID_1032` lub `UF_CRM_1740931330` | string | "105" |
| Priorytet SPA | `UF_CRM_1743329864` | string | "1957" |

---

## 🚀 **Następne kroki**

1. ✅ Utworzyć modele Pydantic z tymi polami
2. ✅ Uwzględnić `result["item"]` dla SPA
3. ✅ Obsłużyć ujemne wartości w "wolne miejsca"
4. ✅ Zmapować priorytety dynamiczne
5. ✅ Użyć `as_list_fast()` dla dużych zbiorów

---

**Data:** 2025-10-02  
**SDK:** b24pysdk==0.1.0a1  
**Status:** ✅ Gotowe do implementacji

