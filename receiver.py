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
server_IP = "gaia.cs.umass.edu"
server_Port = 20000

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

# Message: in the form of "HELLO R <loss_rate> <corrupt_rate> <max_delay> <ID>" with a white space between them
Message = "HELLO" + " " + sender_or_receiver + " " + loss_rate_str + " " + currupt_rate_str + " " + max_delay_str + " " + ID_str
print("Message: {}".format(Message))



###### Print out INFO ######
name = "Ziwei Hu"
print("\nName: {} \tDate/Time: {}\n".format(name, get_date_time_str()))
sleep(5)

###### Create a TCP socket ######
s = socket(AF_INET, SOCK_STREAM)
# Set the maximum wait time for the client
maxWaitTime = 60
s.settimeout(maxWaitTime)


######  Connect through TCP socket  ######
try:
	# Connect to the server
	print("[-] Connecting to the {}:{}".format(server_IP, server_Port))
	s.connect((server_IP, server_Port))
except OSError:
	print("[-] A connect request was made on an already connected socket")
	s.close()
except ConnectionRefusedError:
	print("[-] connection was REFUSED.")
	s.close()
	exit()
print("[+] Connected.")



###### Sending HELLO message to the server ######
msg_OK = False
waiting = False
sleep_server = 0.2
while not msg_OK:
	sleep(sleep_server)
	try:
		# Send the message if not received WAITING message from the server
		if not waiting:
			print("[-] Sending a message: [{}]".format(Message))
			s.send(bytes(Message, encoding="utf-8"))
			sleep(sleep_server)

		# Receive a message from the server
		print("[-] Receiving...")
		msg_len, msg = rdt_rcv(s)
		msg_split = msg.split()
		sleep(sleep_server)
		if len(msg) != 0:
			print("[+] Received a message: [{}]".format(msg))
			print("[+] Received a message: [{}]".format(msg_split))
			if msg_split[0] == "OK":
				# When get OK message, then proceed to the next step
				msg_OK = True
				break
			if msg_split[0] == "ERROR" or msg_split[0] == "WAITINGOK":
				# When get ERROR message, then exit the program after closing the socket
				s.close()
				exit()
			if msg_split[0] == "WAITING":
				# When get WAITING message, then wait for the next message
				waiting = True
		else:
			# When received no data from the server
			print("No data")
			# sleep(0.1)
	except KeyboardInterrupt:
		print("KeyboardInterrupt")
		s.close()
		exit()
	except timeout:
		# After Maximum time, the server is closing the opened socket and exit.
		print("TCP connection closing... Max time out reached: {} seconds".format(maxWaitTime))
		s.close()
		exit()
	except ConnectionResetError:
		print("connection was CLOSED.")
		s.close()
		exit()
wait_before_send = 1.0
print("[+] Received OK message. Wait for {} seconds before communicating...".format(wait_before_send))
###### Print out INFO ######
name = "Ziwei Hu"
print("\nName: {} \tDate/Time: {}\n".format(name, get_date_time_str()))
sleep(wait_before_send)
sleep(5)

###### Finite State Machine ######
FSM = {"State 1": 1, # Wait for call 0 from below
	   "State 2": 2, # Wait for call 1 from below
	  }
state = FSM["State 1"]

###### Statistics ######
rcv_bytes = ""
num_pkt_snt = 0
num_pkt_rcv = 0
num_crpt_msg_rcv = 0

