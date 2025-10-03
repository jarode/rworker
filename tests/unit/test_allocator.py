"""
Testy jednostkowe dla SlotAllocator

KRYTYCZNA FUNKCJONALNOŚĆ!
To jest największy błąd w webhook6.php - brak liczników kategorii

Zgodnie z ANALIZA_DWOCH_TYPOW.md:

BEZPŁCIOWE:
- Prosty licznik globalny
- Awansuj do limitu "Wolne wszystkie"

PŁCIOWE:
- Liczniki dla każdej kategorii (M_nasze, K_nasze, etc.)
- Elastyczny przydział (główna → alternatywna)
- Limit globalny I kategoria
"""
import pytest
from src.business_logic.allocator import SlotAllocator
from src.models import SPA, Deal, Gender, Housing, DealPriority
from datetime import datetime


class TestGenderlessAllocation:
    """
    Alokacja dla zamówień BEZPŁCIOWYCH
    
    Logika: Prosty licznik - awansuj pierwsze N dealów do limitu
    """
    
    def test_allocate_up_to_limit(self, genderless_spa):
        """✅ Awansuj do limitu (proste - pierwsze N)"""
        # Given
        allocator = SlotAllocator()
        # genderless_spa.free_all = 15
        
        deals = [
            Deal(ID=str(i), TITLE=f"Deal {i}", STAGE_ID="C25:UC_5I8UBF")
            for i in range(20)  # 20 dealów
        ]
        
        # When
        allocated = allocator.allocate(deals, genderless_spa)
        
        # Then
        assert len(allocated) == 15, "Powinno awansować 15 dealów (limit)"
        assert allocated[0].id == "0", "Pierwszy deal powinien być ID=0"
        assert allocated[14].id == "14", "Ostatni deal powinien być ID=14"
    
    def test_allocate_less_than_limit(self, genderless_spa):
        """✅ Mniej dealów niż limit - awansuj wszystkie"""
        # Given
        allocator = SlotAllocator()
        
        deals = [
            Deal(ID=str(i), TITLE=f"Deal {i}", STAGE_ID="C25:UC_5I8UBF")
            for i in range(10)  # Tylko 10 (limit = 15)
        ]
        
        # When
        allocated = allocator.allocate(deals, genderless_spa)
        
        # Then
        assert len(allocated) == 10, "Powinno awansować wszystkie 10 dealów"
    
    def test_zero_limit_allocates_nothing(self):
        """✅ Limit = 0 → nie awansuj nikogo"""
        # Given
        allocator = SlotAllocator()
        spa = SPA(
            id=999,
            title="Test",
            stageId="DT1032_17:UC_CU0OTZ",
            ufCrm9_1740930205=0,  # Limit = 0
            ufCrm9_1747740109=1991,  # Bezpłciowe
        )
        
        deals = [Deal(ID="1", TITLE="Test", STAGE_ID="C25:UC_5I8UBF")]
        
        # When
        allocated = allocator.allocate(deals, spa)
        
        # Then
        assert len(allocated) == 0, "Limit 0 → nie awansuj nikogo"
    
    def test_negative_limit_allocates_nothing(self):
        """✅ Limit ujemny (przełożone) → nie awansuj nikogo"""
        # Given
        allocator = SlotAllocator()
        spa = SPA(
            id=999,
            title="Test",
            stageId="DT1032_17:UC_CU0OTZ",
            ufCrm9_1740930205=-10,  # Ujemny!
            ufCrm9_1747740109=1991,
        )
        
        deals = [Deal(ID="1", TITLE="Test", STAGE_ID="C25:UC_5I8UBF")]
        
        # When
        allocated = allocator.allocate(deals, spa)
        
        # Then
        assert len(allocated) == 0, "Limit ujemny → nie awansuj nikogo"


