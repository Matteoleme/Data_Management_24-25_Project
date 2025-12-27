import pandas as pd
import json
import math

def safe_value(v):
    # check if is NaN and return None
    if v is None or (isinstance(v, float) and math.isnan(v)):
        return None
    return v

def first_structure(df):
    result = []
    
    for _, row in df.iterrows():
        doc = {
            # Fields of the flight
            'YEAR': safe_value(row['YEAR']),
            'MONTH': safe_value(row['MONTH']),
            'DAY': safe_value(row['DAY']),
            'DAY_OF_WEEK': safe_value(row['DAY_OF_WEEK']),
            'FLIGHT_NMB': safe_value(row['FLIGHT_NUMBER']),
            'TAIL_NMB': safe_value(row['TAIL_NUMBER']),
            'SCHEDULED_DEP': safe_value(row['SCHEDULED_DEPARTURE']),
            'DEP_TIME': safe_value(row['DEPARTURE_TIME']),
            'DEP_DELAY': safe_value(row['DEPARTURE_DELAY']),
            'TAXI_OUT': safe_value(row['TAXI_OUT']),
            'WHEELS_OFF': safe_value(row['WHEELS_OFF']),
            'SCHED_TIME': safe_value(row['SCHEDULED_TIME']),
            'ELAPSED_TIME': safe_value(row['ELAPSED_TIME']),
            'AIR_TIME': safe_value(row['AIR_TIME']),
            'DISTANCE': safe_value(row['DISTANCE']),
            'WHEELS_ON': safe_value(row['WHEELS_ON']),
            'TAXI_IN': safe_value(row['TAXI_IN']),
            'SCHEDULED_ARR': safe_value(row['SCHEDULED_ARRIVAL']),
            'ARR_TIME': safe_value(row['ARRIVAL_TIME']),
            'ARR_DELAY': safe_value(row['ARRIVAL_DELAY']),
            'DIVERTED': safe_value(row['DIVERTED']),
            'CANC': safe_value(row['CANCELLED']),
            'CANC_REASON': safe_value(row['CANCELLATION_REASON']),
            'AIR_SYS_DELAY': safe_value(row['AIR_SYSTEM_DELAY']),
            'SEC_DELAY': safe_value(row['SECURITY_DELAY']),
            'AIRLINE_DELAY': safe_value(row['AIRLINE_DELAY']),
            'LATE_AIRCRAFT_DELAY': safe_value(row['LATE_AIRCRAFT_DELAY']),
            'WEATHER_DELAY': safe_value(row['WEATHER_DELAY']),
            
            # Nested airport info
            'ORIGIN': {
                'CODE': safe_value(row['IATA_CODE_x']), 
                'NAME': safe_value(row['AIRPORT']),
                'CITY': safe_value(row['CITY']),
                'STATE': safe_value(row['STATE']),
                'COUNTRY': safe_value(row['COUNTRY']),
                'LAT': safe_value(row['LATITUDE']),
                'LONG': safe_value(row['LONGITUDE'])
            },
            
            'DEST': {
                'CODE': safe_value(row['IATA_CODE_DESTINATION']), 
                'NAME': safe_value(row['AIRPORT_DESTINATION']),
                'CITY': safe_value(row['CITY_DESTINATION']),
                'STATE': safe_value(row['STATE_DESTINATION']),
                'COUNTRY': safe_value(row['COUNTRY_DESTINATION']),
                'LAT': safe_value(row['LATITUDE_DESTINATION']),
                'LONG': safe_value(row['LONGITUDE_DESTINATION'])
            },
            # Nested airline info  
            'AIRLINE': {
                'CODE': safe_value(row['IATA_CODE_y']),
                'NAME': safe_value(row['AIRLINE_y'])
            }
        }
        result.append(doc)
    
    return result

def first_denormalization():
    flights_with_origin_airports = pd.merge(flights_df, airports_df, left_on='ORIGIN_AIRPORT', right_on="IATA_CODE", 
                                        how='left', suffixes=("","_ORIGIN"))
    flights_with_airports = pd.merge(flights_with_origin_airports, airports_df, left_on='DESTINATION_AIRPORT', 
                                 right_on="IATA_CODE", how='left', suffixes=("","_DESTINATION"))
    complete_df = pd.merge(flights_with_airports, airlines_df, left_on='AIRLINE', right_on="IATA_CODE", how='left')
    return first_structure(complete_df)


