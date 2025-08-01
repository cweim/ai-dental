-- Create database
CREATE DATABASE ai_dentist;

-- Connect to the database
\c ai_dentist;

-- Create user (optional, you can use the default postgres user)
CREATE USER ai_dentist_user WITH PASSWORD 'your_password_here';

-- Grant privileges
GRANT ALL PRIVILEGES ON DATABASE ai_dentist TO ai_dentist_user;

-- The tables will be created automatically by SQLAlchemy/Alembic
-- This file is just for initial database setup