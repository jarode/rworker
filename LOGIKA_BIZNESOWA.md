# 📋 LOGIKA BIZNESOWA SYSTEMU SPA

## 🎯 **DWA TYPY ZAMÓWIEŃ**

System rozróżnia **dwa całkowicie różne** przepływy przetwarzania:

1. **Zamówienia BEZPŁCIOWE** - uproszczona logika
2. **Zamówienia PŁCIOWE** - pełna logika z kategoriami

---

## 🔵 **TYP 1: ZAMÓWIENIA BEZPŁCIOWE**

### **Warunek:**
```python
ufCrm9_1747740109 == 1991  # "Tak"
```

### **Logika przetwarzania:**

#### **1. Warunki kwalifikacji (uproszczone):**
```
✅ Data przyjazdu < Data szkolenia
✅ Wiek < Limit wieku
⏭️  POMIJA całkowicie: płeć, mieszkanie, kategorie miejsc
```

#### **2. Sortowanie:**
```
1. Priorytet SPA (1 > 2 > 3 > 4)
2. Czas dodania do EXECUTING (starsze pierwsze)
```

#### **3. Awansowanie:**
```
Limit = "Wolne wszystkie" (ufCrm9_1740930205)

while (licznik < limit AND są deale):
    awansuj_deal()
    licznik++
```

#### **4. Kluczowe różnice:**
- ❌ **NIE sprawdza** pól płci (`UF_CRM_1740931105`)
- ❌ **NIE sprawdza** pól mieszkania (`UF_CRM_1740931164`)
- ❌ **NIE używa** pól kategorii (M_nasze, K_nasze, itd.)
- ✅ **Używa TYLKO** głównego limitu "Wolne wszystkie"
- ✅ **Prostsze** sortowanie (tylko 2 kryteria)

#### **5. Pseudokod:**
```python
def process_genderless_spa(spa: SPA, deals: List[Deal]) -> List[Deal]:
    # Krok 1: Filtruj według podstawowych warunków
    qualified = [
        d for d in deals 
        if d.arrival_date < spa.training_date 
        and d.age < spa.age_limit
    ]
    
    # Krok 2: Sortuj
    sorted_deals = sort_by_priority_and_date(qualified)
    
    # Krok 3: Awansuj do limitu
    promoted = sorted_deals[:spa.free_all]
    
    return promoted
```

---

## 🟢 **TYP 2: ZAMÓWIENIA PŁCIOWE**

### **Warunek:**
```python
ufCrm9_1747740109 == 1993  # "Nie" (lub NULL)
```

### **Logika przetwarzania:**

#### **1. Warunki kwalifikacji (pełne):**
```
✅ Data przyjazdu < Data szkolenia
✅ Wiek < Limit wieku
✅ Płeć i mieszkanie określone
✅ Dostępne miejsca w kategorii (głównej LUB alternatywnej)
```

#### **2. Kategorie miejsc:**
```
Deal.płeć + Deal.mieszkanie → Kategoria miejsca

Mapowanie:
- M (1909) + Nasze (1919) → "M_nasze" → ufCrm9_1740930322
- M (1909) + Własne (1917) → "M_wlasne" → ufCrm9_1740930392
- K (1907) + Nasze (1919) → "K_nasze" → ufCrm9_1740930346
- K (1907) + Własne (1917) → "K_wlasne" → ufCrm9_1740930427
- PARA (1911) + Nasze (1919) → "PARY_nasze" → ufCrm9_1740930371
- PARA (1911) + Własne (1917) → "PARY_wlasne" → ufCrm9_1740930439
```

#### **3. Elastyczny przydział miejsc:**
```
Priorytet: Główna kategoria → Alternatywna kategoria

Przykład:
Deal chce: M + Nasze (M_nasze)

if (wolne_M_nasze > 0):
    przydziel_do("M_nasze")
elif (wolne_M_wlasne > 0):  # Alternatywa
    przydziel_do("M_wlasne")
else:
    odrzuć_deala()
```

#### **4. Sortowanie:**
```
1. Priorytet SPA (1 > 2 > 3 > 4)
2. Czas dodania do EXECUTING (starsze pierwsze)
3. Dynamiczne priorytety z SPA (TODO - nie zaimplementowane!)
```

#### **5. Awansowanie z licznikami kategorii:**
```
Limity:
- Globalny: "Wolne wszystkie" (ufCrm9_1740930205)
- Kategoria: np. "M_nasze" (ufCrm9_1740930322)

Liczniki (tracking):
- used_global = 0
- used_categories = {
    "M_nasze": 0,
    "K_nasze": 0,
    ...
  }

for deal in sorted_deals:
    if used_global >= limit_global:
        break  # Globalny limit wyczerpany
    
    category = get_category(deal)
    category_limit = get_category_limit(spa, category)
    
    if used_categories[category] >= category_limit:
        # Spróbuj alternatywy
        alt_category = get_alternative(category)
        if used_categories[alt_category] < get_category_limit(spa, alt_category):
            category = alt_category  # Użyj alternatywnej
        else:
            continue  # Pomiń - brak miejsc
    
    # Awansuj
    awansuj_deal(deal, category)
    used_global += 1
    used_categories[category] += 1
```

#### **6. Kluczowe różnice:**
- ✅ **SPRAWDZA** płeć i mieszkanie
- ✅ **UŻYWA** limitów kategorii
- ✅ **Śledzi** liczniki kategorii podczas awansowania
- ✅ **Elastyczny przydział** - jeśli główna pełna → alternatywna
- ⚠️ **Bardziej skomplikowane** - więcej warunków i edge cases

