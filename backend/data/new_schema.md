-- HR Staff Table with Business Context
CREATE TABLE public.v_staff_hr_format (
    -- Identity Fields
    id serial4 NOT NULL,
    emp_no text NULL,                    -- Employee ID (8-digit format)
    emp_name text NULL,                  -- Full legal name
    alias text NULL,                     -- Workplace nickname/common name
    
    -- Organizational Hierarchy (IMPORTANT FOR GROUPING)
    company text NULL,                   -- Legal entity name ("Marina View Residences", "TANGLIN CORPORATION PRIVATE LIMITED", "WOH HUP ENGINEERING PTE. LTD.", "WOH HUP HOLDINGS PRIVATE LIMITED", "WOH HUP (PRIVATE) LIMITED")
    classification text NULL,            -- Employment type classification ("Staff (Woh Hup)")
    occupation text NULL,                -- Specific job title
    category text NULL,                  -- Functional area (WSHE, M&E, Innovation, etc.)
    section text NULL,                   -- Sub-division (rarely used, mostly NULL)
    division text NULL,                  -- List division: (General Management & Business Innovation, Production, C&S, Contracts, M&E, Archi Technical, Site Support, Engineering, Corporate Office, QAQC, WSHE, Innovation, Maintenance, Environmental, Social, Governance, Technology, Security, Information Technology, Finance, HR)
    
    -- Cost Centers (CRITICAL FOR BUSINESS QUERIES)
    cost_centre text NULL,               -- Full cost center name, project name
    cost_centre_short text NULL,         -- Business acronym, project short name (BB5, CFC, CPW, CR106, CRP, CTM, FJX, HLD, HOS13, HOS15, HOS - Local Talent Pipeline, IWB, IWB (MAINT), JCU, KCD, KG2, KHR, MVR, P105, PDD, PDD (MAINT), PNG, PSR, RKD, RKD (MAINT), SG6, SGK, TBC, TGW, TPY, WCE, WCP, WHH03, WHPL04, WHQ, ZRA, ZRB)
    
    -- Employment Details
    job_level text NULL,                 -- Hierarchy level (A=highest executive,B,C,D,E,EG1,F,G,H,I,INC1,INC2,INN2,J,JEG2,K,L,M1,M2,M3,N1,N2,NEG2,O,W30)
    hired_date date NULL,                -- Original employment start date, ignore NULL value
    termination_date date NULL,          -- Employment end date (NULL=currently active employee, not NULL = Resigned)
    termination_reason text NULL,        
    remarks text NULL,                   -- Additional employment notes
    
    -- Current Deployment Information
    start_of_deployment date NULL,       -- Current assignment start date
    end_of_deployment date NULL,         -- Current assignment end date (1900-01-01 or 1900-01-02 = indefinite/permanent)
    
    -- Future Deployment Planning
    next_deployment_start_date date NULL, -- Planned future assignment start
    next_deployment_end_date date NULL,  -- Planned future assignment end
    next_deployment_site text NULL,      -- Future assignment location/project
    next_deployment_fte text NULL,       -- Future full-time equivalent details
    
    -- System Fields
    created_at timestamp DEFAULT CURRENT_TIMESTAMP NULL,
    updated_at timestamp DEFAULT CURRENT_TIMESTAMP NULL,
    CONSTRAINT hr_staff_pkey PRIMARY KEY (id)
);

-- ============================================================================
-- TEMPORAL QUERY PATTERNS (CRITICAL FOR DATE-BASED QUERIES)
-- ============================================================================

-- EMPLOYMENT STATUS QUERIES:
-- "Who is employed on DATE?"
--   WHERE (termination_date IS NULL OR termination_date > DATE)
--     AND hired_date <= DATE

-- DEPLOYMENT STATUS QUERIES:
-- "Who is deployed/assigned on DATE?" (has active project assignment)
--   WHERE (termination_date IS NULL OR termination_date > DATE)
--     AND start_of_deployment <= DATE
--     AND (end_of_deployment IS NULL OR end_of_deployment >= DATE)

