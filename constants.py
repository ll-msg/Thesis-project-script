### helper file for dbTime ###

BASE = "http://127.0.0.1:8000"

typhimurium_base = f"{BASE}/typhimurium"
salmonella_base = f"{BASE}/salmonella"

# 1. Initial Isolates
INITIAL_API_ENDPOINTS = [
    f"{salmonella_base}/initial-isolates",
    f"{salmonella_base}/initial-projectIsolates",
]

# 2. Home
HOME_API_ENDPOINTS = [
    f"{BASE}/",
    f"{BASE}/home",
    f"{salmonella_base}/",
]

# 3. Project Management
PROJECT_API_ENDPOINTS = [
    f"{salmonella_base}/projects",
    f"{salmonella_base}/project-create",
    f"{salmonella_base}/project-89-edit",
    f"{salmonella_base}/project-35153-detail",
    f"{salmonella_base}/project-114-delete",
]

# 4. Isolate Management
ISOLATE_API_ENDPOINTS = [
    f"{salmonella_base}/isolate-list",
    f"{salmonella_base}/isolate-create?project=89",
    f"{salmonella_base}/isolate-124484-edit",
    f"{salmonella_base}/isolate-50802-detail",
    f"{salmonella_base}/isolate-124488-delete",
    # url for add multiple isolates - isolate-createBmd
]

# 5. Search
SEARCH_API_ENDPOINTS = [
    f"{salmonella_base}/search-projectDetail",
    f"{salmonella_base}/search-isolateList",  
    f"{salmonella_base}/search-isolateDetail",
    f"{salmonella_base}/top-st", 
    f"{salmonella_base}/timeStCount",
    f"{salmonella_base}/timeLocStCnt",
    f"{salmonella_base}/getDataForReport"
]


DB_CONNECTION = {
    "dbname": "salmonella",
    "user": "your-username",
    "password": "your-password",
    "host": "localhost",
    "port": "5432"
}