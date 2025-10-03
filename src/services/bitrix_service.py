"""
BitrixService - wrapper na operacje Bitrix24

Używa bezpośrednich requestów dla update (b24pysdk ma problemy z deferred calls)
"""
import os
import requests
from typing import List, Dict, Any


class BitrixService:
    """Service do aktualizacji dealów w Bitrix24"""
    
    def __init__(self):
        self.domain = os.getenv("BITRIX_DOMAIN", "ralengroup.bitrix24.pl")
        self.user_id = os.getenv("BITRIX_USER_ID", "25031")
        self.webhook_key = os.getenv("BITRIX_WEBHOOK_KEY", "6cg9uncuyvbxtiq3")
        self.base_url = f"https://{self.domain}/rest/{self.user_id}/{self.webhook_key}"
    
    def update_deal_stage(self, deal_id: str, new_stage: str) -> bool:
        """
        Aktualizuje etap deala
        
        Args:
            deal_id: ID deala
            new_stage: Nowy etap (STAGE_ID)
            
        Returns:
            bool: True jeśli sukces
        """
        url = f"{self.base_url}/crm.deal.update"
        
        data = {
            "id": deal_id,
            "fields": {
                "STAGE_ID": new_stage
            }
        }
        
        response = requests.post(url, json=data, timeout=10)
        result = response.json()
        
        return result.get('result', False)
    
    def batch_update_stages(
        self, 
        updates: List[Dict[str, str]]
    ) -> Dict[str, bool]:
        """
        Batch update etapów dealów
        
        Args:
            updates: Lista dict z kluczami 'id' i 'stage'
            
        Returns:
            Dict[str, bool]: Mapowanie deal_id → success
        """
        results = {}
        
        for update in updates:
            deal_id = update['id']
            new_stage = update['stage']
            
            success = self.update_deal_stage(deal_id, new_stage)
            results[deal_id] = success
        
        return results

