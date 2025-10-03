#!/usr/bin/env python3
"""
Webhook endpoint dla automatycznego przetwarzania SPA

Zgodnie z API webhookb6.php:
GET /webhook/spa/<spa_id>

Zwraca JSON z wynikami przetwarzania.
"""
import os
import logging
from flask import Flask, request, jsonify
from datetime import datetime
from src.config import get_bitrix_client
from src.models import SPA, Deal, DealStage
from src.business_logic import DealPromoter
from src.services import BitrixService
from src.utils.logger import setup_logger

app = Flask(__name__)

# Setup logging
logger = setup_logger("spa_webhook", level=os.getenv("LOG_LEVEL", "INFO"))


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "service": "SPA Automation",
        "version": "2.0.0-python",
        "timestamp": datetime.now().isoformat()
    })


@app.route('/webhook/spa/<int:spa_id>', methods=['GET', 'POST'])
def process_spa_webhook(spa_id: int):
    """
    Główny webhook przetwarzania SPA
    
    Parametry:
        spa_id: ID projektu SPA do przetworzenia
        
    Zwraca:
        JSON z wynikami przetwarzania
    """
    logger.info(f"=" * 80)
    logger.info(f"🚀 START przetwarzania SPA ID: {spa_id}")
    logger.info(f"=" * 80)
    
    try:
        # Inicjalizacja
        client = get_bitrix_client()
        bitrix_service = BitrixService()
        promoter = DealPromoter()
        
        # KROK 1: Pobierz dane SPA
        logger.info(f"📦 Krok 1: Pobieranie danych SPA...")
        spa_result = client.crm.item.get(
            bitrix_id=spa_id,
            entity_type_id=1032
        )
        spa = SPA.from_api(spa_result.result)
        
        logger.info(f"✅ SPA: {spa.title[:50]}")
        logger.info(f"   Wolne wszystkie: {spa.free_all}")
        logger.info(f"   Typ: {'Bezpłciowe' if spa.is_genderless_order() else 'Płciowe'}")
        
        # KROK 2: Pobierz deale z Sortowania i Rezerwy
        logger.info(f"📦 Krok 2: Pobieranie dealów...")
        deals = []
        
        for stage in [DealStage.SORTING, DealStage.RESERVE]:
            deals_result = client.crm.deal.list(
                filter={
                    "STAGE_ID": stage.value,
                    "UF_CRM_1740931330": str(spa_id),
                },
                select=[
                    "ID", "TITLE", "STAGE_ID", "PARENT_ID_1032",
                    "UF_CRM_1743329864",    # Priorytet
                    "UF_CRM_1740931330",    # SPA ID
                    "UF_CRM_1740931105",    # Płeć
                    "UF_CRM_1740931164",    # Mieszkanie
                    "UF_CRM_1669643033481", # Wiek
                    "UF_CRM_1740931256",    # Data przyjazdu
                    "UF_CRM_1741856527",    # Data EXECUTING
                ]
            )
            
            # Użyj as_list_fast() dla efektywności
            stage_count = 0
            for deal_data in deals_result.as_list_fast().result:
                deals.append(Deal.from_api(deal_data))
                stage_count += 1
            
            logger.info(f"   {stage.name}: {stage_count} dealów")
        
        logger.info(f"✅ Łącznie: {len(deals)} dealów")
        
        # KROK 3: Przetwórz
        logger.info(f"⚙️  Krok 3: Przetwarzanie (walidacja, sortowanie, przydział)...")
        promoted, reserve, stats = promoter.process(spa, deals)
        
        logger.info(f"✅ Wyniki:")
        logger.info(f"   Kwalifikujące się: {stats['qualified']}")
        logger.info(f"   Awansowane: {stats['promoted']}")
        logger.info(f"   Do rezerwy: {stats['reserve']}")
        logger.info(f"   Odrzucone: {stats['rejected']}")
        
        if stats.get('category_stats'):
            logger.info(f"   Kategorie:")
            for cat, count in stats['category_stats'].items():
                if count > 0:
                    logger.info(f"      {cat}: {count}")
        
        # KROK 4: Aktualizuj etapy w Bitrix24 (batch)
        logger.info(f"💾 Krok 4: Aktualizacja etapów w Bitrix24...")
        updates_count = 0
        
        if promoted:
            logger.info(f"   Awansowanie {len(promoted)} dealów do Lista Główna...")
            
            # Użyj BitrixService (bezpośrednie REST API calls)
            for deal in promoted:
                try:
                    success = bitrix_service.update_deal_stage(
                        deal_id=deal.id,
                        new_stage=DealStage.MAIN_LIST.value
                    )
                    
                    if success:
                        updates_count += 1
                        logger.info(f"      ✅ Deal {deal.id} → Lista Główna")
                    else:
                        logger.warning(f"      ⚠️  Deal {deal.id} - update zwrócił False")
                        
                except Exception as e:
                    logger.error(f"      ❌ Deal {deal.id} - błąd: {e}")
        
        if reserve:
            logger.info(f"   Aktualizacja {len(reserve)} dealów w Rezerwie...")
            
            # Użyj BitrixService
            for deal in reserve:
                # Przenieś do rezerwy tylko jeśli nie jest już w rezerwie
                if deal.stage_id != DealStage.RESERVE.value:
                    try:
                        success = bitrix_service.update_deal_stage(
                            deal_id=deal.id,
                            new_stage=DealStage.RESERVE.value
                        )
                        
                        if success:
                            updates_count += 1
                            logger.info(f"      ✅ Deal {deal.id} → Rezerwa")
                        else:
                            logger.warning(f"      ⚠️  Deal {deal.id} - update zwrócił False")
                            
                    except Exception as e:
                        logger.error(f"      ❌ Deal {deal.id} - błąd: {e}")
        
        logger.info(f"✅ ZAKOŃCZONO: {updates_count} zmian w Bitrix24")
        logger.info(f"=" * 80)
        
        # KROK 5: Zwróć wyniki
        return jsonify({
            "status": "success",
            "spa_id": spa_id,
            "spa_title": spa.title,
            "spa_type": "genderless" if spa.is_genderless_order() else "gendered",
            "free_all": spa.free_all,
            "stats": {
                "total_input": stats["total_input"],
                "qualified": stats["qualified"],
                "promoted": stats["promoted"],
                "reserve": stats["reserve"],
                "rejected": stats["rejected"],
                "updates_executed": updates_count,
            },
            "category_allocation": stats.get("category_stats", {}),
            "promoted_deals": [
                {
                    "id": d.id,
                    "title": d.title,
                    "priority": d.priority,
                    "category": stats["assignments"].get(d.id) if "assignments" in stats else None
                }
                for d in promoted
            ],
            "summary": promoter.get_promotion_summary(stats),
        })
        
    except Exception as e:
        # Obsługa błędów
        import traceback
        error_trace = traceback.format_exc()
        
        logger.error(f"❌ BŁĄD podczas przetwarzania SPA {spa_id}")
        logger.error(f"   Typ: {type(e).__name__}")
        logger.error(f"   Message: {str(e)}")
        logger.error(f"   Traceback:\n{error_trace}")
        
        return jsonify({
            "status": "error",
            "spa_id": spa_id,
            "error": str(e),
            "error_type": type(e).__name__,
            "traceback": error_trace
        }), 500


