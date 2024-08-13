import cProfile
import pstats
import os
import io
import sys

class Profiler:
    def __init__(self, function_call=''):
        self.function_call = function_call
        self.enabled = '--profiling' in sys.argv
        self.profiler = None
        self.stream = io.StringIO()
        self.log_dir = os.path.join(os.getcwd(), 'profilings')
        self.log_file_path = os.path.join(self.log_dir, f"{self.function_call}.log")
        self._setup_log_dir()

    def _setup_log_dir(self):
        os.makedirs(self.log_dir, exist_ok=True)

    def __enter__(self):
        if self.enabled:
            self.profiler = cProfile.Profile()
            self.profiler.enable()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.enabled and self.profiler:
            self.profiler.disable()
            self._save_profiling_data()

    def _save_profiling_data(self):
        stats = pstats.Stats(self.profiler, stream=self.stream)
        stats.sort_stats('tottime')
        stats.print_stats(self.stream)

        with open(self.log_file_path, 'w') as log_file:
            log_file.write(self.stream.getvalue())
