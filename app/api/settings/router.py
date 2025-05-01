import psycopg
from ninja import Schema
from django.conf import settings
from typing import Dict

from psycopg import OperationalError

from ninja import Router

router = Router(tags=["settings"])

class MessageResponse(Schema):
    message: str
    success: bool


@router.post("/create_truncate_procedure/", response=MessageResponse)
def create_truncate_procedure(request) -> Dict:
    """Creates the database truncate procedure in PostgreSQL"""
    try:
        conn = psycopg.connect(
            dbname=settings.DATABASES['default']["NAME"],
            user=settings.DATABASES['default']["USER"],
            password=settings.DATABASES['default']["PASSWORD"],
            host=settings.DATABASES['default']["HOST"],
            port=settings.DATABASES['default']["PORT"]
        )

        create_sql = """
        CREATE OR REPLACE PROCEDURE truncate_cybersecurity_db()
        LANGUAGE sql
        AS $$
          TRUNCATE TABLE
            user_activity_logs,
            threat_incident_association,
            threat_vulnerability_association,
            threat_asset_association,
            api_threatintelligence,
            api_alert,
            incident_assets,
            api_incident,
            asset_vulnerabilities,
            api_vulnerability,
            api_asset,
            api_user
          CASCADE;
        $$;
        """

        with conn.cursor() as cur:
            cur.execute(create_sql)
        conn.commit()
        conn.close()

        return {"message": "Truncate procedure created successfully", "success": True}
    except OperationalError as e:
        return {"message": f"Database operation failed: {str(e)}", "success": False}

@router.post("/execute_truncate_procedure/", response=MessageResponse)
def execute_truncate_procedure(request) -> Dict:
    """Executes the database truncate procedure"""
    try:
        conn = psycopg.connect(
            dbname=settings.DATABASES['default']["NAME"],
            user=settings.DATABASES['default']["USER"],
            password=settings.DATABASES['default']["PASSWORD"],
            host=settings.DATABASES['default']["HOST"],
            port=settings.DATABASES['default']["PORT"]
        )

        with conn.cursor() as cur:
            cur.execute("CALL truncate_cybersecurity_db();")
        conn.commit()
        conn.close()

        return {"message": "Database truncated successfully", "success": True}
    except OperationalError as e:
        return {"message": f"Database operation failed: {str(e)}", "success": False}

@router.post("/create_database_no_procedure/", response=MessageResponse)
def create_database(request) -> Dict:
    """Creates the cyber_db database"""
    try:
        conn = psycopg.connect(
            dbname="postgres",
            user=settings.DATABASES['default']["USER"],
            password=settings.DATABASES['default']["PASSWORD"],
            host=settings.DATABASES['default']["HOST"],
            port=settings.DATABASES['default']["PORT"]
        )
        conn.autocommit = True
        with conn.cursor() as cur:
            cur.execute("SELECT 1 FROM pg_database WHERE datname = 'cyber_db'")
            if not cur.fetchone():
                cur.execute("CREATE DATABASE cyber_db")
        conn.close()
        return {"message": "Database created successfully", "success": True}
    except OperationalError as e:
        return {"message": f"Database operation failed: {str(e)}", "success": False}

@router.post("/drop_database/", response=MessageResponse)
def drop_database(request) -> Dict:
    """Drops the cyber_db database directly without stored procedure"""
    try:
        conn = psycopg.connect(
            dbname="postgres",
            user=settings.DATABASES['default']["USER"],
            password=settings.DATABASES['default']["PASSWORD"],
            host=settings.DATABASES['default']["HOST"],
            port=settings.DATABASES['default']["PORT"]
        )
        conn.autocommit = True
        with conn.cursor() as cur:
            cur.execute("DROP DATABASE IF EXISTS cyber_db;")
        conn.close()
        return {"message": "Database dropped successfully", "success": True}
    except OperationalError as e:
        return {"message": f"Database operation failed: {str(e)}", "success": False}

