import multiprocessing
import zmq
import random
import json
import sys
import time

class ClusterClient:
    """The Client which sends matrix to broker"""

    NUM_OF_CLIENTS = 0 # Total Number of Clients
    PROCESSES = [] # Keeps track of the multithreaded processes (clients)

    def __init__(self, num_of_clients = 1):
        self.NUM_OF_CLIENTS = num_of_clients

    def client_task(self, ident, matA, matB):
        """Basic request-reply client using REQ socket."""
        socket = zmq.Context().socket(zmq.REQ)
        socket.identity = u"Client-{}".format(ident).encode("ascii")
        socket.connect("ipc://frontend.ipc")

        # Create a list to be sent as json packet
        json_data1 = {
            'matrix_A' : matA,
            'matrix_B' : matB
        }

        json_data = json.dumps(json_data1)

        # Send request, get reply
        socket.send_json(json_data)
        print ("Message sent by: {}".format(ident))
        tstart = time.time()
        reply = socket.recv_json()
        tend = time.time()

        print ("----------------------------------------")
        print("{}".format(socket.identity.decode("ascii")))
        print ("matA: {}".format(matA))
        print ("matB: {}".format(matB))
        print ("Solution: {}".format(reply['Solution']))
        print("Total elapsed time: %d msec" % ((tend - tstart) * 1000))
        print ("----------------------------------------")


    def start(self, *args):
        process = multiprocessing.Process(target=self.client_task, args=args)
        process.daemon = True
        process.start()
        self.PROCESSES.append(process)

    def generate_random_matrix(self):
        """Create random matrices"""

        # Randomly choose n for nxn matrix between 2 to 5
        n = random.randrange(2, 5)

        # Randomly create nxn matrices for each element range between 1 to 100
        matA = [[random.randrange(0, 100) for x in range(n)] for y in range(n)]
        matB = [[random.randrange(0, 100) for x in range(n)] for y in range(n)]

        return matA, matB

    def begin_transmission(self):
        """Create random matrices and start transmission"""
        if self.NUM_OF_CLIENTS > 0:
            for i in range(self.NUM_OF_CLIENTS):
                matA, matB = self.generate_random_matrix()
                self.start(i, matA, matB)
                print ("Client-{} Running".format(i))
            for p in self.PROCESSES:
                p.join()
            return True
        else:
            ValueError("Number of clients not specified")
            return False

if __name__ == "__main__":
    if len(sys.argv) > 1 and int(float(sys.argv[1])) > 0:
        client = ClusterClient(int(float(sys.argv[1])))
        client.begin_transmission()
    else:
        client = ClusterClient(2)
        client.begin_transmission()

    print("Clients Started")