"""
Enumy dla systemu SPA
Wszystkie wartości ID z Bitrix24 (potwierdzone przez API Discovery)
"""
from enum import Enum


class DealStage(str, Enum):
    """Etapy dealów (Rekrutacja NEW, Category ID: 25)"""
    
    # Etapy procesu
    SORTING = "C25:UC_10QO3W"          # Sortowanie
    RESERVE = "C25:UC_5I8UBF"          # Rezerwa
    MAIN_LIST = "C25:UC_0LRPVJ"        # Lista Główna
    IN_PROGRESS = "C25:FINAL_INVOICE"  # W procesie
    PLANNED_ARRIVAL = "C25:UC_1U3ODN"  # Zaplanowany przyjazd
    READY_TO_WORK = "C25:UC_MRU2SY"    # Przyjechał / Gotowy do pracy
    
    # Etapy końcowe
    NOT_ARRIVED = "C25:LOSE"           # Nie przyjechał
    NOT_HIRING = "C25:UC_BS2Y58"       # Nie zatrudniamy
    ARRIVED_LEFT = "C25:APOLOGY"       # Przyjechał-uciekł


class SPAStage(str, Enum):
    """Etapy SPA (Smart Process, Entity Type: 1032)"""
    
    NEW = "DT1032_17:NEW"              # Nowy
    IN_PROGRESS = "DT1032_17:UC_CU0OTZ"  # W trakcie (Otwarta Rekrutacja)
    SUCCESS = "DT1032_17:SUCCESS"      # Sukces


class Gender(str, Enum):
    """Płeć kandydata (UF_CRM_1740931105)"""
    
    FEMALE = "1907"  # Kobieta (K)
    MALE = "1909"    # Mężczyzna (M)
    COUPLE = "1911"  # Para (PARA)


class Housing(str, Enum):
    """Typ mieszkania (UF_CRM_1740931164)"""
    
    OWN = "1917"   # Własne
    OURS = "1919"  # Nasze


class DealPriority(str, Enum):
    """Priorytet SPA deala (UF_CRM_1743329864)"""
    
    P1 = "1951"  # Priorytet 1 (najwyższy)
    P2 = "1953"  # Priorytet 2
    P3 = "1955"  # Priorytet 3
    P4 = "1957"  # Priorytet 4 (najniższy)


class GenderlessOrder(str, Enum):
    """Czy zamówienie jest bezpłciowe? (ufCrm9_1747740109)"""
    
    YES = "1991"  # Tak - pomija filtry płci
    NO = "1993"   # Nie - sprawdza płeć i mieszkanie


class YesNo(str, Enum):
    """Standardowe pole Tak/Nie w Bitrix24"""
    
    YES = "1913"  # Tak
    NO = "1915"   # Nie


class SPAPriorityType(int, Enum):
    """
    Typy priorytetów w SPA (wartości pól Priority 1/2/3)
    Zgodnie z LOGIKA_AWANSU.md
    """
    
    # Priority 1 (ufCrm9_1740930561)
    SANEPID_P1 = 1867
    ARRIVAL_DATE_P1 = 1875
    HOUSING_OURS_P1 = 1873
    HOUSING_OWN_P1 = 1871
    RECOMMENDATION_P1 = 1877
    RETURN_P1 = 2013
    EXPERIENCE_P1 = 2015
    GENDER_F_P1 = 2017
    GENDER_M_P1 = 2019
    COORDINATOR_P1 = 2021
    DATE_ADDED_P1 = 1869
    
    # Priority 2 (ufCrm9_1740930829)
    AGE_P2 = 1879
    ARRIVAL_DATE_P2 = 1881
    HOUSING_OURS_P2 = 1885
    HOUSING_OWN_P2 = 1883
    RECOMMENDATION_P2 = 1889
    RETURN_P2 = 1887
    EXPERIENCE_P2 = 2023
    SANEPID_P2 = 2025
    GENDER_F_P2 = 2027
    GENDER_M_P2 = 2029
    COORDINATOR_P2 = 2031
    DATE_ADDED_P2 = 2033
    
    # Priority 3 (ufCrm9_1740930917)
    AGE_P3 = 1891
    ARRIVAL_DATE_P3 = 1899
    HOUSING_OURS_P3 = 1897
    HOUSING_OWN_P3 = 1895
    RECOMMENDATION_P3 = 1901
    RETURN_P3 = 1893
    EXPERIENCE_P3 = 2035
    SANEPID_P3 = 2037
    GENDER_F_P3 = 2039
    GENDER_M_P3 = 2041
    COORDINATOR_P3 = 2043
    DATE_ADDED_P3 = 2045


# Pomocnicze mapowania dla czytelności kodu

GENDER_LABELS = {
    Gender.FEMALE: "Kobieta",
    Gender.MALE: "Mężczyzna",
    Gender.COUPLE: "Para",
}

HOUSING_LABELS = {
    Housing.OWN: "Własne",
    Housing.OURS: "Nasze",
}

PRIORITY_LABELS = {
    DealPriority.P1: "Priorytet 1 (najwyższy)",
    DealPriority.P2: "Priorytet 2",
    DealPriority.P3: "Priorytet 3",
    DealPriority.P4: "Priorytet 4 (najniższy)",
}

STAGE_LABELS = {
    DealStage.SORTING: "Sortowanie",
    DealStage.RESERVE: "Rezerwa",
    DealStage.MAIN_LIST: "Lista Główna",
    DealStage.IN_PROGRESS: "W procesie",
    DealStage.PLANNED_ARRIVAL: "Zaplanowany przyjazd",
    DealStage.READY_TO_WORK: "Przyjechał / Gotowy do pracy",
}


def get_category_key(gender: Gender, housing: Housing) -> str:
    """
    Zwraca klucz kategorii miejsca (np. 'M_nasze', 'K_wlasne')
    Używane do mapowania na pola SPA
    """
    gender_map = {
        Gender.MALE: "M",
        Gender.FEMALE: "K",
        Gender.COUPLE: "PARY",
    }
    
    housing_map = {
        Housing.OURS: "nasze",
        Housing.OWN: "wlasne",
    }
    
    gender_str = gender_map.get(gender, "?")
    housing_str = housing_map.get(housing, "?")
    
    return f"{gender_str}_{housing_str}"

