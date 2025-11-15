import json
import os
import re
import requests
import psycopg2
import time
import constants

# Full feature set 10 times run
base = constants.BASE
typhimurium_base = constants.typhimurium_base
salmonella_base = constants.salmonella_base
SEARCH_API_ENDPOINTS = constants.SEARCH_API_ENDPOINTS
HOME_API_ENDPOINTS = constants.HOME_API_ENDPOINTS
INITIAL_API_ENDPOINTS = constants.INITIAL_API_ENDPOINTS
ISOLATE_API_ENDPOINTS = constants.ISOLATE_API_ENDPOINTS
PROJECT_API_ENDPOINTS = constants.PROJECT_API_ENDPOINTS
DB_CONNECTION = constants.DB_CONNECTION
LOGIN_URL = f"{base}/accounts/login/"

session = requests.session()
session.get(LOGIN_URL)
csrftoken = session.cookies['csrftoken']
LOG_PATH = "your-log-path"
VIEW_PATH = "your-view-sql-path"

'''
Payloads used in searching features
'''
full_payload = {
    "arrIso": json.dumps([{"identifier": "SRR1816009"},{"serovar":"1"},{"isQuery":"f"},{"privacy_status":"PV"},{"server_status":"U"},{"assignment_status":"A"},{"mgt1":"1"}]),
    "arrLoc": json.dumps([{"continent":"Europe"},{"country":"Australia"},{"state":"NSW"},{"postcode":"2007"}]),
    "arrAp": json.dumps([{"ap2_0_st":"1"},{"ap3_0_st":"1"},{"ap4_0_st":"1"},{"ap5_0_st":"1"},{"ap6_0_st":"1"},{"ap7_0_st":"1"},{"ap8_0_st":"1"}]),
    "arrCc": json.dumps([{"cc2_2": "1"}, {"cc2_3":"1"},{"cc2_4":"1"}, {"cc1_2": "1"}, {"cc1_3":"12"},{"cc1_4":"12"},{"cc1_5":"12"},{"cc1_6":"12"},{"cc1_7":"12"},{"cc1_8":"12"}]),
    "arrEpi": json.dumps([]),
    "arrIsln": json.dumps([{"source":"stool"},{"type":"environmental/other"},{"host":"Homo sapiens"},{"disease":"Salmonellosis"},{"date":"2025-04-02"},{"year":"2018"},{"month":"6"}])
}

light_payload = {
    "arrIso": json.dumps([{"identifier": "SRR1816009"}]),
    "arrLoc": json.dumps([]),
    "arrAp": json.dumps([]),
    "arrCc": json.dumps([]),
    "arrEpi": json.dumps([]),
    "arrIsln": json.dumps([]),
}

random_payload = {
    "arrIso": json.dumps([{"serovar": "Agona"}, {"mgt1": "1"}]),
    "arrLoc": json.dumps([{"country": "United States"}]),
    "arrAp": json.dumps([]),
    "arrCc": json.dumps([]),
    "arrEpi": json.dumps([]),
    "arrIsln": json.dumps([]),
}

cc_payload = {
    "arrIso": json.dumps([]),
    "arrLoc": json.dumps([]),
    "arrAp": json.dumps([]), 
    "arrCc": json.dumps([{"cc2_2": "1"}, {"cc2_3":"1"},{"cc2_4":"1"}, {"cc1_2": "1"}, {"cc1_3":"12"},{"cc1_4":"12"},{"cc1_5":"12"},{"cc1_6":"12"},{"cc1_7":"12"},{"cc1_8":"12"}]),
    "arrEpi": json.dumps([]), "arrIsln": json.dumps([])
}


'''
Create csrf token
'''
def get_csrf_token(session, url):
    session.get(url)
    csrftoken = session.cookies['csrftoken']
    return csrftoken

