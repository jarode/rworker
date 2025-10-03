"""
Testy jednostkowe dla QualificationValidator

Zgodnie z LOGIKA_AWANSU.md - warunki kwalifikacji deala do SPA:
1. Data przyjazdu < Data szkolenia SPA
2. Wiek < Limit wieku SPA
3. Jeśli bezpłciowe → pomija filtry płci
4. Jeśli płciowe → sprawdza dostępność miejsc (kategoria)
"""
import pytest
from datetime import datetime, timedelta
from src.business_logic.validators import QualificationValidator
from src.models import SPA, Deal, Gender, Housing


class TestArrivalDateValidation:
    """
    WARUNEK 1: Data przyjazdu < Data szkolenia SPA
    
    Zgodnie z LOGIKA_AWANSU.md:
    - UF_CRM_1740931256 (deal) < ufCrm9_1740930537 (SPA)
    """
    
    def test_arrival_before_training_passes(self, sample_spa, sample_deal):
        """✅ Deal przyjeżdża PRZED szkoleniem - PASS"""
        # Given
        validator = QualificationValidator()
        
        # When
        result = validator.check_arrival_date(sample_deal, sample_spa)
        
        # Then
        assert result is True, "Deal z datą przyjazdu przed szkoleniem powinien przejść"
    
    def test_arrival_after_training_fails(self, sample_spa, deal_late_arrival):
        """❌ Deal przyjeżdża PO szkoleniu - FAIL"""
        # Given
        validator = QualificationValidator()
        
        # When
        result = validator.check_arrival_date(deal_late_arrival, sample_spa)
        
        # Then
        assert result is False, "Deal z datą przyjazdu po szkoleniu nie powinien przejść"
    
    def test_arrival_on_training_day_fails(self, sample_spa):
        """❌ Deal przyjeżdża W DNIU szkolenia - FAIL (musi być PRZED)"""
        # Given
        validator = QualificationValidator()
        deal = Deal(
            ID="999",
            TITLE="Test",
            STAGE_ID="C25:UC_5I8UBF",
            UF_CRM_1740931256=sample_spa.training_date.isoformat(),  # Dokładnie w dniu szkolenia
        )
        
        # When
        result = validator.check_arrival_date(deal, sample_spa)
        
        # Then
        assert result is False, "Deal przyjeżdżający w dniu szkolenia nie powinien przejść"
    
    def test_no_training_date_passes(self, sample_deal):
        """✅ Brak daty szkolenia - PASS (nie walidujemy)"""
        # Given
        validator = QualificationValidator()
        spa = SPA(
            id=999,
            title="Test",
            stageId="DT1032_17:UC_CU0OTZ",
            ufCrm9_1740930205=10,
            ufCrm9_1740930537=None,  # Brak daty szkolenia
        )
        
        # When
        result = validator.check_arrival_date(sample_deal, spa)
        
        # Then
        assert result is True, "Brak daty szkolenia → brak walidacji → PASS"
    
    def test_no_arrival_date_passes(self, sample_spa):
        """✅ Brak daty przyjazdu - PASS (nie walidujemy)"""
        # Given
        validator = QualificationValidator()
        deal = Deal(
            ID="999",
            TITLE="Test",
            STAGE_ID="C25:UC_5I8UBF",
            UF_CRM_1740931256=None,  # Brak daty przyjazdu
        )
        
        # When
        result = validator.check_arrival_date(deal, sample_spa)
        
        # Then
        assert result is True, "Brak daty przyjazdu → brak walidacji → PASS"


