#!/usr/bin/env python3
"""Client TCP : échange des messages JSON préfixés par 4 octets.
Usage : python3 tcp_client.py [port] [N]"""
import json, socket, struct, sys, time

port = int(sys.argv[1]) if len(sys.argv) > 1 else 6000
N = int(sys.argv[2]) if len(sys.argv) > 2 else 200

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

def une_connexion():
    t = time.perf_counter()
    with socket.create_connection(("127.0.0.1", port), timeout=2) as s:
        for i in range(N):
            envoyer_message(s, json.dumps({"id": i, "montant": 10}))
            recevoir_message(s)
    return (time.perf_counter() - t) * 1000

def test_retour_ligne():
    with socket.create_connection(("127.0.0.1", port), timeout=2) as s:
        # Message contenant explicitement un retour à la ligne (\n)
        msg = json.dumps({"id": 999, "montant": 50, "note": "Ligne 1\nLigne 2"})
        envoyer_message(s, msg)
        reponse = json.loads(recevoir_message(s))
        print("Test avec \\n réussi :", repr(reponse["echo"]["note"]))

a = une_connexion()
print("%d requêtes (préfixe 4 octets) : %.1f ms (%.2f ms/req)" % (N, a, a / N))
test_retour_ligne()