class TestGenderedAllocation:
    """
    Alokacja dla zamówień PŁCIOWYCH
    
    KRYTYCZNA LOGIKA:
    - Tracking liczników dla każdej kategorii
    - Elastyczny przydział (główna → alternatywna)
    - Limit globalny I limit kategorii
    """
    
    def test_allocate_single_category(self):
        """✅ Awansowanie w jednej kategorii (M_nasze)"""
        # Given
        allocator = SlotAllocator()
        spa = SPA(
            id=999,
            title="Test",
            stageId="DT1032_17:UC_CU0OTZ",
            ufCrm9_1740930205=10,  # Globalny limit
            ufCrm9_1740930322=3,   # M_nasze limit = 3
            ufCrm9_1747740109=1993,  # Płciowe
        )
        
        # 5 dealów M+nasze
        deals = [
            Deal(
                ID=str(i),
                TITLE=f"Deal {i}",
                STAGE_ID="C25:UC_5I8UBF",
                UF_CRM_1740931105=Gender.MALE.value,
                UF_CRM_1740931164=Housing.OURS.value,
            )
            for i in range(5)
        ]
        
        # When
        allocated = allocator.allocate(deals, spa)
        
        # Then
        assert len(allocated) == 3, "Powinno awansować 3 (limit M_nasze)"
        # Sprawdź tracking kategorii
        stats = allocator.get_allocation_stats()
        assert stats["M_nasze"] == 3, "Licznik M_nasze powinien być 3"
    
    def test_allocate_multiple_categories(self):
        """✅ Awansowanie w wielu kategoriach jednocześnie"""
        # Given
        allocator = SlotAllocator()
        spa = SPA(
            id=999,
            title="Test",
            stageId="DT1032_17:UC_CU0OTZ",
            ufCrm9_1740930205=10,
            ufCrm9_1740930322=2,  # M_nasze = 2
            ufCrm9_1740930346=2,  # K_nasze = 2
            ufCrm9_1740930371=1,  # PARY_nasze = 1
            ufCrm9_1747740109=1993,
        )
        
        deals = [
            # 3x M+nasze (ale limit = 2!)
            Deal(ID="m1", TITLE="M1", STAGE_ID="C25:UC_5I8UBF",
                 UF_CRM_1740931105=Gender.MALE.value, UF_CRM_1740931164=Housing.OURS.value),
            Deal(ID="m2", TITLE="M2", STAGE_ID="C25:UC_5I8UBF",
                 UF_CRM_1740931105=Gender.MALE.value, UF_CRM_1740931164=Housing.OURS.value),
            Deal(ID="m3", TITLE="M3", STAGE_ID="C25:UC_5I8UBF",
                 UF_CRM_1740931105=Gender.MALE.value, UF_CRM_1740931164=Housing.OURS.value),
            # 2x K+nasze
            Deal(ID="k1", TITLE="K1", STAGE_ID="C25:UC_5I8UBF",
                 UF_CRM_1740931105=Gender.FEMALE.value, UF_CRM_1740931164=Housing.OURS.value),
            Deal(ID="k2", TITLE="K2", STAGE_ID="C25:UC_5I8UBF",
                 UF_CRM_1740931105=Gender.FEMALE.value, UF_CRM_1740931164=Housing.OURS.value),
            # 1x PARA+nasze
            Deal(ID="p1", TITLE="P1", STAGE_ID="C25:UC_5I8UBF",
                 UF_CRM_1740931105=Gender.COUPLE.value, UF_CRM_1740931164=Housing.OURS.value),
        ]
        
        # When
        allocated = allocator.allocate(deals, spa)
        
        # Then
        assert len(allocated) == 5, "Powinno awansować 5 (2M + 2K + 1P)"
        
        # Sprawdź ID awansowanych
        allocated_ids = [d.id for d in allocated]
        assert "m1" in allocated_ids
        assert "m2" in allocated_ids
        assert "m3" not in allocated_ids, "m3 nie powinien przejść (limit M_nasze = 2)"
        assert "k1" in allocated_ids
        assert "k2" in allocated_ids
        assert "p1" in allocated_ids
        
        # Sprawdź liczniki
        stats = allocator.get_allocation_stats()
        assert stats["M_nasze"] == 2
        assert stats["K_nasze"] == 2
        assert stats["PARY_nasze"] == 1
    
    def test_elastic_allocation_to_alternative(self):
        """✅ ELASTYCZNY PRZYDZIAŁ: Główna pełna → użyj alternatywnej"""
        # Given
        allocator = SlotAllocator()
        spa = SPA(
            id=999,
            title="Test",
            stageId="DT1032_17:UC_CU0OTZ",
            ufCrm9_1740930205=5,
            ufCrm9_1740930322=2,  # M_nasze = 2
            ufCrm9_1740930392=2,  # M_wlasne = 2
            ufCrm9_1747740109=1993,
        )
        
        deals = [
            # 4x M+nasze (ale limit M_nasze = 2!)
            Deal(ID="m1", TITLE="M1", STAGE_ID="C25:UC_5I8UBF",
                 UF_CRM_1740931105=Gender.MALE.value, UF_CRM_1740931164=Housing.OURS.value),
            Deal(ID="m2", TITLE="M2", STAGE_ID="C25:UC_5I8UBF",
                 UF_CRM_1740931105=Gender.MALE.value, UF_CRM_1740931164=Housing.OURS.value),
            Deal(ID="m3", TITLE="M3", STAGE_ID="C25:UC_5I8UBF",
                 UF_CRM_1740931105=Gender.MALE.value, UF_CRM_1740931164=Housing.OURS.value),
            Deal(ID="m4", TITLE="M4", STAGE_ID="C25:UC_5I8UBF",
                 UF_CRM_1740931105=Gender.MALE.value, UF_CRM_1740931164=Housing.OURS.value),
        ]
        
        # When
        allocated = allocator.allocate(deals, spa)
        
        # Then
        assert len(allocated) == 4, "Wszystkie 4 powinny przejść (2 M_nasze + 2 M_wlasne elastycznie)"
        
        # Sprawdź liczniki
        stats = allocator.get_allocation_stats()
        assert stats["M_nasze"] == 2, "2 w głównej kategorii"
        assert stats["M_wlasne"] == 2, "2 w alternatywnej kategorii (elastyczny przydział!)"
    
    def test_global_limit_stops_allocation(self):
        """✅ Limit globalny zatrzymuje alokację (mimo że kategorie mają miejsca)"""
        # Given
        allocator = SlotAllocator()
        spa = SPA(
            id=999,
            title="Test",
            stageId="DT1032_17:UC_CU0OTZ",
            ufCrm9_1740930205=3,   # GLOBALNY LIMIT = 3!
            ufCrm9_1740930322=10,  # M_nasze = 10 (więcej niż globalny!)
            ufCrm9_1747740109=1993,
        )
        
        deals = [
            Deal(ID=str(i), TITLE=f"M{i}", STAGE_ID="C25:UC_5I8UBF",
                 UF_CRM_1740931105=Gender.MALE.value, UF_CRM_1740931164=Housing.OURS.value)
            for i in range(5)
        ]
        
        # When
        allocated = allocator.allocate(deals, spa)
        
        # Then
        assert len(allocated) == 3, "Globalny limit (3) powinien zatrzymać na 3"
        assert allocator.get_allocated_count() == 3
    
    def test_category_with_no_deals_doesnt_use_slots(self):
        """✅ Niewykorzystane miejsca w kategorii NIE przechodzą do innych"""
        # Given
        allocator = SlotAllocator()
        spa = SPA(
            id=999,
            title="Test",
            stageId="DT1032_17:UC_CU0OTZ",
            ufCrm9_1740930205=10,
            ufCrm9_1740930322=5,  # M_nasze = 5 (niewykorzystane!)
            ufCrm9_1740930346=2,  # K_nasze = 2
            ufCrm9_1747740109=1993,
        )
        
        # Tylko deale K+nasze (brak M+nasze!)
        deals = [
            Deal(ID=str(i), TITLE=f"K{i}", STAGE_ID="C25:UC_5I8UBF",
                 UF_CRM_1740931105=Gender.FEMALE.value, UF_CRM_1740931164=Housing.OURS.value)
            for i in range(5)  # 5 K (ale limit K_nasze = 2)
        ]
        
        # When
        allocated = allocator.allocate(deals, spa)
        
        # Then
        assert len(allocated) == 2, "Tylko 2 K (limit K_nasze), nie używa M_nasze"
        stats = allocator.get_allocation_stats()
        assert stats["K_nasze"] == 2
        assert stats["M_nasze"] == 0, "M_nasze nie powinno być użyte"
    
    def test_tracks_assigned_categories(self):
        """✅ Śledzi do której kategorii został przydzielony każdy deal"""
        # Given
        allocator = SlotAllocator()
        spa = SPA(
            id=999,
            title="Test",
            stageId="DT1032_17:UC_CU0OTZ",
            ufCrm9_1740930205=10,
            ufCrm9_1740930322=1,  # M_nasze = 1 (pełne po 1)
            ufCrm9_1740930392=2,  # M_wlasne = 2 (alternatywna)
            ufCrm9_1747740109=1993,
        )
        
        deals = [
            Deal(ID="m1", TITLE="M1", STAGE_ID="C25:UC_5I8UBF",
                 UF_CRM_1740931105=Gender.MALE.value, UF_CRM_1740931164=Housing.OURS.value),
            Deal(ID="m2", TITLE="M2", STAGE_ID="C25:UC_5I8UBF",
                 UF_CRM_1740931105=Gender.MALE.value, UF_CRM_1740931164=Housing.OURS.value),
            Deal(ID="m3", TITLE="M3", STAGE_ID="C25:UC_5I8UBF",
                 UF_CRM_1740931105=Gender.MALE.value, UF_CRM_1740931164=Housing.OURS.value),
        ]
        
        # When
        allocated = allocator.allocate(deals, spa)
        
        # Then
        assignments = allocator.get_assignments()
        assert assignments["m1"] == "M_nasze", "m1 → główna kategoria"
        assert assignments["m2"] == "M_wlasne", "m2 → alternatywna (elastyczny!)"
        assert assignments["m3"] == "M_wlasne", "m3 → alternatywna"


