from pymongo import MongoClient
import time
import pprint
import sys
import json
import subprocess
import time

DOCKER_PATH = r"C:\Program Files\Docker\Docker\Docker Desktop.exe"
CONTAINER_NAME = "mymongo"

client_side = True
server_side = True
#warm_up = client_side == server_side
warm_up = False
restart = not warm_up
ITERATIONS = 5


print("Remember to open the terminal in admin mode!!")

def restart_docker():
    # Kill Docker Desktop
    subprocess.run([
        "powershell",
        "-Command",
        ("Stop-Process -Name 'Docker Desktop' -Force -ErrorAction SilentlyContinue; "
        "Stop-Process -Name 'com.docker.backend' -Force -ErrorAction SilentlyContinue; "
        "Stop-Process -Name 'Docker Desktop Backend' -Force -ErrorAction SilentlyContinue")
    ])

    # Wait to ensure Docker has stopped
    time.sleep(5)

    # Restart Docker Desktop
    subprocess.run([
        "powershell",
        "-Command",
        fr"Start-Process '{DOCKER_PATH}' -Verb RunAs"
    ])
    print("Docker Desktop started, waiting...")


def docker_ready():
    try:
        subprocess.run(["docker", "ps"], check=True, capture_output=True)
        return True
    except:
        return False



# Database configuration
def connect_to_mongodb():
    try:
        client = MongoClient("mongodb://localhost:27017/",
                            username="mongo",
                            password="1234",
                            serverSelectionTimeoutMS=5000)
        client.admin.command('ping')
        db = client["airlinesDB"]
        flights = db["flights"]
        print("Connected to MongoDB!")
        return client, db, flights
    except Exception as e:
        print(f"Connection error: {e}")
        exit()

LIMIT = int(sys.argv[1]) if len(sys.argv) > 1 else 10000


# --- Queries to analyze ---
# Aggregation query for joins
AGGREGATION_PIPELINE5 = [
    {
        '$lookup': {
            'from': 'airlines', 
            'localField': 'AIRLINE', 
            'foreignField': 'IATA_CODE', 
            'as': 'airline_details'
        }
    }, {
        '$unwind': '$airline_details'
    }, {
        '$group': {
            '_id': '$AIRLINE', 
            'count': {
                '$sum': 1
            }, 
            'airline_name': {
                '$first': '$airline_details.AIRLINE'
            }
        }
    }
]


AGGREGATION_PIPELINE = [
    {
        '$lookup': {
            'from': 'airlines', 
            'localField': 'AIRLINE', 
            'foreignField': 'IATA_CODE', 
            'as': 'airline_info'
        }
    }, {
        '$lookup': {
            'from': 'airports', 
            'localField': 'ORIGIN_AIRPORT', 
            'foreignField': 'IATA_CODE', 
            'as': 'origin_airport_info'
        }
    }, {
        '$lookup': {
            'from': 'airports', 
            'localField': 'DESTINATION_AIRPORT', 
            'foreignField': 'IATA_CODE', 
            'as': 'destination_airport_info'
        }
    }, {
        '$unwind': '$airline_info'
    }, {
        '$unwind': '$origin_airport_info'
    }, {
        '$unwind': '$destination_airport_info'
    },
    {
        '$limit': LIMIT
    }
]

client_timings = []
server_timings = []

# Find query
FIND_QUERY = {'ORIGIN_AIRPORT': 'LAX'}

# Find one query
FIND_ONE_QUERY = {"_id": "5f9d1b7e9b0e1d0f8c7b8e1a"} # Replace with an existing ID


# --- Analysis functions ---
def _execute_query_client_side(collection, query_type, query):
    """Executes a query and measures the total time (client-side)."""
    start_time = time.perf_counter()
    try:
        if query_type == 'aggregate':
            results = list(collection.aggregate(query))
        elif query_type == 'find':
            results = list(collection.find(query).limit(LIMIT))
        elif query_type == 'find_one':
            results = [collection.find_one(query)]
        
        end_time = time.perf_counter()
        execution_time = (end_time - start_time) * 1000
        doc_count = len(results) if results else 0
        return int(execution_time), doc_count
    except Exception as e:
        print(f"Error during client-side execution: {e}")
        return None, 0