#### **7. Pseudokod:**
```python
def process_gendered_spa(spa: SPA, deals: List[Deal]) -> List[Deal]:
    # Krok 1: Filtruj według wszystkich warunków
    qualified = [
        d for d in deals 
        if d.arrival_date < spa.training_date 
        and d.age < spa.age_limit
        and d.gender is not None
        and d.housing is not None
        and (has_slots_in_category(d, spa) or has_slots_in_alternative(d, spa))
    ]
    
    # Krok 2: Sortuj
    sorted_deals = sort_by_priority_and_date(qualified)
    
    # Krok 3: Awansuj z tracking kategorii
    promoted = []
    used_global = 0
    used_categories = {cat: 0 for cat in CATEGORIES}
    
    for deal in sorted_deals:
        if used_global >= spa.free_all:
            break
        
        # Przydziel kategorię (główna lub alternatywna)
        category = allocate_category(deal, spa, used_categories)
        
        if category:
            promoted.append(deal)
            used_global += 1
            used_categories[category] += 1
    
    return promoted
```

---

## 📊 **PORÓWNANIE TYPÓW**

| Aspekt | Bezpłciowe (1991) | Płciowe (1993) |
|--------|-------------------|----------------|
| **Sprawdza płeć** | ❌ NIE | ✅ TAK |
| **Sprawdza mieszkanie** | ❌ NIE | ✅ TAK |
| **Używa kategorii** | ❌ NIE | ✅ TAK |
| **Elastyczny przydział** | ❌ NIE | ✅ TAK |
| **Liczniki kategorii** | ❌ NIE | ✅ TAK |
| **Limit globalny** | ✅ TAK | ✅ TAK |
| **Kompleksowość** | 🟢 PROSTA | 🔴 ZŁOŻONA |
| **Warunki** | 2 | 4+ |
| **Sortowanie** | 2 kryteria | 2+ kryteria |

---

## 🔧 **IMPLEMENTACJA W KODZIE**

### **Walidacja (już zaimplementowane ✅):**
```python
# src/business_logic/validators.py
class QualificationValidator:
    
    def check_gender_slots(self, deal: Deal, spa: SPA) -> bool:
        # BEZPŁCIOWE → pomija filtry
        if spa.is_genderless_order():
            return True  # ⏭️ Koniec - nie sprawdza płci
        
        # PŁCIOWE → sprawdza kategorie
        category = deal.get_category_key()
        primary_slots = spa.get_free_slots_for_category(category)
        
        if primary_slots > 0:
            return True
        
        # Elastyczny przydział
        alternative = get_alternative_category(category)
        return spa.get_free_slots_for_category(alternative) > 0
```

### **Sortowanie (TODO):**
```python
# src/business_logic/prioritizer.py (do zrobienia)
class DealPrioritizer:
    
    def sort_deals(self, deals: List[Deal], spa: SPA) -> List[Deal]:
        # BEZPŁCIOWE: prosta logika
        if spa.is_genderless_order():
            return self.sort_simple(deals)
        
        # PŁCIOWE: złożona logika z priorytetami
        return self.sort_complex(deals, spa)
```

### **Alokacja (TODO):**
```python
# src/business_logic/allocator.py (do zrobienia)
class SlotAllocator:
    
    def allocate_deals(self, deals: List[Deal], spa: SPA) -> List[Deal]:
        # BEZPŁCIOWE: prosty licznik
        if spa.is_genderless_order():
            return deals[:spa.free_all]  # Pierwsze N dealów
        
        # PŁCIOWE: tracking kategorii
        return self.allocate_with_categories(deals, spa)
```

---

## ⚠️ **KRYTYCZNE ODKRYCIA**

### **1. Wolne miejsca mogą być UJEMNE!**
```python
spa.free_all = -134  # PRZEŁOŻONE!
```

**Obsługa:**
```python
# Jeśli ujemne → brak miejsc
if spa.free_all <= 0:
    return []  # Nie awansuj nikogo
```

### **2. Kategorie też mogą być ujemne:**
```python
spa.free_m_own = -1   # Przełożone M własne
spa.free_k_own = -2   # Przełożone K własne
```

**Obsługa:**
```python
# Sprawdź > 0, nie >= 0
if category_slots > 0:
    # Są miejsca
```

### **3. Elastyczny przydział NIE zamienia kategorii!**
```python
# ❌ ŹLE (webhook6.php tak robi)
# Sprawdza czy są miejsca, ale NIE przydziela faktycznie

# ✅ DOBRZE (powinno być)
# Śledzi która kategoria została użyta
allocated_category = assign_category(deal, spa, used_slots)
used_slots[allocated_category] += 1
```

---

## 🎯 **NASTĘPNE KROKI IMPLEMENTACJI**

### **Priorytet 1: DealPrioritizer** 
Sortowanie dla obu typów:
- Bezpłciowe: prosta logika (Priorytet + Data)
- Płciowe: złożona logika (Priorytet + Data + Dynamiczne priorytety)

### **Priorytet 2: SlotAllocator**
Alokacja miejsc:
- Bezpłciowe: prosty licznik globalny
- Płciowe: liczniki kategorii + elastyczny przydział

### **Priorytet 3: DealPromoter**
Główna logika łącząca:
- Walidacja (✅ gotowa)
- Sortowanie (TODO)
- Alokacja (TODO)
- Update w Bitrix24

---

**Status:** Walidacja ✅ | Sortowanie ⏳ | Alokacja ⏳ | Webhook ⏳

