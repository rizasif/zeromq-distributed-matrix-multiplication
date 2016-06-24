
#Matrix Multiplication Cluster
This project impliments distributed computing architecture to perform matrix multiplication.
The major dependacy to this project is ZeroMQ. The program runs on IPC mechanism.

#Running the program
Follow these steps in order to run the code

1) Start Server:

The server is responsible for taking requests from clients; distribute and route the task to workers; combine data from different workers and send the results to relevant client.
	
		 $ python server.py 
		
2) Start Workers:

The workers directly communicate with the server using REQ sockets. Their basic task is do the calculation part for the server. You can create multiple workets
		
		 $ python worker.py <no. of workers> 
		
3) Start Client:
	
The client randomly generates two nxn matrices, where n can any number between 2-5 and each element of the matrix between 0-100. The client direclty communicates with the server using a REQ socket. You may create multiple clients.
		
		 $ python client.py <no. of clients> 
		


For more info please see the PDF attached

Created by Rizwan Asif 12beerasif@seecs.edu.pk
