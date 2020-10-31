from socket import *
import sys
import threading
from utils import *
from time import sleep


# 2020.10.24.Sat ~ 2020.10.30.Fri
# CS 453 Computer Networking
# rdt 3.0 protocol uses ACK, seq, checksum and timers
# Checksum is used for checking corrupted packet
# ACK indicates if the corresponding sequence number of packet was delivered.
# e.g., ACK is 0 when the Receiver got the seq of 0 right.
# Sender should check the sent checksum and received checksum, and compare if those matches.
# Timer deals with delays, premature timeouts.
# Timer send the packet again if no response from the Receiver


# Check the number of command line arguments
if len(sys.argv) < 5:
	print("Usage: python sender.py <connection_id> <loss_rate> <corrupt_rate> <max_delay> <transmission_timeout>")
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



###### Print out INFO ######
name = "Ziwei Hu"
print("\nName: {} \tDate/Time: {}\n".format(name, get_date_time_str()))
# sleep(5)

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
# sleep(5)



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

s.settimeout(1)

# Loop until first 200 bytes sent
while len(snt_bytes) < num_bytes_to_send:
	print("\nCurrent file size: [{}] bytes. First-ten: [{}]".format(len(file), file[:10]))
	if state == FSM["State 1"]:
		print("\n[State 1]")
		print("State 1 - Current file size: [{}] bytes. First-ten: [{}]".format(len(file), file[:10]))

		# Make a packet to send with the seq 0
		send_pkt = make_pkt_snd(0, file)
		print("make_pkt_snd:[{}]".format(send_pkt))

		# Timer thread starts
		timer = threading.Timer(time_val, udt_send, args=(s, send_pkt))
		threads.append(timer)
		print("State 1 - Timer thread ADDED. # of threads: [{}]".format(len(threads)))
		print("\t  last thread: {}".format(threads[-1]))
		timer.start()
		print("State 1 - Timer thread START. # of threads: [{}]".format(len(threads)))
		print("\t  last thread: {}".format(threads[-1]))
		print("[/] State 1 - \n\t\tsending.... [{}] {} bytes".format(send_pkt, len(send_pkt)))

		# Send the packet
		udt_send(s, send_pkt)
		num_pkt_snt += 1

		# Store this checksum for the State 2
		sent_chk = send_pkt[-5:]

		# Change the FSM state
		state = FSM["State 2"]

	elif state == FSM["State 2"]:
		print("\n[State 2]")
		while True:
			# If there are no alive Timer threads (TIMEOUT event happens)
			if len(threads) == 0 or not threads[-1].is_alive():
				# Statistics
				num_timeouts += 1
				print("State 2 - threads is empty or last thread is dead")
				print("State 2 - len(threads):{}  threads[-1]:{}".format(len(threads), threads[-1]))
				print("State 2 - Timer thread is STOPPED.... # of threads: [{}]".format(len(threads)))
				print("\t  last thread: {}".format(threads[-1]))

				# Create a new Timer
				timer = threading.Timer(time_val, udt_send, args=(s, send_pkt))
				threads.append(timer)
				print("State 2 - Timer thread ADDED. # of threads: [{}]".format(len(threads)))
				print("\t  last thread: {}".format(threads[-1]))

				# Start the new Timer
				timer.start()
				# Statistics
				num_pkt_snt += 1
				print("State 2 - Timer thread START. # of threads: [{}]".format(len(threads)))
				print("\t  last thread: {}".format(threads[-1]))
				print("[/] State 2 - \n\t\tsending.... [{}] {} bytes".format(send_pkt, len(send_pkt)))

			# Keep receiving packets
			try:
				print("[/] State 2 - receiving...")
				rcvpkt_len, rcvpkt = rdt_rcv(s)
				print("\n[+] State 2 - received : {} bytes, [{}]".format(rcvpkt_len, rcvpkt))

				# If received 0, then there will be no more packets to receive.
				if rcvpkt_len == 0:
					print("\n[-] Empty data received. No more data flows. Close the connection...")
					s.close()
					break

				# If received any packet, then proceed to the next step (Stop receiving)
				else:
					break
			except Exception:
				print("[-] State 2 - exception! Try to receive again...\n")
				continue

		# After receiving the packet, increase the number of statistics
		num_pkt_rcv += 1

		# If the packet is good
		# (The packet is NOT corrupted and the ACK is of seq 0)
		if not isCorrupt_snd(rcvpkt, sent_chk) and isACK(rcvpkt, 0):
			print("[+] State 2 - not isCorrupt_snd() && isACK(0)")
			print("State 2 - Stopping Timer thread.... # of threads: [{}]".format(len(threads)))
			print("State 2 - last thread:{}".format(threads[-1]))

			# Kill all Timer threads
			cancel_timers(threads)
			print("State 2 - Timer thread STOPPED .... # of threads: [{}]".format(len(threads)))
			print("State 2 - last thread:{}".format(threads[-1]))
			
			# Change the FSM state
			state = FSM["State 3"]

		# If the packet is not good
		# (The packet is corrupted or not the expected ACK)
		elif isCorrupt_snd(rcvpkt, sent_chk) or isACK(rcvpkt, 1):
			print("[-] State 2 - isCorrupt_snd() || isACK(1)\n")
			# Debugging messages
			if isCorrupt_snd(rcvpkt, sent_chk):
				print("[-] State 2 - Corrupted!")
				print("[-] Corrupted message: [{}]".format(rcvpkt))
				# Statistics
				num_crpt_msg_rcv += 1
			if isACK(rcvpkt, 1):
				print("[-] State 2 - ACK is 1!")
				print("[-] ACK: {}".format(rcvpkt[2]))
			# Receive again because the packet was not good
			continue

	elif state == FSM["State 3"]:
		print("\n[State 3]")
		print("State 3 - Current file size: [{}] bytes. First-ten: [{}]".format(len(file), file[:10]))

		# Make a packet to send with the seq 1
		send_pkt = make_pkt_snd(1, file)
		print("make_pkt_snd:[{}]".format(send_pkt))

		# Timer thread starts
		timer = threading.Timer(time_val, udt_send, args=(s, send_pkt))
		threads.append(timer)
		print("State 3 - Timer thread ADDED. # of threads: [{}]".format(len(threads)))
		print("\t  last thread: {}".format(threads[-1]))
		timer.start()
		print("State 3 - Timer thread START. # of threads: [{}]".format(len(threads)))
		print("\t  last thread: {}".format(threads[-1]))
		print("[/] State 3 - \n\t\tsending.... [{}] {} bytes".format(send_pkt, len(send_pkt)))

		# Send the packet
		udt_send(s, send_pkt)
		num_pkt_snt += 1

		# Store this checksum for the State 4
		sent_chk = send_pkt[-5:]

		# Change the FSM state
		state = FSM["State 4"]

	elif state == FSM["State 4"]:
		print("\n[State 4]")
		while True:
			# If there are no alive Timer threads (TIMEOUT event happens)
			if len(threads) == 0 or not threads[-1].is_alive():
				# Statistics
				num_timeouts += 1
				print("State 4 - threads is empty or last thread is dead")
				print("State 4 - len(threads):{}  threads[-1]:{}".format(len(threads), threads[-1]))
				print("State 4 - Timer thread is STOPPED.... # of threads: [{}]".format(len(threads)))
				print("State 4 - last thread:{}".format(threads[-1]))

				# Create a new Timer
				timer = threading.Timer(time_val, udt_send, args=(s, send_pkt))
				threads.append(timer)
				print("State 4 - Timer thread ADDED. # of threads: [{}]".format(len(threads)))
				print("\t  last thread: {}".format(threads[-1]))

				# Start the new Timer
				timer.start()
				# Statistics
				num_pkt_snt += 1
				print("State 4 - Timer thread START. # of threads: [{}]".format(len(threads)))
				print("\t  last thread: {}".format(threads[-1]))
				print("[/] State 4 - \n\t\tsending.... [{}] {} bytes".format(send_pkt, len(send_pkt)))
			
			# Keep receiving packets
			try:
				print("[/] State 4 - receiving...")
				rcvpkt_len, rcvpkt = rdt_rcv(s)
				print("\n[+] State 4 - received : {} bytes, [{}]".format(rcvpkt_len, rcvpkt))
				
				# If received 0, then there will be no more packets to receive.
				if rcvpkt_len == 0:
					print("\n[-] Empty data received. No more data flows. Close the connection...")
					s.close()
					break
				# If received any packet, then proceed to the next step (Stop receiving)
				else:
					break
			except Exception:
				print("[-] State 4 - exception! Try to receive again...\n")
				continue
		
		# Statistics
		num_pkt_rcv += 1
		print("\n[+] State 4 - received : {} bytes, [{}]".format(rcvpkt_len, rcvpkt))
		# If the packet is not good
		# (The packet is corrupted or not the expected ACK)
		if not isCorrupt_snd(rcvpkt, sent_chk) and isACK(rcvpkt, 1):
			print("\n[+] State 4 - not isCorrupt_snd() && isACK(1)")
			print("State 4 - Stopping Timer thread.... # of threads: [{}]".format(len(threads)))
			print("State 4 - last thread:{}".format(threads[-1]))

			# Kill all Timer threads
			cancel_timers(threads)
			print("State 4 - Timer thread STOPPED .... # of threads: [{}]".format(len(threads)))
			print("State 4 - last thread:{}".format(threads[-1]))

			# Change the FSM state
			state = FSM["State 1"]
			print("Succefully transferred {} bytes".format(len(send_pkt)))
			print("Succefully transferred [{}]".format(send_pkt))

			# Bytes successfully delivered through rdt 3.0 protocol
			snt_bytes += extract(send_pkt)
			print("Total sent_bytes: {} bytes\n\n".format(len(snt_bytes)))
			file = file[20:]

		# If the packet is not good
		# (The packet is corrupted or not the expected ACK)
		elif isCorrupt_snd(rcvpkt, sent_chk) or isACK(rcvpkt, 0):
			print("[-] State 4 - isCorrupt_snd() || isACK(0)\n")
			# Debugging messages
			if isCorrupt_snd(rcvpkt, sent_chk):
				print("[-] State 4 - Corrupted!")
				print("[-] Corrupted message: [{}]".format(rcvpkt))
				# Statistics
				num_crpt_msg_rcv += 1
			if isACK(rcvpkt, 0):
				print("[-] State 2 - ACK is 0!")
				print("[-] ACK: {}".format(rcvpkt[2]))
			# Receive again because the packet was not good
			continue


###### Statistics ######
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
