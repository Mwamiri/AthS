# Records API Reference

## Complete Endpoint Reference Guide

### Base URL
```
http://localhost:5000/api/records
```

---

## Personal Bests Endpoints

### Get All Personal Bests for Athlete
```
GET /api/records/personal-best/{athlete_id}
```

**Parameters:**
- `athlete_id` (path): Unique athlete identifier

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "athlete_id": 123,
      "event_id": 5,
      "event_name": "1500m",
      "time": 206.40,
      "date_achieved": "2024-01-15T10:30:00",
      "location": "Nairobi",
      "race_id": 456,
      "national_ranking": 1,
      "world_ranking": 12,
      "qualifies_for_national": true,
      "qualifies_for_continental": true,
      "qualifies_for_world": false
    }
  ]
}
```

**Status Codes:**
- `200`: Success
- `404`: Athlete not found

---

### Get Specific Event Personal Best
```
GET /api/records/personal-best/{athlete_id}/{event_name}
```

**Parameters:**
- `athlete_id` (path): Athlete ID
- `event_name` (path): Event name (e.g., "1500m", "5K", "Marathon")

**Response:**
```json
{
  "success": true,
  "data": {
    "id": 1,
    "athlete_id": 123,
    "event_name": "1500m",
    "time": 206.40,
    "date_achieved": "2024-01-15",
    "location": "Nairobi",
    "national_ranking": 1
  }
}
```

**Status Codes:**
- `200`: Success
- `404`: PB not found for this event

---

### Create or Update Personal Best
```
POST /api/records/personal-best
Content-Type: application/json
```

**Request Body:**
```json
{
  "athlete_id": 123,
  "event_id": 5,
  "event_name": "1500m",
  "time": 205.80,
  "date_achieved": "2024-03-20",
  "location": "Nairobi",
  "race_id": 456
}
```

**Required Fields:**
- `athlete_id`: integer
- `event_name`: string
- `time`: float (seconds)
- `date_achieved`: date string (YYYY-MM-DD)
- `location`: string

**Optional Fields:**
- `race_id`: integer
- `event_id`: integer

**Response (New PB):**
```json
{
  "success": true,
  "message": "⭐ New Personal Best! 205.80s",
  "data": {
    "id": 2,
    "athlete_id": 123,
    "event_name": "1500m",
    "time": 205.80
  }
}
```

**Response (Updated PB):**
```json
{
  "success": true,
  "message": "✅ Personal Best Updated! 205.80s (-0.60s)",
  "data": {
    "id": 1,
    "time": 205.80,
    "previous_time": 206.40
  }
}
```

**Status Codes:**
- `201`: Created successfully
- `200`: Updated successfully
- `400`: Validation error
- `422`: Time not better than existing PB (rejected)

---

## Season Bests Endpoints

### Get Season Best
```
GET /api/records/season-best/{athlete_id}/{season}
```

**Parameters:**
- `athlete_id` (path): Athlete ID
- `season` (path): Year as integer (e.g., 2024)

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "athlete_id": 123,
      "event_name": "1500m",
      "season": 2024,
      "time": 206.50,
      "date_achieved": "2024-06-15",
      "location": "Stockholm",
      "season_ranking": 2
    }
  ]
}
```

---

### Create Season Best
```
POST /api/records/season-best
Content-Type: application/json
```

**Request Body:**
```json
{
  "athlete_id": 123,
  "event_id": 5,
  "event_name": "1500m",
  "season": 2024,
  "time": 206.50,
  "date_achieved": "2024-06-15",
  "location": "Stockholm",
  "race_id": 789
}
```

**Response:**
```json
{
  "success": true,
  "message": "🔥 Season Best Set! 206.50s",
  "data": { ... }
}
```

---

## Country Records Endpoints

### Get All Country Records
```
GET /api/records/country-records/{country}
```

