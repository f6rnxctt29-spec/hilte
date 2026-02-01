import threading, queue, time

class Runner:
    def __init__(self, config):
        self.config = config
        self.q = queue.Queue()
        self.running = False

    def start(self):
        if self.running:
            return
        self.running = True
        t = threading.Thread(target=self._worker, daemon=True)
        t.start()

    def _worker(self):
        while self.running:
            try:
                task = self.q.get(timeout=1)
                # simple dispatcher placeholder
                print("Running task:", task)
                self.q.task_done()
            except Exception:
                time.sleep(1)

    def stop(self):
        self.running = False
