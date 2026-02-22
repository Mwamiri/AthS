"""
Record Detector Module
Automatically detects and creates records when race results are saved
"""

from datetime import datetime
from typing import Dict, Tuple, Optional
from sqlalchemy.orm import Session


class RecordDetector:
    """Detects record-breaking situations and creates record entries"""

    def __init__(self, db: Session):
        self.db = db

    def process_race_result(self, athlete_id: int, event_id: int, event_name: str, 
                            time: float, race_id: int, location: str, country: str) -> Dict:
        """
        Process a race result and detect/create records
        
        Args:
            athlete_id: Athlete ID
            event_id: Event ID
            event_name: Event name (e.g., "1500m")
            time: Finish time in seconds
            race_id: Race ID
            location: Race location
            country: Athlete country
            
        Returns:
            Dictionary with record detection results
        """
        from models import PersonalBest, SeasonBest, CourseRecord, CountryRecord

        records_detected = {
            'personal_best': False,
            'season_best': False,
            'country_record': False,
            'course_record': False,
            'messages': []
        }

        try:
            # 1. Check and update Personal Best
            pb_result = self._update_personal_best(
                athlete_id, event_id, event_name, time, race_id, location
            )
            if pb_result:
                records_detected['personal_best'] = True
                records_detected['messages'].append(pb_result)

            # 2. Check and update Season Best
            sb_result = self._update_season_best(
                athlete_id, event_id, event_name, time, race_id, location
            )
            if sb_result:
                records_detected['season_best'] = True
                records_detected['messages'].append(sb_result)

            # 3. Check Country Record
            cr_result = self._check_country_record(
                athlete_id, event_name, time, location, country
            )
            if cr_result:
                records_detected['country_record'] = True
                records_detected['messages'].append(cr_result)

            # 4. Check Course Record
            course_result = self._check_course_record(
                athlete_id, race_id, event_name, time, location
            )
            if course_result:
                records_detected['course_record'] = True
                records_detected['messages'].append(course_result)

            self.db.commit()

        except Exception as e:
            self.db.rollback()
            records_detected['error'] = str(e)

        return records_detected

    def _update_personal_best(self, athlete_id: int, event_id: int, event_name: str,
                             time: float, race_id: int, location: str) -> Optional[str]:
        """Update personal best if this time is better"""
        from models import PersonalBest

        existing_pb = self.db.query(PersonalBest).filter_by(
            athlete_id=athlete_id,
            event_name=event_name
        ).first()

        if existing_pb:
            if time < existing_pb.time:
                improvement = existing_pb.time - time
                existing_pb.time = time
                existing_pb.date_achieved = datetime.now()
                existing_pb.race_id = race_id
                existing_pb.location = location
                self.db.add(existing_pb)
                return f"✅ Personal Best Updated! {existing_pb.time:.2f}s (-{improvement:.2f}s)"
            return None
        else:
            # Create new personal best
            new_pb = PersonalBest(
                athlete_id=athlete_id,
                event_id=event_id,
                event_name=event_name,
                time=time,
                date_achieved=datetime.now(),
                race_id=race_id,
                location=location
            )
            self.db.add(new_pb)
            return f"⭐ New Personal Best! {time:.2f}s"

    def _update_season_best(self, athlete_id: int, event_id: int, event_name: str,
                           time: float, race_id: int, location: str) -> Optional[str]:
        """Update season best if this time is better"""
        from models import SeasonBest
        from datetime import datetime as dt

        current_season = dt.now().year

        existing_sb = self.db.query(SeasonBest).filter_by(
            athlete_id=athlete_id,
            event_name=event_name,
            season=current_season
        ).first()

        if existing_sb:
            if time < existing_sb.time:
                improvement = existing_sb.time - time
                existing_sb.time = time
                existing_sb.date_achieved = datetime.now()
                existing_sb.race_id = race_id
                self.db.add(existing_sb)
                return f"🔥 Season Best Updated! {existing_sb.time:.2f}s (-{improvement:.2f}s)"
            return None
        else:
            # Create new season best
            new_sb = SeasonBest(
                athlete_id=athlete_id,
                event_id=event_id,
                event_name=event_name,
                season=current_season,
                time=time,
                date_achieved=datetime.now(),
                race_id=race_id,
                location=location
            )
            self.db.add(new_sb)
            return f"🎯 Season Best Set! {time:.2f}s"

    def _check_country_record(self, athlete_id: int, event_name: str, time: float,
                             location: str, country: str) -> Optional[str]:
        """Check if this breaks a country record"""
        from models import CountryRecord

        existing_cr = self.db.query(CountryRecord).filter_by(
            country=country,
            event_name=event_name
        ).first()

        if existing_cr:
            if time < existing_cr.time:
                improvement = existing_cr.time - time
                existing_cr.time = time
                existing_cr.date_set = datetime.now()
                existing_cr.improvement = improvement
                existing_cr.previous_record = existing_cr.time
                self.db.add(existing_cr)
                return f"🏆 COUNTRY RECORD! {time:.2f}s (-{improvement:.2f}s) 🇰🇪"
            return None
        else:
            # Create new country record
            new_cr = CountryRecord(
                country=country,
                event_name=event_name,
                time=time,
                athlete_id=athlete_id,
                location=location,
                date_set=datetime.now()
            )
            self.db.add(new_cr)
            return f"🏆 COUNTRY RECORD ESTABLISHED! {time:.2f}s 🇰🇪"

    def _check_course_record(self, athlete_id: int, race_id: int, event_name: str,
                            time: float, location: str) -> Optional[str]:
        """Check if this breaks a course record at this venue"""
        from models import CourseRecord

        existing_course = self.db.query(CourseRecord).filter_by(
            race_id=race_id,
            event_name=event_name
        ).first()

        if existing_course:
            if time < existing_course.time:
                improvement = existing_course.time - time
                existing_course.time = time
                existing_course.athlete_id = athlete_id
                existing_course.date_set = datetime.now()
                existing_course.improvement = improvement
                self.db.add(existing_course)
                return f"🏅 COURSE RECORD! {time:.2f}s (-{improvement:.2f}s)"
            return None
        else:
            # Create new course record
            new_course = CourseRecord(
                race_id=race_id,
                event_name=event_name,
                time=time,
                athlete_id=athlete_id,
                location=location,
                date_set=datetime.now()
            )
            self.db.add(new_course)
            return f"🏅 COURSE RECORD SET! {time:.2f}s"

    def check_championship_qualification(self, athlete_id: int, time: float,
                                        event_name: str, category: str,
                                        championship: str) -> Dict:
        """
        Check if athlete achieved a qualifying standard for a championship
        
        Returns:
            Dictionary with qualification status and details
        """
        from models import QualifyingStandard, AthleteStandard

        result = {
            'qualified': False,
            'standards_achieved': [],
            'messages': []
        }

        try:
            # Get all standards for this championship
            standards = self.db.query(QualifyingStandard).filter_by(
                championship=championship,
                event_name=event_name,
                category=category
            ).all()

            for standard in standards:
                if time <= standard.standard_time:
                    # Create athlete standard achievement record
                    achievement = AthleteStandard(
                        athlete_id=athlete_id,
                        standard_id=standard.id,
                        championship=championship,
                        final_time=time,
                        status='qualified',
                        achieved_date=datetime.now(),
                        time_below_standard=standard.standard_time - time,
                        percentage_below=((standard.standard_time - time) / standard.standard_time) * 100
                    )
                    self.db.add(achievement)
                    result['qualified'] = True
                    result['standards_achieved'].append(standard.type)

                    if standard.type == 'A':
                        result['messages'].append(
                            f"🎉 AUTO-QUALIFIED for {championship}! Time: {time:.2f}s"
                        )
                    else:
                        result['messages'].append(
                            f"✅ Achieved {championship} Consideration Standard! Time: {time:.2f}s"
                        )

            self.db.commit()

        except Exception as e:
            self.db.rollback()
            result['error'] = str(e)

        return result

    def get_athlete_achievements(self, athlete_id: int) -> Dict:
        """Get summary of all athlete's achievements and records"""
        from models import PersonalBest, SeasonBest, CountryRecord, AthleteStandard

        achievements = {
            'personal_bests_count': 0,
            'season_bests_count': 0,
            'country_records_count': 0,
            'standards_qualified': 0,
            'top_events': [],
            'qualifications': []
        }

        try:
            # Count records
            achievements['personal_bests_count'] = self.db.query(PersonalBest).filter_by(
                athlete_id=athlete_id
            ).count()

            achievements['season_bests_count'] = self.db.query(SeasonBest).filter_by(
                athlete_id=athlete_id
            ).count()

            achievements['country_records_count'] = self.db.query(CountryRecord).filter_by(
                athlete_id=athlete_id
            ).count()

            # Get qualified standards
            qualified = self.db.query(AthleteStandard).filter_by(
                athlete_id=athlete_id,
                status='qualified'
            ).all()

            achievements['standards_qualified'] = len(qualified)
            achievements['qualifications'] = [
                {
                    'championship': q.championship,
                    'time': q.final_time,
                    'date': q.achieved_date.isoformat()
                }
                for q in qualified
            ]

            # Get top events (by personal best count)
            from sqlalchemy import func
            top_events = self.db.query(
                PersonalBest.event_name,
                func.count(PersonalBest.id).label('count')
            ).filter_by(athlete_id=athlete_id).group_by(
                PersonalBest.event_name
            ).order_by(func.count(PersonalBest.id).desc()).limit(5).all()

            achievements['top_events'] = [
                {'event': e[0], 'attempts': e[1]} for e in top_events
            ]

        except Exception as e:
            achievements['error'] = str(e)

        return achievements
