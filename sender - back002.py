from socket import *
import sys
import time
import threading

# Check the number of command line arguments
if len(sys.argv) < 5:
	print("Usage: python sender.py <connection_id> <loss_rate> <corrupt_rate> <max_delay> <transmission_timeout>")
	exit()
# Server IP address (str)
# Server Port number (int)
server_IP = "127.0.0.1"
server_Port = 80
# server_IP = "gaia.cs.umass.edu"
# server_Port = 20000

# Connection ID of the client
ID_str = sys.argv[1]
ID = int(ID_str)

# loss_rate
loss_rate_str = sys.argv[2]
loss_rate = float(loss_rate_str)

# corrupt_rate
currupt_rate_str = sys.argv[3]
corrupt_rate = float(currupt_rate_str)

# max_delay
max_delay_str = sys.argv[4]
max_delay = int(max_delay_str)

# transmission_timeout
transmission_timeout_str = sys.argv[5]
transmission_timeout = int(transmission_timeout_str)


# Message: in the form of "HELLO S <loss_rate> <corrupt_rate> <max_delay> <ID>" with a white space between them
Message = ID_str + " " + loss_rate_str + " " + currupt_rate_str + " " + max_delay_str + " " + transmission_timeout_str
print("Message: {}".format(Message))


# Create an TCP socket
s = socket(AF_INET, SOCK_STREAM)
# Set the maximum wait time for the client
s.settimeout(10)

try:
	# Connect to the server
	s.connect((server_IP, server_Port))
except ConnectionRefusedError:
	print("connection was REFUSED.")
	s.close()
	exit()


while True:
	try:
		time.sleep(0.1)
		# Send the message
		s.send(bytes(Message, encoding='utf-8'))
		data = s.recv(1024).decode("utf-8").split()
		# if not data:
			# print("no data")
			# break
		print(data)
	except KeyboardInterrupt:
		print("bye")
		break
	except timeout:
		# After Maximum time, the server is closing the opened socket and exit.
		print("TCP Server Closing... Max time out reached: {} seconds".format(maxWaitTime))
		s.close()
		break

	except ConnectionResetError:
		print("connection was CLOSED.")
		s.close()
		break



# print("\t\t\tdata:{}".format(data), end=" ")
# data_str = data.decode("utf-8") 

# while data == "WAITING":
# 	# s.send(bytes(Message, encoding='utf-8'))
# 	data = s.recv(1024).decode("utf-8")
# 	print(data)
# 	time.sleep(2)


# with socket(AF_INET, SOCK_STREAM) as s:
	# s.connect((server_IP, server_Port))
	# s.settimeout(3)
	# data = s.recv(1024)


	# while True:
	# time.sleep(1)



# while True:
# 	try:
# 		client_socket.send(bytes(Message, encoding='utf-8'))

# 		# Recive data
# 		data = client_socket.recv(1024)
# 		print("\t\t\tdata:{}".format(data), end=" ")
# 		# Flip the flag

# 	except:
# 		pass

	# # If the data is sent:
	# if sendto == True:
	# 	try:
	# 		# Recive data
	# 		data = client_socket.recv(1024)
	# 		print("\t\t\tdata:{}".format(data), end=" ")
	# 		# Flip the flag
	# 		sendto = False
	# 	# If Maximum timeout exceeded
	# 	except timeout:
	# 		print("\t\t\t\t\t\tTimeout!")
	# 		# Count one trial
	# 		trial += 1
	# 		sendto = False
	# # If the data is not sent yet:
	# else:
	# 	try:
	# 		# If trial number exceeded, then exit
	# 		if trial >= 3:
	# 			print("Connection Failure")
	# 			break
	# 		# Connect to the TCP server
	# 		client_socket.connect((server_IP, server_Port))
	# 		# Send the message
	# 		client_socket.send(bytes(Message, encoding='utf-8'))
	# 		# Receive the data from the TCP server
	# 		data = client_socket.recv(1024)
	# 		# Decode the data and split by token
	# 		message = data.decode('ascii').split()
	# 		# If received OK message:
	# 		if message[0] == "OK":
	# 			# Extract client Id, client IP address, client Port number in the server
	# 			recv_id = message[1]
	# 			recv_ip = message[2]
	# 			recv_port = message[3]
	# 			print("Connection established {} {} {}".format(recv_id, recv_ip, recv_port))
	# 			break
	# 		# If received RESET message
	# 		elif message[0] == "RESET":
	# 			sendto = False
	# 			print("Connection Error {}".format(Connection_ID_str))
	# 			break

	# 	# If timed out the maximum time
	# 	except timeout:
	# 		print("\t\t\t\t\t\t\ttimeout")
	# 		print("Connection Error {}".format(Connection_ID_str))
	# 		sendto = False

	# 	# If failed the connection to the server
	# 	except ConnectionRefusedError:
	# 		sendto = True
	# 		print("Connection Error {}".format(Connection_ID_str))
			
	# 		##### This is the part I can choose whether or not to take user input when the connection failed.
	# 		##### Comment below parts out to get the user input.
	# 		# new_id = input("Enter different client ID: ")
	# 		# Connection_ID = int(new_id)
	# 		# Connection_ID_str = new_id
	# 		# Message = sys.argv[1] + new_id
	# 		pass


s.close()
