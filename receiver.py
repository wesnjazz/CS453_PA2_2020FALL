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
# Message = "HELLO" + " " + sender_or_receiver + " " + loss_rate_str + " " + currupt_rate_str + " " + max_delay_str + " " + ID_str
# print("Message: {}".format(Message))
# print(Message.split())
# Message = "HELLO S 0.0 0.0 0 1234"

# # Message: in the form of "HELLO S <loss_rate> <corrupt_rate> <max_delay> <ID>" with a white space between them
# Message = ID_str + " " + loss_rate_str + " " + currupt_rate_str + " " + max_delay_str
# print("Message: {}".format(Message))


# ## local connect (make receiver as host) ##
# # Create an TCP socket
# s = socket(AF_INET, SOCK_STREAM)
# s.bind((server_IP, server_Port))
# s.listen(5)

## gaia server (connect as a client) ##
# Create an TCP socket
s = socket(AF_INET, SOCK_STREAM)
# s.connect((server_IP, server_Port))
s.bind((server_IP, server_Port))
s.listen(5)


# Set the maximum wait time for the client
maxWaitTime = 15
s.settimeout(maxWaitTime)
# s.send(bytes(Message, encoding='utf-8'))


message_OK = False


FSM = {"State 1": 1, # Wait for call 0 from below
	   "State 2": 2, # Wait for call 1 from below
	  }



Timer = False
file = ""
conn, address = s.accept()
state = FSM["State 1"]
while True:
	if state == FSM["State 1"]:
		print("State 1")
		print("\nreceiving...")
		rcvpkt_len, rcvpkt = rdt_rcv(conn)
		print("State 1 - received : [{}], [{}]".format(rcvpkt_len, rcvpkt))
		if not isCorrupt(rcvpkt) and has_seq(rcvpkt, 0):
			print("\t\tState 1 - not isCorrupt() && has_seq(0)")
			print("\t\t\tfile:[{}]".format(file), end=" ")
			file += extract(rcvpkt)
			print("\t\t\tfile:[{}]".format(file))
			data = rcvpkt[4:-6]
			print("\t\t\tdata:[{}]".format(data))
			chk_rcv = checksum(data)
			print("\t\t\tchk_rcv:[{}]".format(chk_rcv))
			send_pkt = make_pkt_rcv(0, 0, chk_rcv)
			print("\nsending... [{}]".format(send_pkt))
			udt_send(conn, send_pkt)
			sleep(2)
			state = FSM["State 2"]
		else:
			print("\t\tState 1 - isCorrupt() || has_seq(1)")
			send_pkt = make_pkt_rcv(0, 1, chk_rcv)
			print("\nsending... [{}]".format(send_pkt))
			udt_send(conn, send_pkt)
			sleep(2)
	if state == FSM["State 2"]:
		print("State 2")
		print("\nreceiving...")
		rcvpkt_len, rcvpkt = rdt_rcv(conn)
		print("State 2 - received : [{}], [{}]".format(rcvpkt_len, rcvpkt))
		if not isCorrupt(rcvpkt) and has_seq(rcvpkt, 1):
			print("\t\tState 2 - not isCorrupt() && has_seq(1)")
			file += extract(rcvpkt)
			print("\t\t\tfile:[{}]".format(file))
			data = rcvpkt[4:-6]
			print("\t\t\tdata:[{}]".format(data))
			chk_rcv = checksum(data)
			print("\t\t\tchk_rcv:[{}]".format(chk_rcv))
			send_pkt = make_pkt_rcv(0, 1, chk_rcv)
			print("\nsending... [{}]".format(send_pkt))
			udt_send(conn, send_pkt)
			sleep(2)
			state = FSM["State 1"]
		else:
			print("\t\tState 2 - isCorrupt() || has_seq(0)")
			send_pkt = make_pkt_rcv(0, 0, chk_rcv)
			print("\nsending... [{}]".format(send_pkt))
			udt_send(conn, send_pkt)
			sleep(2)














# ###  OK message  ###
# while not message_OK:
# 	try:
# 		sleep(0.5)
# 		conn, address = s.accept()
# 		# Send the message
# 		# data = s.recv(1024).decode("utf-8")
# 		data_len, data = rdt_rcv(conn)
# 		data_split = data.split()
# 		print(data_len, data, data_split)
# 		if data_len != 0:
# 			print("received")
# 			udt_send(conn, s, "HIHIHI")

# 		continue
# 		# if not data:
# 			# print("no data")
# 			# break
# 		if len(data) != 0:
# 			if data_split[0] == "OK":
# 				message_OK = True
# 			if data_split[0] == "ERROR":
# 				print(data)
# 				# break
# 			if data_split[0] == "WAITING":
# 				print(data)
# 				# sleep(5)
# 		else:
# 			print("No data")
# 			# sleep(1)
# 		# sleep(2)
# 	except KeyboardInterrupt:
# 		print("KeyboardInterrupt")
# 		s.close()
# 		break

# 	except timeout:
# 		# After Maximum time, the server is closing the opened socket and exit.
# 		print("TCP Server Closing... Max time out reached: [{}] seconds".format(maxWaitTime))
# 		s.close()
# 		break

# 	except ConnectionResetError:
# 		print("connection was CLOSED.")
# 		s.close()
# 		break

# print("OK Message")


# while True:
# 	try:
# 		conn, address = s.accept()
# 		data = conn.recv(1024)
# 		message = data.decode("utf-8").split()
# 		sleep(0.1)
# 		print(message)
# 		sending_message = "OK"
# 		conn.send(bytes(sending_message, encoding='utf-8'))

# 	except KeyboardInterrupt:
# 		print("bye")
# 		s.close()
# 		break

# 	except timeout:
# 		# After Maximum time, the server is closing the opened socket and exit.
# 		print("TCP Server Closing... Max time out reached: {} seconds".format(maxWaitTime))
# 		s.close()
# 		break


s.close()
