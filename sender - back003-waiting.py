from socket import *
import sys
from time import sleep
import threading

# Check the number of command line arguments
if len(sys.argv) < 5:
	print("Usage: python sender.py <connection_id> <loss_rate> <corrupt_rate> <max_delay> <transmission_timeout>")
	exit()
# Server IP address (str)
# Server Port number (int)
# server_IP = "127.0.0.1"
# server_Port = 80
server_IP = "gaia.cs.umass.edu"
server_Port = 20000

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

# sender or receiver
sender_or_receiver = "S"

# Message: in the form of "HELLO S <loss_rate> <corrupt_rate> <max_delay> <ID>" with a white space between them
Message = "HELLO" + " " + sender_or_receiver + " " + loss_rate_str + " " + currupt_rate_str + " " + max_delay_str + " " + ID_str
print("Message: {}".format(Message))
print(Message.split())
# Message = "HELLO S 0.0 0.0 0 1234"

# Create an TCP socket
s = socket(AF_INET, SOCK_STREAM)
# Set the maximum wait time for the client
s.settimeout(10)

try:
	# Connect to the server
	s.connect((server_IP, server_Port))
except OSError:
	print("A connect request was made on an already connected socket")
	s.close()
except ConnectionRefusedError:
	print("connection was REFUSED.")
	s.close()
	exit()


while True:
	try:
		sleep(0.5)
		# Send the message
		s.send(bytes(Message, encoding='utf-8'))
		data = s.recv(1024).decode("utf-8")
		data_split = data.split()
		print(data, data_split)
		# if not data:
			# print("no data")
			# break
		if len(data) != 0:
			if data_split[0] == "ERROR":
				print(data)
				break
			if data_split[0] == "WAITING":
				print(data)
				sleep(5)
		else:
			print("No data")
			sleep(1)
		# sleep(2)
	except KeyboardInterrupt:
		print("KeyboardInterrupt")
		s.close()
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

	# except ConnectionAbortedError:
		# print(data)
		# s.close()
		# break


s.close()
