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
time_val_str = sys.argv[5]
time_val = float(time_val_str)

# sender or receiver
sender_or_receiver = "S"

# Message: in the form of "HELLO S <loss_rate> <corrupt_rate> <max_delay> <ID>" with a white space between them
Message = "HELLO" + " " + sender_or_receiver + " " + loss_rate_str + " " + currupt_rate_str + " " + max_delay_str + " " + ID_str
print("Message: {}".format(Message))
# print(Message.split())
# Message = "HELLO S 0.0 0.0 0 1234"




###### Print out INFO ######
name = "Ziwei Hu"
print("\nName: {} \tDate/Time: {}\n".format(name, get_date_time_str()))


###### Create a TCP socket ######
s = socket(AF_INET, SOCK_STREAM)
# Set the maximum wait time for the client
maxWaitTime = 10
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
while not msg_OK:
	sleep(0.1)
	try:
		# Send the message if not received WAITING message from the server
		if not waiting:
			print("[-] Sending a message: [{}]".format(Message))
			s.send(bytes(Message, encoding="utf-8"))
			sleep(1)

		# Receive a message from the server
		print("[-] Receiving...")
		msg_len, msg = rdt_rcv(s)
		msg_split = msg.split()
		sleep(1)
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
			sleep(0.1)
	except KeyboardInterrupt:
		print("KeyboardInterrupt")
		s.close()
		exit()
	except timeout:
		# After Maximum time, the server is closing the opened socket and exit.
		print("TCP Server Closing... Max time out reached: {} seconds".format(maxWaitTime))
		s.close()
		exit()
	except ConnectionResetError:
		print("connection was CLOSED.")
		s.close()
		exit()
wait_before_send = 2.0
print("[+] Received OK message. Wait for {} seconds before sending...".format(wait_before_send))
sleep(wait_before_send)


###### Finite State Machine ######
FSM = {"State 1": 1, # Wait for call 0 from above
	   "State 2": 2, # Wait for ACK 0
	   "State 3": 3, # Wait for call 1 from above
	   "State 4": 4  # Wait for ACK 1
	  }
state = FSM["State 1"]

###### Timer threads ######
threads = []

###### File ######
file = open("declaration.txt", "r").read()
num_bytes_to_send = 200
print("\n[+] File opened. Sending first {} bytes:\n[{}]".format(num_bytes_to_send, file[:num_bytes_to_send]))
what_to_send = file[:num_bytes_to_send]

###### Statistics ######
snt_bytes = ""
num_pkt_snt = 0
num_pkt_rcv = 0
num_crpt_msg_rcv = 0
num_timeouts = 0


