#!/usr/bin/env python3
"""Compare les clients face à un service instable : naïf, réessais, disjoncteur consécutif vs fenêtre glissante.
Usage : python3 client_resilient.py [URL] [N]    (service_instable.py doit tourner)"""
import sys, time, requests
from resilience import Disjoncteur, DisjoncteurFenetre, DisjoncteurOuvert, reessayer

URL = sys.argv[1] if len(sys.argv) > 1 else "http://127.0.0.1:7100"
N = int(sys.argv[2]) if len(sys.argv) > 2 else 50

def appel():
    r = requests.get(URL + "/notifier", timeout=1)
    r.raise_for_status()
    return r.json()

def mesurer(nom, f):
    ok = ko = 0; t = time.perf_counter()
    for _ in range(N):
        try: f(); ok += 1
        except Exception: ko += 1
    print("%-28s succès %3d  échecs %3d  durée %.2f s" % (nom, ok, ko, time.perf_counter() - t))

dj = Disjoncteur(seuil=3, delai=2)
dj_fen = DisjoncteurFenetre(taille=20, seuil_taux=0.4, min_appels=5, delai=2)

mesurer("naïf", appel)
mesurer("réessais (4 essais)", lambda: reessayer(appel, essais=4, base=0.05, plafond=0.3))
mesurer("disjoncteur consécutif (3)", lambda: reessayer(lambda: dj.appeler(appel), essais=4, base=0.05, plafond=0.3))
mesurer("disjoncteur fenêtre (20)", lambda: reessayer(lambda: dj_fen.appeler(appel), essais=4, base=0.05, plafond=0.3))
print("compteur côté service :", requests.get(URL + "/compteur").json())
