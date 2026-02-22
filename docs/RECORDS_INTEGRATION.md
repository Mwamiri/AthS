# Records System - Quick Integration Guide

## 5-Minute Setup

### Step 1: Enable Record Detection in Race Results

In your race results endpoint (`/src/backend/routes/results.py` or wherever you handle race results):

```python
from flask import Blueprint, request, jsonify
from models import db, Result, Race, Athlete, Event
from utils.record_detector import RecordDetector

@blueprint.route('/races/<race_id>/results', methods=['POST'])
def save_race_result(race_id):
    """Save race result and automatically detect records"""
    
    try:
        data = request.json
        race = db.query(Race).get(race_id)
        athlete = db.query(Athlete).get(data['athlete_id'])
        event = db.query(Event).get(data['event_id'])
        
        if not all([race, athlete, event]):
            return jsonify({'error': 'Missing race, athlete, or event'}), 404
        
        # Save the race result
        result = Result(
            race_id=race_id,
            athlete_id=athlete.id,
            event_id=event.id,
            time=data['time'],
            position=data['position'],
            status='finished'
        )
        db.add(result)
        db.flush()  # Get ID without committing
        
        # Detect records automatically
        detector = RecordDetector(db)
        record_detection = detector.process_race_result(
            athlete_id=athlete.id,
            event_id=event.id,
            event_name=event.name,
            time=data['time'],
            race_id=race_id,
            location=race.location,
            country=athlete.country
        )
        
        # Check championship qualification if applicable
        qualification = None
        if race.championship:
            qualification = detector.check_championship_qualification(
                athlete_id=athlete.id,
                time=data['time'],
                event_name=event.name,
                category=athlete.gender,
                championship=race.championship
            )
        
        # Commit all changes
        db.commit()
        
        return jsonify({
            'success': True,
            'result': result.to_dict(),
            'records': {
                'detected': record_detection,
                'qualification': qualification
            }
        }), 201
        
    except Exception as e:
        db.rollback()
        return jsonify({'error': str(e)}), 500
```

### Step 2: Frontend - Display Record Messages

After saving a result, show the achievement messages:

```html
<!-- In your race results page -->
<div id="record-notifications"></div>

<script>
async function submitRaceResult() {
    const data = {
        athlete_id: 123,
        event_id: 1,
        time: 205.80,
        position: 1
    };
    
    const response = await fetch('/api/races/456/results', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
    });
    
    const result = await response.json();
    
    if (result.records.detected.messages.length > 0) {
        // Display celebration messages
        let notificationHTML = '';
        
        result.records.detected.messages.forEach(msg => {
            notificationHTML += `
                <div class="notification success">
                    ${msg}
                </div>
            `;
        });
        
        if (result.records.qualification && result.records.qualification.messages.length > 0) {
            result.records.qualification.messages.forEach(msg => {
                notificationHTML += `
                    <div class="notification championship">
                        ${msg}
                    </div>
                `;
            });
        }
        
        document.getElementById('record-notifications').innerHTML = notificationHTML;
        
        // Auto-dismiss after 5 seconds
        setTimeout(() => {
            document.getElementById('record-notifications').innerHTML = '';
        }, 5000);
    }
}
</script>

<style>
.notification {
    padding: 1rem;
    margin-bottom: 0.5rem;
    border-radius: 6px;
    animation: slideIn 0.3s;
}

.notification.success {
    background: #d4edda;
    color: #155724;
    border: 1px solid #c3e6cb;
}

.notification.championship {
    background: linear-gradient(135deg, #ffd700, #ffed4e);
    color: #333;
    border: 1px solid #ffb700;
    font-weight: 600;
}

@keyframes slideIn {
    from {
        opacity: 0;
        transform: translateY(-10px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}
</style>
```

### Step 3: Seed Initial Data

Run once to populate records:

```bash
cd /src/backend
python scripts/seed_records.py
```

Output:
```
🌱 Seeding World Athletics Records System...

📝 Seeding World Records...
   ✓ Added 16 world records
🏅 Seeding Olympic Standards...
   ✓ Added 30 Olympic standards
🇰🇪 Seeding Country Records...
   ✓ Added 8 country records
🌍 Seeding Regional Records...
   ✓ Added 5 regional records
🏟️ Seeding Stadium Records...
   ✓ Added 3 stadium records
📊 Seeding Sample Rankings...
   ✓ Added 4 ranking entries

✅ All records seeded successfully!
```

## Common Implementation Scenarios

### Scenario 1: Track Meet Results Sheet Import

```python
from utils.record_detector import RecordDetector
from models import db, Race, Athlete, Event

def import_results_csv(race_id, csv_file):
    """Import results from CSV and detect records"""
    
    race = db.query(Race).get(race_id)
    detector = RecordDetector(db)
    
    results_summary = []
    
    for row in csv.DictReader(csv_file):
        athlete = db.query(Athlete).filter_by(
            bib_number=row['bib']
        ).first()
        
        event = db.query(Event).filter_by(
            name=row['event']
        ).first()
        
        if athlete and event:
            # Process result
            detection = detector.process_race_result(
                athlete_id=athlete.id,
                event_id=event.id,
                event_name=event.name,
                time=float(row['time']),
                race_id=race_id,
                location=race.location,
                country=athlete.country
            )
            
            results_summary.append({
                'athlete': athlete.name,
                'event': event.name,
                'time': row['time'],
                'records': detection['messages']
            })
    
    db.commit()
    return results_summary
```

