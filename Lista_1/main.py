import data_loader
from timer import Timer

timer = Timer()

result = timer.run(data_loader.main)

print(f'Data loaded to graph in {timer.elapsed_time}')
print(result)