**Parameters:**
- `country` (path): ISO country code (e.g., "KEN", "USA", "ETH")

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "country": "KEN",
      "event_name": "1500m",
      "category": "Male",
      "time": 206.40,
      "athlete_name": "William Kemboi",
      "athlete_id": 123,
      "date_set": "2013-07-07",
      "location": "Monaco",
      "improvement": 0.50,
      "previous_record": 206.90,
      "ratified": true
    }
  ]
}
```

---

### Get Specific Country Record
```
GET /api/records/country-records/{country}/{event_name}
```

**Parameters:**
- `country`: ISO country code
- `event_name`: Event name (e.g., "1500m")

**Response:**
```json
{
  "success": true,
  "data": {
    "id": 1,
    "country": "KEN",
    "event_name": "1500m",
    "time": 206.40,
    "athlete_name": "William Kemboi"
  }
}
```

---

### Set/Update Country Record
```
POST /api/records/country-records
Content-Type: application/json
```

**Request Body:**
```json
{
  "country": "KEN",
  "event_name": "1500m",
  "category": "Male",
  "time": 205.20,
  "athlete_name": "Elijah Kipchoge",
  "athlete_id": 123,
  "date_set": "2024-03-15",
  "location": "Monaco",
  "ratified": true
}
```

**Response (New Record):**
```json
{
  "success": true,
  "message": "🏆 COUNTRY RECORD ESTABLISHED! 205.20s 🇰🇪",
  "data": { ... }
}
```

**Response (Improved Record):**
```json
{
  "success": true,
  "message": "🎉 NEW COUNTRY RECORD! 205.20s (-1.20s improvement) 🇰🇪",
  "data": { ... }
}
```

---

## World Records Endpoints

### Get All World Records
```
GET /api/records/world-records
```

**Query Parameters:**
- `category` (optional): "Male" or "Female"
- `distance` (optional): Filter by distance (e.g., "1500m")

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "event_name": "1500m",
      "category": "Male",
      "time": 206.00,
      "athlete_name": "Hicham El Guerrouj",
      "country": "MAR",
      "date_set": "1998-07-14",
      "location": "Rome",
      "source": "World Athletics",
      "external_url": "https://worldathletics.org/..."
    }
  ]
}
```

---

### Get Specific World Record
```
GET /api/records/world-records/{event_name}
```

**Parameters:**
- `event_name`: Event name (e.g., "1500m")

**Response:**
```json
{
  "success": true,
  "data": {
    "event_name": "1500m",
    "category": "Male",
    "time": 206.00,
    "athlete_name": "Hicham El Guerrouj"
  }
}
```

---

## Qualifying Standards Endpoints

### Get Championship Standards
```
GET /api/records/standards/{championship}
```

**Parameters:**
- `championship`: Championship name (e.g., "Olympic Games", "World Championships", "African Championships")

**Query Parameters:**
- `year` (optional): Filter by year
- `category` (optional): "Male" or "Female"

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "championship": "Olympic Games",
      "year": 2024,
      "event_name": "1500m",
      "category": "Male",
      "standard_time": 213.80,
      "type": "A",
      "created_date": "2023-06-01"
    }
  ]
}
```

---

### Get Specific Standard
```
GET /api/records/standards/{championship}/{event_name}/{category}
```

**Parameters:**
- `championship`: Championship name
- `event_name`: Event name
- `category`: "Male" or "Female"

**Response:**
```json
{
  "success": true,
  "data": {
    "championship": "Olympic Games",
    "event_name": "1500m",
    "category": "Male",
    "standard_A": 213.80,
    "standard_B": 215.40
  }
}
```

---

## Athlete Standards Endpoints

### Get Athlete's Qualified Standards
```
GET /api/records/athlete-standards/{athlete_id}
```

**Parameters:**
- `athlete_id`: Athlete ID

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "athlete_id": 123,
      "championship": "Olympic Games",
      "event_name": "1500m",
      "final_time": 205.80,
      "status": "qualified",
      "achieved_date": "2024-03-10",
      "time_below_standard": 8.00,
      "percentage_below": 3.76,
      "rank_for_team": 1
    }
  ]
}
```

