"""
Konfiguracja Bitrix24 SDK
Zgodnie z oficjalną dokumentacją b24pysdk

API REFERENCE (b24pysdk 0.1.0a1):
- client.crm.item.get(bitrix_id=X, entity_type_id=Y)  # Pobierz item
- client.crm.deal.list(filter={...}, select=[...])     # Lista dealów
- client.crm.deal.update(bitrix_id=X, fields={...})    # Update deala
- request.result                                        # Wynik requestu
- request.as_list()                                     # Pełna lista (auto-pagination)
- request.as_list_fast()                                # Generator (lazy loading)
"""
import os
from dotenv import load_dotenv
from b24pysdk import BitrixWebhook, Client

# Wczytaj zmienne środowiskowe
load_dotenv()


class BitrixConfig:
    """Konfiguracja połączenia z Bitrix24"""
    
    def __init__(self):
        self.domain = os.getenv("BITRIX_DOMAIN", "ralengroup.bitrix24.pl")
        self.user_id = os.getenv("BITRIX_USER_ID", "25031")
        self.webhook_key = os.getenv("BITRIX_WEBHOOK_KEY", "6cg9uncuyvbxtiq3")
        
        # Webhook token w formacie: user_id/webhook_key
        self.auth_token = f"{self.user_id}/{self.webhook_key}"
    
    def get_client(self) -> Client:
        """
        Zwraca skonfigurowanego klienta Bitrix24
        
        Zgodnie z dokumentacją:
        https://github.com/bitrix24/b24pysdk
        
        Przykłady użycia:
        
        # Pobierz SPA (Smart Process, entityTypeId=1032)
        spa = client.crm.item.get(
            bitrix_id=112,
            entity_type_id=1032
        )
        
        # Lista dealów z filtrowaniem
        deals = client.crm.deal.list(
            filter={"STAGE_ID": "C25:UC_5I8UBF"},
            select=["ID", "TITLE"]
        ).as_list_fast().result  # Generator dla dużych zbiorów
        
        # Update deala
        client.crm.deal.update(
            bitrix_id=123,
            fields={"STAGE_ID": "C25:UC_0LRPVJ"}
        )
        """
        bitrix_webhook = BitrixWebhook(
            domain=self.domain,
            auth_token=self.auth_token
        )
        
        return Client(bitrix_webhook)


# Singleton - jedna instancja dla całej aplikacji
_config = None

def get_bitrix_client() -> Client:
    """Zwraca globalnego klienta Bitrix24"""
    global _config
    if _config is None:
        _config = BitrixConfig()
    return _config.get_client()

