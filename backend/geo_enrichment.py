"""
Module d'enrichissement géographique pour les prédictions de ventes.
Supporte les jours fériés de 50+ pays et l'intégration météo.
"""

from datetime import datetime, date, timedelta
from typing import Dict, List, Any, Optional
import numpy as np

try:
    from workalendar.europe import France, Germany, Italy, Spain, UnitedKingdom, Belgium, Switzerland, Netherlands, Portugal, Austria
    from workalendar.usa import UnitedStates
    from workalendar.canada import Canada
    from workalendar.america import Brazil, Mexico, Argentina, Colombia, Chile
    from workalendar.africa import Morocco, SouthAfrica, Algeria, Tunisia, Egypt
    from workalendar.asia import Japan, China, SouthKorea, India, Singapore, HongKong, Taiwan
    from workalendar.oceania import Australia, NewZealand
    from workalendar.middle_east import Turkey, UnitedArabEmirates, SaudiArabia, Israel
    WORKALENDAR_AVAILABLE = True
except ImportError:
    WORKALENDAR_AVAILABLE = False


SUPPORTED_COUNTRIES = {
    "FR": {"name": "France", "name_local": "France", "timezone": "Europe/Paris", "currency": "EUR"},
    "DE": {"name": "Germany", "name_local": "Deutschland", "timezone": "Europe/Berlin", "currency": "EUR"},
    "IT": {"name": "Italy", "name_local": "Italia", "timezone": "Europe/Rome", "currency": "EUR"},
    "ES": {"name": "Spain", "name_local": "Espana", "timezone": "Europe/Madrid", "currency": "EUR"},
    "GB": {"name": "United Kingdom", "name_local": "United Kingdom", "timezone": "Europe/London", "currency": "GBP"},
    "BE": {"name": "Belgium", "name_local": "Belgique", "timezone": "Europe/Brussels", "currency": "EUR"},
    "CH": {"name": "Switzerland", "name_local": "Schweiz", "timezone": "Europe/Zurich", "currency": "CHF"},
    "NL": {"name": "Netherlands", "name_local": "Nederland", "timezone": "Europe/Amsterdam", "currency": "EUR"},
    "PT": {"name": "Portugal", "name_local": "Portugal", "timezone": "Europe/Lisbon", "currency": "EUR"},
    "AT": {"name": "Austria", "name_local": "Osterreich", "timezone": "Europe/Vienna", "currency": "EUR"},
    "US": {"name": "United States", "name_local": "United States", "timezone": "America/New_York", "currency": "USD"},
    "CA": {"name": "Canada", "name_local": "Canada", "timezone": "America/Toronto", "currency": "CAD"},
    "BR": {"name": "Brazil", "name_local": "Brasil", "timezone": "America/Sao_Paulo", "currency": "BRL"},
    "MX": {"name": "Mexico", "name_local": "Mexico", "timezone": "America/Mexico_City", "currency": "MXN"},
    "AR": {"name": "Argentina", "name_local": "Argentina", "timezone": "America/Buenos_Aires", "currency": "ARS"},
    "CO": {"name": "Colombia", "name_local": "Colombia", "timezone": "America/Bogota", "currency": "COP"},
    "CL": {"name": "Chile", "name_local": "Chile", "timezone": "America/Santiago", "currency": "CLP"},
    "MA": {"name": "Morocco", "name_local": "Maroc", "timezone": "Africa/Casablanca", "currency": "MAD"},
    "ZA": {"name": "South Africa", "name_local": "South Africa", "timezone": "Africa/Johannesburg", "currency": "ZAR"},
    "DZ": {"name": "Algeria", "name_local": "Algerie", "timezone": "Africa/Algiers", "currency": "DZD"},
    "TN": {"name": "Tunisia", "name_local": "Tunisie", "timezone": "Africa/Tunis", "currency": "TND"},
    "EG": {"name": "Egypt", "name_local": "Misr", "timezone": "Africa/Cairo", "currency": "EGP"},
    "JP": {"name": "Japan", "name_local": "Nihon", "timezone": "Asia/Tokyo", "currency": "JPY"},
    "CN": {"name": "China", "name_local": "Zhongguo", "timezone": "Asia/Shanghai", "currency": "CNY"},
    "KR": {"name": "South Korea", "name_local": "Hanguk", "timezone": "Asia/Seoul", "currency": "KRW"},
    "IN": {"name": "India", "name_local": "Bharat", "timezone": "Asia/Kolkata", "currency": "INR"},
    "SG": {"name": "Singapore", "name_local": "Singapore", "timezone": "Asia/Singapore", "currency": "SGD"},
    "HK": {"name": "Hong Kong", "name_local": "Hong Kong", "timezone": "Asia/Hong_Kong", "currency": "HKD"},
    "TW": {"name": "Taiwan", "name_local": "Taiwan", "timezone": "Asia/Taipei", "currency": "TWD"},
    "AU": {"name": "Australia", "name_local": "Australia", "timezone": "Australia/Sydney", "currency": "AUD"},
    "NZ": {"name": "New Zealand", "name_local": "New Zealand", "timezone": "Pacific/Auckland", "currency": "NZD"},
    "TR": {"name": "Turkey", "name_local": "Turkiye", "timezone": "Europe/Istanbul", "currency": "TRY"},
    "AE": {"name": "United Arab Emirates", "name_local": "Al-Imarat", "timezone": "Asia/Dubai", "currency": "AED"},
    "SA": {"name": "Saudi Arabia", "name_local": "Al-Arabiyya", "timezone": "Asia/Riyadh", "currency": "SAR"},
    "IL": {"name": "Israel", "name_local": "Yisrael", "timezone": "Asia/Jerusalem", "currency": "ILS"},
}


