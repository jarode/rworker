# 🎯 SZCZEGÓŁOWA ANALIZA: 2 TYPY ZAMÓWIEŃ SPA

## 📋 **IDENTYFIKACJA TYPU ZAMÓWIENIA**

```python
if spa.ufCrm9_1747740109 == 1991:
    # TYP 1: BEZPŁCIOWE
else:
    # TYP 2: PŁCIOWE (1993 lub NULL)
```

---

# 🔵 **TYP 1: ZAMÓWIENIA BEZPŁCIOWE** (ufCrm9_1747740109 = 1991)

## 📊 **KOMPLETNY FLOW**

### **KROK 1: Warunki kwalifikacji** ✅
```python
def qualify_genderless(deal: Deal, spa: SPA) -> bool:
    # ✅ Warunek 1: Data przyjazdu
    if deal.arrival_date >= spa.training_date:
        return False
    
    # ✅ Warunek 2: Wiek
    if deal.age >= spa.age_limit:
        return False
    
    # ⏭️ POMIJA: płeć, mieszkanie, kategorie
    
    return True
```

### **KROK 2: Sortowanie** (2 kryteria)
```python
def sort_genderless(deals: List[Deal]) -> List[Deal]:
    return sorted(deals, key=lambda d: (
        d.get_priority_level(),      # 1. Priorytet SPA (1 > 2 > 3 > 4)
        d.executing_date or MAX_DATE # 2. Data EXECUTING (starsze pierwsze)
    ))
```

### **KROK 3: Awansowanie** (prosty licznik)
```python
def promote_genderless(
    sorted_deals: List[Deal], 
    spa: SPA
) -> List[Deal]:
    limit = max(0, spa.free_all)  # Zabezpieczenie przed ujemnymi
    
    promoted = []
    
    for i, deal in enumerate(sorted_deals):
        if i >= limit:
            break  # Limit wyczerpany
        
        promoted.append(deal)
    
    return promoted
```

### **Przykład:**
```
SPA:
- Wolne wszystkie: 2
- Bezpłciowe: TAK (1991)
- M_nasze: 0 (ignorowane!)
- K_nasze: 0 (ignorowane!)

Deale (po sortowaniu):
1. Deal A - P1, data: 2025-07-09T23:04:08
2. Deal B - P1, data: 2025-07-09T23:06:05
3. Deal C - P1, data: 2025-07-09T23:06:07
4. Deal D - P3, data: 2025-07-09T23:05:54

Wynik:
✅ Awansowano: A, B (pierwsze 2)
❌ Pominięto: C, D (limit = 2)
```

### **Kluczowe cechy:**
- ✅ **PROSTE** - tylko 2 kryteria sortowania
- ✅ **SZYBKIE** - brak sprawdzania kategorii
- ✅ **IGNORUJE** pola płci i mieszkania całkowicie
- ✅ **JEDEN licznik** - tylko globalny limit

---

# 🟢 **TYP 2: ZAMÓWIENIA PŁCIOWE** (ufCrm9_1747740109 = 1993 lub NULL)

## 📊 **KOMPLETNY FLOW**

### **KROK 1: Warunki kwalifikacji** ✅
```python
def qualify_gendered(deal: Deal, spa: SPA) -> bool:
    # ✅ Warunek 1: Data przyjazdu
    if deal.arrival_date >= spa.training_date:
        return False
    
    # ✅ Warunek 2: Wiek
    if deal.age >= spa.age_limit:
        return False
    
    # ✅ Warunek 3: Płeć i mieszkanie określone
    if not deal.gender or not deal.housing:
        return False
    
    # ✅ Warunek 4: Dostępne miejsca w kategorii
    category = deal.get_category_key()  # np. "M_nasze"
    primary_slots = spa.get_free_slots_for_category(category)
    
    if primary_slots > 0:
        return True  # Główna kategoria OK
    
    # Sprawdź alternatywną kategorię (elastyczny przydział)
    alt_category = get_alternative(category)  # "M_nasze" -> "M_wlasne"
    alt_slots = spa.get_free_slots_for_category(alt_category)
    
    return alt_slots > 0
```

