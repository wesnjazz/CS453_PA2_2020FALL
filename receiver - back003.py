from socket import *
import sys
import time
import threading

# Check the number of command line arguments
if len(sys.argv) < 4:
	print("Usage: python sender.py <connection_id> <loss_rate> <corrupt_rate> <max_delay>")
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

# Message: in the form of "HELLO S <loss_rate> <corrupt_rate> <max_delay> <ID>" with a white space between them
Message = ID_str + " " + loss_rate_str + " " + currupt_rate_str + " " + max_delay_str
print("Message: {}".format(Message))


## local connect (make receiver as host) ##
# Create an TCP socket
s = socket(AF_INET, SOCK_STREAM)
s.bind((server_IP, server_Port))
s.listen(5)

## gaia server (connect as a client) ##
# Create an TCP socket
s = socket(AF_INET, SOCK_STREAM)
s.connect((server_IP, server_Port))
# s.bind((server_IP, server_Port))
# s.listen(5)


# Set the maximum wait time for the client
s.settimeout(10)

maxWaitTime = 10.0
while True:
	try:
		conn, address = s.accept()
		data = conn.recv(1024)
		message = data.decode("utf-8").split()
		time.sleep(0.1)
		print(message)
		sending_message = "OK"
		conn.send(bytes(sending_message, encoding='utf-8'))

	except KeyboardInterrupt:
		print("bye")
		s.close()
		break

	except timeout:
		# After Maximum time, the server is closing the opened socket and exit.
		print("TCP Server Closing... Max time out reached: {} seconds".format(maxWaitTime))
		s.close()
		break


s.close()
