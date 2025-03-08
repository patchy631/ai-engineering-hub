-- Drop existing table if exists
DROP TABLE IF EXISTS cities;

-- Create cities table
CREATE TABLE IF NOT EXISTS cities (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    state TEXT NOT NULL,
    population INTEGER,
    area REAL,
    description TEXT
);

-- Insert sample data for US cities only
INSERT OR IGNORE INTO cities (name, state, population, area, description) VALUES
    ('New York City', 'New York', 8336817, 783.8, 'The most populous city in the United States, known for its diverse culture and iconic landmarks.'),
    ('Los Angeles', 'California', 3898747, 503.0, 'The largest city in California, known for Hollywood, entertainment industry, and diverse culture.'),
    ('Chicago', 'Illinois', 2746388, 588.7, 'The third-most populous city in the US, known for its architecture, blues music, and deep-dish pizza.'),
    ('Houston', 'Texas', 2313000, 671.7, 'The most populous city in Texas, known for its space center, energy industry, and cultural diversity.'),
    ('Miami', 'Florida', 442241, 143.1, 'A major city in Florida, known for its beaches, Latin American culture, and vibrant nightlife.'),
    ('Seattle', 'Washington', 737015, 217.0, 'The largest city in the Pacific Northwest, known for its tech industry, coffee culture, and Space Needle.'); 