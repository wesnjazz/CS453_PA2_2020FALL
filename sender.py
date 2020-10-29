from socket import *
import sys
from time import sleep
import threading
from utils import *


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

# sender or receiver
sender_or_receiver = "S"

# Message: in the form of "HELLO S <loss_rate> <corrupt_rate> <max_delay> <ID>" with a white space between them
# Message = "HELLO" + " " + sender_or_receiver + " " + loss_rate_str + " " + currupt_rate_str + " " + max_delay_str + " " + ID_str
# print("Message: {}".format(Message))
# print(Message.split())
# Message = "HELLO S 0.0 0.0 0 1234"

# Create an TCP socket
s = socket(AF_INET, SOCK_STREAM)
# Set the maximum wait time for the client
maxWaitTime = 15
s.settimeout(maxWaitTime)


###  Connection  ###
try:
	# Connect to the server
	print("[.] Connecting to the {}:{}".format(server_IP, server_Port))
	s.connect((server_IP, server_Port))
except OSError:
	print("[-] A connect request was made on an already connected socket")
	s.close()
except ConnectionRefusedError:
	print("[-] connection was REFUSED.")
	s.close()
	exit()
print("[+] Connected.")

message_OK = False


FSM = {"State 1": 1, # Wait for call 0 from above
	   "State 2": 2, # Wait for ACK 0
	   "State 3": 3, # Wait for call 1 from above
	   "State 4": 4  # Wait for ACK 1
	  }
state = FSM["State 1"]
threads = []
time_val = 7.0

file = open("declaration-short.txt", "r").read()
num_bytes_to_send = 80
print("\n[+] File opened. Sending first {} bytes:\n[{}]".format(num_bytes_to_send, file[:num_bytes_to_send]))
what_to_send = file[:num_bytes_to_send]
sent_bytes = ""

sleep(1)
while len(sent_bytes) < num_bytes_to_send:
	print("\nCurrent file size: [{}] bytes. First-ten: [{}]".format(len(file), file[:10]))
	if state == FSM["State 1"]:
		print("\n[State 1]")
		# print("\nreceiving...")
		# rcvpkt_len, rcvpkt = rdt_rcv(s)
		send_pkt = make_pkt_snd(0, file)
		print("State 1 - Current file size: [{}] bytes. First-ten: [{}]".format(len(file), file[:10]))
		timer = threading.Timer(time_val, udt_send, args=(s, send_pkt,))
		# timer = RepeatingTimer(time_val, udt_send(s, send_pkt,))
		threads.append(timer)
		print("State 1 - Timer thread ADDED. # of threads: [{}]".format(len(threads)))
		print("\t  last thread: {}".format(threads[-1]))
		timer.start()
		print("State 1 - Timer thread START. # of threads: [{}]".format(len(threads)))
		print("\t  last thread: {}".format(threads[-1]))
		print("State 1 - \n\t\tsending.... [{}] {} bytes".format(send_pkt, len(send_pkt)))
		udt_send(s, send_pkt)
		state = FSM["State 2"]
		sleep(0.1)
	elif state == FSM["State 2"]:
		print("\n[State 2]")
		if len(threads) == 0:
			print("State 2 - Timer thread is STOPPED.... # of threads: [{}]".format(len(threads)))
			print("\t  last thread: {}".format(threads[-1]))
			# timer = RepeatingTimer(time_val, udt_send, (s, send_pkt,))
			timer = threading.Timer(time_val, udt_send, args=(s, send_pkt,))
			threads.append(timer)
			print("State 2 - Timer thread ADDED. # of threads: [{}]".format(len(threads)))
			print("\t  last thread: {}".format(threads[-1]))
			timer.start()
			print("State 2 - Timer thread START. # of threads: [{}]".format(len(threads)))
			print("\t  last thread: {}".format(threads[-1]))
			print("State 2 - \n\t\tsending.... [{}] {} bytes".format(send_pkt, len(send_pkt)))
			sleep(0.1)
		print("receiving...")
		rcvpkt_len, rcvpkt = rdt_rcv(s)
		print("\nState 2 - received : {} bytes, [{}]".format(rcvpkt_len, rcvpkt))
		if not isCorrupt(rcvpkt) and isACK(rcvpkt, 0):
			print("\tState 2 - not isCorrupt() && isACK(0)")
			print("\tState 2 - Stopping Timer thread.... # of threads: [{}]".format(len(threads)))
			print("\tState 2 - last thread:{}".format(threads[-1]))
			cancel_timers(threads)
			# threads = []
			print("\tState 2 - Timer thread STOPPED .... # of threads: [{}]".format(len(threads)))
			print("\tState 2 - last thread:{}".format(threads[-1]))
			state = FSM["State 3"]
			sleep(0.1)
		elif isCorrupt(rcvpkt) or isACK(rcvpkt, 1):
			print("\tState 2 - isCorrupt() || isACK(1)")
			sleep(0.1)
			continue
	elif state == FSM["State 3"]:
		print("\n[State 3]")
		# print("\nreceiving...")
		# rcvpkt_len, rcvpkt = rdt_rcv(s)
		send_pkt = make_pkt_snd(1, file)
		print("State 3 - Current file size: [{}] bytes. First-ten: [{}]".format(len(file), file[:10]))
		# timer = RepeatingTimer(time_val, udt_send, (s, send_pkt,))
		timer = threading.Timer(time_val, udt_send, args=(s, send_pkt,))
		threads.append(timer)
		print("State 3 - Timer thread ADDED. # of threads: [{}]".format(len(threads)))
		print("\t  last thread: {}".format(threads[-1]))
		timer.start()
		print("State 3 - Timer thread START. # of threads: [{}]".format(len(threads)))
		print("\t  last thread: {}".format(threads[-1]))
		print("State 3 - \n\t\tsending.... [{}] {} bytes".format(send_pkt, len(send_pkt)))
		udt_send(s, send_pkt)
		state = FSM["State 4"]
		sleep(0.1)
	elif state == FSM["State 4"]:
		print("\n[State 4]")
		if len(threads) == 0:
			print("State 4 - Timer thread is STOPPED.... # of threads: [{}]".format(len(threads)))
			print("State 4 - last thread:{}".format(threads[-1]))
			# timer = RepeatingTimer(time_val, udt_send, (s, send_pkt,))
			timer = threading.Timer(time_val, udt_send, args=(s, send_pkt,))
			threads.append(timer)
			print("State 4 - Timer thread ADDED. # of threads: [{}]".format(len(threads)))
			print("\t  last thread: {}".format(threads[-1]))
			timer.start()
			print("State 4 - Timer thread START. # of threads: [{}]".format(len(threads)))
			print("\t  last thread: {}".format(threads[-1]))
			print("State 4 - \n\t\tsending.... [{}] {} bytes".format(send_pkt, len(send_pkt)))
			sleep(0.1)
		print("receiving...")
		rcvpkt_len, rcvpkt = rdt_rcv(s)
		print("\nState 4 - received : {} bytes, [{}]".format(rcvpkt_len, rcvpkt))
		if not isCorrupt(rcvpkt) and isACK(rcvpkt, 1):
			print("\tState 4 - not isCorrupt() && isACK(1)")
			print("\tState 4 - Stopping Timer thread.... # of threads: [{}]".format(len(threads)))
			print("\tState 4 - last thread:{}".format(threads[-1]))
			cancel_timers(threads)
			# threads = []
			print("\tState 4 - Timer thread STOPPED .... # of threads: [{}]".format(len(threads)))
			print("\tState 4 - last thread:{}".format(threads[-1]))
			state = FSM["State 1"]
			print("Succefully transferred {} bytes".format(len(send_pkt)))
			print("Succefully transferred [{}]".format(send_pkt))
			sent_bytes += extract(send_pkt)
			print("Total sent_bytes: {} bytes\n\n".format(len(sent_bytes)))
			file = file[20:]
			sleep(0.1)
		elif isCorrupt(rcvpkt) or isACK(rcvpkt, 0):
			print("\tState 4 - isCorrupt() || isACK(0)")
			sleep(0.1)
			continue



