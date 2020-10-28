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

def make_pkt_snd(seq, data):
	ACK = str(0)
	payload = data[:20]
	chk = checksum(payload)
	pkt = " ".join([str(seq), ACK, payload, chk])
	return pkt

def make_pkt_rcv(ACK, seq, chk_rcv):
    pkt = "  a                      chksm"
    pkt = pkt.replace("a", str(ACK))
    pkt = pkt.replace("chksm", chk_rcv)
    return pkt

def udt_send(socket, send_pkt):
	socket.send(bytes(send_pkt, encoding='utf-8'))

def has_seq(rcvpkt, seq):
    return int(rcvpkt[0]) == seq

def isACK(rcvpkt, ACK):
	return int(rcvpkt[2]) == ACK

def isCorrupt(rcvpkt):
	return len(rcvpkt) != 30

def rdt_rcv(socket):
	rcvpkt = socket.recv(1024).decode("utf-8")
	return len(rcvpkt), rcvpkt

def extract(rcvpkt):
    return rcvpkt[4:24]

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