"""
Model SPA (Smart Process Automation)
Entity Type ID: 1032 w Bitrix24
"""
from pydantic import BaseModel, Field, field_validator
from typing import Optional
from datetime import datetime
from .enums import SPAStage, GenderlessOrder, SPAPriorityType


class SPA(BaseModel):
    """
    Model projektu SPA
    
    Zgodnie z API Discovery - dane przychodzą w result["item"]
    """
    
    # Podstawowe pola
    id: int
    title: str
    stage_id: str = Field(alias="stageId")
    
    # Limity miejsc (UWAGA: mogą być ujemne!)
    free_all: int = Field(alias="ufCrm9_1740930205", description="Wolne wszystkie (główny limit)")
    free_m_ours: int = Field(default=0, alias="ufCrm9_1740930322", description="Wolne M nasze")
    free_k_ours: int = Field(default=0, alias="ufCrm9_1740930346", description="Wolne K nasze")
    free_couple_ours: int = Field(default=0, alias="ufCrm9_1740930371", description="Wolne PARY nasze")
    free_m_own: int = Field(default=0, alias="ufCrm9_1740930392", description="Wolne M własne")
    free_k_own: int = Field(default=0, alias="ufCrm9_1740930427", description="Wolne K własne")
    free_couple_own: int = Field(default=0, alias="ufCrm9_1740930439", description="Wolne PARY własne")
    
    # Warunki kwalifikacji
    age_limit: Optional[int] = Field(default=None, alias="ufCrm9_1740930520", description="Limit wieku (<=)")
    training_date: Optional[datetime] = Field(default=None, alias="ufCrm9_1740930537", description="Data szkolenia")
    arrival_from: Optional[datetime] = Field(default=None, alias="ufCrm9_1740931899", description="Przyjazd OD (początek zakresu)")
    arrival_to: Optional[datetime] = Field(default=None, alias="ufCrm9_1740931913", description="Przyjazd DO (koniec zakresu)")
    
    # Priorytety dynamiczne (wartości SPAPriorityType)
    priority_1: Optional[int] = Field(default=None, alias="ufCrm9_1740930561", description="Priority 1")
    priority_2: Optional[int] = Field(default=None, alias="ufCrm9_1740930829", description="Priority 2")
    priority_3: Optional[int] = Field(default=None, alias="ufCrm9_1740930917", description="Priority 3")
    
    # Specjalne flagi (API zwraca int, ale przechowujemy jako string dla spójności z enumem)
    is_genderless: Optional[int] = Field(default=None, alias="ufCrm9_1747740109", description="Czy bezpłciowe?")
    
    # Metadane
    created_time: Optional[datetime] = Field(default=None, alias="createdTime")
    updated_time: Optional[datetime] = Field(default=None, alias="updatedTime")
    assigned_by_id: Optional[int] = Field(default=None, alias="assignedById")
    
    class Config:
        populate_by_name = True  # Pozwala używać zarówno alias jak i nazwy
        use_enum_values = True   # Automatycznie konwertuje enumy na wartości
    
    @classmethod
    def from_api(cls, api_result: dict) -> "SPA":
        """
        Parsuje response z API Bitrix24
        
        WAŻNE: API zwraca dane w result["item"], nie bezpośrednio!
        
        Args:
            api_result: Dict z kluczem "item" zawierającym dane SPA
            
        Returns:
            SPA: Zwalidowany model
            
        Example:
            >>> api_data = {"item": {"id": 112, "title": "...", ...}}
            >>> spa = SPA.from_api(api_data)
        """
        if "item" in api_result:
            return cls(**api_result["item"])
        else:
            # Fallback jeśli dane są bezpośrednio
            return cls(**api_result)
    
    def is_genderless_order(self) -> bool:
        """
        Sprawdza czy zamówienie jest bezpłciowe
        
        Zgodnie z LOGIKA_AWANSU.md:
        - 1991 = Tak (pomija filtry płci)
        - 1993 = Nie (sprawdza płeć i mieszkanie)
        """
        return self.is_genderless == 1991
    
    def has_free_slots(self) -> bool:
        """Czy są jakiekolwiek wolne miejsca?"""
        return self.free_all > 0
    
    def get_free_slots_for_category(self, category: str) -> int:
        """
        Zwraca liczbę wolnych miejsc dla danej kategorii
        
        Args:
            category: Klucz kategorii (np. 'M_nasze', 'K_wlasne', 'PARY_nasze')
            
        Returns:
            int: Liczba wolnych miejsc (może być ujemna!)
        """
        category_map = {
            "M_nasze": self.free_m_ours,
            "M_wlasne": self.free_m_own,
            "K_nasze": self.free_k_ours,
            "K_wlasne": self.free_k_own,
            "PARY_nasze": self.free_couple_ours,
            "PARY_wlasne": self.free_couple_own,
        }
        return category_map.get(category, 0)
    
    def get_priority_types(self) -> list[SPAPriorityType]:
        """
        Zwraca listę typów priorytetów ustawionych w SPA
        
        Returns:
            List[SPAPriorityType]: Lista priorytetów w kolejności 1, 2, 3
        """
        priorities = []
        
        for priority_value in [self.priority_1, self.priority_2, self.priority_3]:
            if priority_value is not None:
                try:
                    priorities.append(SPAPriorityType(priority_value))
                except ValueError:
                    # Nieznana wartość priorytetu - pomiń
                    pass
        
        return priorities
    
    @field_validator('training_date', 'arrival_from', 'arrival_to', 'created_time', 'updated_time', mode='before')
    @classmethod
    def parse_datetime(cls, value):
        """Parsuje datetime z API (może być string lub None)"""
        if value is None or value == "":
            return None
        if isinstance(value, datetime):
            return value
        if isinstance(value, str):
            # API zwraca format: "2026-01-30T03:00:00+03:00"
            try:
                return datetime.fromisoformat(value.replace('+03:00', '+00:00'))
            except (ValueError, AttributeError):
                return None
        return None
    
    def __repr__(self) -> str:
        return f"SPA(id={self.id}, title='{self.title[:30]}...', free_all={self.free_all})"
    
    def to_summary(self) -> dict:
        """Zwraca podsumowanie SPA dla logowania/debugowania"""
        return {
            "id": self.id,
            "title": self.title,
            "stage": self.stage_id,
            "free_all": self.free_all,
            "free_slots": {
                "M_nasze": self.free_m_ours,
                "M_wlasne": self.free_m_own,
                "K_nasze": self.free_k_ours,
                "K_wlasne": self.free_k_own,
                "PARY_nasze": self.free_couple_ours,
                "PARY_wlasne": self.free_couple_own,
            },
            "is_genderless": self.is_genderless_order(),
            "age_limit": self.age_limit,
            "training_date": self.training_date.isoformat() if self.training_date else None,
        }

