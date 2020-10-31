import threading
from datetime import datetime


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
    # print("calc:{}  expect:{}".format(calc_checksum, expected_checksum))
    # step 3: compare with expected checksum
    if calc_checksum == expected_checksum:
        return True
    return False

def make_pkt_snd(seq, data):
    ACK = str(0)
    payload = data[:20]
    prefix = " ".join([str(seq), ACK, payload]) + " "
    chk = checksum(prefix)
    pkt = "".join([prefix, chk])
    return pkt

def make_pkt_rcv(ACK, seq, chk_rcv):
    pkt = "  a                      chksm"
    pkt = pkt.replace("a", str(ACK))
    pkt = pkt.replace("chksm", chk_rcv)
    return pkt

def udt_send(socket, send_pkt):
    socket.send(bytes(send_pkt, encoding='utf-8'))
    print("\t\tudt_send(): [{}]".format(send_pkt))

def has_seq(rcvpkt, seq):
    return str(rcvpkt[0]) == str(seq)

def isACK(rcvpkt, ACK):
	return str(rcvpkt[2]) == str(ACK)

def isCorrupt_rcv(rcvpkt):
    digit = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']
    chk_ok = checksum_verifier(rcvpkt)
    if not chk_ok:
        # print("chk_not same")
        return True
    if str(rcvpkt[0]) not in ["0", "1"]:
        # print("[0] not in 0 or 1")
        return True
    if rcvpkt[1] != " ":
        # print("white [1]")
        return True
    if str(rcvpkt[2]) not in ["0", "1"]:
        # print("[2] not in 0 or 1")
        return True
    if rcvpkt[3] != " ":
        # print("white [3]")
        return True
    if rcvpkt[24] != " ":
        # print("white [24]")
        return True
    if rcvpkt[25] not in digit:
        # print("non digit [25]")
        return True
    if rcvpkt[26] not in digit:
        # print("non digit [26]")
        return True
    if rcvpkt[27] not in digit:
        # print("non digit [27]")
        return True
    if rcvpkt[28] not in digit:
        # print("non digit [28]")
        return True
    if rcvpkt[29] not in digit:
        # print("non digit [29]")
        return True
    return False

def isCorrupt_snd(rcvpkt, sent_chk):
    digit = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']
    if rcvpkt[-5:] != sent_chk:
        # print("sent_chk not same")
        return True
    # else:
        # print("sent_chk same")
    if rcvpkt[:2] != "  ":
        # print("white [0:2]")
        return True
    if str(rcvpkt[2]) not in ["0", "1"]:
        # print("[2] not in 0 or 1")
        return True
    if rcvpkt[3:25] != "                      ":
        # print("white [3:25]")
        return True
    if rcvpkt[25] not in digit:
        # print("non digit [25]")
        return True
    if rcvpkt[26] not in digit:
        # print("non digit [26]")
        return True
    if rcvpkt[27] not in digit:
        # print("non digit [27]")
        return True
    if rcvpkt[28] not in digit:
        # print("non digit [28]")
        return True
    if rcvpkt[29] not in digit:
        # print("non digit [29]")
        return True
    return False

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

def cancel_timers(threads):
    for t in threads[::-1]:
        t.cancel()

def get_date_time_str():
    now = datetime.now()
    dt = now.strftime("%m/%d/%Y %H:%M:%S")
    return dt