class TestComplexScenarios:
    """Testy złożonych scenariuszy (realnych przypadków)"""
    
    def test_realistic_mixed_scenario(self):
        """✅ Realistyczny scenariusz - mix kategorii, elastyczny przydział"""
        # Given
        allocator = SlotAllocator()
        spa = SPA(
            id=999,
            title="Test",
            stageId="DT1032_17:UC_CU0OTZ",
            ufCrm9_1740930205=5,   # Globalny = 5
            ufCrm9_1740930322=2,   # M_nasze = 2
            ufCrm9_1740930392=1,   # M_wlasne = 1
            ufCrm9_1740930346=1,   # K_nasze = 1
            ufCrm9_1740930427=1,   # K_wlasne = 1
            ufCrm9_1747740109=1993,
        )
        
        deals = [
            # 3x M+nasze
            Deal(ID="m1", TITLE="M1", STAGE_ID="C25:UC_5I8UBF",
                 UF_CRM_1740931105=Gender.MALE.value, UF_CRM_1740931164=Housing.OURS.value),
            Deal(ID="m2", TITLE="M2", STAGE_ID="C25:UC_5I8UBF",
                 UF_CRM_1740931105=Gender.MALE.value, UF_CRM_1740931164=Housing.OURS.value),
            Deal(ID="m3", TITLE="M3", STAGE_ID="C25:UC_5I8UBF",
                 UF_CRM_1740931105=Gender.MALE.value, UF_CRM_1740931164=Housing.OURS.value),
            # 2x K+nasze
            Deal(ID="k1", TITLE="K1", STAGE_ID="C25:UC_5I8UBF",
                 UF_CRM_1740931105=Gender.FEMALE.value, UF_CRM_1740931164=Housing.OURS.value),
            Deal(ID="k2", TITLE="K2", STAGE_ID="C25:UC_5I8UBF",
                 UF_CRM_1740931105=Gender.FEMALE.value, UF_CRM_1740931164=Housing.OURS.value),
        ]
        
        # When
        allocated = allocator.allocate(deals, spa)
        
        # Then
        assert len(allocated) == 5, "Globalny limit = 5"
        
        # Sprawdź przydziały
        assignments = allocator.get_assignments()
        assert assignments["m1"] == "M_nasze"   # 1/2 M_nasze
        assert assignments["m2"] == "M_nasze"   # 2/2 M_nasze (pełne!)
        assert assignments["m3"] == "M_wlasne"  # 1/1 M_wlasne (elastyczny!)
        assert assignments["k1"] == "K_nasze"   # 1/1 K_nasze (pełne!)
        assert assignments["k2"] == "K_wlasne"  # 1/1 K_wlasne (elastyczny!)
        
        # Sprawdź liczniki
        stats = allocator.get_allocation_stats()
        assert stats["M_nasze"] == 2
        assert stats["M_wlasne"] == 1
        assert stats["K_nasze"] == 1
        assert stats["K_wlasne"] == 1
        assert allocator.get_allocated_count() == 5

