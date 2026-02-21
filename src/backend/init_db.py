"""
Database Initialization Script
Seeds the database with initial demo data
"""

from models import (
    init_db, SessionLocal,
    User, Athlete, Race, Event, Registration, Result
)
from datetime import datetime, timedelta
import sys

def seed_database():
    """Populate database with initial demo data"""
    print("🔄 Initializing database...")
    
    # Create all tables
    try:
        init_db()
        print("✅ Database tables created")
    except Exception as e:
        print(f"⚠️  Database initialization warning: {e}")
    
    db = SessionLocal()
    
    try:
        # Check if data already exists
        if db.query(User).count() > 0:
            print("⚠️  Database already has data. Skipping seed.")
            return
        
        print("🔄 Seeding database with demo data...")
        
        # Create Users with hashed passwords
        users = [
            {
                'name': 'Admin User',
                'email': 'admin@athsys.com',
                'password': 'Admin@123',
                'role': 'admin',
                'status': 'active'
            },
            {
                'name': 'Chief Registrar',
                'email': 'chief@athsys.com',
                'password': 'Chief@123',
                'role': 'chief_registrar',
                'status': 'active'
            },
            {
                'name': 'Registrar User',
                'email': 'registrar@athsys.com',
                'password': 'Registrar@123',
                'role': 'registrar',
                'status': 'active'
            },
            {
                'name': 'Starter Official',
                'email': 'starter@athsys.com',
                'password': 'Starter@123',
                'role': 'starter',
                'status': 'active'
            },
            {
                'name': 'John Athlete',
                'email': 'john@athsys.com',
                'password': 'Athlete@123',
                'role': 'athlete',
                'status': 'active'
            },
            {
                'name': 'Sarah Coach',
                'email': 'sarah@athsys.com',
                'password': 'Coach@123',
                'role': 'coach',
                'status': 'active'
            },
            {
                'name': 'Public Viewer',
                'email': 'viewer@athsys.com',
                'password': 'Viewer@123',
                'role': 'viewer',
                'status': 'active'
            }
        ]
        
        user_objects = []
        for user_data in users:
            user = User(
                name=user_data['name'],
                email=user_data['email'],
                role=user_data['role'],
                status=user_data['status']
            )
            user.set_password(user_data['password'])
            user_objects.append(user)
            db.add(user)
        
        db.commit()
        print(f"✅ Created {len(user_objects)} users")
        
        # Create Athletes
        athletes_data = [
            {
                'name': 'Eliud Kipchoge',
                'country': 'KEN',
                'date_of_birth': datetime(1984, 11, 5).date(),
                'gender': 'Male',
                'email': 'eliud@athletics.com',
                'phone': '+254700000001',
                'coach_name': 'Patrick Sang',
                'bib_number': 'KEN001'
            },
            {
                'name': 'Faith Kipyegon',
                'country': 'KEN',
                'date_of_birth': datetime(1994, 1, 10).date(),
                'gender': 'Female',
                'email': 'faith@athletics.com',
                'phone': '+254700000002',
                'coach_name': 'Patrick Sang',
                'bib_number': 'KEN002'
            },
            {
                'name': 'Usain Bolt',
                'country': 'JAM',
                'date_of_birth': datetime(1986, 8, 21).date(),
                'gender': 'Male',
                'email': 'usain@athletics.com',
                'phone': '+1876000001',
                'coach_name': 'Glen Mills',
                'bib_number': 'JAM001'
            },
            {
                'name': 'Shelly-Ann Fraser-Pryce',
                'country': 'JAM',
                'date_of_birth': datetime(1986, 12, 27).date(),
                'gender': 'Female',
                'email': 'shelly@athletics.com',
                'phone': '+1876000002',
                'coach_name': 'Stephen Francis',
                'bib_number': 'JAM002'
            },
            {
                'name': 'Joshua Cheptegei',
                'country': 'UGA',
                'date_of_birth': datetime(1996, 9, 12).date(),
                'gender': 'Male',
                'email': 'joshua@athletics.com',
                'phone': '+256700000001',
                'coach_name': 'Addy Ruiter',
                'bib_number': 'UGA001'
            },
            {
                'name': 'Sydney McLaughlin',
                'country': 'USA',
                'date_of_birth': datetime(1999, 8, 7).date(),
                'gender': 'Female',
                'email': 'sydney@athletics.com',
                'phone': '+1555000001',
                'coach_name': 'Bobby Kersee',
                'bib_number': 'USA001'
            }
        ]
        
        athlete_objects = []
        for athlete_data in athletes_data:
            athlete = Athlete(**athlete_data)
            athlete_objects.append(athlete)
            db.add(athlete)
        
        db.commit()
        print(f"✅ Created {len(athlete_objects)} athletes")
        
        # Create Races
        races_data = [
            {
                'name': 'National Athletics Championship 2026',
                'date': datetime(2026, 3, 15).date(),
                'location': 'National Stadium, Nairobi',
                'status': 'open',
                'registration_open': True,
                'registration_link': 'pub_race_nac2026'
            },
            {
                'name': 'Regional Track Meet 2026',
                'date': datetime(2026, 4, 10).date(),
                'location': 'Regional Sports Complex',
                'status': 'draft',
                'registration_open': False,
                'registration_link': 'pub_race_rtm2026'
            },
            {
                'name': 'International Invitational 2026',
                'date': datetime(2026, 5, 20).date(),
                'location': 'Olympic Stadium',
                'status': 'open',
                'registration_open': True,
                'registration_link': 'pub_race_int2026'
            }
        ]
        
        race_objects = []
        for race_data in races_data:
            race = Race(**race_data)
            race_objects.append(race)
            db.add(race)
        
        db.commit()
        print(f"✅ Created {len(race_objects)} races")
        
        # Create Events for each race
        events_data = [
            # National Championship events
            {'race': race_objects[0], 'name': '100m Sprint', 'category': 'Track', 'gender': 'Men', 'distance': 100},
            {'race': race_objects[0], 'name': '100m Sprint', 'category': 'Track', 'gender': 'Women', 'distance': 100},
            {'race': race_objects[0], 'name': '1500m', 'category': 'Track', 'gender': 'Women', 'distance': 1500},
            {'race': race_objects[0], 'name': '5000m', 'category': 'Track', 'gender': 'Men', 'distance': 5000},
            {'race': race_objects[0], 'name': 'Marathon', 'category': 'Road', 'gender': 'Men', 'distance': 42195},
            
            # Regional Meet events
            {'race': race_objects[1], 'name': '200m Sprint', 'category': 'Track', 'gender': 'Men', 'distance': 200},
            {'race': race_objects[1], 'name': '400m', 'category': 'Track', 'gender': 'Women', 'distance': 400},
            
            # International Invitational events
            {'race': race_objects[2], 'name': '100m Sprint', 'category': 'Track', 'gender': 'Both', 'distance': 100},
            {'race': race_objects[2], 'name': '10000m', 'category': 'Track', 'gender': 'Men', 'distance': 10000},
        ]
        
        event_objects = []
        for event_data in events_data:
            race = event_data.pop('race')
            event = Event(race_id=race.id, **event_data)
            event_objects.append(event)
            db.add(event)
        
        db.commit()
        print(f"✅ Created {len(event_objects)} events")
        
        # Create Registrations
        registrations_data = [
            {'athlete': athlete_objects[0], 'event': event_objects[3], 'bib_number': 'KEN001', 'status': 'confirmed'},
            {'athlete': athlete_objects[0], 'event': event_objects[4], 'bib_number': 'KEN001', 'status': 'confirmed'},
            {'athlete': athlete_objects[1], 'event': event_objects[2], 'bib_number': 'KEN002', 'status': 'confirmed'},
            {'athlete': athlete_objects[2], 'event': event_objects[0], 'bib_number': 'JAM001', 'status': 'confirmed'},
            {'athlete': athlete_objects[3], 'event': event_objects[1], 'bib_number': 'JAM002', 'status': 'confirmed'},
            {'athlete': athlete_objects[4], 'event': event_objects[8], 'bib_number': 'UGA001', 'status': 'confirmed'},
        ]
        
        registration_objects = []
        for reg_data in registrations_data:
            athlete = reg_data.pop('athlete')
            event = reg_data.pop('event')
            registration = Registration(
                athlete_id=athlete.id,
                event_id=event.id,
                **reg_data
            )
            registration_objects.append(registration)
            db.add(registration)
        
        db.commit()
        print(f"✅ Created {len(registration_objects)} registrations")
        
        # Create some results
        results_data = [
            {'registration': registration_objects[3], 'position': 1, 'time_seconds': 9.58, 'points': 100, 'status': 'finished'},
            {'registration': registration_objects[4], 'position': 1, 'time_seconds': 10.76, 'points': 100, 'status': 'finished'},
            {'registration': registration_objects[1], 'position': 2, 'time_seconds': 1234.5, 'points': 80, 'status': 'finished'},
        ]
        
        result_objects = []
        for result_data in results_data:
            registration = result_data.pop('registration')
            result = Result(
                registration_id=registration.id,
                **result_data
            )
            result_objects.append(result)
            db.add(result)
        
        db.commit()
        print(f"✅ Created {len(result_objects)} results")
        
        print("\n" + "="*50)
        print("✅ Database seeded successfully!")
        print("="*50)
        print("\n📊 Summary:")
        print(f"   Users: {len(user_objects)}")
        print(f"   Athletes: {len(athlete_objects)}")
        print(f"   Races: {len(race_objects)}")
        print(f"   Events: {len(event_objects)}")
        print(f"   Registrations: {len(registration_objects)}")
        print(f"   Results: {len(result_objects)}")
        print("\n🔑 Login Credentials:")
        print("   Admin: admin@athsys.com / Admin@123")
        print("   Chief Registrar: chief@athsys.com / Chief@123")
        print("   Registrar: registrar@athsys.com / Registrar@123")
        print("   Starter: starter@athsys.com / Starter@123")
        print("   Athlete: john@athsys.com / Athlete@123")
        print("   Coach: sarah@athsys.com / Coach@123")
        print("   Viewer: viewer@athsys.com / Viewer@123")
        print("="*50)
        
    except Exception as e:
        print(f"❌ Error seeding database: {e}")
        db.rollback()
        sys.exit(1)
    finally:
        db.close()


if __name__ == '__main__':
    seed_database()