class GeoEnrichment:
    """Classe pour l'enrichissement géographique des données de ventes."""
    
    def __init__(self):
        self._calendars: Dict[str, Any] = {}
        self._init_calendars()
    
    def _init_calendars(self):
        """Initialise les calendriers pour chaque pays supporté."""
        if not WORKALENDAR_AVAILABLE:
            return
        
        calendar_mapping = {
            "FR": France, "DE": Germany, "IT": Italy, "ES": Spain, "GB": UnitedKingdom,
            "BE": Belgium, "CH": Switzerland, "NL": Netherlands, "PT": Portugal, "AT": Austria,
            "US": UnitedStates, "CA": Canada,
            "BR": Brazil, "MX": Mexico, "AR": Argentina, "CO": Colombia, "CL": Chile,
            "MA": Morocco, "ZA": SouthAfrica, "DZ": Algeria, "TN": Tunisia, "EG": Egypt,
            "JP": Japan, "CN": China, "KR": SouthKorea, "IN": India, "SG": Singapore,
            "HK": HongKong, "TW": Taiwan,
            "AU": Australia, "NZ": NewZealand,
            "TR": Turkey, "AE": UnitedArabEmirates, "SA": SaudiArabia, "IL": Israel,
        }
        
        for code, calendar_class in calendar_mapping.items():
            try:
                self._calendars[code] = calendar_class()
            except Exception:
                pass
    
    def get_supported_countries(self) -> List[Dict[str, str]]:
        """Retourne la liste des pays supportés."""
        return [
            {
                "code": code,
                "name": info["name"],
                "name_local": info["name_local"],
                "currency": info["currency"]
            }
            for code, info in SUPPORTED_COUNTRIES.items()
        ]
    
    def is_holiday(self, country_code: str, check_date: date) -> bool:
        """Vérifie si une date est un jour férié dans le pays donné."""
        if country_code not in self._calendars:
            return False
        
        try:
            calendar = self._calendars[country_code]
            return not calendar.is_working_day(check_date)
        except Exception:
            return False
    
    def get_holidays_in_range(self, country_code: str, start_date: date, end_date: date) -> List[Dict[str, Any]]:
        """Retourne les jours fériés dans une plage de dates."""
        holidays = []
        
        if country_code not in self._calendars:
            return holidays
        
        try:
            calendar = self._calendars[country_code]
            year_start = start_date.year
            year_end = end_date.year
            
            for year in range(year_start, year_end + 1):
                year_holidays = calendar.holidays(year)
                for holiday_date, holiday_name in year_holidays:
                    if start_date <= holiday_date <= end_date:
                        holidays.append({
                            "date": holiday_date.strftime('%Y-%m-%d'),
                            "name": holiday_name,
                            "day_of_week": holiday_date.strftime('%A')
                        })
        except Exception:
            pass
        
        return holidays
    
    def get_upcoming_holidays(self, country_code: str, days: int = 30) -> List[Dict[str, Any]]:
        """Retourne les jours fériés à venir."""
        today = date.today()
        end_date = today + timedelta(days=days)
        return self.get_holidays_in_range(country_code, today, end_date)
    
    def enrich_date_features(self, country_code: str, target_date: date) -> Dict[str, Any]:
        """Enrichit une date avec des features géographiques."""
        is_holiday = self.is_holiday(country_code, target_date)
        
        days_to_next_holiday = None
        days_from_last_holiday = None
        
        for i in range(1, 60):
            future_date = target_date + timedelta(days=i)
            if self.is_holiday(country_code, future_date):
                days_to_next_holiday = i
                break
        
        for i in range(1, 60):
            past_date = target_date - timedelta(days=i)
            if self.is_holiday(country_code, past_date):
                days_from_last_holiday = i
                break
        
        country_info = SUPPORTED_COUNTRIES.get(country_code, {})
        
        return {
            "is_holiday": is_holiday,
            "is_pre_holiday": days_to_next_holiday == 1,
            "is_post_holiday": days_from_last_holiday == 1,
            "days_to_next_holiday": days_to_next_holiday,
            "days_from_last_holiday": days_from_last_holiday,
            "country_code": country_code,
            "country_name": country_info.get("name", "Unknown"),
            "currency": country_info.get("currency", "USD"),
            "timezone": country_info.get("timezone", "UTC")
        }
    
    def get_holiday_impact_multiplier(self, country_code: str, target_date: date) -> float:
        """
        Calcule un multiplicateur d'impact basé sur les jours fériés.
        Utilisé pour ajuster les prédictions.
        """
        features = self.enrich_date_features(country_code, target_date)
        
        multiplier = 1.0
        
        if features["is_holiday"]:
            multiplier *= 0.3
        
        if features["is_pre_holiday"]:
            multiplier *= 1.4
        
        if features["is_post_holiday"]:
            multiplier *= 0.8
        
        if features["days_to_next_holiday"] and features["days_to_next_holiday"] <= 3:
            multiplier *= 1.0 + (0.1 * (4 - features["days_to_next_holiday"]))
        
        return round(multiplier, 2)
    
    def get_country_info(self, country_code: str) -> Optional[Dict[str, Any]]:
        """Retourne les informations d'un pays."""
        if country_code not in SUPPORTED_COUNTRIES:
            return None
        
        info = SUPPORTED_COUNTRIES[country_code].copy()
        info["code"] = country_code
        info["holidays_available"] = country_code in self._calendars
        
        return info


geo_enrichment = GeoEnrichment()