class TestArrivalDateRangeValidation:
    """
    WARUNEK 1 - ROZSZERZONY: Zakres dat przyjazdu (OD-DO)
    
    NOWE WYMAGANIA:
    - Deal.przyjazd >= SPA.arrival_from
    - Deal.przyjazd <= SPA.arrival_to
    - Deal.przyjazd < SPA.training_date
    """
    
    def test_arrival_in_range_passes(self):
        """✅ Data przyjazdu w zakresie OD-DO - PASS"""
        from datetime import datetime
        
        # Given
        validator = QualificationValidator()
        spa = SPA(
            id=999,
            title="Test",
            stageId="DT1032_17:UC_CU0OTZ",
            ufCrm9_1740930205=10,
            ufCrm9_1740931899=datetime(2026, 4, 1).isoformat(),   # Przyjazd OD
            ufCrm9_1740931913=datetime(2026, 4, 30).isoformat(),  # Przyjazd DO
            ufCrm9_1740930537=datetime(2026, 5, 15).isoformat(),  # Szkolenie
        )
        deal = Deal(
            ID="999",
            TITLE="Test",
            STAGE_ID="C25:UC_5I8UBF",
            UF_CRM_1740931256=datetime(2026, 4, 15).isoformat(),  # W środku zakresu
        )
        
        # When
        result = validator.check_arrival_date(deal, spa)
        
        # Then
        assert result is True, "Data w zakresie OD-DO powinna przejść"
    
    def test_arrival_before_range_fails(self):
        """❌ Data przyjazdu PRZED zakresem (OD) - FAIL"""
        from datetime import datetime
        
        validator = QualificationValidator()
        spa = SPA(
            id=999,
            title="Test",
            stageId="DT1032_17:UC_CU0OTZ",
            ufCrm9_1740930205=10,
            ufCrm9_1740931899=datetime(2026, 4, 1).isoformat(),
            ufCrm9_1740930537=datetime(2026, 5, 15).isoformat(),
        )
        deal = Deal(
            ID="999",
            TITLE="Test",
            STAGE_ID="C25:UC_5I8UBF",
            UF_CRM_1740931256=datetime(2026, 3, 25).isoformat(),  # Przed OD!
        )
        
        result = validator.check_arrival_date(deal, spa)
        assert result is False, "Data przed zakresem OD nie powinna przejść"
    
    def test_arrival_after_range_fails(self):
        """❌ Data przyjazdu PO zakresie (DO) - FAIL"""
        from datetime import datetime
        
        validator = QualificationValidator()
        spa = SPA(
            id=999,
            title="Test",
            stageId="DT1032_17:UC_CU0OTZ",
            ufCrm9_1740930205=10,
            ufCrm9_1740931899=datetime(2026, 4, 1).isoformat(),
            ufCrm9_1740931913=datetime(2026, 4, 30).isoformat(),  # DO
            ufCrm9_1740930537=datetime(2026, 5, 15).isoformat(),
        )
        deal = Deal(
            ID="999",
            TITLE="Test",
            STAGE_ID="C25:UC_5I8UBF",
            UF_CRM_1740931256=datetime(2026, 5, 5).isoformat(),  # Po DO!
        )
        
        result = validator.check_arrival_date(deal, spa)
        assert result is False, "Data po zakresie DO nie powinna przejść"


class TestAgeValidation:
    """
    WARUNEK 2: Wiek < Limit wieku SPA
    
    Zgodnie z LOGIKA_AWANSU.md:
    - UF_CRM_1740930520 (deal) < ufCrm9_1740930520 (SPA)
    """
    
    def test_age_below_limit_passes(self, sample_spa, sample_deal):
        """✅ Wiek poniżej limitu - PASS"""
        # Given
        validator = QualificationValidator()
        
        # When
        result = validator.check_age(sample_deal, sample_spa)
        
        # Then
        assert result is True, "Deal z wiekiem poniżej limitu powinien przejść"
    
    def test_age_above_limit_fails(self, sample_spa, deal_too_old):
        """❌ Wiek powyżej limitu - FAIL"""
        # Given
        validator = QualificationValidator()
        
        # When
        result = validator.check_age(deal_too_old, sample_spa)
        
        # Then
        assert result is False, "Deal z wiekiem powyżej limitu nie powinien przejść"
    
    def test_age_equal_limit_passes(self, sample_spa):
        """✅ Wiek równy limitowi - PASS (ZMIENIONE: <= zamiast <)"""
        # Given
        validator = QualificationValidator()
        deal = Deal(
            ID="999",
            TITLE="Test",
            STAGE_ID="C25:UC_5I8UBF",
            UF_CRM_1669643033481=45,  # Dokładnie limit (sample_spa ma 45)
        )
        
        # When
        result = validator.check_age(deal, sample_spa)
        
        # Then
        assert result is True, "Deal z wiekiem równym limitowi POWINIEN przejść (<=)"
    
    def test_no_age_limit_passes(self, sample_deal):
        """✅ Brak limitu wieku - PASS"""
        # Given
        validator = QualificationValidator()
        spa = SPA(
            id=999,
            title="Test",
            stageId="DT1032_17:UC_CU0OTZ",
            ufCrm9_1740930205=10,
            ufCrm9_1740930520=None,  # Brak limitu
        )
        
        # When
        result = validator.check_age(sample_deal, spa)
        
        # Then
        assert result is True, "Brak limitu wieku → brak walidacji → PASS"