'''
Clear statements history
'''
def clear_pg_stat_statements():
    conn = psycopg2.connect(**DB_CONNECTION)
    cur = conn.cursor()
    cur.execute("SELECT pg_stat_statements_reset()")
    conn.commit()
    cur.close()
    conn.close()

'''
Log in to the MGTdb website
'''
def user_login(session):
    global csrftoken
    login_data = {
        "username": "your-username",
        "password": "your-password",
    }
    headers = {
        "X-CSRFToken": csrftoken,
        "Referer": LOGIN_URL,
        "Content-Type": "application/x-www-form-urlencoded"
    }
    response = session.post(LOGIN_URL, data=login_data, headers=headers)
    if response.status_code in [200, 302]:
        csrftoken = get_csrf_token(session, LOGIN_URL)
        return csrftoken
    else:
        raise ValueError("Login Failed")

'''
Execute pg_stat_statements to retrieve database time
'''
def get_execute_queries():
    conn = psycopg2.connect(**DB_CONNECTION)
    cur = conn.cursor()
    cur.execute("""
        SELECT query, calls, mean_exec_time
        FROM pg_stat_statements
        ORDER BY mean_exec_time DESC
    """)
    queries = cur.fetchall()
    cur.close()
    conn.close()
    return queries

'''
Delete 50,000 isolates from the isolate table
'''
def delete_50k_isolates():
    conn = psycopg2.connect(**DB_CONNECTION)
    cur = conn.cursor()
    cur.execute('''
        DELETE FROM "Salmonella_isolate"
            USING (
            SELECT id FROM (
                SELECT id, row_number() OVER () AS rn
                FROM "Salmonella_isolate"
            ) numbered
            WHERE rn <= 50000
            ) to_delete
            WHERE "Salmonella_isolate".id = to_delete.id;
    ''')
    conn.commit()
    cur.close()
    conn.close()

''' 
Calculate current isolate counts 
'''
def get_isolate_count():
    conn = psycopg2.connect(**DB_CONNECTION)
    cur = conn.cursor()
    cur.execute('SELECT COUNT(*) FROM "Salmonella_isolate";')
    count = cur.fetchone()[0]
    cur.close()
    conn.close()
    return count

'''
Refresh and update database view after isolate deletion
'''
def run_view_refresh():
    conn = psycopg2.connect(**DB_CONNECTION)
    cur = conn.cursor()
    with open(VIEW_PATH, "r") as sql_file:
        sql = sql_file.read()
        cur.execute(sql)
    conn.commit()
    cur.close()
    conn.close()

'''
Send API request and log the results from pg_stat_statements
'''
def simulate_request(session, API_ENDPOINT, field=None):
    url = f"{API_ENDPOINT}?{field}" if field else API_ENDPOINT
    try:
        response = session.get(url, timeout=600)
        queries = get_execute_queries()
        clear_pg_stat_statements()
    except requests.exceptions.RequestException as e:
        queries = [("timeout", 0, 0)]
    time.sleep(2)
    total_time = 0
    # calculate total time
    for query in queries:
        total_time += query[2]
    # write log files
    with open(LOG_PATH, "a") as log_file:
        log_file.write(f"API: {url}\n")
        for query in queries:
            log_file.write(f"- (query: {query[0]}, calls: {query[1]}, time: {query[2]:.2f}ms)\n")
        log_file.write(f"-time: {total_time}ms\n")
        log_file.write("="*50 + "\n\n")
    return total_time

