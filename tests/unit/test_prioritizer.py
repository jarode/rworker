"""
Testy jednostkowe dla DealPrioritizer

Zgodnie z LOGIKA_AWANSU.md - sortowanie dealów:

BEZPŁCIOWE:
1. Priorytet SPA (1-4)
2. Czas dodania do EXECUTING (starsze pierwsze)

PŁCIOWE:
1. Priorytet SPA (1-4)
2. Czas dodania do EXECUTING (starsze pierwsze)
3. TODO: Dynamiczne priorytety z SPA (Priority 1, 2, 3)
"""
import pytest
from datetime import datetime, timedelta
from src.business_logic.prioritizer import DealPrioritizer
from src.models import SPA, Deal, DealPriority


class TestGenderlessSorting:
    """
    Sortowanie dla zamówień BEZPŁCIOWYCH
    
    Kryteria:
    1. Priorytet SPA (1 > 2 > 3 > 4)
    2. Data EXECUTING (starsze pierwsze)
    """
    
    def test_sort_by_priority_ascending(self, genderless_spa):
        """✅ Sortowanie po priorytecie SPA (1, 2, 3, 4)"""
        # Given
        prioritizer = DealPrioritizer()
        
        deals = [
            Deal(ID="4", TITLE="P4", STAGE_ID="C25:UC_5I8UBF", 
                 UF_CRM_1743329864=DealPriority.P4.value,
                 UF_CRM_1741856527=datetime(2025, 10, 1).isoformat()),
            Deal(ID="1", TITLE="P1", STAGE_ID="C25:UC_5I8UBF", 
                 UF_CRM_1743329864=DealPriority.P1.value,
                 UF_CRM_1741856527=datetime(2025, 10, 1).isoformat()),
            Deal(ID="3", TITLE="P3", STAGE_ID="C25:UC_5I8UBF", 
                 UF_CRM_1743329864=DealPriority.P3.value,
                 UF_CRM_1741856527=datetime(2025, 10, 1).isoformat()),
            Deal(ID="2", TITLE="P2", STAGE_ID="C25:UC_5I8UBF", 
                 UF_CRM_1743329864=DealPriority.P2.value,
                 UF_CRM_1741856527=datetime(2025, 10, 1).isoformat()),
        ]
        
        # When
        sorted_deals = prioritizer.sort(deals, genderless_spa)
        
        # Then
        assert sorted_deals[0].id == "1", "Pierwszy powinien być P1"
        assert sorted_deals[1].id == "2", "Drugi powinien być P2"
        assert sorted_deals[2].id == "3", "Trzeci powinien być P3"
        assert sorted_deals[3].id == "4", "Czwarty powinien być P4"
    
    def test_sort_by_executing_date_when_same_priority(self, genderless_spa):
        """✅ Dla tego samego priorytetu - sortuj po dacie EXECUTING (starsze pierwsze)"""
        # Given
        prioritizer = DealPrioritizer()
        
        deals = [
            Deal(ID="late", TITLE="Późny", STAGE_ID="C25:UC_5I8UBF",
                 UF_CRM_1743329864=DealPriority.P1.value,
                 UF_CRM_1741856527=datetime(2025, 10, 10).isoformat()),  # Późniejsza
            Deal(ID="early", TITLE="Wczesny", STAGE_ID="C25:UC_5I8UBF",
                 UF_CRM_1743329864=DealPriority.P1.value,
                 UF_CRM_1741856527=datetime(2025, 10, 1).isoformat()),   # Wcześniejsza
            Deal(ID="middle", TITLE="Środkowy", STAGE_ID="C25:UC_5I8UBF",
                 UF_CRM_1743329864=DealPriority.P1.value,
                 UF_CRM_1741856527=datetime(2025, 10, 5).isoformat()),   # Środkowa
        ]
        
        # When
        sorted_deals = prioritizer.sort(deals, genderless_spa)
        
        # Then
        assert sorted_deals[0].id == "early", "Najwcześniejsza data powinna być pierwsza"
        assert sorted_deals[1].id == "middle", "Środkowa data powinna być druga"
        assert sorted_deals[2].id == "late", "Najpóźniejsza data powinna być trzecia"
    
    def test_priority_dominates_date(self, genderless_spa):
        """✅ Priorytet SPA ważniejszy niż data EXECUTING"""
        # Given
        prioritizer = DealPrioritizer()
        
        deals = [
            Deal(ID="p2_early", TITLE="P2 wcześniejszy", STAGE_ID="C25:UC_5I8UBF",
                 UF_CRM_1743329864=DealPriority.P2.value,
                 UF_CRM_1741856527=datetime(2025, 9, 1).isoformat()),   # Wcześniejsza data
            Deal(ID="p1_late", TITLE="P1 późniejszy", STAGE_ID="C25:UC_5I8UBF",
                 UF_CRM_1743329864=DealPriority.P1.value,
                 UF_CRM_1741856527=datetime(2025, 10, 1).isoformat()),  # Późniejsza data
        ]
        
        # When
        sorted_deals = prioritizer.sort(deals, genderless_spa)
        
        # Then
        assert sorted_deals[0].id == "p1_late", "P1 powinien być pierwszy mimo późniejszej daty"
        assert sorted_deals[1].id == "p2_early", "P2 powinien być drugi mimo wcześniejszej daty"
    
    def test_missing_priority_goes_last(self, genderless_spa):
        """✅ Deale bez priorytetu na końcu"""
        # Given
        prioritizer = DealPrioritizer()
        
        deals = [
            Deal(ID="no_prio", TITLE="Bez priorytetu", STAGE_ID="C25:UC_5I8UBF",
                 UF_CRM_1741856527=datetime(2025, 9, 1).isoformat()),  # Brak priorytetu
            Deal(ID="has_prio", TITLE="Z priorytetem", STAGE_ID="C25:UC_5I8UBF",
                 UF_CRM_1743329864=DealPriority.P4.value,
                 UF_CRM_1741856527=datetime(2025, 10, 1).isoformat()),
        ]
        
        # When
        sorted_deals = prioritizer.sort(deals, genderless_spa)
        
        # Then
        assert sorted_deals[0].id == "has_prio", "Deal z priorytetem powinien być pierwszy"
        assert sorted_deals[1].id == "no_prio", "Deal bez priorytetu powinien być ostatni"
    
    def test_missing_executing_date_goes_last(self, genderless_spa):
        """✅ Deale bez daty EXECUTING na końcu (w ramach tego samego priorytetu)"""
        # Given
        prioritizer = DealPrioritizer()
        
        deals = [
            Deal(ID="no_date", TITLE="Bez daty", STAGE_ID="C25:UC_5I8UBF",
                 UF_CRM_1743329864=DealPriority.P1.value),  # Brak daty
            Deal(ID="has_date", TITLE="Z datą", STAGE_ID="C25:UC_5I8UBF",
                 UF_CRM_1743329864=DealPriority.P1.value,
                 UF_CRM_1741856527=datetime(2025, 10, 1).isoformat()),
        ]
        
        # When
        sorted_deals = prioritizer.sort(deals, genderless_spa)
        
        # Then
        assert sorted_deals[0].id == "has_date", "Deal z datą powinien być pierwszy"
        assert sorted_deals[1].id == "no_date", "Deal bez daty powinien być ostatni"


