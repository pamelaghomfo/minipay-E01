#!/usr/bin/env python3
"""Serveur TCP : échange des messages JSON préfixés par leur longueur (4 octets).
Usage : python3 tcp_serveur.py [port]"""
import json, socket, struct, sys, threading

def lire_exactement(sock, n):
    tampon = bytearray()
    while len(tampon) < n:
        morceau = sock.recv(n - len(tampon))
        if not morceau:
            return None
        tampon.extend(morceau)
    return bytes(tampon)

def recevoir_message(sock):
    entete = lire_exactement(sock, 4)
    if not entete:
        return None
    (taille,) = struct.unpack("!I", entete)
    donnees = lire_exactement(sock, taille)
    if not donnees:
        return None
    return donnees.decode("utf-8")

def envoyer_message(sock, texte):
    donnees = texte.encode("utf-8")
    sock.sendall(struct.pack("!I", len(donnees)) + donnees)

def traiter(conn):
    with conn:
        while True:
            brut = recevoir_message(conn)
            if brut is None:
                break
            req = json.loads(brut)
            rep = {"ok": True, "echo": req, "solde": 1_000_000 - req.get("montant", 0)}
            envoyer_message(conn, json.dumps(rep))

def main(port):
    s = socket.socket()
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(("127.0.0.1", port))
    s.listen(16)
    print("TCP (préfixe 4 octets) en écoute sur", port, flush=True)
    while True:
        conn, adr = s.accept()
        threading.Thread(target=traiter, args=(conn,), daemon=True).start()

if __name__ == "__main__":
    main(int(sys.argv[1]) if len(sys.argv) > 1 else 6000)