def second_structure(df):
    result = []
    
    for _, row in df.iterrows():
        doc = {
            # fields of the flight
            'YEAR': safe_value(row['YEAR']),
            'MONTH': safe_value(row['MONTH']),
            'DAY': safe_value(row['DAY']),
            'DAY_OF_WEEK': safe_value(row['DAY_OF_WEEK']),
            'FLIGHT_NMB': safe_value(row['FLIGHT_NUMBER']),
            'TAIL_NMB': safe_value(row['TAIL_NUMBER']),
            'SCHEDULED_DEP': safe_value(row['SCHEDULED_DEPARTURE']),
            'DEP_TIME': safe_value(row['DEPARTURE_TIME']),
            'DEP_DELAY': safe_value(row['DEPARTURE_DELAY']),
            'TAXI_OUT': safe_value(row['TAXI_OUT']),
            'WHEELS_OFF': safe_value(row['WHEELS_OFF']),
            'SCHED_TIME': safe_value(row['SCHEDULED_TIME']),
            'ELAPSED_TIME': safe_value(row['ELAPSED_TIME']),
            'AIR_TIME': safe_value(row['AIR_TIME']),
            'DISTANCE': safe_value(row['DISTANCE']),
            'WHEELS_ON': safe_value(row['WHEELS_ON']),
            'TAXI_IN': safe_value(row['TAXI_IN']),
            'SCHEDULED_ARR': safe_value(row['SCHEDULED_ARRIVAL']),
            'ARR_TIME': safe_value(row['ARRIVAL_TIME']),
            'ARR_DELAY': safe_value(row['ARRIVAL_DELAY']),
            'DIVERTED': safe_value(row['DIVERTED']),
            'CANC': safe_value(row['CANCELLED']),
            'CANC_REASON': safe_value(row['CANCELLATION_REASON']),
            'AIR_SYS_DELAY': safe_value(row['AIR_SYSTEM_DELAY']),
            'SEC_DELAY': safe_value(row['SECURITY_DELAY']),
            'AIRLINE_DELAY': safe_value(row['AIRLINE_DELAY']),
            'LATE_AIRCRAFT_DELAY': safe_value(row['LATE_AIRCRAFT_DELAY']),
            'WEATHER_DELAY': safe_value(row['WEATHER_DELAY']),
            'ORG_AIRPORT': safe_value(row['ORIGIN_AIRPORT']),
            'DEST_AIRPORT': safe_value(row['DESTINATION_AIRPORT']),
            # Nested airline info  
            'AIRLINE': {
                'CODE': safe_value(row['IATA_CODE']),
                'NAME': safe_value(row['AIRLINE_y'])
            }
        }
        result.append(doc)
    
    return result

def second_denormalization():
    flights_with_airlines = pd.merge(flights_df, airlines_df, left_on='AIRLINE', right_on="IATA_CODE", how='left')
    print(flights_with_airlines.columns)
    input("Aspetto")
    return second_structure(flights_with_airlines)

path = "G:\\Il mio Drive\\Uni\\PrimoAnno\\SecondoSemestre\\DataManagement\\Project\\2015_flight_delays_and_cancellations\\"

print("Loading csvs")
# Load CSVs
flights_df = pd.read_csv(f'{path}flights.csv')
airports_df = pd.read_csv(f'{path}airports.csv') 
airlines_df = pd.read_csv(f'{path}airlines.csv')

print("Loaded")


#flight_documents = first_denormalization()
flight_documents = second_denormalization()


# Save in JSON format for MongoDB
output_filename = 'compress_flights_denormalized2.json'

print(f"\nSaving to {output_filename}...")

with open(output_filename, 'w', encoding='utf-8') as f:
    for doc in flight_documents:
        f.write(json.dumps(doc, ensure_ascii=False) + "\n")

print(f"File saved: {output_filename}")
print(f"Total documents: {len(flight_documents)}")