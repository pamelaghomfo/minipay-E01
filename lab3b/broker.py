#!/usr/bin/env python3
"""Mini-courtier de messages (pédagogique) : files, accusés de réception, redistribution.
Garantie offerte : AU MOINS UNE FOIS. Un message livré mais non acquitté dans le délai
de visibilité est redistribué (le consommateur peut donc le recevoir plusieurs fois).
Après MAX_ESSAIS livraisons sans ack, le message est déplacé dans <file>_rebuts.

Usage : python3 broker.py [port]
  POST /publier/<file>            corps JSON {"id": "...", ...}  -> {"msg_id": n}
  GET  /consommer/<file>?visibilite=5  -> message ou 204 si rien
  POST /ack/<file>/<msg_id>       -> acquitte (supprime) le message
  GET  /stats/<file>              -> {"en_attente", "en_cours", "livraisons", "rebuts"}
"""
import sys, threading, time
from flask import Flask, jsonify, request

app = Flask(__name__)
verrou = threading.Lock()
FILES = {}        # nom -> {"msgs": {msg_id: {...}}, "suivant": int, "livraisons": int}
MAX_ESSAIS = 3

def etat(nom):
    return FILES.setdefault(nom, {"msgs": {}, "suivant": 1, "livraisons": 0})

@app.post("/publier/<nom>")
def publier(nom):
    with verrou:
        f = etat(nom); mid = f["suivant"]; f["suivant"] += 1
        f["msgs"][mid] = {"corps": request.get_json(), "visible_a": 0.0, "essais": 0}
    return jsonify(msg_id=mid), 201

@app.get("/consommer/<nom>")
def consommer(nom):
    vis = float(request.args.get("visibilite", 5))
    maintenant = time.time()
    with verrou:
        f = etat(nom)
        for mid in sorted(list(f["msgs"])):
            m = f["msgs"][mid]
            if m["visible_a"] <= maintenant:
                # Défi : déplacement vers <nom>_rebuts après 3 livraisons sans ack
                if m["essais"] >= MAX_ESSAIS and not nom.endswith("_rebuts"):
                    del f["msgs"][mid]
                    rebuts = etat(f"{nom}_rebuts")
                    rid = rebuts["suivant"]; rebuts["suivant"] += 1
                    rebuts["msgs"][rid] = {
                        "corps": m["corps"],
                        "visible_a": 0.0,
                        "essais": 0,
                        "msg_id_origine": mid
                    }
                    continue

                m["visible_a"] = maintenant + vis      # invisible pendant 'vis' secondes
                m["essais"] += 1; f["livraisons"] += 1
                return jsonify(msg_id=mid, corps=m["corps"], essai=m["essais"])
    return "", 204

@app.post("/ack/<nom>/<int:mid>")
def ack(nom, mid):
    with verrou:
        existait = etat(nom)["msgs"].pop(mid, None) is not None
    return jsonify(ok=existait)

@app.get("/stats/<nom>")
def stats(nom):
    t = time.time()
    with verrou:
        f = etat(nom)
        en_cours = sum(1 for m in f["msgs"].values() if m["visible_a"] > t)
        nb_rebuts = len(FILES[f"{nom}_rebuts"]["msgs"]) if f"{nom}_rebuts" in FILES else 0
        return jsonify(
            en_attente=len(f["msgs"]) - en_cours,
            en_cours=en_cours,
            livraisons=f["livraisons"],
            rebuts=nb_rebuts
        )

if __name__ == "__main__":
    app.run(port=int(sys.argv[1]) if len(sys.argv) > 1 else 7000, threaded=True)
