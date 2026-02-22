# Records & Standards System Documentation

*World Athletics-style records framework for athlete tracking, personal bests, rankings, and championships qualification*

## Overview

The Records & Standards System provides complete infrastructure for tracking:
- **Personal Bests**: Individual athlete best times per event
- **Season Bests**: Fastest time for each athlete each season
- **Country Records**: National records by event, tracked per country
- **Regional Records**: Continental/regional records (Africa, Europe, Asia, Americas)
- **World Records**: World best times for reference
- **Stadium Records**: Best times at specific venues
- **Qualifying Standards**: Championship qualification times (Olympic Games, Worlds, etc.)
- **Rankings**: National, seasonal, and all-time leaderboards

## Database Schema

### Core Models

#### PersonalBest
Tracks an athlete's best time per event
```
athlete_id (FK)
event_id (FK)
event_name: string (e.g., "1500m")
time: float (seconds)
date_achieved: datetime
location: string
race_id (FK): which race this PB was set at
national_ranking: int (where ranked nationally)
world_ranking: int (where ranked globally)
qualifies_for_national: bool
qualifies_for_continental: bool
qualifies_for_world: bool
```

#### SeasonBest
Best time in a specific season
```
athlete_id (FK)
event_id (FK)
season: int (year)
time: float
date_achieved: datetime
race_id (FK)
location: string
season_ranking: int
improvement_from_pb: float (seconds)
```

#### CountryRecord
National records by country
```
country: string (ISO code, e.g., "KEN")
event_name: string
category: string (Male/Female)
time: float
athlete_name: string
athlete_id (FK)
date_set: datetime
location: string
previous_record: float
improvement: float (seconds)
ratified: bool
```

#### RegionalRecord
Continental records
```
region: string (Africa/Europe/Asia/Americas/Oceania)
country: string
event_name: string
category: string
time: float
athlete_name: string
date_set: datetime
ratified: bool
improvement: float
```

#### StadiumRecord
Best time at specific venue
```
stadium_name: string
location: string
event_name: string
category: string
time: float
athlete_name: string
athlete_id (FK)
date_set: datetime
track_type: string (synthetic/clay/grass)
elevation: float (meters)
course_difficulty: string
previous_record: float
improvement: float
```

#### WorldRecord
World best times (reference data)
```
event_name: string
category: string
time: float
athlete_name: string
country: string
date_set: datetime
location: string
source: string (World Athletics)
external_url: string (link to official record)
```

#### QualifyingStandard
Championship qualifying times
```
championship: string (Olympic Games, World Championships, etc.)
year: int
event_name: string
category: string
standard_time: float
type: string (A for auto-qualify, B for consideration)
created_date: datetime
```

#### AthleteStandard
Track when athlete achieves a standard
```
athlete_id (FK)
standard_id (FK)
championship: string
final_time: float
status: string (qualified/not_qualified)
achieved_date: datetime
time_below_standard: float
percentage_below: float
rank_for_team: int
```

#### CourseRecord
Record for specific race
```
race_id (FK)
event_name: string
category: string
time: float
athlete_name: string
athlete_id (FK)
year: int
location: string
weather: string
temperature: float
elevation: float
course_difficulty: string
track_type: string
previous_record: float
improvement: float
date_set: datetime
```

#### RankingByTime
Pre-calculated rankings for fast queries
```
ranking_type: string (national/regional/all_time)
country: string
region: string
year: int
event_name: string
category: string
position: int
athlete_id (FK)
athlete_name: string
time: float
date_achieved: datetime
```

## API Endpoints

### Personal Bests

#### Get all PBs for athlete
```
GET /api/records/personal-best/<athlete_id>

Returns:
{
  "success": true,
  "data": [
    {
      "event_name": "1500m",
      "time": 206.40,
      "date_achieved": "2024-01-15",
      "location": "Nairobi",
      "national_ranking": 1,
      ...
    }
  ]
}
```

#### Get specific event PB
```
GET /api/records/personal-best/<athlete_id>/<event_name>

Example: GET /api/records/personal-best/123/1500m
```

#### Create/Update PB
```
POST /api/records/personal-best
Content-Type: application/json

{
  "athlete_id": 123,
  "event_name": "1500m",
  "time": 205.80,
  "date_achieved": "2024-03-20",
  "location": "Nairobi",
  "race_id": 456  // optional
}

Response: Updated PB with success message
```

### Season Bests

#### Get season best
```
GET /api/records/season-best/<athlete_id>/<season>

Example: GET /api/records/season-best/123/2024
```

#### Create season best
```
POST /api/records/season-best
Content-Type: application/json

{
  "athlete_id": 123,
  "event_name": "1500m",
  "season": 2024,
  "time": 206.20,
  "date_achieved": "2024-06-15",
  "location": "Stockholm",
  "race_id": 789
}
```

### Country Records

#### Get all country records
```
GET /api/records/country-records/<country>

Example: GET /api/records/country-records/KEN

Returns all national records for Kenya
```