class TestGenderlessSlotsValidation:
    """
    WARUNEK 3: Zamówienie bezpłciowe pomija filtry płci
    
    Zgodnie z LOGIKA_AWANSU.md:
    - Jeśli ufCrm9_1747740109 = 1991 (Tak) → pomija sprawdzanie płci/mieszkania
    """
    
    def test_genderless_order_skips_gender_check(self, genderless_spa, sample_deal):
        """✅ Zamówienie bezpłciowe - pomija filtry płci nawet gdy brak miejsc"""
        # Given
        validator = QualificationValidator()
        # genderless_spa ma 0 miejsc M_nasze, ale jest bezpłciowe
        
        # When
        result = validator.check_gender_slots(sample_deal, genderless_spa)
        
        # Then
        assert result is True, "Zamówienie bezpłciowe powinno pomijać filtry płci"
    
    def test_gendered_order_checks_slots(self, sample_spa, sample_deal):
        """✅ Zamówienie płciowe - sprawdza miejsca (M_nasze dostępne)"""
        # Given
        validator = QualificationValidator()
        # sample_spa ma 5 miejsc M_nasze
        
        # When
        result = validator.check_gender_slots(sample_deal, sample_spa)
        
        # Then
        assert result is True, "Zamówienie płciowe z dostępnymi miejscami powinno przejść"


