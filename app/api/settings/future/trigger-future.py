# Line 3. The trigger creates a PostgreSQL function that runs after each insert on the asset_vulnerabilities table:
# Line 11. When a new vulnerability-asset association is created, it fetches relevant information:
# Line 24. It then checks if this combination requires an alert. If conditions are met, it creates an alert in the api_alert table and logs the activity.
# Line 77. The trigger is automatically applied to the asset_vulnerabilities table, so it runs whenever a new vulnerability is associated with an asset.
trigger = """
CREATE OR REPLACE FUNCTION create_critical_vulnerability_alert() 
RETURNS TRIGGER AS $$
DECLARE
    asset_criticality VARCHAR(50);
    vulnerability_severity VARCHAR(50);
    vulnerability_title VARCHAR(255);
    asset_name VARCHAR(150);
BEGIN
    -- Get the asset criticality level
    SELECT a.criticality_level, a.asset_name INTO asset_criticality, asset_name
    FROM api_asset a
    WHERE a.asset_id = NEW.asset_id;
    
    -- Get vulnerability severity and title
    SELECT v.severity, v.title INTO vulnerability_severity, vulnerability_title
    FROM api_vulnerability v
    WHERE v.vulnerability_id = NEW.vulnerability_id;
    
    -- Create alert for critical vulnerabilities on high criticality assets
    IF (asset_criticality = 'high' AND vulnerability_severity = 'critical') OR
       (asset_criticality = 'high' AND vulnerability_severity = 'high') THEN
        
        -- Insert a new alert
        INSERT INTO api_alert (
            source,
            name,
            alert_type,
            severity,
            status,
            alert_time,
            incident_id
        ) VALUES (
            'Vulnerability Management System',
            'Critical vulnerability detected on high-priority asset',
            'vulnerability',
            CASE 
                WHEN vulnerability_severity = 'critical' THEN 'critical'
                ELSE 'high'
            END,
            'new',
            NOW(),
            NULL -- No incident assigned yet
        );
        
        -- Log the activity
        INSERT INTO user_activity_logs (
            user_id,
            activity_type,
            description,
            resource_type,
            resource_id,
            ip_address,
            timestamp
        ) VALUES (
            1, -- System user
            'create',
            'Automatic alert created for ' || vulnerability_title || ' on ' || asset_name,
            'alert',
            currval('api_alert_alert_id_seq'),
            '127.0.0.1',
            NOW()
        );
        
        RAISE NOTICE 'Created alert for critical vulnerability % on high criticality asset %', 
                     vulnerability_title, asset_name;
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create the trigger on asset_vulnerabilities table
CREATE OR REPLACE TRIGGER vulnerability_asset_alert_trigger
AFTER INSERT ON asset_vulnerabilities
FOR EACH ROW
EXECUTE FUNCTION create_critical_vulnerability_alert();
"""


# @router.post("/vulnerabilities/associate")
# async def associate_vulnerability_with_asset(
#         association: VulnerabilityAssetAssociation,
#         db: Session = Depends(get_db)
# ):
#     # Create association in the asset_vulnerabilities table
#     new_association = AssetVulnerability(
#         asset_id=association.asset_id,
#         vulnerability_id=association.vulnerability_id
#     )
#     db.add(new_association)
#     db.commit()
#
#     # The trigger will automatically create alerts if needed
#     return {"status": "success", "message": "Association created"}


# const AlertsPanel = () => {
#   const [alerts, setAlerts] = useState<Alert[]>([]);
#
#   useEffect(() => {
#     // Fetch alerts created by the trigger
#     const fetchAlerts = async () => {
#       const response = await fetch('/api/alerts?type=vulnerability');
#       const data = await response.json();
#       setAlerts(data.alerts);
#     };
#
#     fetchAlerts();
#     // Refresh alerts periodically
#     const interval = setInterval(fetchAlerts, 30000);
#     return () => clearInterval(interval);
#   }, []);
#
#   return (
#     <div className="alerts-panel">
#       <h2>Critical Vulnerability Alerts</h2>
#       {alerts.map(alert => (
#         <AlertCard
#           key={alert.alert_id}
#           title={alert.name}
#           severity={alert.severity}
#           status={alert.status}
#           timestamp={alert.alert_time}
#         />
#       ))}
#     </div>
#   );
# };