### Scenario 2: Live Race Tracking

```python
from utils.record_detector import RecordDetector
from flask_socketio import emit, join_room

@socketio.on('result_finish')
def on_athlete_finish(data):
    """Real-time result processing with live record detection"""
    
    race_id = data['race_id']
    detector = RecordDetector(db)
    
    # Process result
    records = detector.process_race_result(
        athlete_id=data['athlete_id'],
        event_id=data['event_id'],
        event_name=data['event_name'],
        time=data['time'],
        race_id=race_id,
        location=data['location'],
        country=data['country']
    )
    
    # Broadcast to spectators
    emit('record_detected', {
        'athlete': data['athlete_name'],
        'messages': records['messages'],
        'timestamp': datetime.now().isoformat()
    }, room=f'race_{race_id}')
    
    db.commit()
```

### Scenario 3: Athlete Self-Entry App

```python
from utils.record_detector import RecordDetector

@app.route('/api/my-results', methods=['POST'])
def athlete_add_result():
    """Athlete logs their own race result"""
    
    user_id = get_current_user_id()
    data = request.json
    
    detector = RecordDetector(db)
    
    # Detect records
    records = detector.process_race_result(
        athlete_id=user_id,
        event_id=data['event_id'],
        event_name=data['event_name'],
        time=data['time'],
        race_id=data['race_id'],
        location=data['location'],
        country=data['country']
    )
    
    db.commit()
    
    # Return with celebration info
    return jsonify({
        'success': True,
        'achievement_unlocked': bool(records['messages']),
        'achievements': records['messages'],
        'next_target': calculate_next_goal(user_id, data['event_name'])
    })
```

## API Testing with CURL

```bash
# 1. Seed initial data
curl -X POST http://localhost:5000/api/seed/records

# 2. Get athlete's PBs
curl http://localhost:5000/api/records/personal-best/123

# 3. Check country records
curl http://localhost:5000/api/records/country-records/KEN

# 4. View Olympic standards
curl http://localhost:5000/api/records/standards/Olympic%20Games

# 5. Compare athletes
curl http://localhost:5000/api/records/compare/123/456/1500m

# 6. Get athlete profile
curl http://localhost:5000/api/records/athlete-profile/123

# 7. View rankings
curl http://localhost:5000/api/records/rankings/national/KEN/1500m

# 8. Save a result (and detect records)
curl -X POST http://localhost:5000/api/races/456/results \
  -H "Content-Type: application/json" \
  -d '{
    "athlete_id": 123,
    "event_id": 1,
    "time": 205.80,
    "position": 1
  }'
```

## Database Setup Checklist

- [ ] All 11 record models created (PersonalBest, SeasonBest, CountryRecord, etc.)
- [ ] Athlete model extended with relationships (personal_bests, season_bests)
- [ ] Database migrations run: `python manage.py db upgrade`
- [ ] Seed data loaded: `python scripts/seed_records.py`
- [ ] Records blueprint registered in app.py
- [ ] RecordDetector imported in results endpoint
- [ ] Frontend records page accessible at `/records-rankings.html`

## Monitoring Records

### Check latest records set
```python
from models import PersonalBest, CountryRecord
from datetime import datetime, timedelta

# PBs in last 7 days
recent_pbs = db.query(PersonalBest)\
    .filter(PersonalBest.date_achieved >= datetime.now() - timedelta(days=7))\
    .order_by(PersonalBest.date_achieved.desc())\
    .all()

# Country records this month
recent_cr = db.query(CountryRecord)\
    .filter(CountryRecord.date_set >= datetime.now().replace(day=1))\
    .order_by(CountryRecord.date_set.desc())\
    .all()
```

### Generate records report
```python
def get_monthly_records_report(year, month):
    from models import PersonalBest, CountryRecord, CourseRecord
    
    start = datetime(year, month, 1)
    if month == 12:
        end = datetime(year + 1, 1, 1)
    else:
        end = datetime(year, month + 1, 1)
    
    return {
        'period': f'{month}/{year}',
        'personal_bests': db.query(PersonalBest)\
            .filter(PersonalBest.date_achieved.between(start, end))\
            .count(),
        'country_records': db.query(CountryRecord)\
            .filter(CountryRecord.date_set.between(start, end))\
            .count(),
        'course_records': db.query(CourseRecord)\
            .filter(CourseRecord.date_set.between(start, end))\
            .count()
    }
```

## Troubleshooting

**Q: Records not being detected when result is saved**
A: Make sure:
1. RecordDetector is imported and called
2. athlete.country is set correctly
3. event.name matches exactly (e.g., "1500m" not "1.5K")
4. Database is committed after detection

**Q: Duplicate records being created**
A: Check that you're not calling detector twice for same result

**Q: Performance issues with large result sets**
A: Add indexes:
```python
# In models.py
class PersonalBest(db.Model):
    __table_args__ = (
        db.Index('idx_athlete_event', 'athlete_id', 'event_name'),
        db.Index('idx_country_event', 'country', 'event_name'),
    )
```

**Q: Standards not showing in athlete profile**
A: Ensure QualifyingStandard records exist for the championship and standards have been achieved via detector.check_championship_qualification()

## Next Steps

After integration:
1. ✅ Test record detection with sample race
2. ✅ Verify records appear in rankings queries
3. ✅ Display records in athlete profile
4. ✅ Add notifications for achievements
5. ✅ Create admin dashboard for verification/ratification
6. ✅ Set up automated monthly reports
