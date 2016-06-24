import zmq
import json


class server:
    """A server that receives, distributes the task and collects results from workers"""

    CLIENT_DICT = {} # Contains data for ever client and keeps track of completion of distributed tasks
    WORK_STACK = [] # A Stack maintained by server to be sent to worker when free. Implements FIFO

    def __init__(self):
        print ("Server Initalized")

    def isValid(self, matA, matB):
        if(len(matA) == len(matB) and len(matA[0]) == len(matB[0])):
            return True
        else:
            return False

    def make_pairs(self, matA, matB):
        ans = [];
        for i in range(len(matB)):
            for j in range(len(matB[0])):
                for k in range(len(matA[j])):
                    ans.append(
                        [k * 10 + j, matA[k][i], matB[i][j]]
                    );

        return ans

    def add_to_stack(self, data, Client):
        for element in data:
            self.WORK_STACK.append([Client, element])

    def run(self):
        # Prepare context and sockets
        context = zmq.Context.instance()
        frontend = context.socket(zmq.ROUTER)
        frontend.bind("ipc://frontend.ipc")
        backend = context.socket(zmq.ROUTER)
        backend.bind("ipc://backend.ipc")

        # Initialize main loop state
        workers = []
        poller = zmq.Poller()
        # Only poll for requests from backend until workers are available
        poller.register(backend, zmq.POLLIN)

        print ("Server Started")

        while True:
            sockets = dict(poller.poll())

            if backend in sockets:
                print ("Worker Replied")
                # Handle worker activity on the backend
                request = backend.recv_multipart()
                print (request)
                worker, empty, client = request[:3]
                if not workers:
                    # Poll for clients now that a worker is available
                    poller.register(frontend, zmq.POLLIN)
                workers.append(worker)
                if client != b"READY" and len(request) > 3:
                    # If client reply, send rest back to frontend
                    empty, reply = request[3:]

                    #Parse Reply Message
                    data = json.loads(reply)['solution']

                    #Getting index of processed task
                    index = data[0]

                    # Adding solution as part of algorithm
                    self.CLIENT_DICT[client]['Solution'][index/10][index%10] += data[1]

                    #Incrementing that task is received
                    self.CLIENT_DICT[client]['RecTasks'] += 1

                    #print (self.CLIENT_DICT)
                    #print (self.WORK_STACK)

                    if(self.CLIENT_DICT[client]['RecTasks'] == self.CLIENT_DICT[client]['TotalTasks']):
                        json_rep = {
                            'Solution': self.CLIENT_DICT[client]['Solution']
                        }
                        frontend.send_multipart([client, b"", json.dumps(json_rep)])
                        print ("Done with {}".format(client))


            if frontend in sockets:
                # Get next client request, route to last-used worker
                client, empty, request = frontend.recv_multipart()

                print("Request Received from {}".format(client))

                #parse json request
                data = json.loads(request)
                data = json.loads(data)

                #Reply with error if matrices not square
                if(not self.isValid(data['matrix_A'], data['matrix_B'])):
                    ValueError("Matrixes Should be Square")
                    json_rep = {
                        'data': "Error"
                    }
                    frontend.send_multipart([client, b"", task[0], b"", json.dumps(json_rep)])
                    continue

                #Divide request in small tasks
                tasks = self.make_pairs(data['matrix_A'], data['matrix_B'])

                # size of nxn matrix
                n = len(data['matrix_A'])

                #Add the tasks to stack
                self.add_to_stack(tasks, client)

                self.CLIENT_DICT[client] = {}

                #Maintain the client in dictionary
                self.CLIENT_DICT[client]['TotalTasks'] = len(tasks)
                self.CLIENT_DICT[client]['RecTasks'] = 0
                self.CLIENT_DICT[client]['Solution'] = [[0 for x in range(n)] for y in range(n)] #Create a zero matrix for solution

                #print ("Task-1 AWAY")
                #print (self.CLIENT_DICT)
                #print (tasks)

            for worker in workers:
                if(len(self.WORK_STACK) > 0):
                    task = self.WORK_STACK.pop() # i.e task = [ClientID, Element]
                    #print ("Sending task {}".format(task))
                    json_req = {
                        'data': task[1]
                    }
                    backend.send_multipart([worker, b"", task[0], b"", json.dumps(json_req)])
                    workers.remove(worker)

            #if not workers:
                # Don't poll clients if no workers are available
                #poller.unregister(frontend)

        # Clean up
        backend.close()
        frontend.close()
        context.term()

if __name__ == "__main__":
    MyServer = server()
    MyServer.run()