@router.post("/create_tables_procedure/", response=MessageResponse)
def create_tables_procedure(request) -> Dict:
    """Creates a stored procedure to create tables in the cyber_db database"""
    try:
        conn = psycopg.connect(
            dbname=settings.DATABASES['default']["NAME"],
            user=settings.DATABASES['default']["USER"],
            password=settings.DATABASES['default']["PASSWORD"],
            host=settings.DATABASES['default']["HOST"],
            port=settings.DATABASES['default']["PORT"]
        )

        create_tables_sql = """
        CREATE OR REPLACE PROCEDURE create_cybersecurity_tables()
        LANGUAGE plpgsql
        AS $$
        BEGIN
            -- Create User table
            CREATE TABLE IF NOT EXISTS users (
                user_id SERIAL PRIMARY KEY,
                username VARCHAR(150) UNIQUE NOT NULL,
                email VARCHAR(255) UNIQUE NOT NULL,
                role VARCHAR(50) NOT NULL,
                password VARCHAR(255) NOT NULL,
                is_active BOOLEAN DEFAULT TRUE,
                last_login TIMESTAMP,
                date_joined TIMESTAMP
            );

            -- Create Asset table
            CREATE TABLE IF NOT EXISTS assets (
                asset_id SERIAL PRIMARY KEY,
                asset_name VARCHAR(150) UNIQUE NOT NULL,
                asset_type VARCHAR(50) NOT NULL,
                location VARCHAR(50) NOT NULL,
                owner VARCHAR(100) NOT NULL,
                criticality_level VARCHAR(50) NOT NULL
            );

            -- Create Vulnerability table
            CREATE TABLE IF NOT EXISTS vulnerabilities (
                vulnerability_id SERIAL PRIMARY KEY,
                title VARCHAR(255) UNIQUE NOT NULL,
                description TEXT NOT NULL,
                severity VARCHAR(50) NOT NULL,
                cve_reference VARCHAR(100) NOT NULL,
                remediation_steps TEXT NOT NULL,
                discovery_date TIMESTAMP,
                patch_available BOOLEAN DEFAULT TRUE
            );

            -- Create Incident table
            CREATE TABLE IF NOT EXISTS incidents (
                incident_id SERIAL PRIMARY KEY,
                incident_type VARCHAR(100) NOT NULL,
                description TEXT NOT NULL,
                severity VARCHAR(50) NOT NULL,
                status VARCHAR(50) NOT NULL,
                reported_date TIMESTAMP,
                resolved_date TIMESTAMP,
                assigned_to INTEGER REFERENCES users(user_id) ON DELETE SET NULL
            );

            -- Create ThreatIntelligence table
            CREATE TABLE IF NOT EXISTS threat_intelligence (
                threat_id SERIAL PRIMARY KEY,
                threat_actor_name VARCHAR(100) NOT NULL,
                indicator_type VARCHAR(50) NOT NULL,
                indicator_value VARCHAR(255) NOT NULL,
                confidence_level VARCHAR(50) NOT NULL,
                description TEXT NOT NULL,
                related_cve VARCHAR(100),
                date_identified TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );

            -- Create Alert table
            CREATE TABLE IF NOT EXISTS alerts (
                alert_id SERIAL PRIMARY KEY,
                source VARCHAR(255) NOT NULL,
                name VARCHAR(255) NOT NULL,
                alert_type VARCHAR(100) NOT NULL,
                alert_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                severity VARCHAR(50) NOT NULL,
                status VARCHAR(50) NOT NULL,
                incident_id INTEGER REFERENCES incidents(incident_id) ON DELETE SET NULL
            );

            -- Create relationship tables
            CREATE TABLE IF NOT EXISTS asset_vulnerabilities (
                id SERIAL PRIMARY KEY,
                asset_id INTEGER REFERENCES assets(asset_id) ON DELETE CASCADE,
                vulnerability_id INTEGER REFERENCES vulnerabilities(vulnerability_id) ON DELETE CASCADE,
                date_discovered DATE DEFAULT CURRENT_DATE,
                status VARCHAR(50) NOT NULL,
                CONSTRAINT unique_asset_vulnerability UNIQUE (asset_id, vulnerability_id)
            );

            CREATE TABLE IF NOT EXISTS incident_assets (
                id SERIAL PRIMARY KEY,
                incident_id INTEGER REFERENCES incidents(incident_id) ON DELETE CASCADE,
                asset_id INTEGER REFERENCES assets(asset_id) ON DELETE CASCADE,
                impact_level VARCHAR(100) NOT NULL,
                CONSTRAINT unique_incident_asset UNIQUE (incident_id, asset_id)
            );

            CREATE TABLE IF NOT EXISTS threat_asset_association (
                id SERIAL PRIMARY KEY,
                threat_id INTEGER REFERENCES threat_intelligence(threat_id) ON DELETE CASCADE,
                asset_id INTEGER REFERENCES assets(asset_id) ON DELETE CASCADE,
                notes TEXT,
                CONSTRAINT unique_threat_asset UNIQUE (threat_id, asset_id)
            );

            CREATE TABLE IF NOT EXISTS threat_vulnerability_association (
                id SERIAL PRIMARY KEY,
                threat_id INTEGER REFERENCES threat_intelligence(threat_id) ON DELETE CASCADE,
                vulnerability_id INTEGER REFERENCES vulnerabilities(vulnerability_id) ON DELETE CASCADE,
                notes TEXT,
                CONSTRAINT unique_threat_vulnerability UNIQUE (threat_id, vulnerability_id)
            );

            CREATE TABLE IF NOT EXISTS threat_incident_association (
                id SERIAL PRIMARY KEY,
                threat_id INTEGER REFERENCES threat_intelligence(threat_id) ON DELETE CASCADE,
                incident_id INTEGER REFERENCES incidents(incident_id) ON DELETE CASCADE,
                notes TEXT,
                CONSTRAINT unique_threat_incident UNIQUE (threat_id, incident_id)
            );

            CREATE TABLE IF NOT EXISTS user_activity_logs (
                log_id SERIAL PRIMARY KEY,
                user_id INTEGER REFERENCES users(user_id) ON DELETE CASCADE,
                activity_type VARCHAR(100) NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                description TEXT,
                ip_address INET,
                resource_type VARCHAR(100),
                resource_id INTEGER
            );

            -- Create indexes
            CREATE INDEX IF NOT EXISTS idx_alert_incident_id ON alerts(incident_id);
            CREATE INDEX IF NOT EXISTS idx_av_asset_id ON asset_vulnerabilities(asset_id);
            CREATE INDEX IF NOT EXISTS idx_asset_vulnerability_id ON asset_vulnerabilities(vulnerability_id);
            CREATE INDEX IF NOT EXISTS idx_incident_id ON incident_assets(incident_id);
            CREATE INDEX IF NOT EXISTS idx_asset_id_ia ON incident_assets(asset_id);
            CREATE INDEX IF NOT EXISTS idx_taa_threat_id ON threat_asset_association(threat_id);
            CREATE INDEX IF NOT EXISTS idx_taa_asset_id ON threat_asset_association(asset_id);
            CREATE INDEX IF NOT EXISTS idx_tva_threat_id ON threat_vulnerability_association(threat_id);
            CREATE INDEX IF NOT EXISTS idx_tva_vulnerability_id ON threat_vulnerability_association(vulnerability_id);
            CREATE INDEX IF NOT EXISTS idx_tia_threat_id ON threat_incident_association(threat_id);
            CREATE INDEX IF NOT EXISTS idx_tia_incident_id ON threat_incident_association(incident_id);
            CREATE INDEX IF NOT EXISTS idx_ual_user_id ON user_activity_logs(user_id);
            CREATE INDEX IF NOT EXISTS idx_ual_activity_type ON user_activity_logs(activity_type);
            CREATE INDEX IF NOT EXISTS idx_ual_timestamp ON user_activity_logs(timestamp);
        END;
        $$;
        """

        with conn.cursor() as cur:
            cur.execute(create_tables_sql)
        conn.commit()
        conn.close()

        return {"message": "Tables creation procedure created successfully", "success": True}
    except OperationalError as e:
        return {"message": f"Database operation failed: {str(e)}", "success": False}

@router.post("/execute_tables_procedure/", response=MessageResponse)
def execute_tables_procedure(request) -> Dict:
    """Executes the stored procedure to create tables in the cyber_db database"""
    try:
        conn = psycopg.connect(
            dbname="cyber_db",  # Connect to the cyber_db database
            user=settings.DATABASES['default']["USER"],
            password=settings.DATABASES['default']["PASSWORD"],
            host=settings.DATABASES['default']["HOST"],
            port=settings.DATABASES['default']["PORT"]
        )

        with conn.cursor() as cur:
            cur.execute("CALL create_cybersecurity_tables();")
        conn.commit()
        conn.close()

        return {"message": "Database tables created successfully", "success": True}
    except OperationalError as e:
        return {"message": f"Database operation failed: {str(e)}", "success": False}

