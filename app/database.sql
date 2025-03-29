-- Drop the database if it exists and create a new one
DROP DATABASE IF EXISTS cybersecurity_db;
CREATE DATABASE cybersecurity_db;
USE cybersecurity_db;

-- 1. Users Table
CREATE TABLE users (
  user_id INT AUTO_INCREMENT PRIMARY KEY,
  username VARCHAR(150) NOT NULL,
  email VARCHAR(255) NOT NULL UNIQUE,
  role VARCHAR(50),
  password VARCHAR(255), -- password hash storage if needed
  last_login DATETIME DEFAULT NULL
) ENGINE=InnoDB;

-- 2. Assets Table
CREATE TABLE assets (
  asset_id INT AUTO_INCREMENT PRIMARY KEY,
  asset_name VARCHAR(255) NOT NULL,
  asset_type VARCHAR(100) NOT NULL,
  location VARCHAR(255),
  owner INT NULL, -- Allow NULL since ON DELETE SET NULL is used
  criticality_level VARCHAR(50) NOT NULL,
  INDEX idx_owner (owner),
  CONSTRAINT fk_asset_owner FOREIGN KEY (owner) REFERENCES users(user_id) ON DELETE SET NULL
) ENGINE=InnoDB;

-- 3. Vulnerabilities Table
CREATE TABLE vulnerabilities (
  vulnerability_id INT AUTO_INCREMENT PRIMARY KEY,
  title VARCHAR(255) NOT NULL,
  description TEXT NOT NULL,
  severity VARCHAR(50) NOT NULL,
  cve_reference VARCHAR(100),
  remediation_steps TEXT NOT NULL
) ENGINE=InnoDB;

-- 4. AssetVulnerabilities (Join Table for Assets and Vulnerabilities)
CREATE TABLE asset_vulnerabilities (
  asset_id INT NOT NULL,
  vulnerability_id INT NOT NULL,
  date_discovered DATE DEFAULT (CURRENT_DATE()),
  status VARCHAR(50) NOT NULL,
  PRIMARY KEY (asset_id, vulnerability_id),
  INDEX idx_asset_id (asset_id),
  INDEX idx_vulnerability_id (vulnerability_id),
  CONSTRAINT fk_av_asset FOREIGN KEY (asset_id) REFERENCES assets(asset_id) ON DELETE CASCADE,
  CONSTRAINT fk_av_vulnerability FOREIGN KEY (vulnerability_id) REFERENCES vulnerabilities(vulnerability_id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- 5. Incidents Table
CREATE TABLE incidents (
  incident_id INT AUTO_INCREMENT PRIMARY KEY,
  incident_type VARCHAR(100) NOT NULL,
  description TEXT NOT NULL,
  severity VARCHAR(50) NOT NULL,
  status VARCHAR(50) NOT NULL,
  reported_date DATETIME DEFAULT CURRENT_TIMESTAMP,
  resolved_date DATETIME DEFAULT NULL,
  assigned_to INT NULL,
  INDEX idx_assigned_to (assigned_to),
  CONSTRAINT fk_incident_assigned_to FOREIGN KEY (assigned_to) REFERENCES users(user_id) ON DELETE SET NULL
) ENGINE=InnoDB;

-- 6. IncidentAssets (Join Table for Incidents and Assets)
CREATE TABLE incident_assets (
  incident_id INT NOT NULL,
  asset_id INT NOT NULL,
  impact_level VARCHAR(100) NOT NULL,
  PRIMARY KEY (incident_id, asset_id),
  INDEX idx_incident_id (incident_id),
  INDEX idx_asset_id_ia (asset_id),
  CONSTRAINT fk_ia_incident FOREIGN KEY (incident_id) REFERENCES incidents(incident_id) ON DELETE CASCADE,
  CONSTRAINT fk_ia_asset FOREIGN KEY (asset_id) REFERENCES assets(asset_id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- 7. Alerts Table
CREATE TABLE alerts (
  alert_id INT AUTO_INCREMENT PRIMARY KEY,
  source VARCHAR(255) NOT NULL,
  alert_type VARCHAR(100) NOT NULL,
  alert_time DATETIME DEFAULT CURRENT_TIMESTAMP,
  severity VARCHAR(50) NOT NULL,
  status VARCHAR(50) NOT NULL,
  incident_id INT NULL,
  INDEX idx_incident_id_alert (incident_id),
  CONSTRAINT fk_alert_incident FOREIGN KEY (incident_id) REFERENCES incidents(incident_id) ON DELETE SET NULL
) ENGINE=InnoDB;

-- 8. ThreatIntelligence Table
CREATE TABLE threat_intelligence (
  threat_id INT AUTO_INCREMENT PRIMARY KEY,
  threat_actor_name VARCHAR(100) NOT NULL,
  indicator_type VARCHAR(50) NOT NULL,
  indicator_value VARCHAR(255) NOT NULL,
  confidence_level VARCHAR(50) NOT NULL,
  description TEXT NOT NULL,
  related_cve VARCHAR(100)
) ENGINE=InnoDB;

-- 9. Threat-Asset Association Table
CREATE TABLE threat_asset_association (
  threat_id INT NOT NULL,
  asset_id INT NOT NULL,
  PRIMARY KEY (threat_id, asset_id),
  INDEX idx_threat_id_asset (threat_id),
  INDEX idx_asset_id_threat (asset_id),
  CONSTRAINT fk_threat_asset FOREIGN KEY (threat_id) REFERENCES threat_intelligence(threat_id) ON DELETE CASCADE,
  CONSTRAINT fk_asset_threat FOREIGN KEY (asset_id) REFERENCES assets(asset_id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- 10. Threat-Vulnerability Association Table
CREATE TABLE threat_vulnerability_association (
  threat_id INT NOT NULL,
  vulnerability_id INT NOT NULL,
  PRIMARY KEY (threat_id, vulnerability_id),
  INDEX idx_threat_id_vuln (threat_id),
  INDEX idx_vuln_id_threat (vulnerability_id),
  CONSTRAINT fk_threat_vuln FOREIGN KEY (threat_id) REFERENCES threat_intelligence(threat_id) ON DELETE CASCADE,
  CONSTRAINT fk_vuln_threat FOREIGN KEY (vulnerability_id) REFERENCES vulnerabilities(vulnerability_id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- 11. Threat-Incident Association Table
CREATE TABLE threat_incident_association (
  threat_id INT NOT NULL,
  incident_id INT NOT NULL,
  PRIMARY KEY (threat_id, incident_id),
  INDEX idx_threat_id_incident (threat_id),
  INDEX idx_incident_id_threat (incident_id),
  CONSTRAINT fk_threat_incident FOREIGN KEY (threat_id) REFERENCES threat_intelligence(threat_id) ON DELETE CASCADE,
  CONSTRAINT fk_incident_threat FOREIGN KEY (incident_id) REFERENCES incidents(incident_id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- 12. UserActivityLogs Table
CREATE TABLE user_activity_logs (
  activity_id INT AUTO_INCREMENT PRIMARY KEY,
  user_id INT NOT NULL,
  activity_type VARCHAR(100) NOT NULL,
  timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
  description TEXT,
  INDEX idx_user_id_logs (user_id),
  CONSTRAINT fk_log_user FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
) ENGINE=InnoDB;
