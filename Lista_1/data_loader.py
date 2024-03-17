import pandas as pd
import pathlib
import graph

DATA_FOLDER = 'Data'
DATA_FILE_NAME = 'connection_graph.csv'
DATA_DELIMITER = ','
DATA_FILE_PATH = pathlib.Path(DATA_FOLDER).joinpath(DATA_FILE_NAME)

def normalize_time(time_str):
    hour, minute, *_ = map(int, time_str.split(':'))
    hour = hour % 24

    return hour * 60 + minute

def normalize_time_in_dataframe(dataframe: pd.DataFrame):
    dataframe[['departure_time', 'arrival_time']] = dataframe[['departure_time', 'arrival_time']].map(normalize_time).astype(int)

    return dataframe

def normalize_coordinates_in_dataframe(dataframe: pd.DataFrame):  
    average_start_stop = dataframe.groupby('start_stop').agg({'start_stop_lat': 'mean', 'start_stop_lon': 'mean'}).reset_index()
    average_end_stop = dataframe.groupby('end_stop').agg({'end_stop_lat': 'mean', 'end_stop_lon': 'mean'}).reset_index()
    
    dataframe = dataframe.merge(average_start_stop, on='start_stop', how='left', suffixes=('', '_mean'))
    dataframe = dataframe.merge(average_end_stop, on='end_stop', how='left', suffixes=('', '_mean'))


    dataframe['start_stop_lat'] = dataframe['start_stop_lat_mean']
    dataframe['start_stop_lon'] = dataframe['start_stop_lon_mean']

    dataframe['end_stop_lat'] = dataframe['end_stop_lat_mean']
    dataframe['end_stop_lon'] = dataframe['end_stop_lon_mean']

    dataframe.drop(['start_stop_lat_mean', 'start_stop_lon_mean', 'end_stop_lat_mean', 'end_stop_lon_mean'], axis=1, inplace=True)

    return dataframe

def load_data_to_graph(file_path, delimeter, normalize_coordinates=False):
    df = pd.read_csv(file_path, delimiter=delimeter, low_memory=False)

    # df['start_stop'] = df['start_stop'].str.lower()
    # df['end_stop'] = df['end_stop'].str.lower()
    df = normalize_time_in_dataframe(df)

    if normalize_coordinates:
        df = normalize_coordinates_in_dataframe(df)

    df_subset = df.iloc[:, 2:]
    records = list(df_subset.to_records(index=False))

    return graph.Graph(records)

def main():
    #graph = load_data_to_graph(DATA_FILE_PATH, DATA_DELIMITER, True)
    
    #print(len(graph.graph_dict))

    df = pd.read_csv(DATA_FILE_PATH, delimiter=DATA_DELIMITER, low_memory=False)

    df = normalize_time_in_dataframe(df)

    result = df[df['departure_time'] > df['arrival_time']]

    print(result[result['end_stop'] == 'Wrocławski Park Przemysłowy'])

if __name__ == '__main__':
    main()