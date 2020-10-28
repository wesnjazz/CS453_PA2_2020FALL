from socket import *
import sys
from time import sleep
import threading
from utils import *


# Check the number of command line arguments
if len(sys.argv) < 4:
	print("Usage: python sender.py <connection_id> <loss_rate> <corrupt_rate> <max_delay>")
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
currupt_rate_str = sys.argv[3]# Connection ID of the client
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

# sender or receiver
sender_or_receiver = "R"

# Message: in the form of "HELLO S <loss_rate> <corrupt_rate> <max_delay> <ID>" with a white space between them
Message = "HELLO" + " " + sender_or_receiver + " " + loss_rate_str + " " + currupt_rate_str + " " + max_delay_str + " " + ID_str
print("Message: {}".format(Message))
print(Message.split())
print()



## local connect (make receiver as host) ##
# Create an TCP socket
s = socket(AF_INET, SOCK_STREAM)
s.bind((server_IP, server_Port))
s.listen(5)
# Set the maximum wait time for the client
maxWaitTime = 15
s.settimeout(maxWaitTime)


message_OK = False

###  OK message  ###
conn, address = s.accept()
while not message_OK:
	try:
		# sleep(1)
		print("\nreceiving...")
		data_len, data = rdt_rcv(conn)
		data_split = data.split()
		print(data_len, data, data_split)
		send_pkt = make_pkt(0, data)
		# Send the message
		# sleep(3)
		print("\nsending...")
		conn.send(bytes("ASDFASDFA", encoding='utf-8'))
		cnt = 0
		# while cnt < 10:
		# 	print("sending... {}".format(send_pkt))
		# 	conn.send(bytes("ASDFASDFA", encoding='utf-8'))
		# 	cnt += 1
		# 	sleep(1)
		# data = s.recv(1024).decode("utf-8")
		# data_len, data = rdt_rcv(s)
		# print("CONTINUE")
		continue
		# if not data:
			# print("no data")
			# break
		if len(data) != 0:
			if data_split[0] == "OK":
				message_OK = True
			if data_split[0] == "ERROR":
				print(data)
				# break
			if data_split[0] == "WAITING":
				print(data)
				# sleep(5)
		else:
			print("No data")
			# sleep(1)
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

print("OK Message")



s.close()
