-- AthS Database Initialization Script

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create athletes table
CREATE TABLE IF NOT EXISTS athletes (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    date_of_birth DATE,
    gender VARCHAR(20),
    country_code VARCHAR(3),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create events table
CREATE TABLE IF NOT EXISTS events (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(200) NOT NULL,
    event_type VARCHAR(50) NOT NULL,
    category VARCHAR(50),
    unit VARCHAR(20),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create performances table
CREATE TABLE IF NOT EXISTS performances (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    athlete_id UUID REFERENCES athletes(id) ON DELETE CASCADE,
    event_id UUID REFERENCES events(id) ON DELETE CASCADE,
    mark_value DECIMAL(10, 2) NOT NULL,
    wind_reading DECIMAL(5, 2),
    competition_name VARCHAR(200),
    competition_date DATE,
    location VARCHAR(200),
    is_personal_best BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create competitions table
CREATE TABLE IF NOT EXISTS competitions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(200) NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE,
    location VARCHAR(200),
    country_code VARCHAR(3),
    status VARCHAR(20) DEFAULT 'scheduled',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create results table
CREATE TABLE IF NOT EXISTS results (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    competition_id UUID REFERENCES competitions(id) ON DELETE CASCADE,
    athlete_id UUID REFERENCES athletes(id) ON DELETE CASCADE,
    event_id UUID REFERENCES events(id) ON DELETE CASCADE,
    mark_value DECIMAL(10, 2) NOT NULL,
    wind_reading DECIMAL(5, 2),
    rank INTEGER,
    points INTEGER,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_athletes_name ON athletes(last_name, first_name);
CREATE INDEX IF NOT EXISTS idx_performances_athlete ON performances(athlete_id);
CREATE INDEX IF NOT EXISTS idx_performances_event ON performances(event_id);
CREATE INDEX IF NOT EXISTS idx_results_competition ON results(competition_id);
CREATE INDEX IF NOT EXISTS idx_results_athlete ON results(athlete_id);
CREATE INDEX IF NOT EXISTS idx_competitions_dates ON competitions(start_date, end_date);

-- Insert sample data
INSERT INTO athletes (first_name, last_name, date_of_birth, gender, country_code) VALUES
('Usain', 'Bolt', '1986-08-21', 'male', 'JAM'),
('Eliud', 'Kipchoge', '1984-11-05', 'male', 'KEN'),
('Sydney', 'McLaughlin-Levrone', '1999-08-07', 'female', 'USA'),
('Mondo', 'Duplantis', '1999-11-10', 'male', 'SWE'),
('Faith', 'Kipyegon', '1994-01-10', 'female', 'KEN');

INSERT INTO events (name, event_type, category, unit) VALUES
('100m', 'track', 'sprint', 'seconds'),
('200m', 'track', 'sprint', 'seconds'),
('400m Hurdles', 'track', 'hurdles', 'seconds'),
('Marathon', 'track', 'distance', 'time'),
('Pole Vault', 'field', 'jumps', 'meters'),
('1500m', 'track', 'middle_distance', 'time');

INSERT INTO competitions (name, start_date, end_date, location, country_code, status) VALUES
('World Athletics Championships 2023', '2023-08-19', '2023-08-27', 'Budapest', 'HUN', 'completed'),
('Olympic Games Paris 2024', '2024-07-26', '2024-08-11', 'Paris', 'FRA', 'completed'),
('Diamond League Final', '2024-09-14', '2024-09-15', 'Zurich', 'SUI', 'completed');

-- Create function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create triggers for updated_at
CREATE TRIGGER update_athletes_updated_at BEFORE UPDATE ON athletes
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_events_updated_at BEFORE UPDATE ON events
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_performances_updated_at BEFORE UPDATE ON performances
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_competitions_updated_at BEFORE UPDATE ON competitions
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_results_updated_at BEFORE UPDATE ON results
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
