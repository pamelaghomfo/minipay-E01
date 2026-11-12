# Tous les résultats du Lab2a
# Étape 1 : paiement et idempotence
- Premier paiement (id p1, 5000) : ok, solde de awa = 995000
- Même paiement rejoué : la réponse est'deja_traite', pas de second débit
# Mesures (200 requêtes, 10 en parallèle)
Étape	Situation	                               Erreurs	           Débit	           Latence moyenne
2	   1 instance (référence)	                   0	                58,9 req/s	        148,3 ms
3	   monolithe arrêté	                           200 sur 200	        sans objet	        sans objet
4	   2 instances + répartiteur	               0	                65 req/s	        125,6 ms
5	   instance 5002 tuée, répartiteur actif	   0	                60,6 req/s 	        128,1 ms
# Analyse
- Étape 3 : l'arrêt du monolithe donne 100 % d'erreurs, c'est le point unique de panne.
- Étape 4 : pas de gain de débit sur une seule machine (processeur partagé, saut réseau en plus par le répartiteur). L'objectif est la disponibilité.
- Étape 5 : le service continue sans erreur, le répartiteur renvoie les requêtes vers l'instance restante.
# Étape 6 : incohérence
- Solde de awa sur 5001 : 994500
- Solde de awa sur 5002 : 999900
- Chaque instance possède sa propre base