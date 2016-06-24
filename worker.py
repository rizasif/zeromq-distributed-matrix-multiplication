import zmq
import multiprocessing
import json
import sys

class ClusterWorker:
    """Worker that performs the distributed task"""

    NUM_OF_WORKERS = 0
    PROCESSES = []

    def __init__(self, num_of_workers):
        self.NUM_OF_WORKERS = num_of_workers

    def worker_task(self, ident):
        """Worker task, using a REQ socket to do load-balancing."""
        socket = zmq.Context().socket(zmq.REQ)
        socket.identity = u"Worker-{}".format(ident).encode("ascii")
        socket.connect("ipc://backend.ipc")

        # Tell broker we're ready for work
        socket.send(b"READY")

        print ("{} ready".format(socket.identity.decode("ascii")))
        while True:
            address, empty, request = socket.recv_multipart()
            data = json.loads(request)

            json_reply = {
                'solution': [data['data'][0], data['data'][1]*data['data'][2]]
            }

            socket.send_multipart([address, b"", json.dumps(json_reply)])

            print("{}: Data {} Processed form Client {}".format(socket.identity.decode("ascii"), data, address))

    def start(self, *args):
        process = multiprocessing.Process(target=self.worker_task, args=args)
        process.daemon = True
        process.start()
        self.PROCESSES.append(process)

    def start_worker(self):
        """Create workers and make them listen on ports"""
        if self.NUM_OF_WORKERS > 0:
            for i in range(self.NUM_OF_WORKERS):
                self.start(i)

            for p in self.PROCESSES:
                p.join()
            return True
        else:
            ValueError("Number of workers not specified")
            return False

if __name__ == "__main__":

    if len(sys.argv)>1 and int(float(sys.argv[1])) > 0:
        worker = ClusterWorker(int(float(sys.argv[1])))
        worker.start_worker()
    else:
        worker = ClusterWorker(sys.argv[1])
        worker.start_worker()

    print("Workers Started")