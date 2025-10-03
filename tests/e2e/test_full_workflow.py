"""
Test END-TO-END z prawdziwymi danymi z Bitrix24

Test pełnego przepływu:
1. Pobierz SPA z API
2. Pobierz deale z API  
3. Przetworz (waliduj, sortuj, przydziel)
4. Sprawdź wyniki
"""
import pytest
from src.config import get_bitrix_client
from src.models import SPA, Deal, DealStage
from src.business_logic import QualificationValidator, DealPrioritizer, SlotAllocator
from src.business_logic.promoter import DealPromoter


class TestFullWorkflowWithRealData:
    """Testy end-to-end z prawdziwymi danymi z Bitrix24"""
    
    def test_fetch_spa_from_api(self):
        """✅ Pobierz SPA z API i sparsuj do modelu"""
        # Given
        client = get_bitrix_client()
        
        # When
        result = client.crm.item.get(bitrix_id=112, entity_type_id=1032)
        spa = SPA.from_api(result.result)
        
        # Then
        assert spa.id == 112
        assert spa.title is not None
        assert isinstance(spa.free_all, int)
        print(f"\n✅ SPA: {spa.title[:50]}")
        print(f"   Wolne wszystkie: {spa.free_all}")
        print(f"   Bezpłciowe: {spa.is_genderless_order()}")
    
    def test_fetch_deals_from_api(self):
        """✅ Pobierz deale z API i sparsuj do modeli"""
        # Given
        client = get_bitrix_client()
        
        # When
        result = client.crm.deal.list(
            filter={"STAGE_ID": DealStage.RESERVE.value},
            select=[
                "ID", "TITLE", "STAGE_ID",
                "UF_CRM_1743329864",  # Priorytet
                "UF_CRM_1740931330",  # SPA ID
                "UF_CRM_1740931105",  # Płeć
                "UF_CRM_1740931164",  # Mieszkanie
                "UF_CRM_1669643033481",  # Wiek
                "UF_CRM_1740931256",  # Data przyjazdu
                "UF_CRM_1741856527",  # Data EXECUTING
            ]
        )
        
        deals_data = result.result
        deals = [Deal.from_api(d) for d in deals_data]
        
        # Then
        assert len(deals) > 0, "Powinny być jakieś deale w rezerwie"
        print(f"\n✅ Znaleziono {len(deals)} dealów w rezerwie")
        print(f"   Przykład: {deals[0].title[:30]}...")
    
    def test_complete_promotion_workflow(self):
        """✅ Pełny workflow: fetch → process → promote"""
        # Given
        client = get_bitrix_client()
        promoter = DealPromoter()
        
        # 1. Pobierz SPA
        spa_result = client.crm.item.get(bitrix_id=112, entity_type_id=1032)
        spa = SPA.from_api(spa_result.result)
        
        # 2. Pobierz deale z Rezerwy
        deals_result = client.crm.deal.list(
            filter={
                "STAGE_ID": DealStage.RESERVE.value,
                "UF_CRM_1740931330": "112",  # Tylko dla tego SPA
            },
            select=[
                "ID", "TITLE", "STAGE_ID", "PARENT_ID_1032",
                "UF_CRM_1743329864", "UF_CRM_1740931330",
                "UF_CRM_1740931105", "UF_CRM_1740931164",
                "UF_CRM_1669643033481", "UF_CRM_1740931256",
                "UF_CRM_1741856527",
            ]
        )
        
        deals_data = deals_result.result
        deals = [Deal.from_api(d) for d in deals_data]
        
        print(f"\n📊 PRZETWARZANIE:")
        print(f"   SPA: {spa.title[:50]}")
        print(f"   Deale wejściowe: {len(deals)}")
        print(f"   Limit: {spa.free_all}")
        print(f"   Typ: {'Bezpłciowe' if spa.is_genderless_order() else 'Płciowe'}")
        
        # 3. Przetwórz
        promoted, reserve, stats = promoter.process(spa, deals)
        
        print(f"\n📈 WYNIKI:")
        print(f"   Kwalifikujące się: {stats['qualified']}")
        print(f"   Awansowane: {stats['promoted']}")
        print(f"   Do rezerwy: {stats['reserve']}")
        print(f"   Odrzucone: {stats['rejected']}")
        
        if stats['category_stats']:
            print(f"\n🏷️  KATEGORIE:")
            for cat, count in stats['category_stats'].items():
                if count > 0:
                    print(f"   {cat}: {count}")
        
        # Then
        assert isinstance(promoted, list)
        assert isinstance(reserve, list)
        assert stats['total_input'] == len(deals)
        
        # Podsumowanie
        summary = promoter.get_promotion_summary(stats)
        print(f"\n{summary}")
        
        print("\n✅ Pełny workflow działa poprawnie!")