def _execute_query_server_side(collection, query_type, query):
    """Executes explain and returns the pure server execution time."""
    try:
        # Use the 'explain' command for all query types
        execution_time_ms = 0
        if query_type == 'aggregate':
            explain_result = db.command({
                'explain': {
                    'aggregate': collection.name,
                    'pipeline': query,
                    'cursor': {}
                },
                'verbosity': 'executionStats'
            })
            if explain_result.get('stages') is not None:
                execution_time_ms = explain_result['stages'][0]['$cursor']['executionStats']['executionTimeMillis']
            elif explain_result.get('executionStats') is not None:
                execution_time_ms = explain_result['executionStats']['executionTimeMillis']
        elif query_type == 'find' or query_type == 'find_one':
            explain_result = collection.find(query).limit(LIMIT).explain()
            if 'executionStats' in explain_result:
                execution_time_ms = explain_result['executionStats'].get('executionTimeMillis', 0)
        
        return int(execution_time_ms)
    except Exception as e:
        print(f"Error during server-side analysis (explain): {e}")
        return None

def run_analysis_multiple_times(collection, query_type, query, iterations):
    """
    Executes both types of analysis for N iterations.
    """
    print("=" * 70)
    print(f"Performance analysis for {iterations} iterations")
    print(f" Query type: {query_type.upper()}")
    print("=" * 70)
    print("QUERY:")
    pprint.pprint(query, depth=2, width=80)
    
    # Cache warm-up
    if(warm_up):
        print("\nCache warm-up...")
        _execute_query_client_side(collection, query_type, query)
        _execute_query_server_side(collection, query_type, query)
    


    for i in range(iterations):
        print("-" * 50)
        print(f"Iteration {i+1}:")
        
        # Client-side analysis (end-to-end time)
        if client_side:
            client_time, doc_count = _execute_query_client_side(collection, query_type, query)
            if client_time is not None:
                client_timings.append(client_time)
                print(f"  Client side (End-to-end): {client_time} ms | Documents: {doc_count}")
        
        # Server-side analysis (pure DB execution time)
        if server_side:
            server_time = _execute_query_server_side(collection, query_type, query)
            if server_time is not None:
                server_timings.append(server_time)
                print(f"  Server side (explain): {server_time} ms")
    
    print("=" * 70)
    print("Final summary")
    print("=" * 70)
    if client_timings:
        print("Client side times (End-to-end):")
        print(f"  Average: {sum(client_timings) / len(client_timings)} ms")
        print(f"  All times (ms): {client_timings}")
    
    print("-" * 20)
    
    if server_timings:
        print("Server side times (explain):")
        print(f"  Average: {sum(server_timings) / len(server_timings)} ms")
        print(f"  All times (ms): {server_timings}")



if __name__ == "__main__":
    
    if restart:
        restart_docker()
        time.sleep(10)
        while not docker_ready():
            print("Docker not ready yet...")
            time.sleep(5)
        
        subprocess.run(["docker", "restart", CONTAINER_NAME], check=True)
    
    for i in range(1):          # set to 1 if you want no cache warm-up, set multiple to have warm-up
        
        client, db, flights = connect_to_mongodb()
        # Analysis execution
        run_analysis_multiple_times(flights, 'aggregate', AGGREGATION_PIPELINE, ITERATIONS)
        #run_analysis_multiple_times(flights, 'find', FIND_QUERY, ITERATIONS)
        #run_analysis_multiple_times(flights, 'find_one', FIND_ONE_QUERY, ITERATIONS)
        if restart:
            restart_docker()
        
            while not docker_ready():
                print("Docker not ready yet...")
                time.sleep(5)

            print("Docker is ready now.")

            # 4. Restart the specific container
            subprocess.run(["docker", "restart", CONTAINER_NAME], check=True)
            print(f"Container '{CONTAINER_NAME}' restarted successfully")
    client.close()
    print("\nConnection to MongoDB closed.")