sleep(0.5)
while len(snt_bytes) < num_bytes_to_send:
	print("\nCurrent file size: [{}] bytes. First-ten: [{}]".format(len(file), file[:10]))
	if state == FSM["State 1"]:
		print("\n[State 1]")
		print("State 1 - Current file size: [{}] bytes. First-ten: [{}]".format(len(file), file[:10]))
		send_pkt = make_pkt_snd(0, file)
		print("make_pkt_snd:[{}]".format(send_pkt))
		timer = threading.Timer(time_val, udt_send, args=(s, send_pkt,))
		threads.append(timer)
		print("State 1 - Timer thread ADDED. # of threads: [{}]".format(len(threads)))
		print("\t  last thread: {}".format(threads[-1]))
		timer.start()
		print("State 1 - Timer thread START. # of threads: [{}]".format(len(threads)))
		print("\t  last thread: {}".format(threads[-1]))
		print("State 1 - \n\t\tsending.... [{}] {} bytes".format(send_pkt, len(send_pkt)))
		udt_send(s, send_pkt)
		num_pkt_snt += 1
		sent_chk = send_pkt[-5:]
		state = FSM["State 2"]
		sleep(0.1)
	elif state == FSM["State 2"]:
		print("\n[State 2]")
		while True:
			if len(threads) == 0 or not threads[-1].is_alive():
				num_timeouts += 1
				print("State 2 - threads is empty or last thread is dead")
				print("State 2 - len(threads):{}  threads[-1]:{}".format(len(threads), threads[-1]))
				print("State 2 - Timer thread is STOPPED.... # of threads: [{}]".format(len(threads)))
				print("\t  last thread: {}".format(threads[-1]))
				timer = threading.Timer(time_val, udt_send, args=(s, send_pkt,))
				threads.append(timer)
				print("State 2 - Timer thread ADDED. # of threads: [{}]".format(len(threads)))
				print("\t  last thread: {}".format(threads[-1]))
				sleep(0.1)
				timer.start()
				print("State 2 - Timer thread START. # of threads: [{}]".format(len(threads)))
				print("\t  last thread: {}".format(threads[-1]))
				print("State 2 - \n\t\tsending.... [{}] {} bytes".format(send_pkt, len(send_pkt)))
				sleep(0.1)

			sleep(0.1)
			try:
				print("State 2 - receiving...")
				rcvpkt_len, rcvpkt = rdt_rcv(s)
				print("\nState 2 - received : {} bytes, [{}]".format(rcvpkt_len, rcvpkt))
				if rcvpkt_len != 0:
					num_pkt_rcv += 1
					break
			except Exception:
				print("State 2 - exception!")
				# sleep(time_val)

		# print("\nState 2 - received : {} bytes, [{}]".format(rcvpkt_len, rcvpkt))
		if not isCorrupt_snd(rcvpkt, sent_chk) and isACK(rcvpkt, 0):
			print("\tState 2 - not isCorrupt_snd() && isACK(0)")
			print("\tState 2 - Stopping Timer thread.... # of threads: [{}]".format(len(threads)))
			print("\tState 2 - last thread:{}".format(threads[-1]))
			cancel_timers(threads)
			# threads = []
			print("\tState 2 - Timer thread STOPPED .... # of threads: [{}]".format(len(threads)))
			print("\tState 2 - last thread:{}".format(threads[-1]))
			state = FSM["State 3"]
			sleep(0.1)
		elif isCorrupt_snd(rcvpkt, sent_chk) or isACK(rcvpkt, 1):
			if isCorrupt_snd(rcvpkt, sent_chk):
				print("\tState 2 - Corrupted!")
				print("\t[-] Corrupted message: [{}]".format(rcvpkt))
				num_crpt_msg_rcv += 1
			print("\tState 2 - isCorrupt_snd() || isACK(1)")
			sleep(0.1)
			continue
	elif state == FSM["State 3"]:
		print("\n[State 3]")
		# print("\nreceiving...")
		# rcvpkt_len, rcvpkt = rdt_rcv(s)
		print("State 3 - Current file size: [{}] bytes. First-ten: [{}]".format(len(file), file[:10]))
		send_pkt = make_pkt_snd(1, file)
		print("make_pkt_snd:[{}]".format(send_pkt))
		timer = threading.Timer(time_val, udt_send, args=(s, send_pkt,))
		threads.append(timer)
		print("State 3 - Timer thread ADDED. # of threads: [{}]".format(len(threads)))
		print("\t  last thread: {}".format(threads[-1]))
		timer.start()
		print("State 3 - Timer thread START. # of threads: [{}]".format(len(threads)))
		print("\t  last thread: {}".format(threads[-1]))
		print("State 3 - \n\t\tsending.... [{}] {} bytes".format(send_pkt, len(send_pkt)))
		udt_send(s, send_pkt)
		sent_chk = send_pkt[-5:]
		num_pkt_snt += 1
		state = FSM["State 4"]
		sleep(0.1)
	elif state == FSM["State 4"]:
		print("\n[State 4]")
		while True:
			if len(threads) == 0 or not threads[-1].is_alive():
				print("State 4 - threads is empty or last thread is dead")
				print("State 4 - len(threads):{}  threads[-1]:{}".format(len(threads), threads[-1]))
				num_timeouts += 1
				print("State 4 - Timer thread is STOPPED.... # of threads: [{}]".format(len(threads)))
				print("State 4 - last thread:{}".format(threads[-1]))
				timer = threading.Timer(time_val, udt_send, args=(s, send_pkt,))
				threads.append(timer)
				print("State 4 - Timer thread ADDED. # of threads: [{}]".format(len(threads)))
				print("\t  last thread: {}".format(threads[-1]))
				timer.start()
				print("State 4 - Timer thread START. # of threads: [{}]".format(len(threads)))
				print("\t  last thread: {}".format(threads[-1]))
				print("State 4 - \n\t\tsending.... [{}] {} bytes".format(send_pkt, len(send_pkt)))
				sleep(0.1)


			try:
				print("State 4 - receiving...")
				rcvpkt_len, rcvpkt = rdt_rcv(s)
				print("\nState 4 - received : {} bytes, [{}]".format(rcvpkt_len, rcvpkt))
				if rcvpkt_len != 0:
					break
			except Exception:
				print("State 4 - exception!")

		# print("receiving...")
		# rcvpkt_len, rcvpkt = rdt_rcv(s)
		num_pkt_rcv += 1
		print("\nState 4 - received : {} bytes, [{}]".format(rcvpkt_len, rcvpkt))
		if not isCorrupt_snd(rcvpkt, sent_chk) and isACK(rcvpkt, 0):
			print("\tState 4 - not isCorrupt_snd() && isACK(0)")
			print("\tState 4 - Stopping Timer thread.... # of threads: [{}]".format(len(threads)))
			print("\tState 4 - last thread:{}".format(threads[-1]))
			cancel_timers(threads)
			# threads = []
			print("\tState 4 - Timer thread STOPPED .... # of threads: [{}]".format(len(threads)))
			print("\tState 4 - last thread:{}".format(threads[-1]))
			state = FSM["State 1"]
			print("Succefully transferred {} bytes".format(len(send_pkt)))
			print("Succefully transferred [{}]".format(send_pkt))
			snt_bytes += extract(send_pkt)
			print("Total sent_bytes: {} bytes\n\n".format(len(snt_bytes)))
			file = file[20:]
			sleep(0.1)
		elif isCorrupt_snd(rcvpkt, sent_chk) or isACK(rcvpkt, 1):
			print("\tState 4 - isCorrupt_snd() || isACK(1)")
			if isCorrupt_snd(rcvpkt, sent_chk):
				print("\tState 4 - Corrupted!")
				print("\t[-] Corrupted message: [{}]".format(rcvpkt))
				num_crpt_msg_rcv += 1
			sleep(0.1)
			continue


print("\n\nName: {} \tDate/Time: {}".format(name, get_date_time_str()))
chk_send_bytes = checksum(snt_bytes)
print("Checksum of total sent bytes: [{}]".format(chk_send_bytes))
print("# of packets sent:      {}".format(num_pkt_snt))
print("# of packets received:  {}".format(num_pkt_rcv))
print("# of corrupted message: {}".format(num_crpt_msg_rcv))
print("# of timeouts:          {}".format(num_timeouts))
print("sent data:\n[{}]".format(snt_bytes))

###### Closing the connection ######
print("[-] Closing the connection...")
s.close()
print("[+] Connection is closed.")
exit()
