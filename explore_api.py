#!/usr/bin/env python3
"""
Eksploracja API Bitrix24 przez b24pysdk
Testujemy różne metody i sprawdzamy strukturę danych
"""
from src.config import get_bitrix_client
import json


def explore_spa_structure():
    """Eksploruj strukturę SPA (Smart Process)"""
    print("=" * 80)
    print("🔍 EKSPLORACJA: SPA (Smart Process, entityTypeId=1032)")
    print("=" * 80)
    
    client = get_bitrix_client()
    
    # Pobierz jedno SPA dla analizy
    spa_id = 112
    
    try:
        result = client.crm.item.get(
            bitrix_id=spa_id,
            entity_type_id=1032
        )
        
        spa_data = result.result
        
        print(f"\n✅ Pobrano SPA ID: {spa_id}")
        print(f"📦 Typ wyniku: {type(spa_data)}")
        print(f"🔑 Dostępne klucze: {list(spa_data.keys())[:20]}...")  # Pierwsze 20
        
        # Szczegóły ważnych pól
        print("\n📊 KLUCZOWE POLA SPA:")
        important_fields = {
            'id': spa_data.get('id'),
            'title': spa_data.get('title'),
            'stageId': spa_data.get('stageId'),
            'ufCrm9_1740930205': spa_data.get('ufCrm9_1740930205'),  # Wolne wszystkie
            'ufCrm9_1740930537': spa_data.get('ufCrm9_1740930537'),  # Data szkolenia
            'ufCrm9_1747740109': spa_data.get('ufCrm9_1747740109'),  # Bezpłciowe
        }
        
        for key, value in important_fields.items():
            print(f"  {key}: {value}")
        
        # Wszystkie pola UF_CRM (custom fields)
        print("\n🏷️  WSZYSTKIE POLA ufCrm9_* (custom fields):")
        uf_fields = {k: v for k, v in spa_data.items() if k.startswith('ufCrm9_')}
        for key, value in sorted(uf_fields.items()):
            if value:  # Tylko wypełnione
                print(f"  {key}: {value}")
        
        # Zapisz pełną strukturę do pliku
        with open('/tmp/spa_structure.json', 'w', encoding='utf-8') as f:
            json.dump(spa_data, f, indent=2, ensure_ascii=False, default=str)
        print("\n💾 Pełna struktura zapisana do: /tmp/spa_structure.json")
        
    except Exception as e:
        print(f"❌ Błąd: {e}")
        import traceback
        traceback.print_exc()


def explore_deal_structure():
    """Eksploruj strukturę Deal"""
    print("\n" + "=" * 80)
    print("🔍 EKSPLORACJA: Deal (Kandydat)")
    print("=" * 80)
    
    client = get_bitrix_client()
    
    try:
        # Pobierz listę dealów z rezerwy dla SPA 112
        result = client.crm.deal.list(
            filter={
                "STAGE_ID": "C25:UC_5I8UBF",  # Rezerwa
                "UF_CRM_1740931330": "112"     # SPA ID
            },
            select=["*"],  # Wszystkie pola
        )
        
        deals = result.result
        
        print(f"\n✅ Znaleziono {len(deals)} dealów w rezerwie dla SPA 112")
        
        if deals:
            # Analizuj pierwszy deal
            deal = deals[0]
            
            print(f"\n📦 Przykładowy Deal ID: {deal.get('ID')}")
            print(f"📦 Typ wyniku: {type(deal)}")
            print(f"🔑 Dostępne klucze: {len(deal.keys())} pól")
            
            # Szczegóły ważnych pól
            print("\n📊 KLUCZOWE POLA DEAL:")
            important_fields = {
                'ID': deal.get('ID'),
                'TITLE': deal.get('TITLE'),
                'STAGE_ID': deal.get('STAGE_ID'),
                'PARENT_ID_1032': deal.get('PARENT_ID_1032'),  # SPA ID
                'UF_CRM_1743329864': deal.get('UF_CRM_1743329864'),  # Priorytet
                'UF_CRM_1740931105': deal.get('UF_CRM_1740931105'),  # Płeć
                'UF_CRM_1740931164': deal.get('UF_CRM_1740931164'),  # Mieszkanie
                'UF_CRM_1740930520': deal.get('UF_CRM_1740930520'),  # Wiek
                'UF_CRM_1740931256': deal.get('UF_CRM_1740931256'),  # Data przyjazdu
                'UF_CRM_1741856527': deal.get('UF_CRM_1741856527'),  # Data EXECUTING
            }
            
            for key, value in important_fields.items():
                print(f"  {key}: {value}")
            
            # Wszystkie pola UF_CRM
            print("\n🏷️  WSZYSTKIE POLA UF_CRM_* (custom fields):")
            uf_fields = {k: v for k, v in deal.items() if k.startswith('UF_CRM_')}
            for key, value in sorted(uf_fields.items()):
                if value:  # Tylko wypełnione
                    print(f"  {key}: {value}")
            
            # Zapisz pełną strukturę
            with open('/tmp/deal_structure.json', 'w', encoding='utf-8') as f:
                json.dump(deal, f, indent=2, ensure_ascii=False, default=str)
            print("\n💾 Pełna struktura zapisana do: /tmp/deal_structure.json")
        else:
            print("⚠️  Brak dealów w rezerwie dla SPA 112")
            
    except Exception as e:
        print(f"❌ Błąd: {e}")
        import traceback
        traceback.print_exc()


