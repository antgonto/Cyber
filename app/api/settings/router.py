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

@router.post("/create_tables/", response=MessageResponse)
def create_and_execute_tables(request) -> Dict:
    """Creates all tables in the cyber_db database directly without using a stored procedure"""
    try:
        conn = psycopg.connect(
            dbname=settings.DATABASES['default']["NAME"],
            user=settings.DATABASES['default']["USER"],
            password=settings.DATABASES['default']["PASSWORD"],
            host=settings.DATABASES['default']["HOST"],
            port=settings.DATABASES['default']["PORT"]
        )

        create_tables_sql = """
        -- Create User table
        CREATE TABLE IF NOT EXISTS api_user (
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
        CREATE TABLE IF NOT EXISTS api_asset (
            asset_id SERIAL PRIMARY KEY,
            asset_name VARCHAR(150) UNIQUE NOT NULL,
            asset_type VARCHAR(50) NOT NULL,
            location VARCHAR(50) NOT NULL,
            owner VARCHAR(100) NOT NULL,
            criticality_level VARCHAR(50) NOT NULL
        );

        -- Create Vulnerability table
        CREATE TABLE IF NOT EXISTS api_vulnerability (
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
        CREATE TABLE IF NOT EXISTS api_incident (
            incident_id SERIAL PRIMARY KEY,
            incident_type VARCHAR(100) NOT NULL,
            description TEXT NOT NULL,
            severity VARCHAR(50) NOT NULL,
            status VARCHAR(50) NOT NULL,
            reported_date TIMESTAMP,
            resolved_date TIMESTAMP,
            assigned_to INTEGER REFERENCES api_user(user_id) ON DELETE SET NULL
        );

        -- Create ThreatIntelligence table
        CREATE TABLE IF NOT EXISTS api_threatintelligence (
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
        CREATE TABLE IF NOT EXISTS api_alert (
            alert_id SERIAL PRIMARY KEY,
            source VARCHAR(255) NOT NULL,
            name VARCHAR(255) NOT NULL,
            alert_type VARCHAR(100) NOT NULL,
            alert_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            severity VARCHAR(50) NOT NULL,
            status VARCHAR(50) NOT NULL,
            incident_id INTEGER REFERENCES api_incident(incident_id) ON DELETE SET NULL
        );

        -- Create relationship tables
        CREATE TABLE IF NOT EXISTS asset_vulnerabilities (
            id SERIAL PRIMARY KEY,
            asset_id INTEGER REFERENCES api_asset(asset_id) ON DELETE CASCADE,
            vulnerability_id INTEGER REFERENCES api_vulnerability(vulnerability_id) ON DELETE CASCADE,
            date_discovered DATE DEFAULT CURRENT_DATE,
            status VARCHAR(50) NOT NULL,
            CONSTRAINT unique_asset_vulnerability UNIQUE (asset_id, vulnerability_id)
        );

        CREATE TABLE IF NOT EXISTS incident_assets (
            id SERIAL PRIMARY KEY,
            incident_id INTEGER REFERENCES api_incident(incident_id) ON DELETE CASCADE,
            asset_id INTEGER REFERENCES api_asset(asset_id) ON DELETE CASCADE,
            impact_level VARCHAR(100) NOT NULL,
            CONSTRAINT unique_incident_asset UNIQUE (incident_id, asset_id)
        );

        CREATE TABLE IF NOT EXISTS threat_asset_association (
            id SERIAL PRIMARY KEY,
            threat_id INTEGER REFERENCES api_threatintelligence(threat_id) ON DELETE CASCADE,
            asset_id INTEGER REFERENCES api_asset(asset_id) ON DELETE CASCADE,
            notes TEXT,
            CONSTRAINT unique_threat_asset UNIQUE (threat_id, asset_id)
        );

        CREATE TABLE IF NOT EXISTS threat_vulnerability_association (
            id SERIAL PRIMARY KEY,
            threat_id INTEGER REFERENCES api_threatintelligence(threat_id) ON DELETE CASCADE,
            vulnerability_id INTEGER REFERENCES api_vulnerability(vulnerability_id) ON DELETE CASCADE,
            notes TEXT,
            CONSTRAINT unique_threat_vulnerability UNIQUE (threat_id, vulnerability_id)
        );

        CREATE TABLE IF NOT EXISTS threat_incident_association (
            id SERIAL PRIMARY KEY,
            threat_id INTEGER REFERENCES api_threatintelligence(threat_id) ON DELETE CASCADE,
            incident_id INTEGER REFERENCES api_incident(incident_id) ON DELETE CASCADE,
            notes TEXT,
            CONSTRAINT unique_threat_incident UNIQUE (threat_id, incident_id)
        );

        CREATE TABLE IF NOT EXISTS user_activity_logs (
            log_id SERIAL PRIMARY KEY,
            user_id INTEGER REFERENCES api_user(user_id) ON DELETE CASCADE,
            activity_type VARCHAR(100) NOT NULL,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            description TEXT,
            ip_address INET,
            resource_type VARCHAR(100),
            resource_id INTEGER
        );

        -- Create indexes
        CREATE INDEX IF NOT EXISTS idx_alert_incident_id ON api_alert(incident_id);
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
        """

        with conn.cursor() as cur:
            cur.execute(create_tables_sql)
        conn.commit()
        conn.close()

        return {"message": "Database tables created successfully", "success": True}
    except OperationalError as e:
        return {"message": f"Database operation failed: {str(e)}", "success": False}


