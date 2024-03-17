import dataclasses
from typing import List

class Graph:

    def __init__(self, record):
        self.graph_dict : dict[str, Stop] = {}

        for line, departure_time, arrival_time, start_stop, end_stop, start_stop_lat, start_stop_lon, end_stop_lat, end_stop_lon in record:

            if end_stop in self.graph_dict:
                end_stop_node = self.graph_dict[end_stop]
            else:
                end_stop_node = Stop(end_stop, end_stop_lat, end_stop_lon, [])
                self.graph_dict[end_stop] = end_stop_node

            if start_stop in self.graph_dict:
                start_stop_node = self.graph_dict[start_stop]
            else:
                start_stop_node = Stop(start_stop, start_stop_lat, start_stop_lon, [])
                self.graph_dict[start_stop] = start_stop_node

            connection = Connection(line, departure_time, arrival_time, end_stop_node)
            start_stop_node.connections.append(connection)

@dataclasses.dataclass(eq=False, repr=False)
class Stop:
    name : float
    lat : float
    lon : float
    connections : List['Connection']

    def __eq__(self, __value: object) -> bool:
        return self.name == __value.name
    
    def __hash__(self) -> int:
        return hash(self.name)
    
    def __repr__(self) -> str:
        return self.name

@dataclasses.dataclass()
class Connection:
    line : str
    departure_time : int
    arrival_time : int
    end_stop : Stop

def main():
    foo = Stop('foo', 1.0, 1.0, [])
    bar = Stop('bar', 2.0, 2.0, [Connection('A', 1, 2, foo)])
    bar.connections[0].end_stop.name = 'test'
    print(foo)

if __name__ == '__main__':
    main()