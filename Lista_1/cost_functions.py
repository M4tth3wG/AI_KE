from graph import *
import math
from geopy import distance as gp_distance

DEFAULT_ADVANCED_LINE_CHANGE_HEURISTIC_WEIGHT = 0.25
DEFAULT_TIME_HEURISTIC_SPEED = 4.85 / 60 # km/h to km/min
WAITING_LIMIT = 20

# cost functions

def calculate_time(start_time: int, current_cost: int, next_connection: Connection):
    current_time = start_time + current_cost
    current_time = current_time % (24 * 60)
    wating_time = normalized_time_difference(current_time, next_connection.departure_time)
    travel_time = normalized_time_difference(next_connection.departure_time, next_connection.arrival_time)

    return wating_time + travel_time

def normalized_time_difference(start: int, end: int):
    result = end - start

    return result if result >= 0 else result + 24 * 60

def line_changed(previous_connection: Connection, next_connection: Connection):
    if previous_connection == None:
        return False
    
    return previous_connection.line != next_connection.line \
        or previous_connection.arrival_time != next_connection.departure_time

def line_changes_cost(start_time: int, previous_connection: Connection, next_connection: Connection):

    
    if previous_connection == None and normalized_time_difference(start_time, next_connection.departure_time) > WAITING_LIMIT:
        return float('inf')
    elif previous_connection != None and normalized_time_difference(previous_connection.arrival_time, next_connection.departure_time) > WAITING_LIMIT:
        return float('inf')
    
    return 1 if line_changed(previous_connection, next_connection) else 0

# distance functions

def euclidean_distance_gp(a, b):
    return gp_distance.distance(a, b).km

def euclidean_distance(a, b):
    return math.sqrt(sum([(x - y) ** 2 for x, y in zip(a, b)]))

def manhattan_distance_gp(a, b):
    lat_distance = gp_distance.distance(a, (b[0], a[1])).km
    lon_distance = gp_distance.distance((b[0], a[1]), b).km
    
    return lat_distance + lon_distance

def manhattan_distance(a, b):
    return sum([abs(x - y) for x, y in zip(a, b)])

# heuristic functions

def time_heuristic(start_stop, end_stop, dist_func, heuristic_speed = DEFAULT_TIME_HEURISTIC_SPEED):
    start_coordinates = (start_stop.lat, start_stop.lon)
    end_coordinates = (end_stop.lat, end_stop.lon)
    
    return dist_func(start_coordinates, end_coordinates) / heuristic_speed

def simple_line_change_heuristic(current_stop, goal_stop, previous_connection, dist_func, weight):
    start_coordinates = (current_stop.lat, current_stop.lon)
    end_coordinates = (goal_stop.lat, goal_stop.lon)
    
    return dist_func(start_coordinates, end_coordinates) * weight

# def advanced_line_change_heuristic(start_time, current_stop, goal_stop, previous_connection, next_connection, dist_func, weight = DEFAULT_ADVANCED_LINE_CHANGE_HEURISTIC_WEIGHT):
#     start_coordinates = (current_stop.lat, current_stop.lon)
#     next_coordinates = (next_connection.end_stop.lat, next_connection.end_stop.lon)
#     end_coordinates = (goal_stop.lat, goal_stop.lon)

#     current_line_is_direct = previous_connection != None and any(previous_connection.line == end_connection.line for end_connection in goal_stop.connections)
#     next_line_is_direct = any(next_connection.line == end_connection.line for end_connection in goal_stop.connections)
#     line_is_changed = line_changed(previous_connection, next_connection)
#     current_distance = dist_func(start_coordinates, end_coordinates)
#     next_distance = dist_func(next_coordinates, end_coordinates)

#     if previous_connection != None and normalized_time_difference(previous_connection.arrival_time, next_connection.departure_time) > 60:
#         heuristic_cost = 2000
#     elif previous_connection == None and normalized_time_difference(start_time, next_connection.departure_time) > 60:
#         heuristic_cost = 2000
#     elif current_line_is_direct and line_is_changed:
#         heuristic_cost = 1000
#     elif current_line_is_direct:
#         heuristic_cost = 100 if next_distance - current_distance > 0 else 0 # penalty if getting away from goal
#     elif next_line_is_direct:
#         heuristic_cost = 0 # reward
#     else:
#         heuristic_cost = 10 # small penalty

#     return heuristic_cost

def advanced_line_change_heuristic(start_time, current_stop, goal_stop, previous_connection, next_connection, dist_func, weight = DEFAULT_ADVANCED_LINE_CHANGE_HEURISTIC_WEIGHT):
    start_coordinates = (current_stop.lat, current_stop.lon)
    next_coordinates = (next_connection.end_stop.lat, next_connection.end_stop.lon)
    end_coordinates = (goal_stop.lat, goal_stop.lon)

    current_line_is_direct = previous_connection != None and any(previous_connection.line == end_connection.line for end_connection in goal_stop.connections)
    next_line_is_direct = any(next_connection.line == end_connection.line for end_connection in goal_stop.connections)
    line_is_changed = line_changed(previous_connection, next_connection)
    current_distance = dist_func(start_coordinates, end_coordinates)
    next_distance = dist_func(next_coordinates, end_coordinates)

    if current_line_is_direct and line_is_changed:
        heuristic_cost = float('inf') # penalty for changing good line
    elif current_line_is_direct:
        heuristic_cost = 100 * weight if next_distance - current_distance > 0 else 0 # penalty if getting away from goal
    elif next_line_is_direct:
        heuristic_cost = 0 # good change
    elif line_is_changed:
        heuristic_cost = 10 # small penalty
    else:
        heuristic_cost = next_distance

    return heuristic_cost

def time_line_change_heuristic(current_stop, goal_stop, previous_connection, next_connection, dist_func, weight = DEFAULT_ADVANCED_LINE_CHANGE_HEURISTIC_WEIGHT):
    heuristic_time = time_heuristic(current_stop, goal_stop, dist_func)

    if line_changed(previous_connection, next_connection):
        heuristic_time = heuristic_time + 60

    # if all(next_connection.line != end_connection.line for end_connection in goal_stop.connections):
    #     heuristic_time = heuristic_time + 240 

    return heuristic_time
    