"""
Records System Data Seeder
Populates database with World Athletics records and standards

Usage:
    python seed_records.py
"""

import sys
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from models import (
    WorldRecord, QualifyingStandard, CountryRecord, 
    RegionalRecord, StadiumRecord, RankingByTime, db
)


class RecordsSeeder:
    """Seeds records system with World Athletics data"""

    # World Records (as of 2024)
    WORLD_RECORDS = [
        # Men's Track
        ('100m', 'Male', 9.58, 'Usain Bolt', 'JAM'),
        ('200m', 'Male', 19.19, 'Usain Bolt', 'JAM'),
        ('400m', 'Male', 43.03, 'Wayde van Niekerk', 'RSA'),
        ('800m', 'Male', 100.91, 'David Rudisha', 'KEN'),
        ('1500m', 'Male', 206.00, 'Hicham El Guerrouj', 'MAR'),
        ('5000m', 'Male', 1223.30, 'Joshua Cheptegei', 'UGA'),
        ('10000m', 'Male', 2142.49, 'Kenenisa Bekele', 'ETH'),
        ('Marathon', 'Male', 7254.0, 'Eliud Kipchoge', 'KEN'),
        
        # Women's Track
        ('100m', 'Female', 10.49, 'Florence Griffin Joyner', 'USA'),
        ('200m', 'Female', 21.34, 'Florence Griffin Joyner', 'USA'),
        ('400m', 'Female', 47.60, 'Marita Koch', 'GDR'),
        ('800m', 'Female', 113.28, 'Jarmila Kratochvilova', 'TCH'),
        ('1500m', 'Female', 230.46, 'Genzebe Dibaba', 'ETH'),
        ('5000m', 'Female', 1426.51, 'Letesenbet Gidey', 'ETH'),
        ('10000m', 'Female', 2914.20, 'Letesenbet Gidey', 'ETH'),
        ('Marathon', 'Female', 8197.0, 'Tigist Assefa', 'ETH'),
    ]

    # Olympic Games 2024 Qualifying Standards
    OLYMPIC_STANDARDS_2024 = [
        # Men's (event_name, category, standard_A, type)
        ('100m', 'Male', 10.05, 'A'),
        ('100m', 'Male', 10.16, 'B'),
        ('200m', 'Male', 20.16, 'A'),
        ('200m', 'Male', 20.40, 'B'),
        ('400m', 'Male', 45.40, 'A'),
        ('400m', 'Male', 45.90, 'B'),
        ('800m', 'Male', 105.40, 'A'),
        ('800m', 'Male', 106.50, 'B'),
        ('1500m', 'Male', 213.80, 'A'),
        ('1500m', 'Male', 215.40, 'B'),
        ('5000m', 'Male', 1256.00, 'A'),
        ('5000m', 'Male', 1273.00, 'B'),
        ('10000m', 'Male', 2645.00, 'A'),
        ('10000m', 'Male', 2691.00, 'B'),
        
        # Women's
        ('100m', 'Female', 11.07, 'A'),
        ('100m', 'Female', 11.20, 'B'),
        ('200m', 'Female', 22.80, 'A'),
        ('200m', 'Female', 23.10, 'B'),
        ('400m', 'Female', 50.43, 'A'),
        ('400m', 'Female', 51.60, 'B'),
        ('800m', 'Female', 115.70, 'A'),
        ('800m', 'Female', 117.20, 'B'),
        ('1500m', 'Female', 239.40, 'A'),
        ('1500m', 'Female', 242.00, 'B'),
        ('5000m', 'Female', 1443.00, 'A'),
        ('5000m', 'Female', 1469.00, 'B'),
        ('10000m', 'Female', 3040.00, 'A'),
        ('10000m', 'Female', 3105.00, 'B'),
    ]

    # Kenya Country Records (sample)
    KENYA_RECORDS = [
        ('100m', 'Male', 9.85, 'Henry Rono', 'Nairobi', '1984'),
        ('200m', 'Male', 20.23, 'Henry Rono', 'Nairobi', '1985'),
        ('400m', 'Male', 44.92, 'Nixon Kipchoge', 'Nairobi', '2012'),
        ('800m', 'Male', 100.91, 'David Rudisha', 'London', '2012'),
        ('1500m', 'Male', 206.40, 'William Kemboi', 'Monaco', '2013'),
        ('5000m', 'Male', 1223.30, 'Joshua Cheptegei', 'Valencia', '2020'),
        ('10000m', 'Male', 2234.00, 'Kenenisa Bekele', 'Brussels', '2005'),
        ('Marathon', 'Male', 7266.0, 'Eliud Kipchoge', 'Berlin', '2018'),
    ]

    # Regional Records (East Africa)
    EA_RECORDS = [
        ('100m', 'Male', 9.85, 'Henry Rono', 'Africa'),
        ('1500m', 'Male', 206.00, 'Hicham El Guerrouj', 'Africa'),
        ('5000m', 'Male', 1223.30, 'Joshua Cheptegei', 'Africa'),
        ('10000m', 'Male', 2142.49, 'Kenenisa Bekele', 'Africa'),
        ('Marathon', 'Male', 7254.0, 'Eliud Kipchoge', 'Africa'),
    ]

    # Stadium Records (Nairobi venues)
    STADIUM_RECORDS = [
        ('Nyayo Stadium', 'Nairobi', '1500m', 'Male', 206.50, 'William Kemboi', 'Synthetic'),
        ('Kasarani Stadium', 'Nairobi', '5000m', 'Male', 1224.00, 'Joshua Cheptegei', 'Synthetic'),
        ('Moi International Sports Centre', 'Nairobi', '10000m', 'Male', 2245.00, 'Kenenisa Bekele', 'Synthetic'),
    ]

    def seed_all(self):
        """Run all seeding operations"""
        print("🌱 Seeding World Athletics Records System...\n")
        
        try:
            self.seed_world_records()
            self.seed_olympic_standards()
            self.seed_country_records()
            self.seed_regional_records()
            self.seed_stadium_records()
            self.seed_sample_rankings()
            
            print("\n✅ All records seeded successfully!")
            
        except Exception as e:
            print(f"\n❌ Error seeding records: {e}")
            raise

    def seed_world_records(self):
        """Seed World Records"""
        print("📝 Seeding World Records...")
        
        count = 0
        for event_name, category, time, athlete, country in self.WORLD_RECORDS:
            # Check if already exists
            existing = db.query(WorldRecord).filter_by(
                event_name=event_name,
                category=category
            ).first()
            
            if not existing:
                record = WorldRecord(
                    event_name=event_name,
                    category=category,
                    time=time,
                    athlete_name=athlete,
                    country=country,
                    date_set=datetime.now() - timedelta(days=365),
                    location='World',
                    source='World Athletics',
                    external_url=f'https://worldathletics.org/athletes/{athlete.lower()}'
                )
                db.add(record)
                count += 1
        
        db.commit()
        print(f"   ✓ Added {count} world records")

    def seed_olympic_standards(self):
        """Seed Olympic Games qualifying standards"""
        print("🏅 Seeding Olympic Standards...")
        
        count = 0
        for event_name, category, standard_time, std_type in self.OLYMPIC_STANDARDS_2024:
            # Check if already exists
            existing = db.query(QualifyingStandard).filter_by(
                championship='Olympic Games',
                event_name=event_name,
                category=category,
                type=std_type
            ).first()
            
            if not existing:
                standard = QualifyingStandard(
                    championship='Olympic Games',
                    year=2024,
                    event_name=event_name,
                    category=category,
                    standard_time=standard_time,
                    type=std_type,
                    created_date=datetime.now()
                )
                db.add(standard)
                count += 1
        
        db.commit()
        print(f"   ✓ Added {count} Olympic standards")

    def seed_country_records(self):
        """Seed Kenya country records"""
        print("🇰🇪 Seeding Country Records...")
        
        count = 0
        for event_name, category, time, athlete, location, year in self.KENYA_RECORDS:
            existing = db.query(CountryRecord).filter_by(
                country='KEN',
                event_name=event_name,
                category=category
            ).first()
            
            if not existing:
                record = CountryRecord(
                    country='KEN',
                    event_name=event_name,
                    category=category,
                    time=time,
                    athlete_name=athlete,
                    location=location,
                    date_set=datetime(int(year), 1, 1),
                    ratified=True
                )
                db.add(record)
                count += 1
        
        db.commit()
        print(f"   ✓ Added {count} country records")

    def seed_regional_records(self):
        """Seed African regional records"""
        print("🌍 Seeding Regional Records...")
        
        count = 0
        for event_name, category, time, athlete, region in self.EA_RECORDS:
            existing = db.query(RegionalRecord).filter_by(
                region=region,
                event_name=event_name,
                category=category
            ).first()
            
            if not existing:
                record = RegionalRecord(
                    region=region,
                    country='KEN',
                    event_name=event_name,
                    category=category,
                    time=time,
                    athlete_name=athlete,
                    date_set=datetime.now() - timedelta(days=365),
                    ratified=True
                )
                db.add(record)
                count += 1
        
        db.commit()
        print(f"   ✓ Added {count} regional records")

    def seed_stadium_records(self):
        """Seed stadium venue records"""
        print("🏟️ Seeding Stadium Records...")
        
        count = 0
        for stadium, location, event, category, time, athlete, track_type in self.STADIUM_RECORDS:
            existing = db.query(StadiumRecord).filter_by(
                stadium_name=stadium,
                event_name=event,
                category=category
            ).first()
            
            if not existing:
                record = StadiumRecord(
                    stadium_name=stadium,
                    location=location,
                    event_name=event,
                    category=category,
                    time=time,
                    athlete_name=athlete,
                    date_set=datetime.now() - timedelta(days=180),
                    track_type=track_type
                )
                db.add(record)
                count += 1
        
        db.commit()
        print(f"   ✓ Added {count} stadium records")

    def seed_sample_rankings(self):
        """Seed sample ranking data"""
        print("📊 Seeding Sample Rankings...")
        
        # Sample ranking data for Kenya
        ranking_data = [
            ('national', 'KEN', 2024, '1500m', 'Male', 1, 'Elijah Kipchoge', 206.40, 2024),
            ('national', 'KEN', 2024, '1500m', 'Male', 2, 'William Kemboi', 207.80, 2024),
            ('national', 'KEN', 2024, '1500m', 'Male', 3, 'Timothy Kipchoge', 208.50, 2024),
            ('national', 'KEN', 2024, '5000m', 'Male', 1, 'Joshua Cheptegei', 1223.30, 2024),
        ]
        
        count = 0
        for ranking_type, country, year, event, category, position, athlete, time, rank_year in ranking_data:
            existing = db.query(RankingByTime).filter_by(
                ranking_type=ranking_type,
                country=country,
                event_name=event,
                category=category,
                position=position
            ).first()
            
            if not existing:
                ranking = RankingByTime(
                    ranking_type=ranking_type,
                    country=country,
                    year=year,
                    event_name=event,
                    category=category,
                    position=position,
                    athlete_name=athlete,
                    time=time,
                    date_achieved=datetime.now() - timedelta(days=30)
                )
                db.add(ranking)
                count += 1
        
        db.commit()
        print(f"   ✓ Added {count} ranking entries")


def main():
    """Main entry point"""
    seeder = RecordsSeeder()
    seeder.seed_all()


if __name__ == '__main__':
    main()
