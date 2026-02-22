"""
Advanced Search & Filtering Service
Full-text search, faceted filtering, and autocomplete functionality
"""

import logging
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
from sqlalchemy import or_, and_


class AdvancedSearchService:
    """Handle advanced searching and filtering"""
    
    def __init__(self):
        self.logger = logging.getLogger('athsys.search')
    
    def build_athlete_search_query(self, db_session, search_term: str = None, 
                                   filters: Dict[str, Any] = None) -> List[Dict]:
        """
        Search athletes with filters
        
        Args:
            db_session: SQLAlchemy session
            search_term: Search term for name/club
            filters: Filter criteria (gender, country, category, age_min, age_max)
            
        Returns:
            List of matching athletes
        """
        try:
            from models import Athlete
            from sqlalchemy import func
            
            query = db_session.query(Athlete)
            
            # Text search
            if search_term:
                search_pattern = f"%{search_term}%"
                query = query.filter(
                    or_(
                        Athlete.first_name.ilike(search_pattern),
                        Athlete.last_name.ilike(search_pattern),
                        Athlete.club.ilike(search_pattern),
                        Athlete.country.ilike(search_pattern)
                    )
                )
            
            # Apply filters
            if filters:
                if filters.get('gender'):
                    query = query.filter(Athlete.gender == filters['gender'])
                
                if filters.get('country'):
                    query = query.filter(Athlete.country.ilike(f"%{filters['country']}%"))
                
                if filters.get('category'):
                    query = query.filter(Athlete.category == filters['category'])
                
                # Age filter based on date of birth
                if filters.get('age_min') or filters.get('age_max'):
                    today = datetime.utcnow().date()
                    
                    if filters.get('age_max'):
                        min_birth_date = datetime(today.year - filters['age_max'], today.month, today.day).date()
                        query = query.filter(Athlete.date_of_birth >= min_birth_date)
                    
                    if filters.get('age_min'):
                        max_birth_date = datetime(today.year - filters['age_min'], today.month, today.day).date()
                        query = query.filter(Athlete.date_of_birth <= max_birth_date)
            
            results = query.all()
            return [self._athlete_to_dict(a) for a in results]
            
        except Exception as e:
            self.logger.error(f"Athlete search failed: {str(e)}")
            return []
    
    def build_race_search_query(self, db_session, search_term: str = None, 
                               filters: Dict[str, Any] = None) -> List[Dict]:
        """
        Search races with filters
        
        Args:
            db_session: SQLAlchemy session
            search_term: Search term for name/location
            filters: Filter criteria (status, category, date_from, date_to, location)
            
        Returns:
            List of matching races
        """
        try:
            from models import Race
            
            query = db_session.query(Race)
            
            # Text search
            if search_term:
                search_pattern = f"%{search_term}%"
                query = query.filter(
                    or_(
                        Race.name.ilike(search_pattern),
                        Race.location.ilike(search_pattern),
                        Race.description.ilike(search_pattern)
                    )
                )
            
            # Apply filters
            if filters:
                if filters.get('status'):
                    query = query.filter(Race.status == filters['status'])
                
                if filters.get('category'):
                    query = query.filter(Race.category == filters['category'])
                
                if filters.get('location'):
                    query = query.filter(Race.location.ilike(f"%{filters['location']}%"))
                
                if filters.get('date_from'):
                    query = query.filter(Race.date >= filters['date_from'])
                
                if filters.get('date_to'):
                    query = query.filter(Race.date <= filters['date_to'])
                
                if filters.get('distance_min'):
                    query = query.filter(Race.distance >= filters['distance_min'])
                
                if filters.get('distance_max'):
                    query = query.filter(Race.distance <= filters['distance_max'])
            
            results = query.all()
            return [self._race_to_dict(r) for r in results]
            
        except Exception as e:
            self.logger.error(f"Race search failed: {str(e)}")
            return []
    
    def build_results_search_query(self, db_session, race_id: int = None, 
                                  filters: Dict[str, Any] = None) -> List[Dict]:
        """
        Search race results with filters
        
        Args:
            db_session: SQLAlchemy session
            race_id: Filter by race ID
            filters: Filter criteria (status, position_min, position_max, time_max)
            
        Returns:
            List of matching results
        """
        try:
            from models import Result, Race
            
            query = db_session.query(Result).join(Race)
            
            if race_id:
                query = query.filter(Result.race_id == race_id)
            
            # Apply filters
            if filters:
                if filters.get('status'):
                    query = query.filter(Result.status == filters['status'])
                
                if filters.get('position_min'):
                    query = query.filter(Result.position >= filters['position_min'])
                
                if filters.get('position_max'):
                    query = query.filter(Result.position <= filters['position_max'])
                
                if filters.get('time_seconds_max'):
                    query = query.filter(Result.time_seconds <= filters['time_seconds_max'])
            
            query = query.order_by(Result.position)
            results = query.all()
            return [self._result_to_dict(r) for r in results]
            
        except Exception as e:
            self.logger.error(f"Results search failed: {str(e)}")
            return []
    
    def get_search_facets(self, db_session) -> Dict[str, List[str]]:
        """
        Get available facets for filtering
        
        Returns:
            Dictionary of facet values
        """
        try:
            from models import Athlete, Race
            from sqlalchemy import func
            
            facets = {
                'genders': [g[0] for g in db_session.query(Athlete.gender).distinct().all() if g[0]],
                'countries': [c[0] for c in db_session.query(Athlete.country).distinct().all() if c[0]],
                'athlete_categories': [c[0] for c in db_session.query(Athlete.category).distinct().all() if c[0]],
                'race_statuses': [s[0] for s in db_session.query(Race.status).distinct().all() if s[0]],
                'race_categories': [c[0] for c in db_session.query(Race.category).distinct().all() if c[0]],
                'locations': [l[0] for l in db_session.query(Race.location).distinct().all() if l[0]],
            }
            
            return facets
            
        except Exception as e:
            self.logger.error(f"Facet retrieval failed: {str(e)}")
            return {}
    
    def get_autocomplete_suggestions(self, db_session, query_str: str, resource_type: str = 'athlete') -> List[str]:
        """
        Get autocomplete suggestions
        
        Args:
            db_session: SQLAlchemy session
            query_str: Search query
            resource_type: 'athlete', 'race', etc.
            
        Returns:
            List of suggestions
        """
        try:
            from models import Athlete, Race
            
            search_pattern = f"%{query_str}%"
            suggestions = set()
            
            if resource_type == 'athlete' or resource_type == 'all':
                # Names
                athletes = db_session.query(Athlete.first_name, Athlete.last_name).filter(
                    or_(
                        Athlete.first_name.ilike(search_pattern),
                        Athlete.last_name.ilike(search_pattern)
                    )
                ).limit(5).all()
                
                suggestions.update([f"{a[0]} {a[1]}" for a in athletes if a[0]])
                
                # Clubs
                clubs = db_session.query(Athlete.club).filter(
                    Athlete.club.ilike(search_pattern)
                ).distinct().limit(5).all()
                
                suggestions.update([c[0] for c in clubs if c[0]])
            
            if resource_type == 'race' or resource_type == 'all':
                # Race names
                races = db_session.query(Race.name).filter(
                    Race.name.ilike(search_pattern)
                ).limit(5).all()
                
                suggestions.update([r[0] for r in races if r[0]])
                
                # Locations
                locations = db_session.query(Race.location).filter(
                    Race.location.ilike(search_pattern)
                ).distinct().limit(5).all()
                
                suggestions.update([l[0] for l in locations if l[0]])
            
            return sorted(list(suggestions))[:10]
            
        except Exception as e:
            self.logger.error(f"Autocomplete failed: {str(e)}")
            return []
    
    @staticmethod
    def _athlete_to_dict(athlete) -> Dict:
        """Convert athlete model to dict"""
        return {
            'id': athlete.id,
            'user_id': athlete.user_id,
            'first_name': athlete.first_name,
            'last_name': athlete.last_name,
            'date_of_birth': str(athlete.date_of_birth) if athlete.date_of_birth else None,
            'gender': athlete.gender,
            'country': athlete.country,
            'club': athlete.club,
            'category': athlete.category
        }
    
    @staticmethod
    def _race_to_dict(race) -> Dict:
        """Convert race model to dict"""
        return {
            'id': race.id,
            'name': race.name,
            'description': race.description,
            'date': str(race.date) if race.date else None,
            'location': race.location,
            'distance': race.distance,
            'category': race.category,
            'status': race.status
        }
    
    @staticmethod
    def _result_to_dict(result) -> Dict:
        """Convert result model to dict"""
        return {
            'id': result.id,
            'race_id': result.race_id,
            'athlete_id': result.athlete_id,
            'position': result.position,
            'time_seconds': result.time_seconds,
            'pace': result.pace,
            'status': result.status
        }


def get_search_service() -> AdvancedSearchService:
    """Get search service instance"""
    return AdvancedSearchService()
