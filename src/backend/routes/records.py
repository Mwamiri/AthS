"""
Records & Standards API Routes
Handles Personal Bests, Season Bests, Country Records, and World Athletics-style rankings
"""

from flask import Blueprint, request, jsonify
from sqlalchemy import func, desc
from datetime import datetime, date
from models import (
    PersonalBest, SeasonBest, CountryRecord, RegionalRecord, StadiumRecord,
    WorldRecord, QualifyingStandard, AthleteStandard, CourseRecord, RankingByTime,
    Athlete, Result, Event, Race, SessionLocal
)

records_bp = Blueprint('records', __name__, url_prefix='/api/records')
db = SessionLocal()


# ==================== PERSONAL BEST ENDPOINTS ====================

@records_bp.route('/personal-best/<int:athlete_id>', methods=['GET'])
def get_athlete_personal_bests(athlete_id):
    """Get all personal bests for an athlete"""
    try:
        pbs = db.query(PersonalBest).filter_by(athlete_id=athlete_id).all()
        return jsonify({
            'success': True,
            'data': [pb.to_dict() for pb in pbs]
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@records_bp.route('/personal-best/<int:athlete_id>/<event_name>', methods=['GET'])
def get_personal_best_by_event(athlete_id, event_name):
    """Get personal best for specific event"""
    try:
        pb = db.query(PersonalBest).filter_by(
            athlete_id=athlete_id,
            event_name=event_name
        ).first()
        
        if not pb:
            return jsonify({'error': 'No personal best found'}), 404
        
        return jsonify({
            'success': True,
            'data': pb.to_dict()
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@records_bp.route('/personal-best', methods=['POST'])
def create_personal_best():
    """Create/update personal best"""
    try:
        data = request.json
        athlete_id = data.get('athlete_id')
        event_name = data.get('event_name')
        time = float(data.get('time'))
        date_achieved = datetime.strptime(data.get('date_achieved'), '%Y-%m-%d').date()
        
        # Check if PB already exists
        existing_pb = db.query(PersonalBest).filter_by(
            athlete_id=athlete_id,
            event_name=event_name
        ).first()
        
        if existing_pb:
            # Only update if new time is better
            if time < existing_pb.time:
                existing_pb.time = time
                existing_pb.date_achieved = date_achieved
                existing_pb.location = data.get('location', existing_pb.location)
                existing_pb.race_id = data.get('race_id')
                db.commit()
                return jsonify({
                    'success': True,
                    'message': 'Personal best updated!',
                    'data': existing_pb.to_dict()
                }), 200
            else:
                return jsonify({'error': 'New time is not better than existing PB'}), 400
        
        # Create new PB
        pb = PersonalBest(
            athlete_id=athlete_id,
            event_name=event_name,
            time=time,
            date_achieved=date_achieved,
            location=data.get('location'),
            race_id=data.get('race_id')
        )
        
        db.add(pb)
        db.commit()
        
        return jsonify({
            'success': True,
            'message': 'Personal best created!',
            'data': pb.to_dict()
        }), 201
        
    except Exception as e:
        db.rollback()
        return jsonify({'error': str(e)}), 500


# ==================== SEASON BEST ENDPOINTS ====================

@records_bp.route('/season-best/<int:athlete_id>/<int:season>', methods=['GET'])
def get_season_best(athlete_id, season):
    """Get season's best times for athlete"""
    try:
        season_bests = db.query(SeasonBest).filter_by(
            athlete_id=athlete_id,
            season=season
        ).all()
        
        return jsonify({
            'success': True,
            'season': season,
            'data': [sb.to_dict() for sb in season_bests]
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@records_bp.route('/season-best', methods=['POST'])
def create_season_best():
    """Create season best (typically done automatically)"""
    try:
        data = request.json
        sb = SeasonBest(
            athlete_id=data.get('athlete_id'),
            event_name=data.get('event_name'),
            season=data.get('season'),
            time=float(data.get('time')),
            date_achieved=datetime.strptime(data.get('date_achieved'), '%Y-%m-%d').date(),
            location=data.get('location'),
            race_id=data.get('race_id')
        )
        
        db.add(sb)
        db.commit()
        
        return jsonify({
            'success': True,
            'data': sb.to_dict()
        }), 201
    except Exception as e:
        db.rollback()
        return jsonify({'error': str(e)}), 500


# ==================== COUNTRY RECORDS ENDPOINTS ====================

@records_bp.route('/country-records/<country>', methods=['GET'])
def get_country_records(country):
    """Get all national records for a country"""
    try:
        records = db.query(CountryRecord).filter_by(country=country).all()
        
        return jsonify({
            'success': True,
            'country': country,
            'record_count': len(records),
            'data': [r.to_dict() for r in records]
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@records_bp.route('/country-records/<country>/<event_name>', methods=['GET'])
def get_country_record_by_event(country, event_name):
    """Get country record for specific event"""
    try:
        record = db.query(CountryRecord).filter_by(
            country=country,
            event_name=event_name
        ).first()
        
        if not record:
            return jsonify({'error': 'No country record found'}), 404
        
        return jsonify({
            'success': True,
            'data': record.to_dict()
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@records_bp.route('/country-records', methods=['POST'])
def set_country_record():
    """Set/update country record for an event"""
    try:
        data = request.json
        country = data.get('country')
        event_name = data.get('event_name')
        
        # Check if record exists
        existing = db.query(CountryRecord).filter_by(
            country=country,
            event_name=event_name
        ).first()
        
        new_time = float(data.get('time'))
        
        if existing:
            if new_time < existing.time:
                # New record!
                previous_time = existing.time
                existing.time = new_time
                existing.athlete_name = data.get('athlete_name')
                existing.date_set = datetime.strptime(data.get('date_set'), '%Y-%m-%d').date()
                existing.location = data.get('location')
                existing.previous_record = previous_time
                existing.improvement = previous_time - new_time
                existing.ratified = False
                db.commit()
                
                return jsonify({
                    'success': True,
                    'message': f'🎉 NEW COUNTRY RECORD! {country} - {event_name}',
                    'improvement': existing.improvement,
                    'data': existing.to_dict()
                }), 200
            else:
                return jsonify({'error': 'Time not better than existing record'}), 400
        
        # Create new record
        record = CountryRecord(
            country=country,
            event_name=event_name,
            category=data.get('category', 'Open'),
            time=new_time,
            athlete_name=data.get('athlete_name'),
            athlete_id=data.get('athlete_id'),
            date_set=datetime.strptime(data.get('date_set'), '%Y-%m-%d').date(),
            location=data.get('location')
        )
        
        db.add(record)
        db.commit()
        
        return jsonify({
            'success': True,
            'message': 'Country record created',
            'data': record.to_dict()
        }), 201
        
    except Exception as e:
        db.rollback()
        return jsonify({'error': str(e)}), 500


# ==================== WORLD RECORDS ENDPOINTS ====================

@records_bp.route('/world-records', methods=['GET'])
def get_world_records():
    """Get all world records"""
    try:
        records = db.query(WorldRecord).all()
        
        return jsonify({
            'success': True,
            'record_count': len(records),
            'data': [r.to_dict() for r in records]
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@records_bp.route('/world-records/<event_name>', methods=['GET'])
def get_world_record_by_event(event_name):
    """Get world record for specific event"""
    try:
        record = db.query(WorldRecord).filter_by(event_name=event_name).first()
        
        if not record:
            return jsonify({'error': 'World record not found'}), 404
        
        return jsonify({
            'success': True,
            'data': record.to_dict()
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ==================== QUALIFYING STANDARDS ENDPOINTS ====================

@records_bp.route('/standards/<championship>', methods=['GET'])
def get_championship_standards(championship):
    """Get qualifying standards for a championship"""
    try:
        standards = db.query(QualifyingStandard).filter_by(
            championship=championship
        ).all()
        
        return jsonify({
            'success': True,
            'championship': championship,
            'data': [s.to_dict() for s in standards]
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@records_bp.route('/standards/<championship>/<event_name>/<category>', methods=['GET'])
def get_standard_for_event(championship, event_name, category):
    """Get specific qualifying standard"""
    try:
        standard = db.query(QualifyingStandard).filter_by(
            championship=championship,
            event_name=event_name,
            category=category
        ).first()
        
        if not standard:
            return jsonify({'error': 'Standard not found'}), 404
        
        return jsonify({
            'success': True,
            'data': standard.to_dict()
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ==================== ATHLETE STANDARDS (ACHIEVEMENTS) ====================

@records_bp.route('/athlete-standards/<int:athlete_id>', methods=['GET'])
def get_athlete_standards(athlete_id):
    """Get standards achieved by athlete"""
    try:
        standards = db.query(AthleteStandard).filter_by(athlete_id=athlete_id).all()
        
        achieved = len([s for s in standards if s.status == 'achieved'])
        
        return jsonify({
            'success': True,
            'athlete_id': athlete_id,
            'standards_achieved': achieved,
            'data': [s.to_dict() for s in standards]
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ==================== RANKINGS ENDPOINTS ====================

@records_bp.route('/rankings/national/<country>/<event_name>', methods=['GET'])
def get_national_rankings(country, event_name):
    """Get national rankings for an event by time"""
    try:
        rankings = db.query(RankingByTime).filter_by(
            ranking_type='national',
            country=country,
            event_name=event_name
        ).order_by(RankingByTime.position).limit(100).all()
        
        return jsonify({
            'success': True,
            'country': country,
            'event': event_name,
            'data': [r.to_dict() for r in rankings]
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@records_bp.route('/rankings/season/<int:season>/<country>/<event_name>', methods=['GET'])
def get_season_rankings(season, country, event_name):
    """Get season rankings by country and event"""
    try:
        rankings = db.query(RankingByTime).filter_by(
            ranking_type='national',
            country=country,
            event_name=event_name,
            year=season
        ).order_by(RankingByTime.position).all()
        
        return jsonify({
            'success': True,
            'season': season,
            'country': country,
            'event': event_name,
            'data': [r.to_dict() for r in rankings]
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@records_bp.route('/rankings/all-time/<event_name>', methods=['GET'])
def get_all_time_rankings(event_name):
    """Get all-time rankings for an event worldwide"""
    try:
        rankings = db.query(RankingByTime).filter_by(
            ranking_type='all_time',
            event_name=event_name
        ).order_by(RankingByTime.position).limit(100).all()
        
        return jsonify({
            'success': True,
            'event': event_name,
            'data': [r.to_dict() for r in rankings]
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ==================== COURSE RECORDS ====================

@records_bp.route('/course-records/<int:race_id>', methods=['GET'])
def get_course_record(race_id):
    """Get course record for a specific race"""
    try:
        record = db.query(CourseRecord).filter_by(race_id=race_id).first()
        
        if not record:
            return jsonify({'message': 'No course record yet for this race'}), 200
        
        return jsonify({
            'success': True,
            'data': record.to_dict()
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@records_bp.route('/course-records', methods=['POST'])
def set_course_record():
    """Set course record"""
    try:
        data = request.json
        race_id = data.get('race_id')
        
        # Check if record exists
        existing = db.query(CourseRecord).filter_by(race_id=race_id).first()
        
        new_time = float(data.get('time'))
        
        if existing:
            if new_time < existing.time:
                previous_time = existing.time
                existing.time = new_time
                existing.athlete_name = data.get('athlete_name')
                existing.athlete_id = data.get('athlete_id')
                existing.year = data.get('year')
                existing.previous_record = previous_time
                existing.improvement = previous_time - new_time
                db.commit()
                
                return jsonify({
                    'success': True,
                    'message': 'Course record set!',
                    'data': existing.to_dict()
                }), 200
        
        record = CourseRecord(
            race_id=race_id,
            event_name=data.get('event_name'),
            time=new_time,
            athlete_name=data.get('athlete_name'),
            athlete_id=data.get('athlete_id'),
            year=data.get('year')
        )
        
        db.add(record)
        db.commit()
        
        return jsonify({
            'success': True,
            'data': record.to_dict()
        }), 201
    except Exception as e:
        db.rollback()
        return jsonify({'error': str(e)}), 500


# ==================== COMPARISON ENDPOINTS ====================

@records_bp.route('/compare/<int:athlete1_id>/<int:athlete2_id>/<event_name>', methods=['GET'])
def compare_athletes(athlete1_id, athlete2_id, event_name):
    """Compare two athletes' times in an event"""
    try:
        pb1 = db.query(PersonalBest).filter_by(
            athlete_id=athlete1_id,
            event_name=event_name
        ).first()
        
        pb2 = db.query(PersonalBest).filter_by(
            athlete_id=athlete2_id,
            event_name=event_name
        ).first()
        
        athlete1 = db.query(Athlete).get(athlete1_id)
        athlete2 = db.query(Athlete).get(athlete2_id)
        
        if not pb1 or not pb2:
            return jsonify({'error': 'One or both athletes missing PB for this event'}), 404
        
        time_difference = abs(pb1.time - pb2.time)
        faster_id = athlete1_id if pb1.time < pb2.time else athlete2_id
        
        return jsonify({
            'success': True,
            'event': event_name,
            'athlete1': {
                'id': athlete1_id,
                'name': athlete1.first_name + ' ' + athlete1.last_name,
                'time': pb1.time,
                'pb_date': pb1.date_achieved.isoformat()
            },
            'athlete2': {
                'id': athlete2_id,
                'name': athlete2.first_name + ' ' + athlete2.last_name,
                'time': pb2.time,
                'pb_date': pb2.date_achieved.isoformat()
            },
            'faster': faster_id,
            'time_difference': round(time_difference, 2),
            'percentage': round((time_difference / max(pb1.time, pb2.time)) * 100, 2)
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ==================== ATHLETE PROFILE WITH RECORDS ====================

@records_bp.route('/athlete-profile/<int:athlete_id>', methods=['GET'])
def get_athlete_records_profile(athlete_id):
    """Get comprehensive athlete records profile"""
    try:
        athlete = db.query(Athlete).get(athlete_id)
        
        if not athlete:
            return jsonify({'error': 'Athlete not found'}), 404
        
        personal_bests = db.query(PersonalBest).filter_by(athlete_id=athlete_id).all()
        country_records = db.query(CountryRecord).filter_by(athlete_id=athlete_id).all()
        standards = db.query(AthleteStandard).filter_by(athlete_id=athlete_id).all()
        
        # Get current season
        current_season = datetime.now().year
        season_bests = db.query(SeasonBest).filter_by(
            athlete_id=athlete_id,
            season=current_season
        ).all()
        
        # Calculate stats
        total_races = db.query(Result).filter_by(athlete_id=athlete_id).count()
        wins = db.query(Result).filter_by(athlete_id=athlete_id, position=1).count()
        
        return jsonify({
            'success': True,
            'athlete': {
                'id': athlete.id,
                'name': f"{athlete.first_name} {athlete.last_name}",
                'country': athlete.country,
                'club': athlete.club
            },
            'statistics': {
                'total_races': total_races,
                'wins': wins,
                'personal_bests_count': len(personal_bests),
                'country_records': len(country_records),
                'standards_achieved': len([s for s in standards if s.status == 'achieved'])
            },
            'personal_bests': [pb.to_dict() for pb in personal_bests],
            'country_records': [cr.to_dict() for cr in country_records],
            'season_bests': [sb.to_dict() for sb in season_bests],
            'standards': [s.to_dict() for s in standards]
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
