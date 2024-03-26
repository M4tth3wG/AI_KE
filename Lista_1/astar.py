import heapq
from graph import *
from cli_utils import *
import data_loader
from timer import Timer
import cost_functions as cf

TIME_HEURISTIC_WEIGHT = 4.85 / 60 # km/h to km/min
TIME_COST_FUNCTION = lambda start_time, current_cost, end, _, connection : cf.calculate_time(start_time, current_cost, connection)
TIME_HEURISTIC = lambda start_time, start, end, test, _: cf.time_heuristic(start_time, start, end, cf.euclidean_distance_gp, TIME_HEURISTIC_WEIGHT)

LINE_CHANGE_HEURITSTIC_WEIGHT = 10
LINE_CHANGE_COST_FUNCTION = lambda start_time, _, end, previous_connection, next_connection : cf.line_changes_cost(start_time, end, previous_connection, next_connection)
LINE_CHANGE_HEURISTIC = lambda start_time, current, end, previous_connection, next_connection: cf.advanced_line_change_heuristic(start_time, current, end, previous_connection, next_connection, cf.euclidean_distance_gp, LINE_CHANGE_HEURITSTIC_WEIGHT)


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
            previous_connection = came_from[current][1]

            new_cost = current_cost + cost_fn(start_time, current_cost, goal, previous_connection, connection)

            if neighbor_stop not in cost_so_far or new_cost < cost_so_far[neighbor_stop]:

                cost_so_far[neighbor_stop] = new_cost
                priority = new_cost + heuristic_fn(start_time, current, goal, previous_connection, connection)
                heapq.heappush(front, (priority, neighbor_stop))
                came_from[neighbor_stop] = (current, connection)

    path = []
    current_record = came_from[goal]
    while current_record[0] != start:
        path_tuple = (current_record[0], current_record[1])
        path.append(path_tuple)
        current_record = came_from[current_record[0]]
    
    path_tuple = (current_record[0], current_record[1])
    path.append(path_tuple)
    path.reverse()

    return cost_so_far[goal], path

def main():
    INCORRECT_NUMBER_OF_ARGUMENTS_MESSAGE = "Incorrect number of arguments!"
    INCORRECT_TIME_MESSAGE = "Incorrect time!"
    NO_STOP_FOUND_MESSAGE = "Incorrect name of stop:"
    INCORRECT_OPTIMIZATION_CRITERIUM_MESSAGE = "Incorrect optimization option!"

    arguments = sys.argv[1:]

    if len(arguments) != 4:
        print(INCORRECT_NUMBER_OF_ARGUMENTS_MESSAGE)
        return
    
    start_stop = arguments[0].lower()
    goal_stop = arguments[1].lower()
    optimization_criterium = arguments[2].lower()
    time_str = arguments[3]

    try:
        normalized_time = normalize_input_time(time_str)
    except ValueError:
        print(INCORRECT_TIME_MESSAGE)
        return
    
    options_dict = {
        't' : (TIME_COST_FUNCTION, TIME_HEURISTIC),
        'p' : (LINE_CHANGE_COST_FUNCTION, LINE_CHANGE_HEURISTIC)
        }

    if optimization_criterium in options_dict:
        options = options_dict[optimization_criterium]
    else:
        print(INCORRECT_OPTIMIZATION_CRITERIUM_MESSAGE)
        return
    
    cost_fn, heuristic_fn = options

    graph = data_loader.load_data_to_graph(data_loader.DATA_FILE_PATH, data_loader.DATA_DELIMITER, True)

    for stop in (start_stop, goal_stop):
        if not stop in graph.graph_dict:
            print(NO_STOP_FOUND_MESSAGE, stop)
            return
    
    start_stop = graph.graph_dict[start_stop]
    goal_stop = graph.graph_dict[goal_stop]

    timer = Timer()
    time, path = timer.run(lambda : astar(start_stop, goal_stop, normalized_time, cost_fn, heuristic_fn))
    
    schedule = travel_schedule(path)
    print_travel_schedule(schedule)

    print(f'Cost value: {time}', f'Computation time: {timer.elapsed_time} s', file=sys.stderr, sep='\n')

    map = create_map(path)
    open_map(map)

if __name__ == '__main__':
    main()
