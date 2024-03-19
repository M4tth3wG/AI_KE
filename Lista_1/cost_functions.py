from graph import *
import math
from geopy import distance as gp_distance

DEFAULT_ADVANCED_LINE_CHANGE_HEURISTIC_WEIGHT = 0.25
DEFAULT_TIME_HEURISTIC_SPEED = 4.85 / 60 # km/h to km/min


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

def calculate_line_changes(start_time: int, _, previous_connection: Connection, next_connection: Connection):
    if previous_connection == None:
        if start_time > next_connection.departure_time:
            return 1
        else:
            return 0
    
    if previous_connection.line != next_connection.line \
        or previous_connection.arrival_time != next_connection.departure_time:

        return 1

    return 0

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

def advanced_line_change_heuristic(current_stop, goal_stop, previous_connection, next_connection, dist_func, weight = DEFAULT_ADVANCED_LINE_CHANGE_HEURISTIC_WEIGHT):
    start_coordinates = (current_stop.lat, current_stop.lon)
    end_coordinates = (goal_stop.lat, goal_stop.lon)

    if any(next_connection.line == end_connection.line for end_connection in goal_stop.connections):
        return 0
    
    return dist_func(start_coordinates, end_coordinates) * weight

# def time_line_change_heuristic(current_stop, goal_stop, previous_connection, next_connection, dist_func, weight = DEFAULT_ADVANCED_LINE_CHANGE_HEURISTIC_WEIGHT):
#     if previous_connection == None:
#         if start_time > next_connection.departure_time:
#             return 1
#         else:
#             return 0
    
#     if previous_connection.line != next_connection.line \
#         or previous_connection.arrival_time != next_connection.departure_time:

#         return 1

#     return 0