class TestGenderSlotsValidation:
    """
    WARUNEK 4: Dostępność miejsc według kategorii (płeć + mieszkanie)
    
    Zgodnie z LOGIKA_AWANSU.md:
    - Sprawdza kategorię: M_nasze, M_wlasne, K_nasze, K_wlasne, PARY_nasze, PARY_wlasne
    - Jeśli główna kategoria pełna → sprawdź alternatywną (elastyczny przydział)
    """
    
    def test_primary_category_available_passes(self, sample_spa, sample_deal):
        """✅ Główna kategoria dostępna (M_nasze) - PASS"""
        # Given
        validator = QualificationValidator()
        # sample_deal: M + nasze, sample_spa: 5 miejsc M_nasze
        
        # When
        result = validator.check_gender_slots(sample_deal, sample_spa)
        
        # Then
        assert result is True
    
    def test_alternative_category_when_primary_full(self, sample_spa):
        """✅ Główna pełna, alternatywna dostępna - PASS (elastyczny przydział)"""
        # Given
        validator = QualificationValidator()
        spa = SPA(
            id=999,
            title="Test",
            stageId="DT1032_17:UC_CU0OTZ",
            ufCrm9_1740930205=10,
            ufCrm9_1740930322=0,  # M_nasze = 0 (PEŁNE)
            ufCrm9_1740930392=5,  # M_wlasne = 5 (DOSTĘPNE)
            ufCrm9_1747740109=1993,  # NIE bezpłciowe
        )
        deal = Deal(
            ID="999",
            TITLE="Test",
            STAGE_ID="C25:UC_5I8UBF",
            UF_CRM_1740931105=Gender.MALE.value,
            UF_CRM_1740931164=Housing.OURS.value,  # Chce "nasze", ale brak miejsc
        )
        
        # When
        result = validator.check_gender_slots(deal, spa)
        
        # Then
        assert result is True, "Powinien przejść przez alternatywną kategorię (M_wlasne)"
    
    def test_both_categories_full_fails(self):
        """❌ Obie kategorie pełne - FAIL"""
        # Given
        validator = QualificationValidator()
        spa = SPA(
            id=999,
            title="Test",
            stageId="DT1032_17:UC_CU0OTZ",
            ufCrm9_1740930205=10,
            ufCrm9_1740930322=0,  # M_nasze = 0
            ufCrm9_1740930392=0,  # M_wlasne = 0 (OBIE PEŁNE)
            ufCrm9_1747740109=1993,
        )
        deal = Deal(
            ID="999",
            TITLE="Test",
            STAGE_ID="C25:UC_5I8UBF",
            UF_CRM_1740931105=Gender.MALE.value,
            UF_CRM_1740931164=Housing.OURS.value,
        )
        
        # When
        result = validator.check_gender_slots(deal, spa)
        
        # Then
        assert result is False, "Brak miejsc w obu kategoriach → FAIL"
    
    def test_female_own_category(self, sample_spa, deal_female_own):
        """✅ Kategoria K_wlasne dostępna - PASS"""
        # Given
        validator = QualificationValidator()
        # deal_female_own: K + własne, sample_spa: 2 miejsca K_wlasne
        
        # When
        result = validator.check_gender_slots(deal_female_own, sample_spa)
        
        # Then
        assert result is True
    
    def test_couple_category(self, sample_spa, deal_couple):
        """✅ Kategoria PARY_nasze dostępna - PASS"""
        # Given
        validator = QualificationValidator()
        # deal_couple: PARA + nasze, sample_spa: 2 miejsca PARY_nasze
        
        # When
        result = validator.check_gender_slots(deal_couple, sample_spa)
        
        # Then
        assert result is True
    
    def test_missing_gender_fails(self, sample_spa):
        """❌ Brak płci - FAIL"""
        # Given
        validator = QualificationValidator()
        deal = Deal(
            ID="999",
            TITLE="Test",
            STAGE_ID="C25:UC_5I8UBF",
            UF_CRM_1740931105=None,  # Brak płci
            UF_CRM_1740931164=Housing.OURS.value,
        )
        
        # When
        result = validator.check_gender_slots(deal, sample_spa)
        
        # Then
        assert result is False, "Brak danych o płci → nie można przydzielić → FAIL"
    
    def test_missing_housing_fails(self, sample_spa):
        """❌ Brak mieszkania - FAIL"""
        # Given
        validator = QualificationValidator()
        deal = Deal(
            ID="999",
            TITLE="Test",
            STAGE_ID="C25:UC_5I8UBF",
            UF_CRM_1740931105=Gender.MALE.value,
            UF_CRM_1740931164=None,  # Brak mieszkania
        )
        
        # When
        result = validator.check_gender_slots(deal, sample_spa)
        
        # Then
        assert result is False, "Brak danych o mieszkaniu → nie można przydzielić → FAIL"


class TestCompleteValidation:
    """Testy pełnej walidacji (wszystkie warunki razem)"""
    
    def test_valid_deal_passes_all(self, sample_spa, sample_deal):
        """✅ Deal spełniający wszystkie warunki - PASS"""
        # Given
        validator = QualificationValidator()
        
        # When
        result = validator.validate_all(sample_deal, sample_spa)
        
        # Then
        assert result is True, "Deal spełniający wszystkie warunki powinien przejść"
    
    def test_invalid_age_fails_all(self, sample_spa, deal_too_old):
        """❌ Jedna niezgodność (wiek) - FAIL całości"""
        # Given
        validator = QualificationValidator()
        
        # When
        result = validator.validate_all(deal_too_old, sample_spa)
        
        # Then
        assert result is False, "Deal z niewłaściwym wiekiem nie powinien przejść"
    
    def test_invalid_date_fails_all(self, sample_spa, deal_late_arrival):
        """❌ Jedna niezgodność (data) - FAIL całości"""
        # Given
        validator = QualificationValidator()
        
        # When
        result = validator.validate_all(deal_late_arrival, sample_spa)
        
        # Then
        assert result is False, "Deal ze spóźnionym przyjazdem nie powinien przejść"

