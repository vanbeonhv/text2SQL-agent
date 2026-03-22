"""Seed 100 realistic HR staff rows into target.db."""
import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "target.db")

rows = [
    # (emp_no, emp_name, alias, company, classification, occupation, category, section, division,
    #  cost_centre, cost_centre_short, job_level, hired_date, termination_date, termination_reason,
    #  remarks, start_of_deployment, end_of_deployment,
    #  next_deployment_start_date, next_deployment_end_date, next_deployment_site, next_deployment_fte)

    # --- Active employees, various projects ---
    ("10000001", "Tan Wei Ming", "Wei Ming", "WOH HUP (PRIVATE) LIMITED", "Staff (Woh Hup)",
     "Project Manager", "Production", None, "Production",
     "Punggol Digital District", "PDD", "D",
     "2020-03-15", None, None, None,
     "2025-01-05", None, None, None, None, None),

    ("10000002", "Lee Hui Ling", "Hui Ling", "WOH HUP (PRIVATE) LIMITED", "Staff (Woh Hup)",
     "Senior Engineer", "Engineering", None, "Engineering",
     "Zion Road Parcel A", "ZRA", "E",
     "2019-06-01", None, None, None,
     "2025-02-01", "2026-06-30", None, None, None, None),

    ("10000003", "Ng Boon Huat", "Boon Huat", "WOH HUP ENGINEERING PTE. LTD.", "Staff (Woh Hup)",
     "M&E Engineer", "M&E", None, "M&E",
     "Tengah Garden Walk", "TGW", "F",
     "2021-08-10", None, None, None,
     "2025-03-01", "2026-12-31", None, None, None, None),

    ("10000004", "Siti Rahimah Binte Yusof", "Rahimah", "WOH HUP (PRIVATE) LIMITED", "Staff (Woh Hup)",
     "Safety Officer", "WSHE", None, "WSHE",
     "Toa Payoh Lorong 1", "TPY", "G",
     "2022-01-10", None, None, None,
     "2025-01-15", "2026-09-30", None, None, None, None),

    ("10000005", "Muhammad Faizal Bin Othman", "Faizal", "WOH HUP (PRIVATE) LIMITED", "Staff (Woh Hup)",
     "Quantity Surveyor", "Contracts", None, "Contracts",
     "Zion Road (Parcel B)", "ZRB", "F",
     "2023-04-03", None, None, None,
     "2025-04-01", "2027-03-31", None, None, None, None),

    ("10000006", "Chen Jia Yi", "Jia Yi", "WOH HUP (PRIVATE) LIMITED", "Staff (Woh Hup)",
     "BIM Coordinator", "Innovation", None, "Innovation",
     "Tech BIM (C&S)", "HOS13", "H",
     "2022-07-18", None, None, None,
     "2025-01-02", None, None, None, None, None),

    ("10000007", "Rajesh Kumar s/o Subramaniam", "Rajesh", "WOH HUP ENGINEERING PTE. LTD.", "Staff (Woh Hup)",
     "Electrical Engineer", "M&E", None, "M&E",
     "Woodlands Checkpoint Extension (Building)", "WCP", "E",
     "2018-11-22", None, None, None,
     "2025-02-15", "2026-08-31", None, None, None, None),

    ("10000008", "Lim Pei Shan", "Pei Shan", "WOH HUP HOLDINGS PRIVATE LIMITED", "Staff (Woh Hup)",
     "HR Executive", "HR", None, "HR",
     "Woh Hup Building", "WHQ", "G",
     "2023-09-01", None, None, None,
     "2025-09-01", None, None, None, None, None),

    ("10000009", "Goh Swee Leng", "Swee Leng", "WOH HUP (PRIVATE) LIMITED", "Staff (Woh Hup)",
     "Structural Engineer", "C&S", None, "C&S",
     "Holland Drive", "HLD", "E",
     "2021-05-17", None, None, None,
     "2025-03-15", "2026-11-30", None, None, None, None),

    ("10000010", "Nurul Ain Binte Hamzah", "Ain", "WOH HUP (PRIVATE) LIMITED", "Staff (Woh Hup)",
     "Environmental Officer", "Environmental", None, "Environmental",
     "Punggol Digital District", "PDD", "H",
     "2024-01-08", None, None, None,
     "2025-01-08", "2026-12-31", None, None, None, None),

    ("10000011", "Wong Kok Wai", "Kok Wai", "WOH HUP (PRIVATE) LIMITED", "Staff (Woh Hup)",
     "Project Director", "Production", None, "Production",
     "Marina View Residence", "MVR", "B",
     "2015-03-01", None, None, None,
     "2025-01-01", "2026-06-30", None, None, "ZRA", "100%"),

    ("10000012", "Priya d/o Krishnan", "Priya", "TANGLIN CORPORATION PRIVATE LIMITED", "Staff (Woh Hup)",
     "Finance Manager", "Finance", None, "Finance",
     "Finance", "WHH03", "D",
     "2017-09-14", None, None, None,
     "2025-01-01", None, None, None, None, None),

    ("10000013", "Chua Beng Chuan", "Beng Chuan", "WOH HUP (PRIVATE) LIMITED", "Staff (Woh Hup)",
     "QAQC Engineer", "QAQC", None, "QAQC",
     "Lumina Grand", "BB5", "F",
     "2020-10-05", None, None, None,
     "2025-02-01", "2026-05-31", None, None, None, None),

    ("10000014", "Yeo Hui Fen", "Hui Fen", "WOH HUP (PRIVATE) LIMITED", "Staff (Woh Hup)",
     "Site Engineer", "Engineering", None, "Engineering",
     "Irwell Hill Residences", "IWB", "H",
     "2022-03-28", None, None, None,
     "2025-03-28", "2025-12-31", None, None, "ZRB", "100%"),

    ("10000015", "Tan Ah Kow", "Ah Kow", "WOH HUP (PRIVATE) LIMITED", "Staff (Woh Hup)",
     "Senior Foreman", "Site Support", None, "Site Support",
     "The Reef", "RKD", "I",
     "2010-06-15", None, None, None,
     "2025-01-01", None, None, None, None, None),

    ("10000016", "Mdm Fatimah Binte Hassan", "Fatimah", "WOH HUP (PRIVATE) LIMITED", "Staff (Woh Hup)",
     "Admin Executive", "Corporate Office", None, "Corporate Office",
     "Woh Hup Building", "WHQ", "I",
     "2016-02-01", None, None, None,
     "2025-01-01", None, None, None, None, None),

    ("10000017", "Loh Chin Siong", "Chin Siong", "WOH HUP ENGINEERING PTE. LTD.", "Staff (Woh Hup)",
     "Mechanical Engineer", "M&E", None, "M&E",
     "Tech BIM (MEP)", "HOS15", "F",
     "2023-07-03", None, None, None,
     "2025-07-03", None, None, None, None, None),

    ("10000018", "Tan Jing Jie", "Jing Jie", "WOH HUP (PRIVATE) LIMITED", "Staff (Woh Hup)",
     "Innovation Specialist", "Innovation", None, "Innovation",
     "Woh Hup Building", "WHQ", "G",
     "2024-06-01", None, None, None,
     "2025-06-01", None, None, None, None, None),

    ("10000019", "Koh Sheng Wei", "Sheng Wei", "WOH HUP (PRIVATE) LIMITED", "Staff (Woh Hup)",
     "Contracts Manager", "Contracts", None, "Contracts",
     "Clifford Centre", "CFC", "D",
     "2019-01-07", None, None, None,
     "2025-01-07", "2026-03-31", None, None, None, None),

    ("10000020", "Ong Li Ting", "Li Ting", "WOH HUP HOLDINGS PRIVATE LIMITED", "Staff (Woh Hup)",
     "IT Executive", "Technology", None, "Information Technology",
     "Woh Hup Building", "WHQ", "H",
     "2023-11-20", None, None, None,
     "2025-01-01", None, None, None, None, None),

    ("10000021", "Abdul Hamid Bin Salleh", "Hamid", "WOH HUP (PRIVATE) LIMITED", "Staff (Woh Hup)",
     "Senior Project Manager", "Production", None, "Production",
     "Equinix Data Center", "SG6", "C",
     "2013-04-22", None, None, None,
     "2025-01-10", "2026-10-31", None, None, None, None),

    ("10000022", "Tan Mei Xian", "Mei Xian", "WOH HUP (PRIVATE) LIMITED", "Staff (Woh Hup)",
     "Architect", "Archi Technical", None, "Archi Technical",
     "Champion Way", "CPW", "E",
     "2021-09-13", None, None, None,
     "2025-02-01", "2026-08-31", None, None, None, None),

    ("10000023", "Lim Wei Jian", "Wei Jian", "WOH HUP (PRIVATE) LIMITED", "Staff (Woh Hup)",
     "Safety Manager", "WSHE", None, "WSHE",
     "Geras Building 2", "KG2", "E",
     "2020-12-01", None, None, None,
     "2025-02-15", "2026-07-31", None, None, None, None),

    ("10000024", "Nabilah Binte Razali", "Nabilah", "WOH HUP (PRIVATE) LIMITED", "Staff (Woh Hup)",
     "HR Manager", "HR", None, "HR",
     "Woh Hup Building", "WHQ", "D",
     "2018-08-06", None, None, None,
     "2025-01-01", None, None, None, None, None),

    ("10000025", "Chong Kah Mun", "Kah Mun", "WOH HUP (PRIVATE) LIMITED", "Staff (Woh Hup)",
     "Quantity Surveyor", "Contracts", None, "Contracts",
     "Comcentre Redevelopment Project", "CRP", "G",
     "2022-05-09", None, None, None,
     "2025-03-01", "2027-06-30", None, None, None, None),

    ("10000026", "Kevin Tan Wei Liang", "Kevin", "WOH HUP (PRIVATE) LIMITED", "Staff (Woh Hup)",
     "Civil Engineer", "Engineering", None, "Engineering",
     "Woh Hup-Dongah JV (CR106)", "CR106", "F",
     "2023-02-14", None, None, None,
     "2025-02-14", "2027-01-31", None, None, None, None),

    ("10000027", "Yap Soo Bee", "Soo Bee", "WOH HUP (PRIVATE) LIMITED", "Staff (Woh Hup)",
     "General Manager", "General Management & Business Innovation", None,
     "General Management & Business Innovation",
     "Woh Hup Building", "WHQ", "A",
     "2008-01-02", None, None, None,
     "2025-01-01", None, None, None, None, None),

    ("10000028", "Toh Zi Xuan", "Zi Xuan", "WOH HUP ENGINEERING PTE. LTD.", "Staff (Woh Hup)",
     "Electrical Technician", "M&E", None, "M&E",
     "Tengah Garden Walk", "TGW", "J",
     "2025-01-06", None, None, None,
     "2025-01-06", "2026-12-31", None, None, None, None),

    ("10000029", "Mohamad Rizal Bin Ismail", "Rizal", "WOH HUP (PRIVATE) LIMITED", "Staff (Woh Hup)",
     "QAQC Manager", "QAQC", None, "QAQC",
     "34 Kheam Hock Road", "KHR", "D",
     "2016-07-11", None, None, None,
     "2025-01-11", "2026-04-30", None, None, None, None),

    ("10000030", "Grace Lim Xiao Hui", "Grace", "WOH HUP HOLDINGS PRIVATE LIMITED", "Staff (Woh Hup)",
     "IT Systems Analyst", "Technology", None, "Information Technology",
     "Woh Hup Building", "WHQ", "G",
     "2024-03-18", None, None, None,
     "2025-03-18", None, None, None, None, None),

    # --- Employees finishing current deployment, with next deployment planned ---
    ("10000031", "Bernard Lim Teck Kiang", "Bernard", "WOH HUP (PRIVATE) LIMITED", "Staff (Woh Hup)",
     "Project Engineer", "Engineering", None, "Engineering",
     "Newport Plaza", "FJX", "G",
     "2022-10-03", None, None, None,
     "2024-06-01", "2025-06-30", "2025-07-01", "2026-12-31", "Zion Road Parcel A", "100%"),

    ("10000032", "Ho Suet Ying", "Suet Ying", "WOH HUP (PRIVATE) LIMITED", "Staff (Woh Hup)",
     "M&E Coordinator", "M&E", None, "M&E",
     "Irwell Hill Residences", "IWB", "H",
     "2023-06-19", None, None, None,
     "2024-07-01", "2025-09-30", "2025-10-01", "2027-03-31", "Tengah Garden Walk", "100%"),

    ("10000033", "Sim Jing Wen", "Jing Wen", "WOH HUP (PRIVATE) LIMITED", "Staff (Woh Hup)",
     "Safety Coordinator", "WSHE", None, "WSHE",
     "J'den", "JCU", "H",
     "2024-02-26", None, None, None,
     "2024-03-01", "2025-07-31", "2025-08-01", "2026-09-30", "Holland Drive", "100%"),

    ("10000034", "Ang Bak Chuan", "Bak Chuan", "WOH HUP (PRIVATE) LIMITED", "Staff (Woh Hup)",
     "Structural Engineer", "C&S", None, "C&S",
     "Proposed Mixed Development at Pasir Ris Drive 3/8/Central", "PSR", "E",
     "2020-08-03", None, None, None,
     "2024-08-03", "2025-12-31", "2026-01-01", "2027-06-30", "Champion Way", "100%"),

    # --- Available employees (no deployment) ---
    ("10000035", "Melissa Tan Hui Ying", "Melissa", "WOH HUP (PRIVATE) LIMITED", "Staff (Woh Hup)",
     "Environmental Specialist", "Environmental", None, "Environmental",
     "Woh Hup Building", "WHQ", "G",
     "2025-01-13", None, None, None,
     None, None, None, None, None, None),

    ("10000036", "Rajan s/o Pillai", "Rajan", "WOH HUP ENGINEERING PTE. LTD.", "Staff (Woh Hup)",
     "Mechanical Technician", "M&E", None, "M&E",
     "Woh Hup Building", "WHQ", "K",
     "2025-02-03", None, None, None,
     None, None, None, None, None, None),

    ("10000037", "Chua Poh Lin", "Poh Lin", "WOH HUP (PRIVATE) LIMITED", "Staff (Woh Hup)",
     "Procurement Executive", "Corporate Office", None, "Corporate Office",
     "Woh Hup Building", "WHQ", "H",
     "2025-03-10", None, None, None,
     None, None, "2025-07-01", "2026-06-30", "Lumina Grand", "100%"),

    # --- Resigned employees ---
    ("10000038", "Tan Chin Nam", "Chin Nam", "WOH HUP (PRIVATE) LIMITED", "Staff (Woh Hup)",
     "Site Supervisor", "Site Support", None, "Site Support",
     "Contract 821A", "KCD", "I",
     "2019-03-04", "2025-02-28", "Resignation", None,
     "2022-01-01", "2025-02-28", None, None, None, None),

    ("10000039", "Liew Sze Yin", "Sze Yin", "WOH HUP (PRIVATE) LIMITED", "Staff (Woh Hup)",
     "HR Officer", "HR", None, "HR",
     "Woh Hup Building", "WHQ", "H",
     "2021-11-15", "2025-04-30", "Resignation", None,
     "2022-01-01", "2025-04-30", None, None, None, None),

    ("10000040", "Darren Koh Wei Bin", "Darren", "WOH HUP HOLDINGS PRIVATE LIMITED", "Staff (Woh Hup)",
     "Software Developer", "Technology", None, "Information Technology",
     "Woh Hup Building", "WHQ", "G",
     "2023-05-22", "2025-01-31", "End of Contract", None,
     "2023-05-22", "2025-01-31", None, None, None, None),

    # --- More active project staff ---
    ("10000041", "Pang Ah Lim", "Ah Lim", "WOH HUP (PRIVATE) LIMITED", "Staff (Woh Hup)",
     "Senior Site Engineer", "Engineering", None, "Engineering",
     "P105 Punggol Interchange & Extension", "P105", "E",
     "2017-06-26", None, None, None,
     "2025-01-20", "2026-12-31", None, None, None, None),

    ("10000042", "Jennifer Wong Mei Lin", "Jennifer", "Marina View Residences", "Staff (Woh Hup)",
     "Project Coordinator", "Production", None, "Production",
     "Marina View Residence", "MVR", "G",
     "2024-04-01", None, None, None,
     "2025-04-01", "2026-12-31", None, None, None, None),

    ("10000043", "Lau Chin Hock", "Chin Hock", "WOH HUP (PRIVATE) LIMITED", "Staff (Woh Hup)",
     "Maintenance Engineer", "Maintenance", None, "Maintenance",
     "Irwell Hill Residences", "IWB (MAINT)", "F",
     "2018-02-12", None, None, None,
     "2025-01-01", None, None, None, None, None),

    ("10000044", "Soh Bee Lay", "Bee Lay", "WOH HUP (PRIVATE) LIMITED", "Staff (Woh Hup)",
     "Security Officer", "Security", None, "Security",
     "Security", "WHPL04", "J",
     "2022-08-30", None, None, None,
     "2025-01-01", None, None, None, None, None),

    ("10000045", "Lim Jia Qi", "Jia Qi", "WOH HUP (PRIVATE) LIMITED", "Staff (Woh Hup)",
     "Governance Analyst", "Governance", None, "Governance",
     "Woh Hup Building", "WHQ", "G",
     "2025-01-27", None, None, None,
     "2025-01-27", None, None, None, None, None),

    ("10000046", "Ng Wei Ren", "Wei Ren", "WOH HUP (PRIVATE) LIMITED", "Staff (Woh Hup)",
     "Contracts Engineer", "Contracts", None, "Contracts",
     "Contract 9177", "SGK", "F",
     "2023-09-11", None, None, None,
     "2025-02-01", "2026-08-31", None, None, None, None),

    ("10000047", "Tan Ah Boon", "Ah Boon", "WOH HUP (PRIVATE) LIMITED", "Staff (Woh Hup)",
     "Social Manager", "Social", None, "Social",
     "Woh Hup Building", "WHQ", "E",
     "2021-03-08", None, None, None,
     "2025-01-01", None, None, None, None, None),

    ("10000048", "Rajeswari d/o Nair", "Rajes", "TANGLIN CORPORATION PRIVATE LIMITED", "Staff (Woh Hup)",
     "Accountant", "Finance", None, "Finance",
     "Finance", "WHH03", "F",
     "2019-10-21", None, None, None,
     "2025-01-01", None, None, None, None, None),

    ("10000049", "Shaun Teo Jian Ming", "Shaun", "WOH HUP (PRIVATE) LIMITED", "Staff (Woh Hup)",
     "BIM Manager", "Innovation", None, "Innovation",
     "Tech BIM (C&S)", "HOS13", "E",
     "2020-04-06", None, None, None,
     "2025-04-06", None, None, None, None, None),

    ("10000050", "Isabelle Chan Wei Qing", "Isabelle", "WOH HUP HOLDINGS PRIVATE LIMITED", "Staff (Woh Hup)",
     "Data Analyst", "Technology", None, "Information Technology",
     "Woh Hup Building", "WHQ", "G",
     "2025-06-02", None, None, None,
     "2025-06-02", None, None, None, None, None),

    # --- Rows 51–100 ---

    ("10000051", "Chia Boon Leong", "Boon Leong", "WOH HUP (PRIVATE) LIMITED", "Staff (Woh Hup)",
     "Senior Quantity Surveyor", "Contracts", None, "Contracts",
     "Zion Road Parcel A", "ZRA", "E",
     "2016-04-11", None, None, None,
     "2025-01-11", "2026-12-31", None, None, None, None),

    ("10000052", "Suriani Binte Mahmood", "Suriani", "WOH HUP (PRIVATE) LIMITED", "Staff (Woh Hup)",
     "WSHE Executive", "WSHE", None, "WSHE",
     "Toa Payoh Lorong 1", "TPY", "H",
     "2023-03-27", None, None, None,
     "2025-03-27", "2026-09-30", None, None, None, None),

    ("10000053", "Png Chee Wee", "Chee Wee", "WOH HUP (PRIVATE) LIMITED", "Staff (Woh Hup)",
     "Planning Engineer", "Engineering", None, "Engineering",
     "Zion Road (Parcel B)", "ZRB", "F",
     "2022-11-07", None, None, None,
     "2025-01-07", "2027-06-30", None, None, None, None),

    ("10000054", "Tay Li Xin", "Li Xin", "WOH HUP (PRIVATE) LIMITED", "Staff (Woh Hup)",
     "Assistant Engineer", "Engineering", None, "Engineering",
     "Holland Drive", "HLD", "H",
     "2025-01-20", None, None, None,
     "2025-01-20", "2026-06-30", None, None, None, None),

    ("10000055", "Mariam Binte Johari", "Mariam", "WOH HUP (PRIVATE) LIMITED", "Staff (Woh Hup)",
     "HR Assistant", "HR", None, "HR",
     "Woh Hup Building", "WHQ", "J",
     "2024-08-19", None, None, None,
     "2025-01-01", None, None, None, None, None),

    ("10000056", "Low Weng Kit", "Weng Kit", "WOH HUP (PRIVATE) LIMITED", "Staff (Woh Hup)",
     "Senior Structural Engineer", "C&S", None, "C&S",
     "Tengah Garden Walk", "TGW", "E",
     "2018-05-14", None, None, None,
     "2025-01-14", "2027-03-31", None, None, None, None),

    ("10000057", "Alicia Yeo Siew Hwee", "Alicia", "WOH HUP HOLDINGS PRIVATE LIMITED", "Staff (Woh Hup)",
     "Finance Executive", "Finance", None, "Finance",
     "Finance", "WHH03", "G",
     "2021-10-04", None, None, None,
     "2025-01-01", None, None, None, None, None),

    ("10000058", "Lim Kok Seng", "Kok Seng", "WOH HUP (PRIVATE) LIMITED", "Staff (Woh Hup)",
     "Site Manager", "Production", None, "Production",
     "Lumina Grand", "BB5", "E",
     "2014-09-08", None, None, None,
     "2025-02-01", "2026-03-31", None, None, None, None),

    ("10000059", "Hairul Nizam Bin Ramli", "Hairul", "WOH HUP (PRIVATE) LIMITED", "Staff (Woh Hup)",
     "M&E Supervisor", "M&E", None, "M&E",
     "Woodlands Checkpoint Extension (Building)", "WCP", "I",
     "2020-06-22", None, None, None,
     "2025-02-22", "2026-11-30", None, None, None, None),

    ("10000060", "Patricia Seah Mei Fong", "Patricia", "TANGLIN CORPORATION PRIVATE LIMITED", "Staff (Woh Hup)",
     "Senior Accountant", "Finance", None, "Finance",
     "Finance", "WHH03", "E",
     "2015-02-02", None, None, None,
     "2025-01-01", None, None, None, None, None),

    ("10000061", "Yong Wen Hao", "Wen Hao", "WOH HUP (PRIVATE) LIMITED", "Staff (Woh Hup)",
     "Project Engineer", "Engineering", None, "Engineering",
     "Marina View Residence", "MVR", "G",
     "2024-07-15", None, None, None,
     "2025-07-15", "2027-06-30", None, None, None, None),

    ("10000062", "Nor Amirah Binte Roslan", "Amirah", "WOH HUP (PRIVATE) LIMITED", "Staff (Woh Hup)",
     "Safety Officer", "WSHE", None, "WSHE",
     "Equinix Data Center", "SG6", "H",
     "2023-05-08", None, None, None,
     "2025-05-08", "2026-12-31", None, None, None, None),

    ("10000063", "Tan Boon Peng", "Boon Peng", "WOH HUP (PRIVATE) LIMITED", "Staff (Woh Hup)",
     "Senior QAQC Engineer", "QAQC", None, "QAQC",
     "Champion Way", "CPW", "E",
     "2019-07-29", None, None, None,
     "2025-01-29", "2026-08-31", None, None, None, None),

    ("10000064", "Gao Jing", "Jing", "WOH HUP (PRIVATE) LIMITED", "Staff (Woh Hup)",
     "Structural Technician", "C&S", None, "C&S",
     "P105 Punggol Interchange & Extension", "P105", "J",
     "2025-02-17", None, None, None,
     "2025-02-17", "2026-12-31", None, None, None, None),

    ("10000065", "Azman Bin Talib", "Azman", "WOH HUP (PRIVATE) LIMITED", "Staff (Woh Hup)",
     "Senior Safety Manager", "WSHE", None, "WSHE",
     "Punggol Digital District", "PDD", "D",
     "2012-08-01", None, None, None,
     "2025-01-01", "2026-06-30", None, None, None, None),

    ("10000066", "Rachel Koh Pei Yi", "Rachel", "WOH HUP HOLDINGS PRIVATE LIMITED", "Staff (Woh Hup)",
     "Business Analyst", "Technology", None, "Information Technology",
     "Woh Hup Building", "WHQ", "G",
     "2024-11-11", None, None, None,
     "2025-01-01", None, None, None, None, None),

    ("10000067", "Huang Zhi Wei", "Zhi Wei", "WOH HUP (PRIVATE) LIMITED", "Staff (Woh Hup)",
     "Civil Engineer", "Engineering", None, "Engineering",
     "Contract 9177", "SGK", "F",
     "2022-04-25", None, None, None,
     "2025-01-25", "2026-09-30", None, None, None, None),

    ("10000068", "Lim Shu Fen", "Shu Fen", "WOH HUP (PRIVATE) LIMITED", "Staff (Woh Hup)",
     "Architect", "Archi Technical", None, "Archi Technical",
     "Irwell Hill Residences", "IWB", "F",
     "2021-06-14", None, None, None,
     "2025-01-14", "2025-12-31", "2026-01-01", "2027-06-30", "Zion Road Parcel A", "100%"),

    ("10000069", "Vikram s/o Chandran", "Vikram", "WOH HUP ENGINEERING PTE. LTD.", "Staff (Woh Hup)",
     "Mechanical Engineer", "M&E", None, "M&E",
     "Comcentre Redevelopment Project", "CRP", "F",
     "2023-10-02", None, None, None,
     "2025-01-02", "2027-03-31", None, None, None, None),

    ("10000070", "Chew Mei Ling", "Mei Ling", "WOH HUP (PRIVATE) LIMITED", "Staff (Woh Hup)",
     "Contracts Executive", "Contracts", None, "Contracts",
     "J'den", "JCU", "H",
     "2024-01-22", None, None, None,
     "2025-01-22", "2026-06-30", None, None, None, None),

    # --- More with next deployment planned ---
    ("10000071", "Foo Keng Huat", "Keng Huat", "WOH HUP (PRIVATE) LIMITED", "Staff (Woh Hup)",
     "Senior Civil Engineer", "Engineering", None, "Engineering",
     "Geras Building 2", "KG2", "E",
     "2018-03-19", None, None, None,
     "2024-04-01", "2025-08-31", "2025-09-01", "2027-02-28", "Tengah Garden Walk", "100%"),

    ("10000072", "Nurul Hidayah Binte Sulaiman", "Hidayah", "WOH HUP (PRIVATE) LIMITED", "Staff (Woh Hup)",
     "Environmental Executive", "Environmental", None, "Environmental",
     "34 Kheam Hock Road", "KHR", "H",
     "2023-08-28", None, None, None,
     "2024-09-01", "2025-10-31", "2025-11-01", "2027-06-30", "Punggol Digital District", "100%"),

    ("10000073", "Seah Chuan Kheng", "Chuan Kheng", "WOH HUP (PRIVATE) LIMITED", "Staff (Woh Hup)",
     "Project Manager", "Production", None, "Production",
     "Woh Hup-Dongah JV (CR106)", "CR106", "D",
     "2017-11-13", None, None, None,
     "2024-11-13", "2026-03-31", "2026-04-01", None, "ZRA", "100%"),

    ("10000074", "Lin Jing Yuan", "Jing Yuan", "WOH HUP (PRIVATE) LIMITED", "Staff (Woh Hup)",
     "Quantity Surveyor", "Contracts", None, "Contracts",
     "Proposed Mixed Development at Pasir Ris Drive 3/8/Central", "PSR", "G",
     "2024-05-06", None, None, None,
     "2024-05-06", "2025-11-30", "2025-12-01", "2027-06-30", "Champion Way", "100%"),

    # --- Available (no current deployment), future planned ---
    ("10000075", "Irene Teo Hwee Leng", "Irene", "WOH HUP (PRIVATE) LIMITED", "Staff (Woh Hup)",
     "Planning Manager", "Engineering", None, "Engineering",
     "Woh Hup Building", "WHQ", "E",
     "2025-04-14", None, None, None,
     None, None, "2025-08-01", "2027-03-31", "Zion Road (Parcel B)", "100%"),

    ("10000076", "Mohammad Firdaus Bin Hamid", "Firdaus", "WOH HUP (PRIVATE) LIMITED", "Staff (Woh Hup)",
     "Safety Coordinator", "WSHE", None, "WSHE",
     "Woh Hup Building", "WHQ", "I",
     "2025-05-05", None, None, None,
     None, None, "2025-09-01", "2026-12-31", "Lumina Grand", "100%"),

    # --- Available, no deployment at all ---
    ("10000077", "Chan Kok Leong", "Kok Leong", "WOH HUP (PRIVATE) LIMITED", "Staff (Woh Hup)",
     "QAQC Technician", "QAQC", None, "QAQC",
     "Woh Hup Building", "WHQ", "K",
     "2025-03-31", None, None, None,
     None, None, None, None, None, None),

    ("10000078", "Ng Siew Kuan", "Siew Kuan", "WOH HUP HOLDINGS PRIVATE LIMITED", "Staff (Woh Hup)",
     "Admin Officer", "Corporate Office", None, "Corporate Office",
     "Woh Hup Building", "WHQ", "J",
     "2025-02-24", None, None, None,
     None, None, None, None, None, None),

    # --- More active project staff ---
    ("10000079", "Tan Chwee Hock", "Chwee Hock", "WOH HUP (PRIVATE) LIMITED", "Staff (Woh Hup)",
     "Senior Foreman", "Site Support", None, "Site Support",
     "Lumina Grand", "BB5", "I",
     "2011-07-04", None, None, None,
     "2025-02-01", "2026-03-31", None, None, None, None),

    ("10000080", "Kwan Yee Lin", "Yee Lin", "WOH HUP (PRIVATE) LIMITED", "Staff (Woh Hup)",
     "Senior Contracts Manager", "Contracts", None, "Contracts",
     "Marina View Residence", "MVR", "C",
     "2010-10-18", None, None, None,
     "2025-01-18", "2026-12-31", None, None, None, None),

    ("10000081", "Ahmad Fadzli Bin Nordin", "Fadzli", "WOH HUP (PRIVATE) LIMITED", "Staff (Woh Hup)",
     "Maintenance Technician", "Maintenance", None, "Maintenance",
     "The Reef", "RKD (MAINT)", "K",
     "2019-04-30", None, None, None,
     "2025-01-01", None, None, None, None, None),

    ("10000082", "Josephine Tan Bee Kuan", "Josephine", "TANGLIN CORPORATION PRIVATE LIMITED", "Staff (Woh Hup)",
     "Payroll Executive", "Finance", None, "Finance",
     "Finance", "WHH03", "G",
     "2020-09-07", None, None, None,
     "2025-01-01", None, None, None, None, None),

    ("10000083", "Xavier Ong Wei Sheng", "Xavier", "WOH HUP (PRIVATE) LIMITED", "Staff (Woh Hup)",
     "BIM Engineer", "Innovation", None, "Innovation",
     "Tech BIM (MEP)", "HOS15", "G",
     "2024-09-16", None, None, None,
     "2025-01-01", None, None, None, None, None),

    ("10000084", "Lim Ai Ling", "Ai Ling", "WOH HUP (PRIVATE) LIMITED", "Staff (Woh Hup)",
     "Site Engineer", "Engineering", None, "Engineering",
     "Clifford Centre", "CFC", "H",
     "2023-12-01", None, None, None,
     "2025-01-01", "2026-06-30", None, None, None, None),

    ("10000085", "Syed Hisham Bin Syed Hussain", "Hisham", "WOH HUP (PRIVATE) LIMITED", "Staff (Woh Hup)",
     "Security Supervisor", "Security", None, "Security",
     "Security", "WHPL04", "I",
     "2017-01-16", None, None, None,
     "2025-01-01", None, None, None, None, None),

    ("10000086", "Peggy Koh Lay Hwee", "Peggy", "WOH HUP (PRIVATE) LIMITED", "Staff (Woh Hup)",
     "Governance Manager", "Governance", None, "Governance",
     "Woh Hup Building", "WHQ", "D",
     "2016-06-20", None, None, None,
     "2025-01-01", None, None, None, None, None),

    ("10000087", "David Lim Chun Keong", "David", "WOH HUP (PRIVATE) LIMITED", "Staff (Woh Hup)",
     "Project Director", "Production", None, "Production",
     "Tengah Garden Walk", "TGW", "B",
     "2009-05-25", None, None, None,
     "2025-01-25", "2027-12-31", None, None, None, None),

    ("10000088", "Lai Wai Kit", "Wai Kit", "WOH HUP ENGINEERING PTE. LTD.", "Staff (Woh Hup)",
     "Electrical Engineer", "M&E", None, "M&E",
     "Zion Road Parcel A", "ZRA", "F",
     "2022-09-05", None, None, None,
     "2025-03-05", "2026-12-31", None, None, None, None),

    ("10000089", "Siti Norzahira Binte Karim", "Norzahira", "WOH HUP (PRIVATE) LIMITED", "Staff (Woh Hup)",
     "Environmental Officer", "Environmental", None, "Environmental",
     "Toa Payoh Lorong 1", "TPY", "H",
     "2024-10-28", None, None, None,
     "2025-01-01", "2026-09-30", None, None, None, None),

    ("10000090", "Chee Kian Meng", "Kian Meng", "WOH HUP (PRIVATE) LIMITED", "Staff (Woh Hup)",
     "Archi-Technical Manager", "Archi Technical", None, "Archi Technical",
     "Zion Road (Parcel B)", "ZRB", "D",
     "2015-08-31", None, None, None,
     "2025-01-31", "2027-06-30", None, None, None, None),

    # --- More resigned / terminated employees ---
    ("10000091", "Marcus Tan Beng Siong", "Marcus", "WOH HUP (PRIVATE) LIMITED", "Staff (Woh Hup)",
     "Senior Engineer", "Engineering", None, "Engineering",
     "Geras Building 2", "KG2", "E",
     "2020-02-17", "2025-03-31", "Resignation", None,
     "2020-03-01", "2025-03-31", None, None, None, None),

    ("10000092", "Farah Binte Hussain", "Farah", "WOH HUP (PRIVATE) LIMITED", "Staff (Woh Hup)",
     "Admin Executive", "Corporate Office", None, "Corporate Office",
     "Woh Hup Building", "WHQ", "I",
     "2022-06-13", "2025-06-12", "Resignation", None,
     "2022-06-13", "2025-06-12", None, None, None, None),

    ("10000093", "Ho Boon Tiong", "Boon Tiong", "WOH HUP (PRIVATE) LIMITED", "Staff (Woh Hup)",
     "Project Manager", "Production", None, "Production",
     "Newport Plaza", "FJX", "D",
     "2016-11-28", "2025-05-31", "Retirement", None,
     "2022-01-01", "2025-05-31", None, None, None, None),

    ("10000094", "Soo Wai Kheong", "Wai Kheong", "WOH HUP ENGINEERING PTE. LTD.", "Staff (Woh Hup)",
     "Mechanical Technician", "M&E", None, "M&E",
     "Holland Drive", "HLD", "K",
     "2021-04-19", "2025-02-14", "End of Contract", None,
     "2021-05-01", "2025-02-14", None, None, None, None),

    ("10000095", "Crystal Neo Shi Min", "Crystal", "WOH HUP HOLDINGS PRIVATE LIMITED", "Staff (Woh Hup)",
     "IT Analyst", "Technology", None, "Information Technology",
     "Woh Hup Building", "WHQ", "H",
     "2023-01-09", "2025-08-31", "Resignation", None,
     "2023-01-09", "2025-08-31", None, None, None, None),

    # --- Senior leadership / HQ roles ---
    ("10000096", "James Ng Teck Huat", "James", "WOH HUP (PRIVATE) LIMITED", "Staff (Woh Hup)",
     "Chief Operating Officer", "General Management & Business Innovation", None,
     "General Management & Business Innovation",
     "Woh Hup Building", "WHQ", "A",
     "2005-03-01", None, None, None,
     "2025-01-01", None, None, None, None, None),

    ("10000097", "Susan Lau Swee Bee", "Susan", "WOH HUP HOLDINGS PRIVATE LIMITED", "Staff (Woh Hup)",
     "Group HR Director", "HR", None, "HR",
     "Woh Hup Building", "WHQ", "B",
     "2011-07-18", None, None, None,
     "2025-01-01", None, None, None, None, None),

    ("10000098", "Peter Chua Tian Liang", "Peter", "WOH HUP (PRIVATE) LIMITED", "Staff (Woh Hup)",
     "Chief Financial Officer", "Finance", None, "Finance",
     "Woh Hup Building", "WHQ", "A",
     "2007-09-10", None, None, None,
     "2025-01-01", None, None, None, None, None),

    ("10000099", "Wendy Sim Hui Ting", "Wendy", "WOH HUP (PRIVATE) LIMITED", "Staff (Woh Hup)",
     "Head of Innovation", "Innovation", None, "Innovation",
     "Woh Hup Building", "WHQ", "C",
     "2014-01-06", None, None, None,
     "2025-01-01", None, None, None, None, None),

    ("10000100", "Farouk Bin Osman", "Farouk", "WOH HUP (PRIVATE) LIMITED", "Staff (Woh Hup)",
     "Head of WSHE", "WSHE", None, "WSHE",
     "Woh Hup Building", "WHQ", "C",
     "2013-06-03", None, None, None,
     "2025-01-01", None, None, None, None, None),
]

INSERT_SQL = """
INSERT INTO v_staff_hr_format (
    emp_no, emp_name, alias, company, classification, occupation, category, section, division,
    cost_centre, cost_centre_short, job_level, hired_date, termination_date, termination_reason,
    remarks, start_of_deployment, end_of_deployment,
    next_deployment_start_date, next_deployment_end_date, next_deployment_site, next_deployment_fte
) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
"""

conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

# Clear existing data (if any)
cur.execute("DELETE FROM v_staff_hr_format")

cur.executemany(INSERT_SQL, rows)
conn.commit()

count = cur.execute("SELECT COUNT(*) FROM v_staff_hr_format").fetchone()[0]
print(f"OK Inserted {count} rows into v_staff_hr_format in {DB_PATH}")
conn.close()
