import socket, time

s = socket.socket()
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind(("0.0.0.0", 5000))
s.listen()
print("Serveur en attente sur le port 5000")
compteur = 0
traites = set()                      # identifiants déjà traités
while True:
    conn, addr = s.accept()
    data = conn.recv(1024).decode()
    #print("traites", traites)
    #print(data.split("|")[0] in traites)
    if data.split("|")[0] not in traites :
        traites.add(data.split("|")[0])
        #print(traites)
        compteur += 1
        print("paiements exécutés :", compteur)
        time.sleep(3)
        conn.sendall(("OK "+data).encode())
        conn.close()
    else :
        print(f"Paiement {data.split("|")[0]}, déjà traité.")