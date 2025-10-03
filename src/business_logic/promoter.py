"""
Główna logika awansowania dealów (DealPromoter)

Łączy wszystkie komponenty:
- QualificationValidator (walidacja)
- DealPrioritizer (sortowanie)
- SlotAllocator (przydział miejsc)

To jest "orkiestrator" całego procesu.
"""
from typing import List, Tuple, Dict
from src.models import SPA, Deal
from .validators import QualificationValidator
from .prioritizer import DealPrioritizer
from .allocator import SlotAllocator


class DealPromoter:
    """
    Główna logika awansowania dealów z Rezerwy/Sortowania do Listy Głównej
    
    PROCES:
    1. Filtruj (tylko kwalifikujące się deale)
    2. Sortuj (według priorytetów)
    3. Przydziel (z tracking kategorii)
    4. Zwróć (promoted + reserve + stats)
    """
    
    def __init__(self):
        """Inicjalizuje wszystkie komponenty"""
        self.validator = QualificationValidator()
        self.prioritizer = DealPrioritizer()
        self.allocator = SlotAllocator()
    
    def process(
        self, 
        spa: SPA, 
        deals: List[Deal]
    ) -> Tuple[List[Deal], List[Deal], Dict]:
        """
        Przetwarza deale dla SPA
        
        Args:
            spa: Projekt SPA z limitami
            deals: Wszystkie deale (z etapów Sortowanie i Rezerwa)
            
        Returns:
            Tuple[promoted, reserve, stats]:
                - promoted: Deale do awansu na Listę Główną
                - reserve: Deale do przeniesienia/pozostawienia w Rezerwie
                - stats: Statystyki przetwarzania
        """
        stats = {
            "total_input": len(deals),
            "qualified": 0,
            "promoted": 0,
            "reserve": 0,
            "rejected": 0,
            "spa_type": "genderless" if spa.is_genderless_order() else "gendered",
            "category_stats": {},
        }
        
        # KROK 1: Filtruj - tylko kwalifikujące się deale
        qualified_deals = [
            deal for deal in deals
            if self.validator.validate_all(deal, spa)
        ]
        
        stats["qualified"] = len(qualified_deals)
        stats["rejected"] = len(deals) - len(qualified_deals)
        
        if not qualified_deals:
            # Brak kwalifikujących się dealów
            return [], [], stats
        
        # KROK 2: Sortuj według priorytetów
        sorted_deals = self.prioritizer.sort(qualified_deals, spa)
        
        # KROK 3: Przydziel miejsca
        promoted_deals = self.allocator.allocate(sorted_deals, spa)
        
        stats["promoted"] = len(promoted_deals)
        stats["category_stats"] = self.allocator.get_allocation_stats()
        stats["assignments"] = self.allocator.get_assignments()
        
        # KROK 4: Reszta do rezerwy (2x limit główny)
        reserve_limit = max(0, spa.free_all) * 2
        remaining_deals = sorted_deals[len(promoted_deals):]
        reserve_deals = remaining_deals[:reserve_limit]
        
        stats["reserve"] = len(reserve_deals)
        
        return promoted_deals, reserve_deals, stats
    
    def get_promotion_summary(self, stats: Dict) -> str:
        """
        Zwraca czytelne podsumowanie przetwarzania
        
        Args:
            stats: Statystyki z process()
            
        Returns:
            str: Formatowane podsumowanie
        """
        lines = []
        lines.append(f"Typ SPA: {stats['spa_type']}")
        lines.append(f"Deale wejściowe: {stats['total_input']}")
        lines.append(f"Kwalifikujące się: {stats['qualified']}")
        lines.append(f"Odrzucone: {stats['rejected']}")
        lines.append(f"Awansowane: {stats['promoted']}")
        lines.append(f"Do rezerwy: {stats['reserve']}")
        
        if stats.get('category_stats'):
            lines.append("\nPrzydział według kategorii:")
            for cat, count in stats['category_stats'].items():
                if count > 0:
                    lines.append(f"  {cat}: {count}")
        
        return "\n".join(lines)