@router.post("/create_threat_update_trigger/", response=MessageResponse)
def create_threat_update_trigger(request) -> Dict:
    """
    Creates or replaces the trigger function and trigger that stamps last_updated on api_threatintelligence.
    """
    try:
        conn = psycopg.connect(
            dbname=settings.DATABASES['default']["NAME"],
            user=settings.DATABASES['default']["USER"],
            password=settings.DATABASES['default']["PASSWORD"],
            host=settings.DATABASES['default']["HOST"],
            port=settings.DATABASES['default']["PORT"]
        )
        sql = """
        CREATE OR REPLACE FUNCTION trg_threat_update_timestamp()
        RETURNS TRIGGER AS $$
        BEGIN
          NEW.last_updated := NOW();
          RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;

        DROP TRIGGER IF EXISTS tr_threat_timestamp ON api_threatintelligence;
        CREATE TRIGGER tr_threat_timestamp
          BEFORE INSERT OR UPDATE
          ON api_threatintelligence
          FOR EACH ROW
          EXECUTE FUNCTION trg_threat_update_timestamp();
        """
        with conn.cursor() as cur:
            cur.execute(sql)
        conn.commit()
        conn.close()
        return {"message": "Threat update trigger created successfully", "success": True}
    except OperationalError as e:
        return {"message": f"Database operation failed: {str(e)}", "success": False}

@router.post("/create_assoc_touch_triggers/", response=MessageResponse)
def create_assoc_touch_triggers(request) -> Dict:
    """Creates or replaces triggers that bump last_updated on threat associations."""
    try:
        conn = psycopg.connect(
            dbname=settings.DATABASES['default']["NAME"],
            user=settings.DATABASES['default']["USER"],
            password=settings.DATABASES['default']["PASSWORD"],
            host=settings.DATABASES['default']["HOST"],
            port=settings.DATABASES['default']["PORT"],
        )
        sql = """
        CREATE OR REPLACE FUNCTION trg_assoc_touch_threat()
        RETURNS TRIGGER AS $$
        DECLARE
          tid INTEGER;
        BEGIN
          IF TG_OP = 'DELETE' THEN
            tid := OLD.threat_id;
          ELSE
            tid := NEW.threat_id;
          END IF;
          UPDATE api_threatintelligence
            SET last_updated = NOW()
            WHERE threat_id = tid;
          RETURN NULL;
        END;
        $$ LANGUAGE plpgsql;

        DROP TRIGGER IF EXISTS tr_asset_assoc_touch ON threat_asset_association;
        CREATE TRIGGER tr_asset_assoc_touch
          AFTER INSERT OR UPDATE OR DELETE
          ON threat_asset_association
          FOR EACH ROW
          EXECUTE FUNCTION trg_assoc_touch_threat();

        DROP TRIGGER IF EXISTS tr_vuln_assoc_touch ON threat_vulnerability_association;
        CREATE TRIGGER tr_vuln_assoc_touch
          AFTER INSERT OR UPDATE OR DELETE
          ON threat_vulnerability_association
          FOR EACH ROW
          EXECUTE FUNCTION trg_assoc_touch_threat();

        DROP TRIGGER IF EXISTS tr_incident_assoc_touch ON threat_incident_association;
        CREATE TRIGGER tr_incident_assoc_touch
          AFTER INSERT OR UPDATE OR DELETE
          ON threat_incident_association
          FOR EACH ROW
          EXECUTE FUNCTION trg_assoc_touch_threat();
        """
        with conn.cursor() as cur:
            cur.execute(sql)
        conn.commit()
        conn.close()
        return {"message": "Association triggers created successfully", "success": True}
    except OperationalError as e:
        return {"message": f"Database operation failed: {str(e)}", "success": False}

