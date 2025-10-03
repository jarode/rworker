"""
Model Deal (Kandydat)
Category ID: 25 (Rekrutacja NEW) w Bitrix24
"""
from pydantic import BaseModel, Field, field_validator
from typing import Optional
from datetime import datetime
from .enums import DealStage, Gender, Housing, DealPriority, get_category_key


class Deal(BaseModel):
    """
    Model deala (kandydata)
    
    Zgodnie z API Discovery - dane przychodzą bezpośrednio w result
    """
    
    # Podstawowe pola (UWAGA: ID jest stringiem!)
    id: str = Field(alias="ID")
    title: str = Field(alias="TITLE")
    stage_id: str = Field(alias="STAGE_ID")
    
    # Przypisanie do SPA
    spa_id: Optional[str] = Field(default=None, alias="PARENT_ID_1032", description="ID SPA (przez relację)")
    spa_id_alt: Optional[str] = Field(default=None, alias="UF_CRM_1740931330", description="ID SPA (przez pole)")
    
    # Priorytet SPA (1951=P1, 1953=P2, 1955=P3, 1957=P4)
    priority: Optional[str] = Field(default=None, alias="UF_CRM_1743329864", description="Priorytet SPA")
    
    # Dane kandydata - podstawowe
    gender: Optional[str] = Field(default=None, alias="UF_CRM_1740931105", description="Płeć")
    housing: Optional[str] = Field(default=None, alias="UF_CRM_1740931164", description="Mieszkanie")
    age: Optional[float] = Field(default=None, alias="UF_CRM_1669643033481", description="Wiek (POPRAWIONE!)")
    arrival_date: Optional[datetime] = Field(default=None, alias="UF_CRM_1740931256", description="Data przyjazdu")
    
    # Dodatkowe atrybuty priorytetyzacji
    sanepid: Optional[str] = Field(default=None, alias="UF_CRM_1740931132", description="Sanepid")
    recommendation: Optional[str] = Field(default=None, alias="UF_CRM_1740931312", description="Polecenie pracy")
    intermediary: Optional[str] = Field(default=None, alias="UF_CRM_1740931210", description="Pośrednik (Powrót)")
    return_worker: Optional[str] = Field(default=None, alias="UF_CRM_1748981275", description="Powrót")
    experience: Optional[str] = Field(default=None, alias="UF_CRM_1748981302", description="Doświadczenie")
    coordinator: Optional[str] = Field(default=None, alias="UF_CRM_1748981451", description="Koordynator")
    
    # Data dodania do EXECUTING (KRYTYCZNE dla sortowania!)
    executing_date: Optional[datetime] = Field(default=None, alias="UF_CRM_1741856527", description="Data dodania do EXECUTING")
    
    # Metadane
    created_by_id: Optional[str] = Field(default=None, alias="CREATED_BY_ID")
    date_create: Optional[datetime] = Field(default=None, alias="DATE_CREATE")
    date_modify: Optional[datetime] = Field(default=None, alias="DATE_MODIFY")
    
    class Config:
        populate_by_name = True
        use_enum_values = True
    
    @classmethod
    def from_api(cls, api_result: dict) -> "Deal":
        """
        Parsuje response z API Bitrix24
        
        Deal zwraca dane bezpośrednio (nie ma wrappera "item")
        
        Args:
            api_result: Dict z danymi deala
            
        Returns:
            Deal: Zwalidowany model
        """
        return cls(**api_result)
    
    def get_spa_id(self) -> Optional[str]:
        """
        Zwraca ID SPA (próbuje oba pola)
        
        Returns:
            Optional[str]: ID SPA lub None
        """
        return self.spa_id or self.spa_id_alt
    
    def get_category_key(self) -> Optional[str]:
        """
        Zwraca klucz kategorii miejsca (np. 'M_nasze', 'K_wlasne')
        
        Returns:
            Optional[str]: Klucz kategorii lub None jeśli brak danych
        """
        if not self.gender or not self.housing:
            return None
        
        try:
            gender_enum = Gender(self.gender)
            housing_enum = Housing(self.housing)
            return get_category_key(gender_enum, housing_enum)
        except ValueError:
            # Nieznana wartość
            return None
    
    def get_priority_level(self) -> int:
        """
        Zwraca poziom priorytetu jako int (1-4)
        
        Returns:
            int: 1-4 (niższy = wyższy priorytet) lub 999 jeśli brak
        """
        if not self.priority:
            return 999
        
        priority_map = {
            DealPriority.P1.value: 1,
            DealPriority.P2.value: 2,
            DealPriority.P3.value: 3,
            DealPriority.P4.value: 4,
        }
        
        return priority_map.get(self.priority, 999)
    
    def is_assigned_to_spa(self, spa_id: str) -> bool:
        """Sprawdza czy deal jest przypisany do danego SPA"""
        return self.get_spa_id() == str(spa_id)
    
    def is_in_stage(self, stage: DealStage) -> bool:
        """Sprawdza czy deal jest w danym etapie"""
        return self.stage_id == stage.value
    
    @field_validator('arrival_date', 'executing_date', 'date_create', 'date_modify', mode='before')
    @classmethod
    def parse_datetime(cls, value):
        """Parsuje datetime z API"""
        if value is None or value == "":
            return None
        if isinstance(value, datetime):
            return value
        if isinstance(value, str):
            try:
                # API zwraca format: "2025-10-10T03:00:00+03:00"
                return datetime.fromisoformat(value.replace('+03:00', '+00:00'))
            except (ValueError, AttributeError):
                return None
        return None
    
    @field_validator('age', mode='before')
    @classmethod
    def parse_age(cls, value):
        """Parsuje wiek (może być string lub int)"""
        if value is None or value == "":
            return None
        try:
            return int(value)
        except (ValueError, TypeError):
            return None
    
    def __repr__(self) -> str:
        return f"Deal(id={self.id}, title='{self.title[:30]}...', stage={self.stage_id}, priority={self.priority})"
    
    def to_summary(self) -> dict:
        """Zwraca podsumowanie deala dla logowania/debugowania"""
        return {
            "id": self.id,
            "title": self.title,
            "stage": self.stage_id,
            "spa_id": self.get_spa_id(),
            "priority": self.priority,
            "priority_level": self.get_priority_level(),
            "category": self.get_category_key(),
            "age": self.age,
            "arrival_date": self.arrival_date.isoformat() if self.arrival_date else None,
            "executing_date": self.executing_date.isoformat() if self.executing_date else None,
        }

