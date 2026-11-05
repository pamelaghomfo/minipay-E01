import socket, time
t0 = time.time()
try:
	c = socket.create_connection(("10.255.255.1", 5000), timeout=2)
	c.sendall(b"payer 5000")
	print(c.recv(1024).decode())
except OSError as e:
	print("Échec :", e)
print("Durée : %.0f ms" % ((time.time() - t0) * 1000))