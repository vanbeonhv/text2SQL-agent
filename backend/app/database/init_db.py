"""Initialize databases."""
import asyncio
import json
from .history import history_manager
from .connection import history_db, target_db
from ..config import settings


async def init_history_db():
    """Initialize history database schema."""
    print("Initializing history database...")
    await history_manager.reset_database()
    print(f"✓ History database initialized at {settings.history_db_path}")


async def init_target_db():
    """Initialize target database with HR staff schema."""
    print("Initializing target database with HR staff schema...")

    # Drop old tables if they exist
    await target_db.execute("DROP TABLE IF EXISTS orders")
    await target_db.execute("DROP TABLE IF EXISTS products")

    # Create v_staff_hr_format table
    await target_db.execute("""
        CREATE TABLE IF NOT EXISTS v_staff_hr_format (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            emp_no TEXT,
            emp_name TEXT,
            alias TEXT,
            company TEXT,
            classification TEXT,
            occupation TEXT,
            category TEXT,
            section TEXT,
            division TEXT,
            cost_centre TEXT,
            cost_centre_short TEXT,
            job_level TEXT,
            hired_date DATE,
            termination_date DATE,
            termination_reason TEXT,
            remarks TEXT,
            start_of_deployment DATE,
            end_of_deployment DATE,
            next_deployment_start_date DATE,
            next_deployment_end_date DATE,
            next_deployment_site TEXT,
            next_deployment_fte TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    print(f"✓ Target database initialized at {settings.target_db_path}")


def create_example_schema():
    """Create schema.json file for the HR staff table."""
    schema = {
        "tables": [
            {
                "name": "v_staff_hr_format",
                "columns": [
                    {"name": "id", "type": "INTEGER", "primary_key": True},
                    {"name": "emp_no", "type": "TEXT", "description": "Employee ID (8-digit format)"},
                    {"name": "emp_name", "type": "TEXT", "description": "Full legal name"},
                    {"name": "alias", "type": "TEXT", "description": "Workplace nickname/common name"},
                    {"name": "company", "type": "TEXT", "description": "Legal entity name (e.g. 'Marina View Residences', 'TANGLIN CORPORATION PRIVATE LIMITED', 'WOH HUP ENGINEERING PTE. LTD.', 'WOH HUP HOLDINGS PRIVATE LIMITED', 'WOH HUP (PRIVATE) LIMITED')"},
                    {"name": "classification", "type": "TEXT", "description": "Employment type classification (e.g. 'Staff (Woh Hup)')"},
                    {"name": "occupation", "type": "TEXT", "description": "Specific job title"},
                    {"name": "category", "type": "TEXT", "description": "Functional area (WSHE, M&E, Innovation, etc.)"},
                    {"name": "section", "type": "TEXT", "description": "Sub-division (rarely used, mostly NULL)"},
                    {"name": "division", "type": "TEXT", "description": "Division: General Management & Business Innovation, Production, C&S, Contracts, M&E, Archi Technical, Site Support, Engineering, Corporate Office, QAQC, WSHE, Innovation, Maintenance, Environmental, Social, Governance, Technology, Security, Information Technology, Finance, HR"},
                    {"name": "cost_centre", "type": "TEXT", "description": "Full cost center name / project name"},
                    {"name": "cost_centre_short", "type": "TEXT", "description": "Business acronym / project short name (e.g. BB5, CFC, CPW, CR106, CRP, CTM, FJX, HLD, IWB, JCU, KCD, KG2, KHR, MVR, P105, PDD, PNG, PSR, RKD, SG6, SGK, TBC, TGW, TPY, WCE, WCP, WHH03, WHPL04, WHQ, ZRA, ZRB)"},
                    {"name": "job_level", "type": "TEXT", "description": "Hierarchy level (A=highest executive, B, C, D, E, EG1, F, G, H, I, INC1, INC2, INN2, J, JEG2, K, L, M1, M2, M3, N1, N2, NEG2, O, W30)"},
                    {"name": "hired_date", "type": "DATE", "description": "Original employment start date; ignore NULL values"},
                    {"name": "termination_date", "type": "DATE", "description": "Employment end date — NULL means currently active employee; NOT NULL means resigned"},
                    {"name": "termination_reason", "type": "TEXT"},
                    {"name": "remarks", "type": "TEXT", "description": "Additional employment notes"},
                    {"name": "start_of_deployment", "type": "DATE", "description": "Current assignment start date; NULL means not currently deployed to any project"},
                    {"name": "end_of_deployment", "type": "DATE", "description": "Current assignment end date; NULL or values 1900-01-01/1900-01-02 mean indefinite/permanent deployment"},
                    {"name": "next_deployment_start_date", "type": "DATE", "description": "Planned future assignment start date; NULL means no future deployment planned"},
                    {"name": "next_deployment_end_date", "type": "DATE", "description": "Planned future assignment end date; NULL means indefinite future deployment"},
                    {"name": "next_deployment_site", "type": "TEXT", "description": "Future assignment location/project"},
                    {"name": "next_deployment_fte", "type": "TEXT", "description": "Future full-time equivalent details"},
                    {"name": "created_at", "type": "TIMESTAMP"},
                    {"name": "updated_at", "type": "TIMESTAMP"}
                ]
            }
        ],
        "relationships": [],
        "business_context": {
            "employment_status": (
                "Active employee: termination_date IS NULL OR termination_date > CURRENT_DATE. "
                "Resigned employee: termination_date IS NOT NULL AND termination_date <= CURRENT_DATE."
            ),
            "temporal_query_patterns": (
                "EMPLOYMENT STATUS — 'Who is employed on DATE?': "
                "WHERE (termination_date IS NULL OR termination_date > DATE) AND hired_date <= DATE. "
                "\n"
                "DEPLOYMENT STATUS — 'Who is deployed/assigned on DATE?': "
                "WHERE (termination_date IS NULL OR termination_date > DATE) "
                "AND start_of_deployment <= DATE "
                "AND (end_of_deployment IS NULL OR end_of_deployment >= DATE). "
                "\n"
                "AVAILABILITY — 'Who is available/unassigned on DATE or from DATE onwards?': "
                "WHERE (termination_date IS NULL OR termination_date > DATE) "
                "AND hired_date <= DATE "
                "AND NOT ("
                "  (start_of_deployment IS NOT NULL AND start_of_deployment <= DATE AND (end_of_deployment IS NULL OR end_of_deployment >= DATE)) "
                "  OR "
                "  (next_deployment_start_date IS NOT NULL AND next_deployment_start_date <= DATE AND (next_deployment_end_date IS NULL OR next_deployment_end_date >= DATE))"
                "). "
                "Business rule: 'Available' = employed but no project assignment covering the date."
            ),
            "date_sentinel_values": (
                "end_of_deployment = '1900-01-01' or '1900-01-02' means indefinite/permanent deployment (treat as NULL). "
                "termination_date NULL = currently employed. "
                "start_of_deployment NULL = not deployed to any project. "
                "end_of_deployment NULL = indefinite deployment. "
                "next_deployment_start_date NULL = no future deployment planned."
            ),
            "cost_center_mappings": (
                "BB5=Lumina Grand, CFC=Clifford Centre, CPW=Champion Way, CR106=Woh Hup-Dongah JV, "
                "CRP=Comcentre Redevelopment Project, CTM=Central Mall, FJX=Newport Plaza, HLD=Holland Drive, "
                "HOS13=Tech BIM (C&S), HOS15=Tech BIM (MEP), IWB=Irwell Hill Residences, JCU=J'den, "
                "KCD=Contract 821A, KG2=Geras Building 2, KHR=34 Kheam Hock Road, MVR=Marina View Residence, "
                "P105=P105 Punggol Interchange & Extension, PDD=Punggol Digital District, "
                "PNG=P105 Punggol Interchange & Extension, PSR=Proposed Mixed Development at Pasir Ris Drive 3/8/Central, "
                "RKD=The Reef, SG6=Equinix Data Center, SGK=Contract 9177, TGW=Tengah Garden Walk, "
                "TPY=Toa Payoh Lorong 1, WCE=unspecified, WCP=Woodlands Checkpoint Extension (Building), "
                "WHH03=Finance, WHPL04=Security, WHQ=Woh Hup Building, ZRA=Zion Road Parcel A, ZRB=Zion Road (Parcel B)"
            ),
            "query_notes": (
                "Use CURRENT_DATE for today's date (not date('now')). "
                "For cost center queries use cost_centre_short column. "
                "Organizational hierarchy: division > category > occupation. "
                "Use cost_centre_short for project/site queries (e.g. WHERE cost_centre_short = 'PDD')."
            )
        }
    }

    with open(settings.schema_path, 'w') as f:
        json.dump(schema, f, indent=2)

    print(f"✓ Schema file created at {settings.schema_path}")


async def main():
    """Initialize all databases."""
    print("Starting database initialization...\n")

    try:
        await init_history_db()
        await init_target_db()
        create_example_schema()

        print("\n✅ All databases initialized successfully!")
        print("\nYou can now run the server with:")
        print("  uvicorn app.main:app --reload")
    finally:
        await history_db.close()
        await target_db.close()


if __name__ == "__main__":
    asyncio.run(main())