#### Get specific country record
```
GET /api/records/country-records/<country>/<event_name>

Example: GET /api/records/country-records/KEN/1500m
```

#### Set country record
```
POST /api/records/country-records
Content-Type: application/json

{
  "country": "KEN",
  "event_name": "1500m",
  "time": 205.20,
  "athlete_name": "Elijah Kipchoge",
  "date_set": "2024-03-15",
  "location": "Monaco",
  "category": "Male"
}

Response:
{
  "message": "🎉 NEW COUNTRY RECORD! 205.20s (-1.20s improvement)"
}
```

### World Records

#### Get all world records
```
GET /api/records/world-records

Returns all world records by event
```

#### Get specific world record
```
GET /api/records/world-records/1500m

Returns world record for 1500m
```

### Qualifying Standards

#### Get championship standards
```
GET /api/records/standards/<championship>

Example: GET /api/records/standards/Olympic%20Games

Returns all event standards for Olympic Games 2024
```

#### Get specific standard
```
GET /api/records/standards/<championship>/<event_name>/<category>

Example: /api/records/standards/Olympic%20Games/1500m/Male
```

### Athlete Standards Achievement

#### Get athlete's standard qualifications
```
GET /api/records/athlete-standards/<athlete_id>

Returns:
{
  "success": true,
  "data": [
    {
      "championship": "Olympic Games",
      "final_time": 205.80,
      "status": "qualified",
      "achieved_date": "2024-03-10",
      "time_below_standard": 7.20,
      "percentage_below": 3.4
    }
  ]
}
```

### Rankings

#### National rankings
```
GET /api/records/rankings/national/<country>/<event_name>

Example: /api/records/rankings/national/KEN/1500m

Returns top 100 times in Kenya for 1500m
```

#### Season rankings
```
GET /api/records/rankings/season/<season>/<country>/<event_name>

Example: /api/records/rankings/season/2024/KEN/1500m

Returns current season's top runners in Kenya
```

#### All-time world rankings
```
GET /api/records/rankings/all-time/<event_name>

Example: /api/records/rankings/all-time/1500m

Returns top 100 times ever recorded worldwide
```

### Course Records

#### Get course record
```
GET /api/records/course-records/<race_id>

Returns best time ever at this race
```

#### Set course record
```
POST /api/records/course-records
Content-Type: application/json

{
  "race_id": 456,
  "event_name": "1500m",
  "time": 205.40,
  "athlete_name": "Elijah Kipchoge",
  "weather": "clear",
  "temperature": 22.5,
  "elevation": 1600
}
```

### Athlete Comparison

#### Compare two athletes
```
GET /api/records/compare/<athlete1_id>/<athlete2_id>/<event_name>

Returns:
{
  "success": true,
  "athlete1": {
    "name": "Kipchoge",
    "time": 205.20,
    "country": "KEN"
  },
  "athlete2": {
    "name": "Ingebrigsten",
    "time": 206.50,
    "country": "NOR"
  },
  "difference": 1.30,
  "percentage_difference": 0.63,
  "faster_athlete": "Kipchoge"
}
```

### Athlete Profile

#### Comprehensive athlete records
```
GET /api/records/athlete-profile/<athlete_id>

Returns:
{
  "success": true,
  "athlete": {
    "name": "Elijah Kipchoge",
    "country": "KEN",
    "club": "Kenya Army",
    "total_races": 45,
    "wins": 28,
    "personal_bests_count": 8,
    "country_records_count": 3,
    "standards_qualified": 1
  },
  "personal_bests": [...],
  "country_records": [...],
  "season_bests": [...],
  "standards_achieved": [...]
}
```

## Integration with Race Results

### Automatic Record Detection

When a race result is saved, the system automatically detects if:
1. ✅ New personal best
2. 🔥 New season best
3. 🏆 New country record
4. 🏅 New course record
5. 🎉 Achieved championship qualifying standard

### Using RecordDetector

```python
from utils.record_detector import RecordDetector
from models import db

# After saving a race result
detector = RecordDetector(db)

result = detector.process_race_result(
    athlete_id=123,
    event_id=5,
    event_name="1500m",
    time=205.80,
    race_id=456,
    location="Nairobi",
    country="KEN"
)

# result contains:
# {
#   'personal_best': True,
#   'season_best': False,
#   'country_record': True,
#   'course_record': False,
#   'messages': [
#       '✅ Personal Best Updated! 205.80s (-0.40s)',
#       '🏆 COUNTRY RECORD! 205.80s (-0.40s)'
#   ]
# }
```

### Integration Point in Results Endpoint

```python
from flask import request, jsonify
from utils.record_detector import RecordDetector
from models import db, Race, Result, Athlete

@app.route('/api/races/<race_id>/results', methods=['POST'])
def add_race_result(race_id):
    data = request.json
    
    # Save the race result
    result = Result(
        race_id=race_id,
        athlete_id=data['athlete_id'],
        time=data['time'],
        position=data['position']
    )
    db.add(result)
    db.commit()
    
    # Detect records
    detector = RecordDetector(db)
    athlete = db.query(Athlete).get(data['athlete_id'])
    
    records = detector.process_race_result(
        athlete_id=athlete.id,
        event_id=data['event_id'],
        event_name=data['event_name'],
        time=data['time'],
        race_id=race_id,
        location=data['location'],
        country=athlete.country
    )
    
    return jsonify({
        'result': result.to_dict(),
        'records_detected': records
    })
```