s.settimeout(3)
sleep(1)
while True:
	if state == FSM["State 1"]:
		print("\n[State 1]")
		print("[/] State 1 - receiving...")
		try:
			rcvpkt_len, rcvpkt = rdt_rcv(s)
			if rcvpkt_len == 0:
				print("\n[-] Empty data received. No more data flows. Close the connection...")
				s.close()
				break
		except ConnectionAbortedError:
			print("[-] Connection was closed.\n")
			break
		except Exception:
			print("[-] State 1 - exception! Try to receive again...\n")
			continue
		# if rcvpkt_len == 0:
		# 	print("\n[-] State 1 - No data received.\n")
		# 	break
		num_pkt_rcv += 1
		print("[+] State 1 - received: [{}], [{}] bytes".format(rcvpkt, rcvpkt_len))
		prefix = rcvpkt[:-5]
		print("State 1 - prefix  : [{}]".format(prefix))
		chk_rcv = checksum(prefix)
		print("State 1 - checksum: expected:[{}]  calculated:[{}]".format(rcvpkt[-5:], chk_rcv))
		if not isCorrupt_rcv(rcvpkt) and has_seq(rcvpkt, 0):
			print("[+] State 1 - not isCorrupt_rcv() && has_seq(0)")
			print("\trcv_bytes:[{}]".format(rcv_bytes))
			rcv_bytes += extract(rcvpkt)
			print("\trcv_bytes:[{}]".format(rcv_bytes))
			send_pkt = make_pkt_rcv(0, 0, chk_rcv)
			print("\t\tsending.... [{}]".format(send_pkt))
			udt_send(s, send_pkt)
			num_pkt_snt += 1
			# sleep(0.1)
			state = FSM["State 2"]
		elif isCorrupt_rcv(rcvpkt) or has_seq(rcvpkt, 1):
			print("[-] State 1 - isCorrupt_rcv() || has_seq(1)\n")
			if isCorrupt_rcv(rcvpkt):
				print("[-] Corrupted! message: [{}]\n".format(rcvpkt))
				num_crpt_msg_rcv += 1
			if has_seq(rcvpkt, 1):
				print("[-] Seq Error! expected: {}   received: {}\n".format(0, rcvpkt[0]))
			# chk_rcv = checksum(data)
			# print("\tchk_rcv:[{}]".format(chk_rcv))
			send_pkt = make_pkt_rcv(1, 1, chk_rcv)
			print("\t\tsending.... [{}]".format(send_pkt))
			udt_send(s, send_pkt)
			num_pkt_snt += 1
			# sleep(0.1)
	if state == FSM["State 2"]:
		print("\n[State 2]")
		print("[/] State 2 - receiving...")
		try:
			rcvpkt_len, rcvpkt = rdt_rcv(s)
			if rcvpkt_len == 0:
				print("\n[-] Empty data received. No more data flows. Close the connection...")
				s.close()
				break
		except ConnectionAbortedError:
			print("[-] Connection was closed.\n")
			break
		except Exception:
			print("[-] State 2 - exception! Try to receive again...\n")
			continue
		num_pkt_rcv += 1
		print("[+] State 2 - received: [{}], [{}] bytes".format(rcvpkt, rcvpkt_len))
		prefix = rcvpkt[:-5]
		print("State 2 - prefix  : [{}]".format(prefix))
		chk_rcv = checksum(prefix)
		print("State 2 - checksum: expected:[{}]  calculated:[{}]".format(rcvpkt[-5:], chk_rcv))
		if not isCorrupt_rcv(rcvpkt) and has_seq(rcvpkt, 1):
			print("[+] State 2 - not isCorrupt_rcv() && has_seq(1)")
			# rcv_bytes += extract(rcvpkt)
			# rcv_bytes += extract(rcvpkt)
			print("\trcv_bytes:[{}]".format(rcv_bytes))
			# data = rcvpkt[4:-6]
			# print("\tdata:[{}]".format(data), end=" ")
			# chk_rcv = checksum(data)
			# print("State 2 - checksum: expected:[{}]  calculated:[{}]".format(rcvpkt[-5:], chk_rcv))
			send_pkt = make_pkt_rcv(1, 1, chk_rcv)
			print("\t\tsending.... [{}]".format(send_pkt))
			udt_send(s, send_pkt)
			num_pkt_snt += 1
			# sleep(0.1)
			state = FSM["State 1"]
		elif isCorrupt_rcv(rcvpkt) or has_seq(rcvpkt, 0):
			print("[-] State 2 - isCorrupt_rcv() || has_seq(0)\n")
			if isCorrupt_rcv(rcvpkt):
				print("[-] Corrupted! message: [{}]\n".format(rcvpkt))
				num_crpt_msg_rcv += 1
			if has_seq(rcvpkt, 0):
				print("[-] Seq Error! expected: {}   received: {}\n".format(1, rcvpkt[0]))
			send_pkt = make_pkt_rcv(0, 0, chk_rcv)
			print("\t\tsending.... [{}]".format(send_pkt))
			udt_send(s, send_pkt)
			num_pkt_snt += 1
			# sleep(0.1)


print("\n\nName: {} \tDate/Time: {}".format(name, get_date_time_str()))
chk_rcv_bytes = checksum(rcv_bytes)
print("Checksum of total received bytes: [{}]".format(chk_rcv_bytes))
print("# of packets sent:      {}".format(num_pkt_snt))
print("# of packets received:  {}".format(num_pkt_rcv))
print("# of corrupted message: {}".format(num_crpt_msg_rcv))
print("received data:\n[{}]".format(rcv_bytes))

###### Closing the connection ######
print("[-] Closing the connection...")
s.close()
print("[+] Connection is closed.")
exit()
