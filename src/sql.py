import psycopg2
import time
import sys

# db config
DB_HOST = "localhost"
DB_NAME = "flights_2015"
DB_USER = "postgres"
DB_PASS = "1234"

#limit = int(sys.argv[1]) if len(sys.argv) > 1 else 10000


query_to_analyze = f"""
    select f."AIRLINE", count(*) as flights_due_airlines
    from flights f 
    group by f."AIRLINE" 
"""

try:
    conn = psycopg2.connect(
        host=DB_HOST,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASS
    )
    conn.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)
    print("Connected to PostgreSQL")
except Exception as e:
    print(f"Connection Error {e}")
    exit()

def analyze_query_client_side(query):
    """
    Executes a query and collect the client side elapsed time
    """
    try:
        cur = conn.cursor()
        start_time = time.perf_counter()
        
        cur.execute(query)
        results = cur.fetchall()
        
        end_time = time.perf_counter()
        execution_time = (end_time - start_time) * 1000
        row_count = len(results)
        
        cur.close()
        return int(execution_time), row_count
    
    except Exception as e:
        print(f"Client Side execution error: {e}")
        return None, 0

def analyze_query_server_side(query):
    """
    Execute EXPLAIN ANALYZE and collect the only server side elapsed time.
    """
    try:
        cur = conn.cursor()
        explain_sql = "EXPLAIN (ANALYZE, BUFFERS) " + query
        
        cur.execute(explain_sql)
        explain_output = cur.fetchall()
        cur.close()

        execution_time = 0.0
        planning_time = 0.0
        for line in explain_output:
            if "Execution Time:" in line[0]:
                execution_time = round(float(line[0].split("Execution Time: ")[1].split(" ms")[0]))
            if "Planning Time:" in line[0]:
                planning_time = round(float(line[0].split("Planning Time: ")[1].split(" ms")[0]))
        
        return {
            "planning_time_ms": planning_time,
            "execution_time_ms": execution_time,
            "total_time_ms": planning_time + execution_time
        }
    
    except Exception as e:
        print(f"Server side execution error: {e}")
        return None

def run_analysis_multiple_times(query, iterations):
    """
    Execute multiple times the queries
    """
    print("=" * 70)
    print(f"Run queries {iterations} times")
    print("=" * 70)
    print(f"QUERY: {query.strip()}")
    
    client_timings = []
    server_timings = []
    
    
    for i in range(iterations):
        
        print("-" * 50)
        print(f"Iteration {i+1}:")
        
        client_time, row_count = analyze_query_client_side(query)
        if client_time is not None:
            client_timings.append(client_time)
            print(f"Client Side (End-to-end): {client_time} ms | Rows: {row_count}")
        
        server_stats = analyze_query_server_side(query)
        if server_stats:
            server_timings.append(server_stats["execution_time_ms"])
            print(f"Server Side (EXPLAIN ANALYZE): {server_stats['execution_time_ms']} ms")
    
    print("=" * 70)
    print("Final results")
    print("=" * 70)
    if client_timings:
        print("Client Side (End-to-end):")
        print(f"  AVG: {sum(client_timings) / len(client_timings)} ms")
        print(f"  Collected times (ms): {client_timings}")
    
    print("-" * 20)
    
    if server_timings:
        print("Server Side (EXPLAIN ANALYZE):")
        print(f"  AVG: {sum(server_timings) / len(server_timings)} ms")
        print(f"  Collected times (ms): {server_timings}")
        
if __name__ == "__main__":
    ITERATIONS = 1
    #limit = 1000000
    #for limit in [100000, 1000000]:
    #    run_analysis_multiple_times(f"{query_to_analyze} limit {limit}", ITERATIONS)
    run_analysis_multiple_times(query_to_analyze, ITERATIONS)
    conn.close()
    print("\nConnection closed.")