print("What to send: [{}] bytes. \n[{}]".format(len(what_to_send), what_to_send))
print("Sent: [{}] bytes. \n[{}]".format(len(sent_bytes), sent_bytes))
		# print("\nState 4")
		# if Timer == False:
		# 	print("\nState 4 - sending... [{}] {} bytes".format(send_pkt, len(send_pkt)))
		# 	udt_send(s, send_pkt)
		# 	Timer = True
		# 	print("Timer start @ State 4")
		# 	sleep(1)
		# print("\nreceiving...")
		# rcvpkt_len, rcvpkt = rdt_rcv(s)
		# print("\nState 4 - received : {} bytes, [{}]".format(rcvpkt_len, rcvpkt))
		# if isCorrupt(rcvpkt) and isACK(rcvpkt, 1):
		# 	print("\t\tState 4 - not isCorrupt() && isACK(1)")
		# 	print("Timer Stop @ State 2")
		# 	Timer = False
		# 	state = FSM["State 1"]
		# 	sleep(1)
		# else:
		# 	print("\t\tState 4 - isCorrupt() || isACK(0)")
		# 	sleep(1)
		# 	continue


# while True:
# 	sleep(1)
# 	print("\nreceiving...")
# 	rcvpkt_len, rcvpkt = rdt_rcv(s)
# 	print("len:[{}]  data:{}".format(rcvpkt_len, rcvpkt))
# 	send_pkt = make_pkt_snd(0, data)
# 	# print(send_pkt)
# 	sleep(1)
# 	print("\nsending... {}".format(send_pkt))
# 	udt_send(s, send_pkt)

# while True:
# 	sleep(0.1)
# 	# print("State:{}".format(state))
# 	rcvpkt_len, rcvpkt = rdt_rcv(s)
# 	print("len:{}  data:{}".format(rcvpkt_len, rcvpkt))
# 	if state == FSM["State 1"]:
# 		print("\nState 1")
# 		print("make_pkt_snd")
# 		send_pkt = make_pkt_snd(0, data)
# 		print("udt_send")
# 		udt_send(s, send_pkt)
# 		print("Timer start")
# 		timer = threading.Timer(time_val, udt_send, args=(s, send_pkt,))
# 		state = FSM["State 2"]
# 		continue

# 	if state == FSM["State 2"]:
# 		print("\nState 2")
# 		if rcvpkt_len != 0 and (isCorrupt(rcvpkt) or isACK(rcvpkt, 1)):
# 			print("len:{}  isCorrupt:{}  isACK:{}".format(rcvpkt_len, isCorrupt(rcvpkt), isACK(rcvpkt, 1)))
# 			continue



s.close()
exit()






###  OK message  ###
while not message_OK:
	try:
		sleep(0.5)
		# Send the message
		# data = s.recv(1024).decode("utf-8")
		
		print("receiving...")
		data_len, data = rdt_rcv(s)
		sleep(1)
		print("sending...")
		s.send(bytes(Message, encoding='utf-8'))
		sleep(1)

		data_split = data.split()
		print(data_len, data, data_split)
		print("CONTINUE")
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
		# sleep(1)
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


# Read a file to send
file = open("declaration.txt", "r").read()




# Close the socket
s.close()
