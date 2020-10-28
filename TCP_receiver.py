from socket import *
import sys
import time
import threading

if len(sys.argv) < 7:
	print("Usage: python xxx.py HELLO S <loss_rate> <corrupt_rate> <max_delay> <ID>")
	exit()
# Takes command line arguments
# Server IP address (str)
# Server Port number (int)
server_IP = "gaia.cs.umass.edu"
server_Port = 20000
# Sender or Receiver
sender_or_receiver = sys.argv[2]
# loss_rate
loss_rate = float(sys.argv[3])
loss_rate_str = sys.argv[3]
# corrupt_rate
corrupt_rate = float(sys.argv[4])
currupt_rate_str = sys.argv[4]
# max_delay
max_delay = int(sys.argv[5])
max_delay_str = sys.argv[5]
# Connection ID of the client
ID = int(sys.argv[6])
ID_str = sys.argv[6]
# Message: in the form of "HELLO S <loss_rate> <corrupt_rate> <max_delay> <ID>" with a white space between them
Message = sys.argv[1] + " " + sender_or_receiver + " " + loss_rate_str + " " + currupt_rate_str + " " + max_delay_str + " " + ID_str

print("Message: {}".format(Message))
# Create an TCP socket
# client_socket = socket(AF_INET, SOCK_STREAM)
# Set the maximum wait time for the client
# client_socket.settimeout(10)
# Count the total trial numbers
trial = 0
# Flag which indicates if the data is sent
sendto = True



s = socket(AF_INET, SOCK_STREAM)
s.settimeout(5)
s.connect((server_IP, server_Port))


s.send(bytes(Message, encoding='utf-8'))
while True:
	try:
		time.sleep(0.1)
		data = s.recv(1024).decode("utf-8")
		# if not data:
			# print("no data")
			# break
		print(data)
	except KeyboardInterrupt:
		print("bye")
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
