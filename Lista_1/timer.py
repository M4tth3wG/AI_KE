import time

class Timer:
    
    def __init__(self) -> None:
        self.elapsed_time = 0

    def run(self, function):
        start_time = time.time()
        result = function()
        self.elapsed_time = time.time() - start_time
        
        return result