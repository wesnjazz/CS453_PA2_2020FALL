from socket import *
import sys
from time import sleep
import threading


def checksum(msg):
    """
     This function calculates checksum of an input string
     Note that this checksum is not Internet checksum.
    
     Input: msg - String
     Output: String with length of five
     Example Input: "1 0 That was the time fo "
     Expected Output: "02018"
    """

    # step1: covert msg (string) to bytes
    msg = msg.encode("utf-8")
    s = 0
    # step2: sum all bytes
    for i in range(0, len(msg), 1):
        s += msg[i]
    # step3: return the checksum string with fixed length of five 
    #        (zero-padding in front if needed)
    return format(s, '05d')

def checksum_verifier(msg):
    """
     This function compares packet checksum with expected checksum
    
     Input: msg - String
     Output: Boolean - True if they are the same, Otherwise False.
     Example Input: "1 0 That was the time fo 02018"
     Expected Output: True
    """

    expected_packet_length = 30
    # step 1: make sure the checksum range is 30
    if len(msg) < expected_packet_length:
        return False
    # step 2: calculate the packet checksum
    content = msg[:-5]
    calc_checksum = checksum(content)
    expected_checksum = msg[-5:]
    # step 3: compare with expected checksum
    if calc_checksum == expected_checksum:
        return True
    return False

def make_pkt(seq, data):
	ACK = str(0)
	payload = data[:20]
	chk = checksum(payload)
	pkt = " ".join([str(seq), ACK, payload, chk])
	return pkt


def udt_send(socket, send_pkt):
	socket.send(bytes(send_pkt, encoding='utf-8'))


def isACK(rcvpkt, ACK):
	return int(rcvpkt[2]) == ACK


def isCorrupt(rcvpkt):
	return len(rcvpkt) != 30

def rdt_rcv(socket):
	rcvpkt = s.recv(1024).decode("utf-8")
	return len(rcvpkt), rcvpkt

def check_thread_alive(thr):
	# print(thr)
	# return True
	# try:
		# l = thr.is_alive()
	# except TypeError:
		# return False
	# return l
	print(thr)
	thr.join(timeout=0.0)
	# print(thr.is_alive())
	return thr.is_alive()

# # Read a file to send
# file = open("declaration.txt", "r").read()
# send_pkt= make_pkt(0, file)
# print(send_pkt)
# file = file[20:]
# send_pkt= make_pkt(0, file)
# print(send_pkt)
# file = file[20:]
# send_pkt= make_pkt(0, file)
# print(send_pkt)
# print(len(send_pkt))
# print(isCorrupt(send_pkt))
# exit()



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
maxWaitTime = 15
s.settimeout(maxWaitTime)


###  Connection  ###
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

message_OK = False
s.send(bytes(Message, encoding='utf-8'))


FSM = {"State 1": 1, # Wait for call 0 from above
	   "State 2": 2, # Wait for ACK 0
	   "State 3": 3, # Wait for call 1 from above
	   "State 4": 4  # Wait for ACK 1
	  }


data = open("declaration.txt", "r").read()
state = FSM["State 2"]
send_pkt = make_pkt(0, data)
udt_send(s, send_pkt)

timer = threading.Timer(2.0, udt_send, args=(s, send_pkt,))
timer.start()
# timer.join()
while True:
	# if not timer.is_alive():
		# print("Timer dead")
		# exit()
	if not check_thread_alive(timer):
		print("Timer dead")
		exit()
exit()

# while True:
# 	rcvpkt_len, rcvpkt = rdt_rcv(s):
# 	if state == FSM["State 1"]:
# 		send_pkt = make_pkt(seq=0, data)
# 		udt_send(s, send_pkt)
# 		timer = threading.Timer(10.0, udt_send(s, send_pkt))
# 		state = FSM["State 2"]

# 	if state == FSM["State 2"]:
# 		if rcvpkt_len != 0 and (isCorrupt(rcvpkt) or isACK(rcvpkt, 1)):
# 			continue











###  OK message  ###
while not message_OK:
	try:
		sleep(0.5)
		# Send the message
		# data = s.recv(1024).decode("utf-8")
		
		print("receiving...")
		data_len, data = rdt_rcv(s)
		sleep(2)
		print("sending...")
		s.send(bytes(Message, encoding='utf-8'))
		sleep(2)

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


# Read a file to send
file = open("declaration.txt", "r").read()




# Close the socket
s.close()
