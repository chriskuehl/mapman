import threading
# TODO: replace this terrible code with something reasonable

class Parallel():
    max = 20
    stack = []
    threads = []

    def start(self, func):
        def wrapper():
            func()

            try:
                self.threads.remove(threading.current_thread())
            except ValueError:
                pass

            self.next()

        thread = threading.Thread(target=wrapper)
        self.stack.append(thread)
        self.next()

    def next(self):
        if self.stack and len(self.threads) < self.max:
            thread = self.stack.pop()
            thread.start()
            self.threads.append(thread)

    def wait(self):
        while self.threads or self.stack:
#            print("threads={} stack={}".format(len(self.threads), len(self.stack)))
            if self.threads:
                thread = self.threads[0]
                thread.join()
