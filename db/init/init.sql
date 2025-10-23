# Database initialization script

# Create database and user
CREATE USER qoratrader WITH PASSWORD 'qoratrader';
CREATE DATABASE qoratrader;
GRANT ALL PRIVILEGES ON DATABASE qoratrader TO qoratrader;

# Enable extensions if needed
\c qoratrader
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";