'''
Send POST API request and log the results from pg_stat_statements
'''
def simulate_request_post(session, API_ENDPOINT, data=None, file=None):
    global csrftoken
    headers = {
        "X-CSRFToken": csrftoken,
        "Referer": API_ENDPOINT,
        "Content-Type": "application/x-www-form-urlencoded"
    }
    try:
        response = session.post(API_ENDPOINT, timeout=600, data=data, headers=headers, allow_redirects=True, files=file)
        queries = get_execute_queries()
        clear_pg_stat_statements()
    except requests.exceptions.RequestException as e:
        queries = [("timeout", 0, 0)]
    
    time.sleep(2)
    total_post_time = 0
    
    for query in queries:
        total_post_time += query[2]
    
    with open(LOG_PATH, "a") as log_file:
        log_file.write(f"API: {API_ENDPOINT}\n")
        for query in queries:
            log_file.write(f"- (query: {query[0]}, calls: {query[1]}, time: {query[2]:.2f}ms)\n")
        log_file.write(f"-time: {total_post_time}ms\n")
        log_file.write("="*50 + "\n\n")
    return total_post_time

'''
log the web-application feature name
'''
def featureName(featureName):
    with open(LOG_PATH, "a") as log_file:
        log_file.write(f"{featureName}\n")

'''
Run all features
'''
def run_full_feature_set(session):
    featureName("User Login")
    user_login(session)
    featureName("Open Main Page")
    simulate_request(session, HOME_API_ENDPOINTS[0])
    featureName("Open Home Page")
    simulate_request(session, HOME_API_ENDPOINTS[1])
    featureName("Open Isolate Home Page")
    simulate_request(session, HOME_API_ENDPOINTS[2])
    featureName("Initial Isolate")
    simulate_request(session, INITIAL_API_ENDPOINTS[0])
    featureName("List Isolate")
    simulate_request(session, ISOLATE_API_ENDPOINTS[0])
    featureName("Jump to Page 2")
    simulate_request_post(session, INITIAL_API_ENDPOINTS[0], {"pageNumToGet": 2})
    featureName("Jump to Page 900")
    simulate_request_post(session, INITIAL_API_ENDPOINTS[0], {"pageNumToGet": 900})
    featureName("Single Isolate Detail")
    simulate_request(session, ISOLATE_API_ENDPOINTS[3])

    featureName("And Search Random")
    simulate_request_post(session, SEARCH_API_ENDPOINTS[1], random_payload)
    featureName("Or Search Random")
    simulate_request_post(session, SEARCH_API_ENDPOINTS[1], random_payload | {"searchType": "or"})

    featureName("And Search all")
    simulate_request_post(session, SEARCH_API_ENDPOINTS[1], full_payload)

    featureName("Or Search all")
    simulate_request_post(session, SEARCH_API_ENDPOINTS[1], full_payload | {"searchType": "or"})

    featureName("And Search Mgt")
    simulate_request_post(session, SEARCH_API_ENDPOINTS[1], light_payload)
    featureName("Or Search Mgt")
    simulate_request_post(session, SEARCH_API_ENDPOINTS[1], light_payload | {"searchType": "or"})

    featureName("And Search CC")
    simulate_request_post(session, SEARCH_API_ENDPOINTS[1], cc_payload)
    featureName("Or Search CC")
    simulate_request_post(session, SEARCH_API_ENDPOINTS[1], cc_payload | {"searchType": "or"})

    featureName("Download MGT9 ST allelic profiles")
    simulate_request_post(session, INITIAL_API_ENDPOINTS[0], {"isMgt9Ap": True})
    featureName("Download CSV file")
    simulate_request_post(session, INITIAL_API_ENDPOINTS[0], {"isCSV": True})
    featureName("Download For Microreact")
    simulate_request_post(session, INITIAL_API_ENDPOINTS[0], {"isMr": True})
    featureName("Time ST Graph")
    simulate_request(session, SEARCH_API_ENDPOINTS[4])
    featureName("Loc ST Graph")
    simulate_request(session, SEARCH_API_ENDPOINTS[5])
    
    featureName("Sorting Isolate Identifier")
    simulate_request_post(session, INITIAL_API_ENDPOINTS[0], {
        "orderBy": "i.identifier",
        "dir": "Ascending"
    })
    featureName("Sorting Isolate Server")
    simulate_request_post(session, INITIAL_API_ENDPOINTS[0], {
        "orderBy": "i.server_status",
        "dir": "Ascending"
    })
    featureName("Sorting Isolate Assignment")
    simulate_request_post(session, INITIAL_API_ENDPOINTS[0], {
        "orderBy": "i.assignment_status",
        "dir": "Ascending"
    })
    featureName("Sorting Isolate Serovar")
    simulate_request_post(session, INITIAL_API_ENDPOINTS[0], {
        "orderBy": "i.serovar",
        "dir": "Ascending"
    })
    featureName("Sorting Isolate MGT1ST")
    simulate_request_post(session, INITIAL_API_ENDPOINTS[0], {
        "orderBy": "i.mgt1",
        "dir": "Ascending"
    })
    featureName("Sorting Isolate MGT2")
    simulate_request_post(session, INITIAL_API_ENDPOINTS[0], {
        "orderBy": "v.ap2_0_st",
        "dir": "Ascending"
    })
    featureName("Sorting Isolate ODC1")
    simulate_request_post(session, INITIAL_API_ENDPOINTS[0], {
        "orderBy": "v.cc1_8",
        "dir": "Ascending"
    })
    featureName("Sorting Isolate Location")
    simulate_request_post(session, INITIAL_API_ENDPOINTS[0], {
        "orderBy": "iM_l.continent",
        "dir": "Ascending"
    })
    featureName("Sorting Isolate Source")
    simulate_request_post(session, INITIAL_API_ENDPOINTS[0], {
        "orderBy": "iM_i.source",
        "dir": "Ascending"
    })
    featureName("Sorting Isolate Year")
    simulate_request_post(session, INITIAL_API_ENDPOINTS[0], {
        "orderBy": "iM_i.year",
        "dir": "Ascending"
    })

    featureName("Summary Report AU")
    simulate_request_post(session, SEARCH_API_ENDPOINTS[6], {
        "yearStart": 1984,
        "yearEnd": 2025,
        "country": "AU",
        "project": ""
    })
    featureName("Summary Report US")
    simulate_request_post(session, SEARCH_API_ENDPOINTS[6], {
        "yearStart": 1984,
        "yearEnd": 2025,
        "country": "US",
        "project": ""
    })

    #user_login(session)
    
    featureName("List Project")
    simulate_request(session, PROJECT_API_ENDPOINTS[0])
    featureName("Show Project Detail")
    simulate_request(session, PROJECT_API_ENDPOINTS[3])
    featureName("Initial Isolates Inside Project")
    simulate_request(session, INITIAL_API_ENDPOINTS[0])

