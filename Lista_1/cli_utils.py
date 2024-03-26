from graph import *
import sys
import uuid
import webbrowser
import folium
import pathlib

def normalize_input_time(time_str):
    hours, minutes, *_ = map(int, time_str.split(':'))
    
    if hours >= 24 or minutes >= 60:
        raise ValueError 

    return hours * 60 + minutes

def convert_normalized_time(time: int):
    hours = time // 60
    minutes = time - hours * 60
    
    return f'{hours:02d}:{minutes:02d}'

def travel_schedule(path: list[(Stop, Connection)]):
    first_stop, first_connection = path[0]
    _, last_connection = path[0]
    schedule = []

    for stop, connection in path:
        if connection.line != last_connection.line:
            schedule.append((first_stop, first_connection, last_connection))
            first_stop = stop
            first_connection = connection

        last_connection = connection

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

def create_map(path: list[Stop, Connection]):
    colors = ['blue', 'orange', 'purple']
    start_color = 'green'
    end_color = 'red'
    color = colors[0]
    counter = 0
    current_line = previous_line = path[0][1].line
    previous_connection = None
    start_stop = path[0][0]
    start_coordinates = (start_stop.lat, start_stop.lon)
    line_points = []
    folium_map = folium.Map(location=start_coordinates, zoom_start=20)

    for stop, connection in path:  
        if current_line != previous_line:
            line_label = folium.Tooltip(text=f'Linia {previous_line}')
            folium.PolyLine(line_points, color=color, tooltip=line_label).add_to(folium_map)
            counter = counter + 1
            color = colors[counter % len(colors)]
            line_points = [coordinates]   
           
        coordinates = (stop.lat, stop.lon)
        line_points.append(coordinates)
        arrival_time = '' if previous_connection == None else convert_normalized_time(previous_connection.arrival_time)
        departure_time = convert_normalized_time(connection.departure_time)
        stop_label = folium.Tooltip(text=f'{stop.name}\t{arrival_time}\t{departure_time}')

        if stop == start_stop:
            icon = folium.Icon(color=start_color)
        else:
            icon = folium.Icon(color=color)

        folium.Marker(location=coordinates, icon=icon, tooltip=stop_label).add_to(folium_map)

        previous_line = current_line
        current_line = connection.line
        previous_connection = connection

    goal = connection.end_stop
    coordinates = (goal.lat, goal.lon)
    line_points.append(coordinates)

    stop_label = folium.Tooltip(text=f'{goal.name}\t{convert_normalized_time(connection.arrival_time)}')
    folium.Marker(location=coordinates, icon=folium.Icon(color=end_color), tooltip=stop_label).add_to(folium_map)

    line_label = folium.Tooltip(text=f'Linia {previous_line}')
    folium.PolyLine(line_points, color=color, tooltip=line_label).add_to(folium_map)

    return folium_map

def open_map(map: folium.Map):
    map_file = f'map_{uuid.uuid4()}.html'
    map_path = pathlib.Path('Maps').joinpath(map_file)
    map.save(map_path)
    webbrowser.open(map_path)

        