### **KROK 2: Sortowanie** (2+ kryteria - na razie uproszczone)
```python
def sort_gendered(deals: List[Deal], spa: SPA) -> List[Deal]:
    # Sortowanie podstawowe (jak bezpłciowe)
    sorted_deals = sorted(deals, key=lambda d: (
        d.get_priority_level(),      # 1. Priorytet SPA (1-4)
        d.executing_date or MAX_DATE # 2. Data EXECUTING
    ))
    
    # TODO: Dodać dynamiczne priorytety z SPA (Priority 1, 2, 3)
    # Zgodnie z liniami 53-56 z LOGIKA_AWANSU.md
    
    return sorted_deals
```

### **KROK 3: Awansowanie** (tracking kategorii!) ⚠️
```python
def promote_gendered(
    sorted_deals: List[Deal], 
    spa: SPA
) -> List[Deal]:
    limit_global = max(0, spa.free_all)
    
    # Inicjalizuj liczniki kategorii
    used_global = 0
    used_categories = {
        "M_nasze": 0,
        "M_wlasne": 0,
        "K_nasze": 0,
        "K_wlasne": 0,
        "PARY_nasze": 0,
        "PARY_wlasne": 0,
    }
    
    promoted = []
    
    for deal in sorted_deals:
        # Sprawdź limit globalny
        if used_global >= limit_global:
            break
        
        # Przydziel kategorię (główna lub alternatywna)
        category = assign_category(deal, spa, used_categories)
        
        if not category:
            continue  # Brak miejsca w żadnej kategorii
        
        # Awansuj
        promoted.append(deal)
        used_global += 1
        used_categories[category] += 1
    
    return promoted


def assign_category(
    deal: Deal, 
    spa: SPA, 
    used_categories: dict
) -> Optional[str]:
    """
    Przydziela kategorię z elastycznym przydziałem
    
    Returns:
        str: Kategoria do której przydzielono (np. "M_nasze")
        None: Brak dostępnych miejsc
    """
    primary_cat = deal.get_category_key()  # np. "M_nasze"
    
    # Sprawdź główną kategorię
    limit_primary = spa.get_free_slots_for_category(primary_cat)
    used_primary = used_categories[primary_cat]
    
    if used_primary < limit_primary:
        return primary_cat  # ✅ Główna dostępna
    
    # Sprawdź alternatywną (elastyczny przydział)
    alt_cat = get_alternative(primary_cat)  # "M_nasze" -> "M_wlasne"
    limit_alt = spa.get_free_slots_for_category(alt_cat)
    used_alt = used_categories[alt_cat]
    
    if used_alt < limit_alt:
        return alt_cat  # ✅ Alternatywna dostępna
    
    return None  # ❌ Brak miejsc
```

### **Przykład:**
```
SPA:
- Wolne wszystkie: 5
- Bezpłciowe: NIE (1993)
- M_nasze: 2
- M_wlasne: 1
- K_nasze: 1
- K_wlasne: 1

Deale (po sortowaniu):
1. Deal A - P1, M+nasze
2. Deal B - P1, M+nasze
3. Deal C - P1, M+nasze (trzeci M+nasze!)
4. Deal D - P2, K+nasze
5. Deal E - P2, K+wlasne
6. Deal F - P3, M+nasze

Przetwarzanie:
1. Deal A → M_nasze (used: 1/2) ✅
2. Deal B → M_nasze (used: 2/2) ✅ (limit M_nasze wyczerpany!)
3. Deal C → M_wlasne (used: 1/1) ✅ (elastyczny przydział!)
4. Deal D → K_nasze (used: 1/1) ✅
5. Deal E → K_wlasne (used: 1/1) ✅ (limit globalny = 5 wyczerpany!)
6. Deal F → ODRZUCONY (limit globalny wyczerpany)

Wynik:
✅ Awansowano: A, B, C, D, E (5 dealów)
❌ Pominięto: F
```

