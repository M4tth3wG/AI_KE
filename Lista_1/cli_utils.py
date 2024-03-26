from graph import *
import sys

def normalize_input_time(time_str):
    hours, minutes, *_ = map(int, time_str.split(':'))
    
    if hours >= 24 or minutes >= 60:
        raise ValueError 

    return hours * 60 + minutes

def travel_schedule(path: list[(Stop, Connection)]):
    last_stop, last_connection = path[0]
    last_departure_time = last_connection.departure_time
    schedule = []

    for stop, connection in path:
        if connection.line != last_connection.line:
            schedule.append((last_stop, last_departure_time, last_connection))
            last_stop = stop
            last_departure_time = connection.departure_time

        last_connection = connection

    schedule.append((schedule[-1][2].end_stop, schedule[-1][2].departure_time, connection))

    return schedule

def convert_normalized_time(time: int):
    hours = time // 60
    minutes = time - hours * 60
    
    return f'{hours:02d}:{minutes:02d}'

def travel_schedule(path: list[(Stop, Connection)]):
    first_stop, first_connection = path[0]
    last_stop, last_connection = path[0]
    schedule = []

    for stop, connection in path:
        if connection.line != last_connection.line:
            schedule.append((first_stop, first_connection, last_connection))
            first_stop = stop
            first_connection = connection

        last_connection = connection
        last_stop = stop

    schedule.append((first_stop, first_connection, last_connection))

    return schedule

def print_travel_schedule(schedule: list[(Stop, Connection, Connection)]):
    style = "{:<10} {:<40} {:<15} {:<40} {:<15}"
    
    print(style.format("Line", "Start stop", "Departure Time", "End Stop", "Arrival Time"), "\n")
    
    for stop, first_connection, last_connection in schedule:
        print(style.format(
                    first_connection.line, stop.name,
                    convert_normalized_time(first_connection.departure_time),
                    last_connection.end_stop.name,
                    convert_normalized_time(last_connection.arrival_time)))      
    print()

def print_path(path: list[Stop, Connection]):
    style = "{:<10} {:<40} {:<15} {:<40} {:<15}"
    
    print(style.format("Line", "Departure stop", "Departure Time", "Next Stop", "Arrival Time"), "\n")
    
    for stop, connection in path:
        print(style.format(
                    connection.line, stop.name,
                    convert_normalized_time(connection.departure_time),
                    connection.end_stop.name,
                    convert_normalized_time(connection.arrival_time)))
    print()