## Data Seeding

### Seed World Athletics Data

```bash
python /src/backend/scripts/seed_records.py
```

This populates:
- ✓ 16 World Records (men's and women's track)
- ✓ 30 Olympic Games 2024 qualifying standards
- ✓ 8 Kenya country records
- ✓ 5 African regional records
- ✓ 3 Stadium records for Nairobi venues
- ✓ Sample ranking data

## Frontend Usage

### Records Browser Page

Located at: `/src/frontend/records-rankings.html`

Features:
- **Rankings Tab**: Sort by country, event, season
- **Personal Bests Tab**: View athlete PBs with search
- **Country Records Tab**: Browse national records
- **Standards Tab**: Championship qualifying times
- **Compare Tab**: Head-to-head athlete comparison

### Integration in HTML

```html
<iframe src="/records-rankings.html" width="100%" height="600"></iframe>
```

### Loading Records via JavaScript

```javascript
// Load rankings
fetch('/api/records/rankings/national/KEN/1500m')
  .then(r => r.json())
  .then(data => console.log(data.data))

// Load athlete profile
fetch('/api/records/athlete-profile/123')
  .then(r => r.json())
  .then(athlete => console.log(athlete.data))

// Compare athletes
fetch('/api/records/compare/123/456/1500m')
  .then(r => r.json())
  .then(comparison => console.log(comparison))
```

## Best Practices

### 1. Record Validation
- Validate times are reasonable (e.g., 1500m between 150 and 250 seconds)
- Require location and date for official records
- Set `ratified: True` only for official records

### 2. Ranking Updates
- Keep `RankingByTime` table updated quarterly
- Index on (ranking_type, country, event_name) for performance
- Cache top 10 rankings in frontend for fast load

### 3. Standards Management
- Update standards before each championship season
- Maintain separate A and B standards
- Track when standards change

### 4. Performance
- Use pagination for large result sets (rankings)
- Index on athlete_id, country, event_name
- Cache world records (rarely change)

### 5. Data Quality
- Set championships qualification time before accepting results
- Calculate improvement percentage automatically
- Validate athlete exists before creating records

## Sample Queries

### Get all PBs for athlete in 2024 season
```python
from models import PersonalBest
pbs = db.query(PersonalBest).filter_by(
    athlete_id=123
).filter(
    PersonalBest.date_achieved >= datetime(2024, 1, 1)
).all()
```

### Get athletes who qualified for Olympics
```python
from models import AthleteStandard
qualified = db.query(AthleteStandard).filter_by(
    championship='Olympic Games',
    status='qualified'
).all()
```

### Get Kenya's fastest 1500m runners
```python
from models import RankingByTime
rankings = db.query(RankingByTime).filter_by(
    country='KEN',
    event_name='1500m'
).order_by(RankingByTime.position).limit(10).all()
```

### Check if athlete broke country record
```python
from models import CountryRecord, PersonalBest
pb = db.query(PersonalBest).filter_by(
    athlete_id=123,
    event_name='1500m'
).first()

cr = db.query(CountryRecord).filter_by(
    country='KEN',
    event_name='1500m'
).first()

is_record = pb.time < cr.time if cr else True
```

## Testing

### Test Record Detection
```python
from utils.record_detector import RecordDetector

detector = RecordDetector(db)

# Simulate new PB
result = detector.process_race_result(
    athlete_id=1,
    event_id=1,
    event_name='1500m',
    time=203.20,  # Better than any existing
    race_id=1,
    location='Paris',
    country='KEN'
)

assert result['personal_best'] == True
assert '✅' in result['messages'][0]
```

### Test Ranking Queries
```python
response = client.get('/api/records/rankings/national/KEN/1500m')
assert response.status_code == 200
assert len(response.json['data']) > 0
assert response.json['data'][0]['position'] == 1
```

## Troubleshooting

### Records not detected after result
- Check RecordDetector is called in results endpoint
- Verify athlete_id, event_name, time are correct
- Check database commit() is called after detection

### Rankings empty
- Seed data first: `python seed_records.py`
- Check RankingByTime table is populated
- Verify country code matches (KEN, not Kenya)

### Standards not showing
- Import QualifyingStandard records first
- Check championship name matches exactly
- Verify event_name format (e.g., "1500m" not "1.5K")

## Future Enhancements

- 📈 Predictive analytics (estimated time improvements)
- 🔔 Achievement notifications
- 📊 Historical record trends
- 🌍 World Athletics API integration
- 🏅 Medal predictions for championships
- 📱 Mobile app for athlete tracking
- 🎯 Personalized goal recommendations
