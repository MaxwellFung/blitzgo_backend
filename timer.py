import threading
import time

class Timer:
    def __init__(self, duration, callback):
        self.duration = duration
        self.callback = callback
        self.end_time = None
        self._lock = threading.Lock()
        self.running = False
        self.paused = True
        self.timeout = False  # Flag to indicate if the timer has expired
        self.thread = threading.Thread(target=self._run)
        self.thread.daemon = True  # Ensure the thread does not prevent the program from exiting

    def start(self):
        with self._lock:
            if not self.running:
                self.running = True
                self.paused = False
                self.timeout = False  # Reset timeout on start
                self.end_time = time.time() + self.duration
                self.thread.start()

    def pause(self):
        with self._lock:
            if not self.paused:
                self.paused = True
                self.duration = self.end_time - time.time()  # Update remaining duration

    def resume(self):
        with self._lock:
            if self.paused:
                self.paused = False
                self.end_time = time.time() + self.duration

    def _run(self):
        while self.running:
            time.sleep(0.1)  # Reduce CPU usage
            with self._lock:
                if not self.paused and time.time() >= self.end_time:
                    self.running = False
                    self.timeout = True  # Set timeout flag to True
                    self.callback()  # Call the callback function when time is up

    def get_remaining_time(self):
        with self._lock:
            if self.paused:
                return self.duration
            else:
                return max(0, self.end_time - time.time())

    def has_timed_out(self):
        return self.timeout