 --- Procédure d'utilisation du programme ---
1. Installer python 3.7 ou plus récent

2. Lancer l'invite de commande python 3

3. Executer les commandes suivantes :
 - import os
 - os.chdir(r"chemin du dossier du programme")
   (en remplaçant "chemin du dossier du programme" par le chemin d'accès au dossier contenant le fichier .py du programme)
 - exec(open(r"./main.py").read())