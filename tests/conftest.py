"""
Pytest fixtures dla testów
Wspólne dane testowe i helper functions
"""
import pytest
from datetime import datetime, timedelta
from src.models import SPA, Deal, Gender, Housing, DealPriority


@pytest.fixture
def sample_spa():
    """Przykładowe SPA do testów"""
    return SPA(
        id=112,
        title="Test SPA - Projekt testowy",
        stageId="DT1032_17:UC_CU0OTZ",  # W trakcie
        ufCrm9_1740930205=10,  # Wolne wszystkie
        ufCrm9_1740930322=5,   # Wolne M nasze
        ufCrm9_1740930346=3,   # Wolne K nasze
        ufCrm9_1740930371=2,   # Wolne PARY nasze
        ufCrm9_1740930392=3,   # Wolne M własne
        ufCrm9_1740930427=2,   # Wolne K własne
        ufCrm9_1740930439=1,   # Wolne PARY własne
        ufCrm9_1740930520=45,  # Limit wieku
        ufCrm9_1740930537=(datetime.now() + timedelta(days=30)).isoformat(),  # Data szkolenia za 30 dni
        ufCrm9_1747740109=1993,  # Nie bezpłciowe
    )


@pytest.fixture
def genderless_spa():
    """SPA bezpłciowe (pomija filtry płci)"""
    return SPA(
        id=113,
        title="Test SPA - Bezpłciowe",
        stageId="DT1032_17:UC_CU0OTZ",
        ufCrm9_1740930205=15,
        ufCrm9_1740930322=0,  # Brak miejsc M nasze
        ufCrm9_1740930346=0,  # Brak miejsc K nasze
        ufCrm9_1747740109=1991,  # Bezpłciowe!
        ufCrm9_1740930520=50,
        ufCrm9_1740930537=(datetime.now() + timedelta(days=45)).isoformat(),
    )


@pytest.fixture
def sample_deal():
    """Przykładowy deal (mężczyzna, nasze mieszkanie)"""
    return Deal(
        ID="10001",
        TITLE="Jan Kowalski",
        STAGE_ID="C25:UC_5I8UBF",  # Rezerwa
        PARENT_ID_1032="112",
        UF_CRM_1743329864=DealPriority.P1.value,  # Priorytet 1
        UF_CRM_1740931105=Gender.MALE.value,      # Mężczyzna
        UF_CRM_1740931164=Housing.OURS.value,     # Nasze
        UF_CRM_1669643033481=30,  # Wiek (POPRAWIONE POLE!)
        UF_CRM_1740931256=(datetime.now() + timedelta(days=20)).isoformat(),  # Data przyjazdu za 20 dni
        UF_CRM_1741856527=datetime.now().isoformat(),  # Data EXECUTING
    )


@pytest.fixture
def deal_female_own():
    """Deal - kobieta, własne mieszkanie"""
    return Deal(
        ID="10002",
        TITLE="Anna Nowak",
        STAGE_ID="C25:UC_5I8UBF",
        PARENT_ID_1032="112",
        UF_CRM_1743329864=DealPriority.P2.value,
        UF_CRM_1740931105=Gender.FEMALE.value,    # Kobieta
        UF_CRM_1740931164=Housing.OWN.value,      # Własne
        UF_CRM_1669643033481=35,  # POPRAWIONE POLE!
        UF_CRM_1740931256=(datetime.now() + timedelta(days=15)).isoformat(),
        UF_CRM_1741856527=datetime.now().isoformat(),
    )


@pytest.fixture
def deal_couple():
    """Deal - para"""
    return Deal(
        ID="10003",
        TITLE="Jan i Anna",
        STAGE_ID="C25:UC_5I8UBF",
        PARENT_ID_1032="112",
        UF_CRM_1743329864=DealPriority.P3.value,
        UF_CRM_1740931105=Gender.COUPLE.value,    # Para
        UF_CRM_1740931164=Housing.OURS.value,
        UF_CRM_1669643033481=28,  # POPRAWIONE POLE!
        UF_CRM_1740931256=(datetime.now() + timedelta(days=25)).isoformat(),
        UF_CRM_1741856527=datetime.now().isoformat(),
    )


@pytest.fixture
def deal_too_old():
    """Deal - za stary (przekracza limit)"""
    return Deal(
        ID="10004",
        TITLE="Zbigniew Stary",
        STAGE_ID="C25:UC_5I8UBF",
        PARENT_ID_1032="112",
        UF_CRM_1743329864=DealPriority.P1.value,
        UF_CRM_1740931105=Gender.MALE.value,
        UF_CRM_1740931164=Housing.OURS.value,
        UF_CRM_1669643033481=50,  # Za stary! (limit to 45) - POPRAWIONE POLE!
        UF_CRM_1740931256=(datetime.now() + timedelta(days=20)).isoformat(),
        UF_CRM_1741856527=datetime.now().isoformat(),
    )


@pytest.fixture
def deal_late_arrival():
    """Deal - przyjazd po dacie szkolenia"""
    return Deal(
        ID="10005",
        TITLE="Spóźnialski",
        STAGE_ID="C25:UC_5I8UBF",
        PARENT_ID_1032="112",
        UF_CRM_1743329864=DealPriority.P1.value,
        UF_CRM_1740931105=Gender.MALE.value,
        UF_CRM_1740931164=Housing.OURS.value,
        UF_CRM_1669643033481=30,  # POPRAWIONE POLE!
        UF_CRM_1740931256=(datetime.now() + timedelta(days=40)).isoformat(),  # Za późno! (szkolenie za 30 dni)
        UF_CRM_1741856527=datetime.now().isoformat(),
    )

