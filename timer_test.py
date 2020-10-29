import threading
from time import sleep

def a():
	print("a")

def b():
	print("b")

def c():
	print("c")

def d():
	print("d")


thds = []
ta = threading.Timer(3, a)
tb = threading.Timer(3, b)
tc = threading.Timer(3, c)
td = threading.Timer(3, d)

thds.append(ta)
thds.append(tb)
thds.append(tc)
thds.append(td)

ta.start()
td.start()
print(thds)
for x in thds[::-1]:
	print(x)
print(thds[-1])
sleep(1)
# ta.cancel()
thds[-1].cancel()