class TestGenderedSorting:
    """
    Sortowanie dla zamówień PŁCIOWYCH
    
    Kryteria (na razie jak bezpłciowe):
    1. Priorytet SPA (1-4)
    2. Data EXECUTING
    
    TODO: Dodać dynamiczne priorytety (Priority 1, 2, 3)
    """
    
    def test_gendered_sorts_like_genderless_for_now(self, sample_spa):
        """✅ Płciowe sortuje się tak samo jak bezpłciowe (na razie)"""
        # Given
        prioritizer = DealPrioritizer()
        
        deals = [
            Deal(ID="2", TITLE="P2", STAGE_ID="C25:UC_5I8UBF",
                 UF_CRM_1743329864=DealPriority.P2.value,
                 UF_CRM_1741856527=datetime(2025, 10, 1).isoformat()),
            Deal(ID="1", TITLE="P1", STAGE_ID="C25:UC_5I8UBF",
                 UF_CRM_1743329864=DealPriority.P1.value,
                 UF_CRM_1741856527=datetime(2025, 10, 1).isoformat()),
        ]
        
        # When
        sorted_deals = prioritizer.sort(deals, sample_spa)
        
        # Then
        assert sorted_deals[0].id == "1"
        assert sorted_deals[1].id == "2"
    
    def test_returns_sorted_list_not_original(self, sample_spa):
        """✅ Zwraca nową listę (nie modyfikuje oryginału)"""
        # Given
        prioritizer = DealPrioritizer()
        
        original_deals = [
            Deal(ID="2", TITLE="P2", STAGE_ID="C25:UC_5I8UBF",
                 UF_CRM_1743329864=DealPriority.P2.value),
            Deal(ID="1", TITLE="P1", STAGE_ID="C25:UC_5I8UBF",
                 UF_CRM_1743329864=DealPriority.P1.value),
        ]
        
        # When
        sorted_deals = prioritizer.sort(original_deals, sample_spa)
        
        # Then
        assert original_deals[0].id == "2", "Oryginalna lista nie powinna być zmodyfikowana"
        assert sorted_deals[0].id == "1", "Posortowana lista powinna być inna"


class TestEdgeCases:
    """Testy przypadków brzegowych"""
    
    def test_empty_list_returns_empty(self, sample_spa):
        """✅ Pusta lista zwraca pustą listę"""
        prioritizer = DealPrioritizer()
        
        result = prioritizer.sort([], sample_spa)
        
        assert result == []
    
    def test_single_deal_returns_single(self, sample_spa, sample_deal):
        """✅ Jeden deal zwraca listę z jednym dealem"""
        prioritizer = DealPrioritizer()
        
        result = prioritizer.sort([sample_deal], sample_spa)
        
        assert len(result) == 1
        assert result[0].id == sample_deal.id