-- AVAILABILITY QUERIES (NOT ASSIGNED TO ANY PROJECT):
-- "Who is available/unassigned on DATE?" or "from DATE onwards"
--   WHERE (termination_date IS NULL OR termination_date > DATE)
--     AND hired_date <= DATE
--     AND NOT (
--       -- Not in current deployment
--       (start_of_deployment IS NOT NULL
--        AND start_of_deployment <= DATE 
--        AND (end_of_deployment IS NULL OR end_of_deployment >= DATE))
--       OR
--       -- Not in future deployment
--       (next_deployment_start_date IS NOT NULL 
--        AND next_deployment_start_date <= DATE
--        AND (next_deployment_end_date IS NULL OR next_deployment_end_date >= DATE))
--     )
--   BUSINESS RULE: "Available" = employed but no project assignment covering the date

-- ============================================================================
-- DATE SENTINEL VALUES & EDGE CASES
-- ============================================================================

-- NULL Date Values Mean:
--   - termination_date NULL = currently employed (active employee)
--   - start_of_deployment NULL = employee not currently deployed to any project
--   - end_of_deployment NULL = indefinite/permanent deployment (no planned end)
--   - next_deployment_start_date NULL = no future deployment planned yet
--   - next_deployment_end_date NULL = future deployment is indefinite

-- Data Quality Checks:
--   - start_of_deployment should not be NULL if end_of_deployment has value
--   - If employee has next_deployment_start_date, they should have next_deployment_site
--   - Logical: hired_date <= start_of_deployment
--   - Logical: end_of_deployment < next_deployment_start_date (no overlap)

-- ============================================================================
-- BUSINESS CONTEXT
-- ============================================================================
-- Cost Center Mappings (use cost_centre_short column):
-- - BB5: Lumina Grand
-- - CFC: Clifford Centre
-- - CPW: Champion Way
-- - CR106: Woh Hup-Dongah JV (CR106)
-- - CRP: Comcentre Redevelopment Project
-- - CTM: Central Mall
-- - FJX: Newport Plaza
-- - HLD: Holland Drive
-- - HOS13: Tech BIM (C&S)
-- - HOS15: Tech BIM (MEP)
-- - HOS - Local Talent Pipeline: (cost_centre not specified)
-- - IWB: Irwell Hill Residences
-- - IWB (MAINT): (cost_centre not specified)
-- - JCU: J'den
-- - KCD: Contract 821A
-- - KG2: Geras Building 2
-- - KHR: 34 Kheam Hock Road
-- - MVR: Marina View Residence
-- - P105: P105 Punggol Interchange & Extension
-- - PDD: Punggol Digital District
-- - PNG: P105 Punggol Interchange & Extension
-- - PSR: Proposed Mixed Development at Pasir Ris Drive 3/8/Central
-- - RKD: The Reef
-- - RKD (MAINT): (cost_centre not specified)
-- - SG6: Equinix Data Center
-- - SGK: Contract 9177
-- - TBC: (cost_centre not specified)
-- - TGW: Tengah Garden Walk
-- - TPY: Toa Payoh Lorong 1
-- - WCE: (cost_centre not specified)
-- - WCP: Woodlands Checkpoint Extension (Building)
-- - WHH03: Finance
-- - WHPL04: Security
-- - WHQ: Woh Hup Building
-- - ZRA: Zion Road Parcel A
-- - ZRB: Zion Road (Parcel B)

-- Business Rules:
-- - Active employees: termination_date IS NULL OR termination_date > CURRENT_DATE
-- - Use CURRENT_DATE instead of date('now') for PostgreSQL
-- - Projects/Sites referenced in: department, next_deployment_site columns

-- Query Patterns:
-- - For cost center queries: WHERE cost_centre_short = 'ACRONYM'
-- - For organizational breakdown: division > category > occupation hierarchy