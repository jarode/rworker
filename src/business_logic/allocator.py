"""
Alokacja miejsc dla dealów

NAJWAŻNIEJSZA CZĘŚĆ SYSTEMU!
To jest główny błąd w webhook6.php - brak liczników kategorii

Zgodnie z ANALIZA_DWOCH_TYPOW.md:

BEZPŁCIOWE:
- Prosty licznik globalny
- Awansuj pierwsze N dealów

PŁCIOWE:
- Liczniki dla każdej kategorii
- Elastyczny przydział (główna → alternatywna)
- Tracking przydziałów
"""
from typing import List, Dict, Optional
from src.models import SPA, Deal


class SlotAllocator:
    """
    Alokator miejsc z tracking kategorii
    
    KLUCZOWE FUNKCJE:
    - Śledzi ile miejsc zostało użytych w każdej kategorii
    - Implementuje elastyczny przydział (główna → alternatywna)
    - Respektuje limit globalny I limity kategorii
    """
    
    def __init__(self):
        """Inicjalizuje liczniki"""
        self.reset()
    
    def reset(self):
        """Resetuje wszystkie liczniki"""
        # Liczniki użytych miejsc
        self._used_slots = {
            "M_nasze": 0,
            "M_wlasne": 0,
            "K_nasze": 0,
            "K_wlasne": 0,
            "PARY_nasze": 0,
            "PARY_wlasne": 0,
        }
        
        # Tracking przydziałów (deal_id → kategoria)
        self._assignments = {}
        
        # Licznik globalny
        self._total_allocated = 0
    
    def allocate(self, deals: List[Deal], spa: SPA) -> List[Deal]:
        """
        Przydziela miejsca dla dealów
        
        Automatycznie rozpoznaje typ zamówienia (bezpłciowe vs płciowe)
        
        Args:
            deals: Posortowana lista dealów (WAŻNE: już posortowana!)
            spa: Projekt SPA z limitami
            
        Returns:
            List[Deal]: Deale które zostały przydzielone (do awansu)
        """
        self.reset()
        
        # Sprawdź limit globalny
        global_limit = max(0, spa.free_all)
        
        if global_limit <= 0:
            return []  # Brak miejsc
        
        # Wybierz strategię
        if spa.is_genderless_order():
            return self._allocate_genderless(deals, global_limit)
        else:
            return self._allocate_gendered(deals, spa, global_limit)
    
    def _allocate_genderless(
        self, 
        deals: List[Deal], 
        global_limit: int
    ) -> List[Deal]:
        """
        Alokacja dla zamówień BEZPŁCIOWYCH
        
        PROSTA LOGIKA: Weź pierwsze N dealów do limitu
        """
        allocated = []
        
        for deal in deals:
            if self._total_allocated >= global_limit:
                break
            
            allocated.append(deal)
            self._total_allocated += 1
        
        return allocated
    
    def _allocate_gendered(
        self, 
        deals: List[Deal], 
        spa: SPA, 
        global_limit: int
    ) -> List[Deal]:
        """
        Alokacja dla zamówień PŁCIOWYCH
        
        ZŁOŻONA LOGIKA:
        - Tracking kategorii
        - Elastyczny przydział
        - Limit globalny I kategoria
        """
        allocated = []
        
        for deal in deals:
            # Sprawdź limit globalny
            if self._total_allocated >= global_limit:
                break
            
            # Przydziel kategorię (główna lub alternatywna)
            category = self._assign_category(deal, spa)
            
            if not category:
                continue  # Brak dostępnych miejsc w żadnej kategorii
            
            # Awansuj
            allocated.append(deal)
            self._used_slots[category] += 1
            self._assignments[deal.id] = category
            self._total_allocated += 1
        
        return allocated
    
    def _assign_category(
        self, 
        deal: Deal, 
        spa: SPA
    ) -> Optional[str]:
        """
        Przydziela kategorię z elastycznym przydziałem
        
        LOGIKA:
        1. Sprawdź główną kategorię (np. M_nasze)
        2. Jeśli pełna → sprawdź alternatywną (np. M_wlasne)
        3. Jeśli obie pełne → None
        
        Returns:
            str: Kategoria do której przydzielono (np. "M_nasze")
            None: Brak dostępnych miejsc
        """
        # Pobierz kategorię z deala
        primary_category = deal.get_category_key()
        
        if not primary_category:
            return None  # Brak danych o płci/mieszkaniu
        
        # Sprawdź główną kategorię
        if self._has_available_slot(primary_category, spa):
            return primary_category
        
        # Sprawdź alternatywną (elastyczny przydział)
        alternative_category = self._get_alternative_category(primary_category)
        if self._has_available_slot(alternative_category, spa):
            return alternative_category
        
        return None  # Brak miejsc w obu kategoriach
    
    def _has_available_slot(self, category: str, spa: SPA) -> bool:
        """
        Sprawdza czy kategoria ma jeszcze wolne miejsca
        
        Args:
            category: Klucz kategorii (np. "M_nasze")
            spa: Projekt SPA
            
        Returns:
            bool: True jeśli są wolne miejsca
        """
        category_limit = spa.get_free_slots_for_category(category)
        used = self._used_slots.get(category, 0)
        
        return used < category_limit
    
    def _get_alternative_category(self, category: str) -> str:
        """
        Zwraca alternatywną kategorię dla elastycznego przydziału
        
        Reguły: nasze <-> wlasne (dla tej samej płci)
        """
        if "_nasze" in category:
            return category.replace("_nasze", "_wlasne")
        elif "_wlasne" in category:
            return category.replace("_wlasne", "_nasze")
        else:
            return category
    
    def get_allocation_stats(self) -> Dict[str, int]:
        """Zwraca statystyki użytych miejsc w kategoriach"""
        return self._used_slots.copy()
    
    def get_assignments(self) -> Dict[str, str]:
        """Zwraca mapowanie deal_id → kategoria"""
        return self._assignments.copy()
    
    def get_allocated_count(self) -> int:
        """Zwraca całkowitą liczbę awansowanych dealów"""
        return self._total_allocated

