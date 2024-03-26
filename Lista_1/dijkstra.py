import heapq
from graph import *
import data_loader
from timer import Timer
from cli_utils import *
import sys

def calculate_time(current_time: int, connection: Connection):
    current_time = current_time % (24 * 60)
    
    wating_time = connection.departure_time - current_time

    if wating_time < 0:
        wating_time = wating_time + 24 * 60

    travel_time = connection.arrival_time - connection.departure_time

    if travel_time < 0:
        travel_time = travel_time + 24 * 60

    return wating_time + travel_time

def dijkstra(graph_dict: dict[str, Stop], start_stop, start_time: int):
    start_stop_node = graph_dict[start_stop]

    times = {node: float('inf') for node in graph_dict.values()}
    times[start_stop_node] = 0
    pq = [(0, start_stop_node)]
    prev_nodes = {node: (None, None) for node in graph_dict.values()}

    while pq:
        curr_time, curr_node = heapq.heappop(pq)

        if curr_time > times[curr_node]:
            continue

        for connection in curr_node.connections:
            new_time = curr_time + calculate_time(curr_time + start_time, connection)

            if new_time < times[connection.end_stop]:
                times[connection.end_stop] = new_time
                prev_nodes[connection.end_stop] = (curr_node, connection)
                heapq.heappush(pq, (new_time, connection.end_stop))

    return times, prev_nodes

def shortest_path(graph_dict, start_stop, goal_stop, start_time):
    times, prev_nodes = dijkstra(graph_dict, start_stop, start_time)

    goal_stop_node = graph_dict[goal_stop]
    path = []
    curr_node, connection = prev_nodes[goal_stop_node]
    while curr_node is not None:
        path.append((curr_node, connection))
        curr_node, connection = prev_nodes[curr_node]
    path.reverse()
    return times[goal_stop_node], path

def main():
    INCORRECT_NUMBER_OF_ARGUMENTS_MESSAGE = "Incorrect number of arguments!"
    INCORRECT_TIME_MESSAGE = "Incorrect time!"
    NO_STOP_FOUND_MESSAGE = "Incorrect name of stop:"

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

    timer = Timer()
    time, path = timer.run(lambda : shortest_path(graph.graph_dict, start_stop, goal_stop, normalized_time))
    
    schedule = travel_schedule(path)
    print_travel_schedule(schedule)

    print(f'Cost value: {time}', f'Computation time: {timer.elapsed_time} s', file=sys.stderr, sep='\n')

if __name__ == '__main__':
    main()
    