"""
Sortowanie dealów według priorytetów

Zgodnie z LOGIKA_AWANSU.md:

BEZPŁCIOWE:
1. Priorytet SPA (1 > 2 > 3 > 4)
2. Czas dodania do EXECUTING (starsze pierwsze)

PŁCIOWE (na razie jak bezpłciowe):
1. Priorytet SPA (1 > 2 > 3 > 4)
2. Czas dodania do EXECUTING (starsze pierwsze)
TODO: 3. Dynamiczne priorytety (Priority 1, 2, 3)
"""
from typing import List
from datetime import datetime
from src.models import SPA, Deal


class DealPrioritizer:
    """Sortowanie dealów według priorytetów biznesowych"""
    
    # Mapowanie priorytetów SPA na liczby (niższe = wyższy priorytet)
    PRIORITY_ORDER = {
        "1951": 1,  # Priorytet 1 (najwyższy)
        "1953": 2,  # Priorytet 2
        "1955": 3,  # Priorytet 3
        "1957": 4,  # Priorytet 4 (najniższy)
    }
    
    def sort(self, deals: List[Deal], spa: SPA) -> List[Deal]:
        """
        Sortuje deale według priorytetów
        
        Dla obu typów (bezpłciowe i płciowe) używa tej samej logiki:
        1. Priorytet SPA (1-4)
        2. Data EXECUTING (starsze pierwsze)
        
        Args:
            deals: Lista dealów do posortowania
            spa: Projekt SPA (na przyszłość dla dynamicznych priorytetów)
            
        Returns:
            List[Deal]: Posortowana lista (nowa, nie modyfikuje oryginału)
        """
        # Zwróć nową listę (nie modyfikuj oryginału)
        return sorted(deals, key=lambda d: self._get_sort_key(d))
    
    def _get_sort_key(self, deal: Deal) -> tuple:
        """
        Zwraca klucz sortowania dla deala
        
        Returns:
            tuple: (priority_level, executing_date)
        """
        # 1. Priorytet SPA (niższy = lepszy)
        priority_level = self.PRIORITY_ORDER.get(deal.priority or "", 999)
        
        # 2. Data EXECUTING (wcześniejsza = lepsza)
        # Jeśli brak daty → użyj datetime.max (trafi na koniec)
        executing_date = deal.executing_date if deal.executing_date else datetime.max
        
        return (priority_level, executing_date)
    
    def sort_genderless(self, deals: List[Deal]) -> List[Deal]:
        """
        Sortowanie dla zamówień bezpłciowych
        
        (Na razie identyczne jak sort(), ale dedykowana metoda
        na przyszłość jeśli logika się rozejdzie)
        """
        return sorted(deals, key=lambda d: self._get_sort_key(d))
    
    def sort_gendered(self, deals: List[Deal], spa: SPA) -> List[Deal]:
        """
        Sortowanie dla zamówień płciowych
        
        TODO: Dodać dynamiczne priorytety (Priority 1, 2, 3 z SPA)
        
        Na razie identyczne jak bezpłciowe.
        """
        return sorted(deals, key=lambda d: self._get_sort_key(d))