@router.post("/create_fake_data_procedure/", response=MessageResponse)
def create_seed_procedure(request):
    """
    Creates or replaces the `insert_seed_data` stored procedure,
    which inserts all of your initial seed rows.
    """
    try:
        conn = psycopg.connect(
            dbname=settings.DATABASES['default']["NAME"],
            user=settings.DATABASES['default']["USER"],
            password=settings.DATABASES['default']["PASSWORD"],
            host=settings.DATABASES['default']["HOST"],
            port=settings.DATABASES['default']["PORT"]
        )

        create_sql = """
        CREATE OR REPLACE PROCEDURE insert_seed_data()
        LANGUAGE plpgsql
        AS $$
        BEGIN 
            INSERT INTO api_user (user_id, username, email, role, password, last_login, is_active, date_joined) VALUES
            (1, 'admin_user', 'admin@example.com', 'admin', '$2a$12$tI3KXJZxFZhJ/d9cu95kZOp4.m496bBgRKuVN9g7xhRHEOy7.EpMe', '2023-08-15 14:30:00', true, '2023-01-10 09:00:00'),
            (2, 'john_analyst', 'john@example.com', 'analyst', '$2a$12$3fI5t7zdKQh7QjdGPEEureq3XeVBq1b0Cy5Y9s97T8OiJ2aEmq55i', '2023-08-20 11:45:00', true, '2023-02-05 10:15:00'),
            (3, 'sarah_manager', 'sarah@example.com', 'manager', '$2a$12$qxq7SeLn3zZwxLQyQ.cPv.IHFtxPZpYPVOKLHSVxbQ4Nj3eTJ6tDS', '2023-08-21 08:15:00', true, '2023-02-20 14:30:00'),
            (4, 'mike_analyst', 'mike@example.com', 'analyst', '$2a$12$2xyX76ShH/saC.AZH9h9EOvfmL6UO337J9UgFB7Ea0M3hfKM1J.dS', '2023-08-18 16:20:00', true, '2023-03-15 11:00:00'),
            (5, 'lisa_user', 'lisa@example.com', 'user', '$2a$12$dfr5JU3DAQlgZK7KCT9ruO9.X0.aXpgkUyvKcCHlJeBXb.5YZ2ZZe', '2023-08-10 09:30:00', true, '2023-04-05 09:45:00'),
            (6, 'david_manager', 'david@example.com', 'manager', '$2a$12$n.jZ8x4SHq9YwhkFJZXCZOYWLzKZX3qHI9L0IVr2/MTsZs3QR.kX.', '2023-08-19 10:00:00', true, '2023-04-20 13:15:00'),
            (7, 'emma_user', 'emma@example.com', 'user', '$2a$12$tca5NE/37.vT4RAHsrwD9.bqaLG0OnZPQME3nEFXdyfKRT/WK9iEa', NULL, true, '2023-05-12 15:30:00'),
            (8, 'james_analyst', 'james@example.com', 'analyst', '$2a$12$v6GJS2XUGUFv01SQiV5EEeWUQA8OLJk2OXV6iW27X2PZ2EwEq1GOS', '2023-08-17 13:45:00', true, '2023-06-01 08:00:00'),
            (9, 'alex_inactive', 'alex@example.com', 'user', '$2a$12$CQIIwEXVpufyAG9SAh2mP.WJgefzLMNw.a2WlZMbkxYxLgK5oVgJC', '2023-07-10 11:00:00', false, '2023-06-15 10:30:00'),
            (10, 'olivia_user', 'olivia@example.com', 'user', '$2a$12$I01mAh3uT43gjcEkDGXuru/aI.mTyZ8BDEGCQSv4S9P9E0KQFkFKO', '2023-08-15 15:15:00', true, '2023-07-01 09:15:00')
            ON CONFLICT (user_id) DO NOTHING;

            INSERT INTO api_asset (asset_id, asset_name, asset_type, location, owner, criticality_level) VALUES
            (1, 'Web Server Alpha', 'Web Server', 'Data Center', 1, 'Critical'),
            (2,'HR Database', 'HR Database', 'Cloud-HR', 3, 'High'),
            (3,'Marketing Laptop', 'Marketing Endpoint', 'Office 201', 4, 'Medium'),
            (4,'Finance File Server', 'File Server', 'Data Center', 6, 'Critical'),
            (5,'Guest WiFi Network', 'Network', 'All Offices', 2, 'Low-1'),
            (6,'Customer Data Database', 'Customer Database', 'Cloud-Customer', 7, 'Critical'),
            (7,'Dev Environment', 'Virtual Machine', 'Cloud-Dev', 5, 'Medium'),
            (8,'Executive Workstation', 'Executive Endpoint', 'Office 101', 8, 'High'),
            (9,'Workstation', 'Executive Endpoint', '101', 8, 'Low'),
            (10,'Work', 'Executive Endpoint', 'Dev', 5, 'Medium')
            ON CONFLICT (asset_id) DO NOTHING;

            INSERT INTO api_vulnerability (vulnerability_id, title, description, severity, cve_reference, remediation_steps, discovery_date, patch_available) VALUES
            (1,'SQL Injection', 'Ability to inject SQL commands via form inputs', 'Critical', 'CVE-2022-1234', 'Implement prepared statements and input validation', '2022-02-15 10:30:00', true),
            (2,'Cross-Site Scripting', 'Vulnerable to XSS attacks through unvalidated user input', 'High', 'CVE-2022-5678', 'Implement content security policy and output encoding', '2022-03-21 14:45:00', true),
            (3,'Outdated SSL', 'Server using deprecated SSL v3', 'Medium', 'CVE-2021-9876', 'Upgrade to TLS 1.3', '2021-11-05 09:15:00', true),
            (4,'Default Credentials', 'System using factory default login credentials', 'Critical', 'CVE-2020-8765', 'Change all default passwords and implement password policy', '2020-09-18 16:20:00', true),
            (5,'Unpatched Operating System', 'Missing critical security patches', 'High', 'CVE-2023-1111', 'Apply latest security patches and implement patch management process', '2023-01-30 11:00:00', true),
            (6,'Open SMTP Relay', 'Mail server configured as an open relay', 'High', 'CVE-2021-5432', 'Reconfigure mail server to require authentication', '2021-07-12 13:40:00', true)
            ON CONFLICT (vulnerability_id) DO NOTHING;

            INSERT INTO asset_vulnerabilities (asset_id, vulnerability_id, date_discovered, status) VALUES
            (1, 1, '2023-05-15', 'Open'),
            (1, 3, '2023-05-16', 'Mitigated'),
            (2, 1, '2023-05-20', 'Open'),
            (3, 5, '2023-05-21', 'Resolved'),
            (4, 4, '2023-05-25', 'Open'),
            (6, 1, '2023-05-27', 'In Progress'),
            (7, 2, '2023-05-28', 'Open'),
            (7, 5, '2023-05-29', 'Open');

            INSERT INTO api_incident (incident_id, incident_type, description, severity, status, assigned_to_id, reported_date, resolved_date) VALUES
            (1,'Data Breach', 'Unauthorized access to customer database detected', 'Critical', 'active', 5, '2023-06-15 09:30:00', NULL),
            (2,'Malware', 'Ransomware detected on marketing department systems', 'High', 'investigating', 3, '2023-06-10 14:22:00', NULL),
            (3,'DDoS', 'Distributed denial of service attack on public website', 'Medium', 'resolved', 2, '2023-05-28 10:15:00', '2023-05-28 15:45:00'),
            (4,'Phishing', 'Targeted phishing campaign against executive team', 'High', 'contained', 5, '2023-06-05 08:45:00', NULL),
            (5,'Insider Threat', 'Suspicious data exfiltration by terminated employee', 'Medium', 'active', 4, '2023-06-18 11:20:00', NULL),
            (6,'Vulnerability', 'Critical zero-day vulnerability in web application', 'High', 'investigating', 1, '2023-06-20 16:10:00', NULL),
            (7,'Unauthorized Access', 'Login attempts from unknown IP addresses', 'Low', 'resolved', 3, '2023-05-15 07:30:00', '2023-05-15 14:20:00')
            ON CONFLICT (incident_id) DO NOTHING;

            INSERT INTO incident_assets (incident_id, asset_id, impact_level) VALUES
            (1, 6, 'Critical'),
            (2, 3, 'Medium'),
            (3, 1, 'High'),
            (4, 8, 'Medium'),
            (5, 4, 'High');

            INSERT INTO api_alert (source, name, alert_type, alert_time, severity, status, incident_id) VALUES
            ('IDS', 'IDS Signature Alert', 'Signature Match', '2023-04-10 08:15:00', 'Critical', 'Closed', 1),
            ('Antivirus', 'Malware Alert', 'Malware Detection', '2023-04-20 10:05:00', 'High', 'Closed', 2),
            ('Network Monitor', 'Traffic Anomaly Alert', 'Traffic Anomaly', '2023-05-05 09:00:00', 'High', 'Closed', 3),
            ('Email Gateway', 'Phishing Email Alert', 'Phishing Detection', '2023-06-01 11:25:00', 'Medium', 'Active', 4),
            ('SIEM', 'Login Anomaly Alert', 'Abnormal Login', '2023-06-10 22:10:00', 'High', 'Active', 5),
            ('IDS', 'Port Scan Alert', 'Port Scan', '2023-06-12 14:35:00', 'Low', 'Active', NULL),
            ('Firewall', 'Firewall Rule Violation', 'Rule Violation', '2023-06-13 16:40:00', 'Medium', 'Active', NULL);
           

            INSERT INTO api_threatintelligence (threat_id, threat_actor_name, indicator_type, indicator_value, confidence_level, description, related_cve, date_identified, last_updated)
            VALUES
            (1, 'APT29', 'domain', 'malicious-domain.com', 'High', 'Russian state-sponsored group targeting government entities', 'CVE-2021-44228', '2023-01-15', '2023-01-15'),
            (2, 'Lazarus Group', 'ip_address', '192.168.1.100', 'Medium', 'North Korean threat group focusing on financial theft', 'CVE-2020-0601', '2023-02-20', '2023-01-15'),
            (3, 'FIN7', 'hash', 'a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4', 'High', 'Financial crime group targeting retail and hospitality', 'CVE-2019-0708', '2023-03-10', '2023-01-15'),
            (4, 'Sandworm', 'url', 'https://malicious-site.net/payload', 'High', 'Russian military unit targeting critical infrastructure', NULL, '2023-04-05', '2023-01-15'),
            (5, 'Cobalt Group', 'email', 'phishing@fake-bank.com', 'Medium', 'Financial threat actor targeting banking systems', 'CVE-2017-11882', '2023-05-12', '2023-01-15'),
            (6, 'Group', 'email', 'phishing3@fake-bank.com', 'High', 'Threat actor targeting banking systems', 'CVE-2017-11882', '2023-05-12', '2023-01-15')
            ON CONFLICT (threat_id) DO NOTHING;

            INSERT INTO threat_asset_association (threat_id, asset_id, notes)
            VALUES
            (1, 1, 'Primary target for SQL injection attempts'),
            (1, 3, 'Database server vulnerable to the threat actor techniques'),
            (1, 5, 'Potential secondary target if primary defenses are breached'),
            (2, 2, 'Web server targeted through malicious scripts'),
            (2, 4, 'Customer portal shows evidence of XSS probing attempts'),
            (2, 7, 'Development environment used for testing exploits'),
            (3, 1, 'Production API server uses outdated SSL libraries'),
            (3, 6, 'VPN server needs certificate and protocol updates'),
            (3, 8, 'Mobile application backend vulnerable to SSL downgrade attacks'),
            (4, 3, 'Default admin credentials never changed since installation'),
            (4, 9, 'IoT devices with factory settings detected'),
            (4, 10, 'Network equipment using default community strings'),
            (5, 5, 'Critical server missing latest security patches'),
            (5, 7, 'Development server rarely updated'),
            (5, 8, 'Mobile backend running vulnerable OS version');

            INSERT INTO threat_vulnerability_association (threat_id, vulnerability_id, notes)
            VALUES
            (1, 1, 'Primary SQL injection vulnerability actively exploited by this threat actor'),
            (1, 4, 'Default credentials used to gain access before launching SQL injection'),
            (2, 2, 'Sophisticated XSS techniques observed in exploitation attempts'),
            (2, 5, 'Uses unpatched systems as entry points before deploying XSS payloads'),
            (3, 3, 'Specialized in exploiting outdated SSL implementations'),
            (3, 6, 'Uses SMTP relay access to distribute SSL exploit payloads'),
            (4, 4, 'Primary technique involves brute forcing default credential combinations'),
            (4, 5, 'Uses unpatched systems that often have default credentials'),
            (5, 5, 'Specialized in identifying and exploiting unpatched OS vulnerabilities'),
            (5, 3, 'Uses outdated SSL as an entry point before escalating to OS-level exploits'),
            (6, 6, 'Primary focus is on exploiting SMTP relay configurations'),
            (6, 4, 'Often uses default credentials to access mail servers initially');

            INSERT INTO threat_incident_association (threat_id, incident_id, notes) VALUES
            (1, 1, 'Strong evidence of APT29 involvement based on TTPs'),
            (2, 2, 'IP address patterns match Lazarus Group infrastructure'),
            (3, 3, 'Hash matches known FIN7 malware variant'),
            (4, 1, 'URL associated with recent Sandworm campaign'),
            (5, 4, 'Phishing email confirmed to be from Cobalt Group operation');

            INSERT INTO user_activity_logs (user_id, activity_type, timestamp, description) VALUES
            (1, 'Login', '2023-06-15 08:30:00', 'Successful login from 10.0.0.15'),
            (1, 'Configuration Change', '2023-06-15 09:15:00', 'Updated firewall rules'),
            (2, 'Report Generation', '2023-06-14 14:30:00', 'Generated vulnerability assessment report'),
            (3, 'Asset Creation', '2023-06-13 11:50:00', 'Created new asset record'),
            (4, 'Password Reset', '2023-06-10 09:20:00', 'Reset password for account'),
            (2, 'Alert Investigation', '2023-06-12 10:45:00', 'Investigated and triaged IDS alert');          
        END;
        $$;
        """

        with conn.cursor() as cursor:
            cursor.execute(create_sql)
        conn.commit()
        conn.close()

        return {"message": "Seed-data procedure created or replaced successfully", "success": True}
    except OperationalError as e:
        return {"message": f"Database operation failed: {str(e)}", "success": False}

