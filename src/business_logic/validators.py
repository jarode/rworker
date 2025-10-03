"""
Walidatory warunków kwalifikacji dealów do SPA

Zgodnie z LOGIKA_AWANSU.md:
1. Data przyjazdu < Data szkolenia SPA
2. Wiek < Limit wieku SPA  
3. Jeśli bezpłciowe → pomija filtry płci
4. Jeśli płciowe → sprawdza dostępność miejsc
"""
from typing import Optional
from src.models import SPA, Deal


class QualificationValidator:
    """
    Walidator warunków kwalifikacji dealów do SPA
    
    Wszystkie metody zwracają:
    - True = deal spełnia warunek
    - False = deal NIE spełnia warunku
    """
    
    def check_arrival_date(self, deal: Deal, spa: SPA) -> bool:
        """
        WARUNEK 1: Data przyjazdu w zakresie OD-DO i przed szkoleniem
        
        AKTUALIZOWANE WYMAGANIA:
        - Deal.przyjazd >= SPA.arrival_from (ufCrm9_1740931899)
        - Deal.przyjazd <= SPA.arrival_to (ufCrm9_1740931913)  
        - Deal.przyjazd < SPA.training_date (ufCrm9_1740930537)
        
        Args:
            deal: Kandydat
            spa: Projekt SPA
            
        Returns:
            bool: True jeśli data w zakresie i przed szkoleniem
        """
        if not deal.arrival_date:
            return True  # Brak daty → PASS
        
        # 1. Sprawdź czy NIE WCZEŚNIEJ niż przyjazd OD
        if spa.arrival_from:
            if deal.arrival_date < spa.arrival_from:
                return False  # Za wcześnie
        
        # 2. Sprawdź czy NIE PÓŹNIEJ niż przyjazd DO
        if spa.arrival_to:
            if deal.arrival_date > spa.arrival_to:
                return False  # Za późno
        
        # 3. Sprawdź czy PRZED szkoleniem
        if spa.training_date:
            if deal.arrival_date >= spa.training_date:
                return False  # Po szkoleniu lub w dniu
        
        return True
    
    def check_age(self, deal: Deal, spa: SPA) -> bool:
        """
        WARUNEK 2: Wiek <= Limit wieku SPA
        
        AKTUALIZOWANE WYMAGANIA:
        - UF_CRM_1669643033481 (deal) <= ufCrm9_1740930520 (SPA)
        - ZMIANA: Równy lub mniejszy (włącznie!)
        
        Args:
            deal: Kandydat
            spa: Projekt SPA
            
        Returns:
            bool: True jeśli wiek jest równy lub poniżej limitu
        """
        # Jeśli brak limitu lub wieku → nie walidujemy → PASS
        if not spa.age_limit or not deal.age:
            return True
        
        # Wiek może być RÓWNY lub MNIEJSZY (<=)
        return deal.age <= spa.age_limit
    
    def check_gender_slots(self, deal: Deal, spa: SPA) -> bool:
        """
        WARUNEK 3 & 4: Sprawdza dostępność miejsc według płci i mieszkania
        
        Zgodnie z LOGIKA_AWANSU.md:
        - Jeśli zamówienie bezpłciowe (1991) → pomija filtry płci → PASS
        - Jeśli zamówienie płciowe (1993) → sprawdza kategorię miejsc
        
        Elastyczny przydział:
        - Priorytet: główna kategoria (np. M_nasze)
        - Jeśli pełna → sprawdź alternatywną (np. M_wlasne)
        
        Args:
            deal: Kandydat
            spa: Projekt SPA
            
        Returns:
            bool: True jeśli są miejsca (główna lub alternatywna kategoria)
        """
        # WARUNEK 3: Zamówienie bezpłciowe → pomija filtry
        if spa.is_genderless_order():
            return True
        
        # WARUNEK 4: Zamówienie płciowe → sprawdź kategorie
        
        # Brak danych o płci lub mieszkaniu → nie można przydzielić
        if not deal.gender or not deal.housing:
            return False
        
        # Pobierz klucz kategorii (np. 'M_nasze', 'K_wlasne')
        category = deal.get_category_key()
        if not category:
            return False
        
        # Sprawdź główną kategorię
        primary_slots = spa.get_free_slots_for_category(category)
        if primary_slots > 0:
            return True
        
        # Sprawdź alternatywną kategorię (elastyczny przydział)
        # M_nasze <-> M_wlasne, K_nasze <-> K_wlasne, PARY_nasze <-> PARY_wlasne
        alternative_category = self._get_alternative_category(category)
        alternative_slots = spa.get_free_slots_for_category(alternative_category)
        
        return alternative_slots > 0
    
    def _get_alternative_category(self, category: str) -> str:
        """
        Zwraca alternatywną kategorię dla elastycznego przydziału
        
        Reguły:
        - nasze <-> wlasne (dla tej samej płci)
        
        Args:
            category: Klucz kategorii (np. 'M_nasze')
            
        Returns:
            str: Alternatywna kategoria (np. 'M_wlasne')
        """
        # Zamień 'nasze' na 'wlasne' i odwrotnie
        if '_nasze' in category:
            return category.replace('_nasze', '_wlasne')
        elif '_wlasne' in category:
            return category.replace('_wlasne', '_nasze')
        else:
            return category  # Fallback
    
    def validate_all(self, deal: Deal, spa: SPA) -> bool:
        """
        Sprawdza WSZYSTKIE warunki kwalifikacji
        
        Deal musi spełnić WSZYSTKIE warunki:
        1. Data przyjazdu < Data szkolenia
        2. Wiek < Limit wieku
        3. Dostępność miejsc (lub bezpłciowe)
        
        Args:
            deal: Kandydat
            spa: Projekt SPA
            
        Returns:
            bool: True jeśli deal spełnia WSZYSTKIE warunki
        """
        return (
            self.check_arrival_date(deal, spa) and
            self.check_age(deal, spa) and
            self.check_gender_slots(deal, spa)
        )