def explore_pagination():
    """Test paginacji - as_list() vs as_list_fast()"""
    print("\n" + "=" * 80)
    print("🔍 EKSPLORACJA: Paginacja (as_list vs as_list_fast)")
    print("=" * 80)
    
    client = get_bitrix_client()
    
    try:
        # Test 1: Zwykły list (max 50)
        print("\n📋 Test 1: Zwykły .list() (max 50 rekordów)")
        result = client.crm.deal.list(
            filter={"STAGE_ID": "C25:UC_5I8UBF"}
        )
        deals_limited = result.result
        print(f"  Zwrócono: {len(deals_limited)} dealów")
        
        # Test 2: as_list() - wszystkie rekordy
        print("\n📋 Test 2: .as_list() (wszystkie rekordy)")
        result = client.crm.deal.list(
            filter={"STAGE_ID": "C25:UC_5I8UBF"}
        )
        deals_all = result.as_list().result
        print(f"  Zwrócono: {len(deals_all)} dealów")
        print(f"  Typ: {type(deals_all)}")
        
        # Test 3: as_list_fast() - generator
        print("\n📋 Test 3: .as_list_fast() (generator, lazy loading)")
        result = client.crm.deal.list(
            filter={"STAGE_ID": "C25:UC_5I8UBF"}
        )
        deals_generator = result.as_list_fast().result
        print(f"  Typ: {type(deals_generator)}")
        
        # Zlicz przez iterację
        count = 0
        for deal in deals_generator:
            count += 1
            if count <= 3:  # Pokaż pierwsze 3
                print(f"    Deal {count}: ID={deal.get('ID')}, Title={deal.get('TITLE')[:50]}...")
        print(f"  Łącznie: {count} dealów (przez generator)")
        
        print("\n💡 WNIOSEK:")
        print("  - .list() -> max 50 rekordów")
        print("  - .as_list() -> wszystkie rekordy (lista)")
        print("  - .as_list_fast() -> wszystkie rekordy (generator) - ZALECANE dla dużych zbiorów")
        
    except Exception as e:
        print(f"❌ Błąd: {e}")
        import traceback
        traceback.print_exc()


def explore_batch_operations():
    """Test batch operations"""
    print("\n" + "=" * 80)
    print("🔍 EKSPLORACJA: Batch Operations")
    print("=" * 80)
    
    client = get_bitrix_client()
    
    try:
        # Przygotuj batch request (bez wykonania)
        print("\n📦 Tworzenie batch request (symulacja)...")
        
        # Przykład: Pobierz 3 SPA naraz
        batch_requests = {
            "spa_112": client.crm.item.get(bitrix_id=112, entity_type_id=1032),
            "spa_113": client.crm.item.get(bitrix_id=113, entity_type_id=1032),
            "spa_114": client.crm.item.get(bitrix_id=114, entity_type_id=1032),
        }
        
        print(f"  Przygotowano {len(batch_requests)} requestów")
        print("  Klucze:", list(batch_requests.keys()))
        
        # Wykonaj batch (zgodnie z dokumentacją)
        print("\n🚀 Wykonywanie batch request...")
        batch_result = client.call_batch(batch_requests)
        
        print(f"  Status: {type(batch_result)}")
        print(f"  Wyniki: {len(batch_result.result.result)} odpowiedzi")
        
        # Wyświetl wyniki
        for key, spa_data in batch_result.result.result.items():
            title = spa_data.get('title', 'N/A') if isinstance(spa_data, dict) else 'N/A'
            print(f"    {key}: {title}")
        
        print("\n💡 WNIOSEK:")
        print("  - call_batch() wykonuje do 50 requestów naraz")
        print("  - Idealne dla mass updates lub pobierania wielu rekordów")
        
    except Exception as e:
        print(f"❌ Błąd: {e}")
        import traceback
        traceback.print_exc()


def explore_fields_metadata():
    """Pobierz metadane pól (fields)"""
    print("\n" + "=" * 80)
    print("🔍 EKSPLORACJA: Metadane pól (fields)")
    print("=" * 80)
    
    client = get_bitrix_client()
    
    try:
        # Pobierz definicje pól dla dealów
        print("\n📋 Pobieranie definicji pól dla Deal...")
        result = client.crm.deal.fields()
        fields = result.result
        
        print(f"  Znaleziono {len(fields)} pól")
        
        # Pokaż kilka ważnych pól
        important = [
            'STAGE_ID',
            'UF_CRM_1743329864',  # Priorytet
            'UF_CRM_1740931105',  # Płeć
            'UF_CRM_1740931164',  # Mieszkanie
        ]
        
        print("\n🔑 Przykładowe definicje pól:")
        for field_name in important:
            if field_name in fields:
                field_def = fields[field_name]
                print(f"\n  {field_name}:")
                print(f"    Type: {field_def.get('type')}")
                print(f"    Title: {field_def.get('formLabel', field_def.get('listLabel', 'N/A'))}")
                if 'items' in field_def:
                    print(f"    Values: {list(field_def['items'].keys())[:5]}...")
        
        # Zapisz wszystkie definicje
        with open('/tmp/deal_fields.json', 'w', encoding='utf-8') as f:
            json.dump(fields, f, indent=2, ensure_ascii=False, default=str)
        print("\n💾 Pełne definicje zapisane do: /tmp/deal_fields.json")
        
    except Exception as e:
        print(f"❌ Błąd: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    print("\n🚀 EKSPLORACJA API b24pysdk")
    print("=" * 80)
    
    # 1. Struktura SPA
    explore_spa_structure()
    
    # 2. Struktura Deal
    explore_deal_structure()
    
    # 3. Paginacja
    explore_pagination()
    
    # 4. Batch operations
    explore_batch_operations()
    
    # 5. Metadane pól
    explore_fields_metadata()
    
    print("\n" + "=" * 80)
    print("✅ EKSPLORACJA ZAKOŃCZONA!")
    print("=" * 80)
    print("\n📁 Pliki zapisane w /tmp/:")
    print("  - spa_structure.json")
    print("  - deal_structure.json")
    print("  - deal_fields.json")