@router.post("/execute_fake_data_procedure/", response=MessageResponse)
def execute_seed_procedure(request):
    """
    Calls the `insert_seed_data()` procedure to populate all of your tables.
    """
    try:
        conn = psycopg.connect(
            dbname=settings.DATABASES['default']["NAME"],
            user=settings.DATABASES['default']["USER"],
            password=settings.DATABASES['default']["PASSWORD"],
            host=settings.DATABASES['default']["HOST"],
            port=settings.DATABASES['default']["PORT"]
        )
        with conn.cursor() as cursor:
            cursor.execute("CALL insert_seed_data()")
        conn.commit()
        conn.close()
        return {"message": "Data inserted successfully", "success": True}
    except OperationalError as e:
        return {"message": f"Data insertion failed: {str(e)}", "success": False}

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
        LANGUAGE plpgsql
        AS $$
        BEGIN
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
        END;
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

@router.post("/drop_database/", response=MessageResponse)
def drop_database(request) -> Dict:
    """Drops the cyber_db database directly without stored procedure"""
    try:
        database = settings.DATABASES['default']["NAME"]
        # Connect to postgres default database instead of the one we want to drop
        conn = psycopg.connect(
            dbname="postgres",  # Connect to default postgres database instead
            user=settings.DATABASES['default']["USER"],
            password=settings.DATABASES['default']["PASSWORD"],
            host=settings.DATABASES['default']["HOST"],
            port=settings.DATABASES['default']["PORT"]
        )
        conn.autocommit = True
        with conn.cursor() as cur:
            # Close existing connections to the database
            cur.execute(f"""
                SELECT pg_terminate_backend(pg_stat_activity.pid)
                FROM pg_stat_activity
                WHERE pg_stat_activity.datname = %s
                AND pid <> pg_backend_pid();
            """, (database,))
            # Then drop the database
            cur.execute(f"DROP DATABASE IF EXISTS {database}")
        conn.close()
        return {"message": "Database dropped successfully", "success": True}
    except OperationalError as e:
        return {"message": f"Database operation failed: {str(e)}", "success": False}