---

## Rankings Endpoints

### National Rankings
```
GET /api/records/rankings/national/{country}/{event_name}
```

**Parameters:**
- `country`: ISO country code
- `event_name`: Event name

**Query Parameters:**
- `limit` (optional): Max results (default: 100)
- `offset` (optional): Pagination offset

**Response:**
```json
{
  "success": true,
  "country": "KEN",
  "event": "1500m",
  "data": [
    {
      "position": 1,
      "athlete_id": 123,
      "athlete_name": "Elijah Kipchoge",
      "time": 206.40,
      "date_achieved": "2024-01-15",
      "country": "KEN"
    },
    {
      "position": 2,
      "athlete_id": 124,
      "athlete_name": "William Kemboi",
      "time": 207.80,
      "date_achieved": "2024-02-20"
    }
  ]
}
```

---

### Season Rankings
```
GET /api/records/rankings/season/{season}/{country}/{event_name}
```

**Parameters:**
- `season`: Year (e.g., 2024)
- `country`: ISO country code
- `event_name`: Event name

**Response:**
```json
{
  "success": true,
  "ranking_type": "season",
  "season": 2024,
  "country": "KEN",
  "event": "1500m",
  "data": [ ... ]
}
```

---

### All-Time World Rankings
```
GET /api/records/rankings/all-time/{event_name}
```

**Parameters:**
- `event_name`: Event name

**Query Parameters:**
- `limit` (optional): Top N results (default: 100)

**Response:**
```json
{
  "success": true,
  "ranking_type": "all_time_world",
  "event": "1500m",
  "data": [
    {
      "position": 1,
      "athlete_name": "Hicham El Guerrouj",
      "country": "MAR",
      "time": 206.00,
      "date_achieved": "1998-07-14"
    }
  ]
}
```

---

## Course Records Endpoints

### Get Course Record
```
GET /api/records/course-records/{race_id}
```

**Parameters:**
- `race_id`: Race event ID

**Response:**
```json
{
  "success": true,
  "data": {
    "id": 1,
    "race_id": 456,
    "event_name": "1500m",
    "time": 205.40,
    "athlete_name": "Elijah Kipchoge",
    "date_set": "2024-03-10",
    "location": "Nairobi",
    "weather": "clear",
    "temperature": 22.5,
    "elevation": 1600,
    "improvement": 1.20,
    "previous_record": 206.60
  }
}
```

---

### Set Course Record
```
POST /api/records/course-records
Content-Type: application/json
```

**Request Body:**
```json
{
  "race_id": 456,
  "event_name": "1500m",
  "time": 205.40,
  "athlete_name": "Elijah Kipchoge",
  "athlete_id": 123,
  "year": 2024,
  "location": "Nairobi",
  "weather": "clear",
  "temperature": 22.5,
  "elevation": 1600,
  "course_difficulty": "moderate",
  "track_type": "synthetic"
}
```

**Response:**
```json
{
  "success": true,
  "message": "🏅 COURSE RECORD SET! 205.40s",
  "data": { ... }
}
```

---

## Comparison Endpoints

### Compare Two Athletes
```
GET /api/records/compare/{athlete1_id}/{athlete2_id}/{event_name}
```

**Parameters:**
- `athlete1_id`: First athlete ID
- `athlete2_id`: Second athlete ID
- `event_name`: Event to compare

**Response:**
```json
{
  "success": true,
  "comparison": {
    "event": "1500m",
    "athlete1": {
      "name": "Elijah Kipchoge",
      "country": "KEN",
      "time": 206.40,
      "date": "2024-01-15"
    },
    "athlete2": {
      "name": "Jakob Ingebrigsten",
      "country": "NOR",
      "time": 206.50,
      "date": "2024-02-10"
    },
    "time_difference": 0.10,
    "percentage_difference": 0.05,
    "faster_athlete": "Kipchoge",
    "summary": "Kipchoge is 0.10s faster"
  }
}
```