@app.route('/webhook/spa/<int:spa_id>/dry-run', methods=['GET'])
def dry_run_webhook(spa_id: int):
    """
    Dry-run (bez aktualizacji w Bitrix24)
    
    Przydatne do testowania logiki bez modyfikacji danych
    """
    try:
        client = get_bitrix_client()
        promoter = DealPromoter()
        
        # Pobierz SPA
        spa_result = client.crm.item.get(bitrix_id=spa_id, entity_type_id=1032)
        spa = SPA.from_api(spa_result.result)
        
        # Pobierz deale
        deals = []
        for stage in [DealStage.SORTING, DealStage.RESERVE]:
            deals_result = client.crm.deal.list(
                filter={
                    "STAGE_ID": stage.value,
                    "UF_CRM_1740931330": str(spa_id),
                },
                select=["ID", "TITLE", "STAGE_ID", "UF_CRM_1743329864", 
                        "UF_CRM_1740931330", "UF_CRM_1740931105", "UF_CRM_1740931164",
                        "UF_CRM_1669643033481", "UF_CRM_1740931256", "UF_CRM_1741856527"]
            )
            
            for deal_data in deals_result.as_list_fast().result:
                deals.append(Deal.from_api(deal_data))
        
        # Przetwórz (BEZ update!)
        promoted, reserve, stats = promoter.process(spa, deals)
        
        return jsonify({
            "status": "dry-run",
            "spa_id": spa_id,
            "spa_title": spa.title,
            "spa_type": "genderless" if spa.is_genderless_order() else "gendered",
            "stats": stats,
            "would_promote": [d.id for d in promoted],
            "would_reserve": [d.id for d in reserve],
            "summary": promoter.get_promotion_summary(stats),
            "note": "Dry-run: Żadne dane nie zostały zmienione w Bitrix24"
        })
        
    except Exception as e:
        return jsonify({
            "status": "error",
            "error": str(e)
        }), 500


if __name__ == '__main__':
    port = int(os.getenv('FLASK_PORT', 5000))
    debug = os.getenv('FLASK_DEBUG', '0') == '1'
    
    print("=" * 80)
    print("🚀 SPA Automation Webhook")
    print("=" * 80)
    print(f"Port: {port}")
    print(f"Debug: {debug}")
    print(f"\nEndpoints:")
    print(f"  GET  /health")
    print(f"  GET  /webhook/spa/<spa_id>")
    print(f"  GET  /webhook/spa/<spa_id>/dry-run")
    print("=" * 80)
    
    app.run(host='0.0.0.0', port=port, debug=debug)

