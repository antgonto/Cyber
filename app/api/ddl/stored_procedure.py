
# PostgreSQL Stored Procedure: Incident Escalation Manager
# This code defines a Python variable stored_proc containing a PostgreSQL stored procedure called manage_incident_escalation. The procedure automates security incident triage by:
#
#
# Taking parameters for an incident ID and optional user override:
#
#
# CREATE OR REPLACE PROCEDURE manage_incident_escalation(
#     incident_id_param INTEGER,
#     override_user_id INTEGER DEFAULT NULL
# )
# Gathering incident context by querying related tables for:
#
#
# Basic incident details
# Asset criticality levels
# Threat intelligence confidence
# Unacknowledged alert counts
# Implementing escalation logic to determine appropriate roles:
#
#
# IF incident_record.severity = 'critical' THEN
#     appropriate_role := 'manager';
#     escalation_reason := 'Critical severity incident';
# Assigning incidents to users with the proper role using a round-robin approach.
#
#
# Updating incident status to "investigating" for critical cases or when there are multiple unacknowledged alerts.
#
#
# Logging all actions for audit purposes.

stored_proc = """
CREATE OR REPLACE PROCEDURE manage_incident_escalation(
    incident_id_param INTEGER,
    override_user_id INTEGER DEFAULT NULL
)
LANGUAGE plpgsql
AS $$
DECLARE
    incident_record RECORD;
    highest_asset_criticality VARCHAR(50);
    highest_threat_confidence VARCHAR(50);
    unacknowledged_alerts_count INTEGER;
    appropriate_user_id INTEGER;
    appropriate_role VARCHAR(50);
    escalation_reason TEXT;
BEGIN
    -- Get incident information
    SELECT i.* INTO incident_record
    FROM public.api_incident i
    WHERE i.incident_id = incident_id_param;
    
    IF NOT FOUND THEN
        RAISE EXCEPTION 'Incident with ID % not found', incident_id_param;
    END IF;
    
    -- Get highest asset criticality for this incident
    SELECT MAX(a.criticality_level) INTO highest_asset_criticality
    FROM public.incident_assets ia
    JOIN public.api_asset a ON a.asset_id = ia.asset_id
    WHERE ia.incident_id = incident_id_param;
    
    -- Get highest threat confidence
    SELECT MAX(ti.confidence_level) INTO highest_threat_confidence
    FROM public.threat_incident_association tia
    JOIN public.api_threatintelligence ti ON ti.threat_id = tia.threat_id
    WHERE tia.incident_id = incident_id_param;
    
    -- Count unacknowledged alerts
    SELECT COUNT(*) INTO unacknowledged_alerts_count
    FROM public.api_alert
    WHERE incident_id = incident_id_param AND status = 'new';
    
    -- Determine if incident needs escalation and to whom
    escalation_reason := '';
    
    -- Determine appropriate role based on severity and other factors
    IF incident_record.severity = 'critical' THEN
        appropriate_role := 'manager';
        escalation_reason := 'Critical severity incident';
    ELSIF incident_record.severity = 'high' AND highest_asset_criticality = 'high' THEN
        appropriate_role := 'manager';
        escalation_reason := 'High severity incident affecting high criticality asset';
    ELSIF incident_record.severity = 'high' OR highest_threat_confidence = 'very_high' THEN
        appropriate_role := 'analyst';
        escalation_reason := 'High severity incident or very high threat confidence';
    ELSE
        appropriate_role := 'analyst';
        escalation_reason := 'Standard incident assessment';
    END IF;
    
    -- Find an appropriate user to assign (if not overridden)
    IF override_user_id IS NULL THEN
        -- Assign to a user with the appropriate role (simple round-robin approach)
        SELECT user_id INTO appropriate_user_id
        FROM public.api_user
        WHERE role = appropriate_role AND is_active = TRUE
        ORDER BY last_login NULLS FIRST
        LIMIT 1;
    ELSE
        appropriate_user_id := override_user_id;
    END IF;
    
    -- Update incident status if needed
    IF incident_record.status = 'open' AND 
       (incident_record.severity = 'critical' OR unacknowledged_alerts_count > 3) THEN
        UPDATE public.api_incident
        SET status = 'investigating', 
            assigned_to_id = appropriate_user_id
        WHERE incident_id = incident_id_param;
        
        escalation_reason := escalation_reason || ' - Auto-escalated to investigating';
    ELSIF incident_record.assigned_to_id IS NULL THEN
        UPDATE public.api_incident
        SET assigned_to_id = appropriate_user_id
        WHERE incident_id = incident_id_param;
        
        escalation_reason := escalation_reason || ' - Assigned to user';
    END IF;
    
    -- Create an audit log entry
    INSERT INTO public.user_activity_logs (
        user_id, 
        activity_type, 
        description, 
        resource_type, 
        resource_id,
        ip_address,
        timestamp
    ) VALUES (
        COALESCE(override_user_id, 1), -- System user ID 1 if no override
        'update',
        'Auto-escalation process: ' || escalation_reason,
        'incident',
        incident_id_param,
        '127.0.0.1', -- System action
        NOW()
    );
    
    -- Create a high severity alert if critical incident isn't assigned
    IF incident_record.severity = 'critical' AND incident_record.assigned_to_id IS NULL AND appropriate_user_id IS NULL THEN
        INSERT INTO public.api_alert (
            source,
            name,
            alert_type,
            severity,
            status,
            incident_id
        ) VALUES (
            'Incident Escalation System',
            'CRITICAL INCIDENT UNASSIGNED',
            'escalation',
            'critical',
            'new',
            incident_id_param
        );
    END IF;
    
    RAISE NOTICE 'Incident % processed: %', incident_id_param, escalation_reason;
END;
$$;
"""

