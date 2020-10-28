from socket import *
import sys
import threading
import time

# Take command line arguments:
# Server IP address (str)
# Server Port number (int)
Server_IP = sys.argv[1]
Server_Port = int(sys.argv[2])

# Create a TCP socket and bind to the server address and port number
server_socket = socket(AF_INET, SOCK_STREAM)
server_socket.bind((Server_IP, Server_Port))
# Sets the maximum number of TCP connection
server_socket.listen(5)

# connectIdList : A python list which will store cliend ID numbers in order
# timers : A python list which will store python Timer object which will kill the corresponding client ID from connectIdList
connectIdList = []
timers = []

# This function is called by a Timer object.
# After a specific time of the Tiber object, the object will find the corredponding ID.
# Then, it removed the cliend ID.
# Finally, the thread is killed.
def remove_client(client_id, sleep):
	print("Killing... the client [{}]".format(client_id, client_id))
	idx = connectIdList.index(client_id)
	connectIdList.remove(client_id)
	timers[idx].should_abort_immediately = True
	return

# Maximum wait time for the UDP server
maxWaitTime = 300.0
server_socket.settimeout(maxWaitTime)
while True:
	try:
		# TCP server accepts the connection through the socket.
		conn, address = server_socket.accept()
		# Receive the data from TCP connection with 1024 bytes buffer
		data = conn.recv(1024)
		# Decode the bytes type data into ascii string
		message = data.decode('ascii')
		print(message)
		# Client ID is the last four digits
		client_id = message[-4:]
		# Message is the front part excluding the client ID and a white space
		message = message[:-5]
		# address is a tuple of (Client_IP, Client_Port)
		client_ip_address = address[0]
		client_port = address[1]

		# If this client ID is a new number, then save the ID and send OK message
		if client_id not in connectIdList:
			# Add the client ID
			connectIdList.append(client_id)
			# After 60 seconds, the Timer object will kill this client ID
			sleep = 60.0
			# Create a concurrent Timer object
			tt = threading.Timer(sleep, remove_client, [client_id, sleep])
			# Add the Timer object
			timers.append(tt)
			# Timer starts
			tt.start()
			# OK message
			sending_message = "OK " + client_id + " " + client_ip_address + " " + str(client_port)
		# If this client ID is already exist in the list, then send RESET message
		else:
			# RESET message
			sending_message = "RESET " + client_id

		# Encode the sending message to send back
		data = sending_message.encode('ascii')
		# Send the message to the address
		conn.send(bytes(sending_message, encoding='utf-8'))
		print("Sending Message to the client[{}]: {}".format(client_id, sending_message))

	except timeout:
		# After Maximum time, the server is closing the opened socket and exit.
		print("TCP Server Closing... Max time out reached: {} seconds".format(maxWaitTime))
		server_socket.close()
		break

	except KeyboardInterrupt:
		print("bye")
		break
