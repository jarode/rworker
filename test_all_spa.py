#!/usr/bin/env python3
"""Test wszystkich SPA 'W trakcie' z wolnymi miejscami"""
from src.config import get_bitrix_client
import requests
import time

client = get_bitrix_client()

print("=" * 100)
print("🔍 TEST WSZYSTKICH SPA 'W TRAKCIE' Z WOLNYMI MIEJSCAMI")
print("=" * 100)

# Pobierz SPA
spa_result = client.crm.item.list(
    entity_type_id=1032,
    filter={"STAGE_ID": "DT1032_17:UC_CU0OTZ"},
    select=["ID", "TITLE", "ufCrm9_1740930205", "ufCrm9_1747740109"]
)

all_spa = list(spa_result.as_list_fast().result)
spa_with_slots = [s for s in all_spa if (s.get('ufCrm9_1740930205') or 0) > 0]

print(f"\n✅ Znaleziono {len(spa_with_slots)} SPA do przetestowania\n")

for i, spa_data in enumerate(spa_with_slots, 1):
    spa_id = spa_data['id']
    title = spa_data['title'][:50]
    free = spa_data.get('ufCrm9_1740930205', 0)
    is_genderless = spa_data.get('ufCrm9_1747740109') == 1991
    
    print(f"[{i}/{len(spa_with_slots)}] SPA {spa_id}: {title}")
    print(f"      Wolne: {free} | Typ: {'Bezpłciowe' if is_genderless else 'Płciowe'}")
    
    try:
        resp = requests.get(f'http://localhost:5000/webhook/spa/{spa_id}/dry-run', timeout=30)
        
        if resp.status_code == 200:
            result = resp.json()
            stats = result.get('stats', {})
            
            print(f"      ✅ In:{stats.get('total_input',0)} | " +
                  f"Qual:{stats.get('qualified',0)} | " +
                  f"Prom:{stats.get('promoted',0)} | " +
                  f"Rez:{stats.get('reserve',0)} | " +
                  f"Odrzuc:{stats.get('rejected',0)}")
            
            cat_stats = {k:v for k,v in stats.get('category_stats',{}).items() if v>0}
            if cat_stats:
                print(f"      📦 {cat_stats}")
        else:
            print(f"      ❌ HTTP {resp.status_code}")
    except Exception as e:
        print(f"      ❌ {str(e)[:60]}")
    
    print()
    time.sleep(0.2)

print("=" * 100)
print("✅ TEST ZAKOŃCZONY (DRY-RUN - bez zmian w Bitrix24)")
print("=" * 100)