# CALL manage_incident_escalation(123);  -- Using default system assignment
# CALL manage_incident_escalation(123, 5);  -- Manual override assigning to user ID 5


# # app/api/endpoints/incidents.py
# from ninja import Router
# from django.db import connection
# from typing import Dict
#
# router = Router()
#
#
# @router.post("/incidents/{incident_id}/escalate/", response={200: Dict, 404: Dict})
# def escalate_incident(request, incident_id: int, override_user_id: int = None):
#     """Trigger the incident escalation procedure for a specific incident."""
#     try:
#         with connection.cursor() as cursor:
#             # Call the stored procedure
#             if override_user_id:
#                 cursor.execute("CALL manage_incident_escalation(%s, %s)", [incident_id, override_user_id])
#             else:
#                 cursor.execute("CALL manage_incident_escalation(%s)", [incident_id])
#
#         return 200, {"message": f"Incident {incident_id} escalation process completed successfully"}
#     except Exception as e:
#         if "not found" in str(e):
#             return 404, {"error": str(e)}
#         return 500, {"error": str(e)}


# // src/components/incidents/IncidentEscalationButton.tsx
# // import React, { useState } from 'react';
# // import axios from 'axios';
# //
# // interface EscalationButtonProps {
# //   incidentId: number;
# //   onSuccess?: () => void;
# //   onError?: (error: string) => void;
# // }
# //
# // const IncidentEscalationButton: React.FC<EscalationButtonProps> = ({
# //   incidentId,
# //   onSuccess,
# //   onError
# // }) => {
# //   const [loading, setLoading] = useState(false);
# //   const [showManualAssign, setShowManualAssign] = useState(false);
# //   const [manualUserId, setManualUserId] = useState<number | null>(null);
# //
# //   const handleEscalate = async (overrideUserId?: number) => {
# //     setLoading(true);
# //     try {
# //       const url = `/api/incidents/${incidentId}/escalate/`;
# //       const params = overrideUserId ? { override_user_id: overrideUserId } : {};
# //
# //       await axios.post(url, params);
# //       setLoading(false);
# //       if (onSuccess) onSuccess();
# //     } catch (error) {
# //       setLoading(false);
# //       if (onError) onError(error instanceof Error ? error.message : 'Unknown error');
# //     }
# //   };
# //
# //   return (
# //     <div className="escalation-controls">
# //       <button
# //         className="escalate-btn primary"
# //         onClick={() => handleEscalate()}
# //         disabled={loading}
# //       >
# //         {loading ? "Processing..." : "Auto-Escalate Incident"}
# //       </button>
# //
# //       <button
# //         className="escalate-btn secondary"
# //         onClick={() => setShowManualAssign(!showManualAssign)}
# //         disabled={loading}
# //       >
# //         Manual Assignment
# //       </button>
# //
# //       {showManualAssign && (
# //         <div className="manual-assign-form">
# //           <input
# //             type="number"
# //             placeholder="User ID"
# //             value={manualUserId || ''}
# //             onChange={(e) => setManualUserId(parseInt(e.target.value) || null)}
# //           />
# //           <button
# //             onClick={() => manualUserId && handleEscalate(manualUserId)}
# //             disabled={!manualUserId || loading}
# //           >
# //             Assign & Escalate
# //           </button>
# //         </div>
# //       )}
# //     </div>
# //   );
# // };
# //
# // export default IncidentEscalationButton;