from socket import *
import sys
import threading
from utils import *
from time import sleep
from datetime import datetime


def get_date_time_str():
	now = datetime.now()
	dt = now.strftime("%m/%d/%Y %H:%M:%S")
	return dt


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



name = "Ziwei Hu"
print("Name: {} \tDate/Time: {}".format(name, get_date_time_str()))

## gaia server (connect as a client) ##
# Create an TCP socket
s = socket(AF_INET, SOCK_STREAM)
# s.connect((server_IP, server_Port))
s.bind((server_IP, server_Port))
s.listen(5)


# Set the maximum wait time for the client
maxWaitTime = 30
s.settimeout(maxWaitTime)
# s.send(bytes(Message, encoding='utf-     8'))


message_OK = False


FSM = {"State 1": 1, # Wait for call 0 from below
	   "State 2": 2, # Wait for call 1 from below
	  }



Timer = False
# rcv_bytes = ""
conn, address = s.accept()
state = FSM["State 1"]

rcv_bytes = ""

###### Statistics ######
num_pkt_snt = 0
num_pkt_rcv = 0
num_crpt_msg_rcv = 0

while True:
	if state == FSM["State 1"]:
		print("\nState 1")
		print("receiving...")
		try:
			rcvpkt_len, rcvpkt = rdt_rcv(conn)
		except ConnectionAbortedError:
			print("[-] Connection was closed.")
			break
		if rcvpkt_len == 0:
			print("No data received.")
			break
		num_pkt_rcv += 1
		print("State 1 - received : [{}] bytes, [{}]".format(rcvpkt_len, rcvpkt))
		if not isCorrupt(rcvpkt) and has_seq(rcvpkt, 0):
			print("\tState 1 - not isCorrupt() && has_seq(0)")
			print("\trcv_bytes:[{}]".format(rcv_bytes))
			rcv_bytes += extract(rcvpkt)
			print("\trcv_bytes:[{}]".format(rcv_bytes))
			data = rcvpkt[4:-6]
			print("\tdata:[{}]".format(data), end=" ")
			chk_rcv = checksum(data)
			print("\t     chk_rcv:[{}]".format(chk_rcv))
			send_pkt = make_pkt_rcv(0, 0, chk_rcv)
			print("\t\tsending.... [{}]".format(send_pkt))
			udt_send(conn, send_pkt)
			num_pkt_snt += 1
			sleep(0.1)
			state = FSM["State 2"]
		elif isCorrupt(rcvpkt) or has_seq(rcvpkt, 1):
			if isCorrupt(rcvpkt):
				print("[-] Corrupted message: [{}]".format(rcvpkt))
				num_crpt_msg_rcv += 1
			else:
				print("[-] expected seq: {}   received seq: {}".format(0, rcvpkt[0]))
			print("\tState 1 - isCorrupt() || has_seq(1)")
			chk_rcv = checksum(data)
			print("\tchk_rcv:[{}]".format(chk_rcv))
			send_pkt = make_pkt_rcv(0, 1, chk_rcv)
			print("\t\tsending.... [{}]".format(send_pkt))
			udt_send(conn, send_pkt)
			sleep(0.1)
	if state == FSM["State 2"]:
		print("\nState 2")
		print("receiving...")
		try:
			rcvpkt_len, rcvpkt = rdt_rcv(conn)
			num_pkt_rcv += 1
		except ConnectionAbortedError:
			print("[-] Connection was closed.")
			break
		print("State 2 - received : [{}] bytes, [{}]".format(rcvpkt_len, rcvpkt))
		if not isCorrupt(rcvpkt) and has_seq(rcvpkt, 1):
			print("\tState 2 - not isCorrupt() && has_seq(1)")
			# rcv_bytes += extract(rcvpkt)
			# rcv_bytes += extract(rcvpkt)
			print("\trcv_bytes:[{}]".format(rcv_bytes))
			data = rcvpkt[4:-6]
			print("\tdata:[{}]".format(data), end=" ")
			chk_rcv = checksum(data)
			print("\t     chk_rcv:[{}]".format(chk_rcv))
			send_pkt = make_pkt_rcv(0, 1, chk_rcv)
			print("\t\tsending.... [{}]".format(send_pkt))
			udt_send(conn, send_pkt)
			num_pkt_snt += 1
			sleep(0.1)
			state = FSM["State 1"]
		elif isCorrupt(rcvpkt) or has_seq(rcvpkt, 0):
			if isCorrupt(rcvpkt):
				print("[-] Corrupted message: [{}]".format(rcvpkt))
				num_crpt_msg_rcv += 1
			else:
				print("[-] expected seq: {}   received seq: {}".format(1, rcvpkt[0]))
			print("\tState 2 - isCorrupt() || has_seq(0)")
			send_pkt = make_pkt_rcv(0, 0, chk_rcv)
			print("\t\tsending.... [{}]".format(send_pkt))
			udt_send(conn, send_pkt)
			sleep(0.1)


print("\n\nName: {} \tDate/Time: {}".format(name, get_date_time_str()))
chk_rcv_bytes = checksum(rcv_bytes)
print("Checksum of total received bytes: [{}]".format(chk_rcv_bytes))
print("# of packets sent:      {}".format(num_pkt_snt))
print("# of packets received:  {}".format(num_pkt_rcv))
print("# of corrupted message: {}".format(num_crpt_msg_rcv))


print("[-] Closing the connection...", end=" ")
s.close()
print("closed.")
exit()








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

