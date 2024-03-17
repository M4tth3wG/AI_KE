import heapq
import math
from graph import *
from geopy import distance as gp_distance
from cli_utils import *
import data_loader
from timer import Timer


def astar(start: Stop, goal: Stop, start_time, cost_fn, heuristic_fn):
    front = [(0, start)]
    came_from = {start: (None, None)}
    cost_so_far = {start: 0}

    while front:
        _, current = heapq.heappop(front)

        if current == goal:
            break

        for connection in current.connections:
            neighbor_stop = connection.end_stop
            current_cost = cost_so_far[current]

            new_cost = current_cost + cost_fn(start_time + current_cost, connection)
            if neighbor_stop not in cost_so_far or new_cost < cost_so_far[neighbor_stop]:
                cost_so_far[neighbor_stop] = new_cost
                priority = new_cost + heuristic_fn(goal, neighbor_stop, came_from[current][1])
                heapq.heappush(front, (priority, neighbor_stop))
                came_from[neighbor_stop] = (current, connection)

    path = []
    current_record = came_from[goal]
    while current_record[0] != start:
        path_tuple = (current_record[0].name, current_record[1])
        path.append(path_tuple)
        current_record = came_from[current_record[0]]
    
    path_tuple = (current_record[0].name, current_record[1])
    path.append(path_tuple)
    path.reverse()

    return path, cost_so_far[goal]


def calculate_time(current_time: int, connection: Connection):
    current_time = current_time % (24 * 60)
    
    wating_time = connection.departure_time - current_time

    if wating_time < 0:
        wating_time = wating_time + 24 * 60

    travel_time = connection.arrival_time - connection.departure_time

    if travel_time < 0:
        travel_time = travel_time + 24 * 60

    return wating_time + travel_time

def euclidean_distance(a, b):
    return gp_distance.distance(a, b).km

def manhattan_distance(a, b):
    lat_distance = gp_distance.distance(a, (b[0], a[1])).km
    lon_distance = gp_distance.distance((b[0], a[1]), b).km
    
    return lat_distance + lon_distance

def time_heuristic(start_stop, end_stop, dist_func, speed_in_km):
    start_coordinates = (start_stop.lat, start_stop.lon)
    end_coordinates = (end_stop.lat, end_stop.lon)
    
    return dist_func(start_coordinates, end_coordinates) / speed_in_km * 60 


def main():
    INCORRECT_NUMBER_OF_ARGUMENTS_MESSAGE = "Incorrect number of arguments!"
    INCORRECT_TIME_MESSAGE = "Incorrect time!"
    NO_STOP_FOUND_MESSAGE = "Incorrect name of stop:"

    AVG_SPEED_KM_PER_H = 40.00
    cost_fn = calculate_time
    heuristic_fn = lambda start, end, _: time_heuristic(start, end, euclidean_distance, AVG_SPEED_KM_PER_H)

    arguments = sys.argv[1:]

    if len(arguments) != 3:
        print(INCORRECT_NUMBER_OF_ARGUMENTS_MESSAGE)
        return
    
    start_stop = arguments[0].lower()
    goal_stop = arguments[1].lower()
    time_str = arguments[2]

    try:
        normalized_time = normalize_input_time(time_str)
    except ValueError:
        print(INCORRECT_TIME_MESSAGE)
        return

    graph = data_loader.load_data_to_graph(data_loader.DATA_FILE_PATH, data_loader.DATA_DELIMITER, False)

    for stop in (start_stop, goal_stop):
        if not stop in graph.graph_dict:
            print(NO_STOP_FOUND_MESSAGE, stop)
            return


    start_stop = graph.graph_dict[start_stop]
    goal_stop = graph.graph_dict[goal_stop]

    timer = Timer()
    path, time = timer.run(lambda : astar(start_stop, goal_stop, normalized_time, cost_fn, heuristic_fn))
    
    schedule = travel_schedule(path)
    print_travel_schedule(schedule)

    print(f'Cost value: {time}', f'Computation time: {timer.elapsed_time} s', file=sys.stderr, sep='\n')

if __name__ == '__main__':
    main()