---

## Athlete Profile Endpoint

### Get Comprehensive Athlete Profile
```
GET /api/records/athlete-profile/{athlete_id}
```

**Parameters:**
- `athlete_id`: Athlete ID

**Response:**
```json
{
  "success": true,
  "athlete": {
    "id": 123,
    "name": "Elijah Kipchoge",
    "country": "KEN",
    "club": "Kenya Army",
    "dob": "1984-11-05",
    "gender": "Male",
    "statistics": {
      "total_races": 45,
      "total_wins": 28,
      "personal_bests_count": 8,
      "season_bests_count": 12,
      "country_records_count": 3,
      "standards_qualified": 1
    }
  },
  "personal_bests": [
    {
      "event_name": "1500m",
      "time": 206.40,
      "date_achieved": "2024-01-15",
      "national_ranking": 1,
      "world_ranking": 12
    }
  ],
  "country_records": [
    {
      "event_name": "1500m",
      "time": 206.40,
      "date_set": "2013-07-07",
      "improvement": 0.50
    }
  ],
  "season_bests": [
    {
      "season": 2024,
      "event_name": "1500m",
      "time": 206.50,
      "date_achieved": "2024-06-15"
    }
  ],
  "standards_achieved": [
    {
      "championship": "Olympic Games",
      "event_name": "1500m",
      "final_time": 205.80,
      "status": "qualified",
      "achieved_date": "2024-03-10"
    }
  ]
}
```

---

## Error Responses

### 400 Bad Request
```json
{
  "success": false,
  "error": "Missing required field: athlete_id"
}
```

### 404 Not Found
```json
{
  "success": false,
  "error": "Athlete not found"
}
```

### 422 Unprocessable Entity
```json
{
  "success": false,
  "error": "New time not better than existing personal best"
}
```

### 500 Internal Server Error
```json
{
  "success": false,
  "error": "Database error: connection timeout"
}
```

---

## Request/Response Headers

**Request Headers:**
```
Content-Type: application/json
Accept: application/json
Authorization: Bearer {token} (if authentication enabled)
```

**Response Headers:**
```
Content-Type: application/json
X-Records-Version: 1.0
X-Record-Count: {number of records returned}
```

---

## Common Query Examples

### Get top 5 runners in Kenya for 1500m
```
GET /api/records/rankings/national/KEN/1500m?limit=5
```

### Get all PBs for athlete ID 123
```
GET /api/records/personal-best/123
```

### Compare two athletes in 1500m
```
GET /api/records/compare/123/456/1500m
```

### Get Olympic Games 2024 standards
```
GET /api/records/standards/Olympic%20Games?year=2024
```

### Get complete athlete record profile
```
GET /api/records/athlete-profile/123
```

### Set new personal best
```
POST /api/records/personal-best
{
  "athlete_id": 123,
  "event_name": "1500m",
  "time": 205.80,
  "date_achieved": "2024-03-20",
  "location": "Monaco"
}
```

---

## Performance Tips

1. **Ranking queries** - Use `limit=100` for paginated results
2. **World records** - Cache in frontend (rarely change)
3. **Personal bests** - Index on athlete_id for fast lookup
4. **Standards** - Filter by championship year for current standards

---

## Rate Limiting

Currently no rate limiting on Records API.
Recommended: Max 1000 requests/hour per IP

---

## Version History

- **v1.0**: Initial release with 30+ endpoints
  - Personal Bests
  - Season Bests
  - Country Records
  - World Records
  - Qualifying Standards
  - Rankings
  - Comparisons
  - Athlete Profiles

---

## Support

For issues or bugs, create an issue in the repository with:
- Endpoint called
- Request body
- Response error
- Expected behavior