'''
Run the features multiple (n) times
'''
def run_n_times_with_separate_logs(n=10, dataset=0):
    all_times = []
    global LOG_PATH
    for i in range(n):
        print(f"\n=== Run {i+1} of {n} ===")
        clear_pg_stat_statements()
        LOG_PATH = f"your-log-path"
        
        if os.path.exists(LOG_PATH):
            os.remove(LOG_PATH)
        
        run_full_feature_set(session)
        
        with open(LOG_PATH, "r") as log_file:
            log_text = log_file.read()
            matches = re.findall(r"-time:\s*([\d\.]+)ms", log_text)
            if matches:
                total_time = float(matches[-1])
                all_times.append(total_time)
            else:
                all_times.append(0)

'''
Run the features n times with isolate deletion (50,000 isolates each time, stop when <= 70,000 isolates left)
'''
def run_with_deduction():
    dataset_id = 0
    clear_pg_stat_statements()
    
    while True:
        print(f"\n=== Dataset {dataset_id} ===")
    
        run_n_times_with_separate_logs(10, dataset_id)
        
        # check isolate numbers
        if get_isolate_count() <= 70000:
            print("Reached 70,000 isolates.")
            break
        
        # delete isolates and refresh view table
        delete_50k_isolates()
        run_view_refresh()
        
        dataset_id += 1

if __name__ == '__main__':
    run_with_deduction()