### **Kluczowe cechy:**
- 🔴 **ZŁOŻONE** - tracking wielu liczników
- 🔴 **WOLNIEJSZE** - więcej warunków
- ✅ **SPRAWDZA** płeć i mieszkanie
- ✅ **ELASTYCZNY** - przydział alternatywny
- ✅ **DWA limity** - globalny I kategoria

---

## ⚠️ **KRYTYCZNE RÓŻNICE W IMPLEMENTACJI**

| Aspekt | Bezpłciowe | Płciowe |
|--------|------------|---------|
| **Walidacja płci** | ⏭️ Pomija | ✅ Wymaga |
| **Walidacja mieszkania** | ⏭️ Pomija | ✅ Wymaga |
| **Kategorie miejsc** | ❌ Nie używa | ✅ Używa |
| **Liczniki** | 1 (globalny) | 7 (globalny + 6 kategorii) |
| **Elastyczny przydział** | ❌ Nie | ✅ Tak |
| **Sortowanie** | 2 kryteria | 2+ kryteria (+ dynamiczne) |
| **Limit awansu** | `free_all` | `MIN(free_all, suma_kategorii)` |
| **Kompleksowość** | O(n) | O(n × k) |

---

## 🚨 **BŁĘDY W OBECNYM webhook6.php**

### **Problem 1: Brak liczników kategorii w PŁCIOWYCH**
```php
// ❌ webhook6.php (linia 350)
$dealsToMove = array_slice($deals, 0, $limitMiejsc);
// Po prostu bierze pierwsze N dealów!
// NIE śledzi ile miejsc zostało w każdej kategorii!
```

**Skutek:**
- Może awansować 5 dealów M_nasze gdy limit to tylko 2
- Nadpisuje limity kategorii

**Powinno być:**
```python
for deal in sorted_deals:
    category = assign_category(deal, spa, used)
    if category:
        promote(deal)
        used[category] += 1
```

### **Problem 2: Brak rozróżnienia typów**
```php
// webhook6.php sprawdza bezpłciowe tylko w WALIDACJI
// Ale AWANSOWANIE jest takie samo dla obu typów!
```

**Powinno być:**
```python
if spa.is_genderless_order():
    return promote_genderless(deals, spa)  # Prosty
else:
    return promote_gendered(deals, spa)    # Z kategoriami
```

---

## ✅ **PLAN IMPLEMENTACJI PYTHON**

### **1. Validator (GOTOWY ✅)**
- Walidacja dla obu typów różni się tylko w `check_gender_slots()`
- Bezpłciowe: pomija
- Płciowe: sprawdza kategorie

### **2. Prioritizer (TODO)**
```python
class DealPrioritizer:
    def sort(self, deals: List[Deal], spa: SPA) -> List[Deal]:
        # Różne sortowanie dla różnych typów
        if spa.is_genderless_order():
            return self._sort_genderless(deals)
        else:
            return self._sort_gendered(deals, spa)
```

### **3. Allocator (TODO - KRYTYCZNY!)**
```python
class SlotAllocator:
    def allocate(self, deals: List[Deal], spa: SPA) -> List[Deal]:
        # Różna alokacja dla różnych typów
        if spa.is_genderless_order():
            return self._allocate_genderless(deals, spa)  # Prosty licznik
        else:
            return self._allocate_gendered(deals, spa)    # Tracking kategorii
```

---

## 🎯 **CO ROBIMY DALEJ?**

Mamy teraz **pełne zrozumienie logiki!** Następny krok:

**Implementować DealPrioritizer z testami TDD:**
1. Testy dla bezpłciowego sortowania
2. Testy dla płciowego sortowania  
3. Implementacja obu wersji

**Gotowy kontynuować?** 🚀

