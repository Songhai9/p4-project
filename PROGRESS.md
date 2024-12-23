# README

Ce document décrit toutes les étapes et sous-étapes pour compléter le projet POKEMON (Kit Parfaitement Optimisé pour une MONitoring Efficace). Le projet consiste à concevoir une plateforme de supervision de réseau qui détecte et réagit aux anomalies dans un réseau programmable en utilisant P4 et des contrôleurs Python.

**Légende pour le statut des tâches :**
- `[ ]` = Pas encore implémenté
- `[x]` = Implémenté mais non testé
- `[🟧]` = Implémenté mais échoue à certains tests ou tests incomplets
- `[✅]` = Implémenté Set réussissant tous les tests

---


## Création de l'Équipement

### Étape 1 : Implémenter `simple_router`

**Objectif :** Créer un routeur de base capable de routage IP intra-domaine.

- [✅] Créer `simple_router.p4` qui :  
  - [✅] Analyse les en-têtes Ethernet et IPv4  
  - [✅] Effectue des recherches LPM pour les destinations  
  - [✅] Transfère les paquets vers les ports de sortie corrects  
  - [✅] Maintient les compteurs/registres nécessaires
- [✅] Plan de contrôle Python qui :  
  - [✅] Calcule les chemins les plus courts en fonction de la topologie connue  
  - [✅] Installe les entrées de transfert dans les tables P4  
- [✅] Tester la connectivité de base (tests de ping) entre les hôtes finaux

### Étape 2 : Ajouter l'Encapsulation pour le Routage par Points de Passage

**Objectif :** Étendre `simple_router` pour imposer des chemins spécifiques via l'encapsulation.

- [ ] Modifier le programme P4 pour gérer un en-tête supplémentaire pour le routage "imposé par points de passage"  
- [ ] Implémenter la logique pour envoyer les paquets via des nœuds intermédiaires spécifiés (points de passage)  
- [ ] Mettre à jour le plan de contrôle Python pour :  
  - [ ] Installer des règles basées sur les points de passage  
  - [ ] Tester en définissant un chemin incluant des points de passage intermédiaires et vérifier que les paquets le suivent

### Étape 3 : Créer `simple_router_loss` et `simple_router_stupid`

**Objectif :** Introduire des équipements défectueux pour tester la supervision.

- [ ] `simple_router_loss` (modifications P4) :  
  - [ ] Introduire des pertes de paquets probabilistes (par exemple, 30%)  
  - [ ] Utiliser une sélection de chemin aléatoire au lieu des chemins les plus courts pour simuler la corruption
- [ ] `simple_router_stupid` (modifications P4) :  
  - [ ] Transférer incorrectement uniquement lorsqu'aucune spécification explicite de lien par lien n'est présente  
  - [ ] Si un chemin de lien par lien est donné, transférer correctement
- [ ] Tester ces variantes dans une topologie mixte

## Création du Méta-Contrôleur

### Étape 4 : Implémenter l'Interface du Méta-Contrôleur

**Objectif :** Un contrôleur global qui gère tous les équipements.

- [ ] Implémenter les fonctions du méta-contrôleur :  
  - [ ] `read_register_on(switch_id, register_name)`  
  - [ ] `write_register_on(switch_id, register_name, value)`  
  - [ ] `install_entry_on(switch_id, table_name, entry)`  
  - [ ] `remove_entry_on(switch_id, table_name, entry)`
- [ ] S'assurer que le méta-contrôleur peut distribuer les informations de topologie globale aux contrôleurs par switch  
- [ ] Tester en lisant/écrivant un registre de test sur un switch

## Supervision de Base : Analyse des Sondes de Niveau de Lien

### Étape 5 : Implémenter la Supervision des Liens

**Objectif :** Envoyer des sondes pour mesurer la santé de chaque lien sortant.

- [ ] Dans le plan de données P4 de chaque switch :  
  - [ ] Envoyer régulièrement un paquet sonde via le port CPU à travers chaque lien sortant  
  - [ ] Diviser la sonde en autant de "sondes" qu'il y a de liens sortants  
  - [ ] Chaque switch récepteur renvoie explicitement la sonde sur le lien correspondant (aller-retour)
  - [ ] Maintenir les compteurs : nombre envoyé, nombre retourné
- [ ] Méta-contrôleur périodiquement :  
  - [ ] Lit ces compteurs de chaque switch  
  - [ ] Détecte les anomalies si le taux de retour est en dessous d'un seuil
- [ ] Tester en simulant des pannes de lien ou en utilisant `simple_router_loss` pour vérifier la détection

## Supervision des Chemins : Vérification des Chemins les Plus Courts

### Étape 6 : Superviser les Chemins les Plus Courts

**Objectif :** S'assurer que les chemins les plus courts sont suivis.

- [ ] Étendre P4 et les contrôleurs par switch pour :  
  - [ ] Envoyer des sondes de vérification de chemin qui tracent le chemin réel emprunté  
  - [ ] Collecter les informations de saut intermédiaire dans un en-tête dédié
- [ ] Méta-contrôleur :  
  - [ ] Rassembler les résultats des sondes de chemin de chaque contrôleur  
  - [ ] Comparer les chemins réels aux chemins les plus courts attendus  
  - [ ] Détecter les déviations
- [ ] Tester avec `simple_router_stupid` pour s'assurer que le méta-contrôleur détecte les paquets mal acheminés

## Détection et Réaction

### Étape 7 : Réagir aux Anomalies

**Objectif :** Modifier la configuration du réseau pour éviter les routeurs/liens problématiques.

- [ ] Logique du méta-contrôleur :  
  - [ ] Identifier les routeurs problématiques (perte ou mauvais acheminement)  
  - [ ] Ajuster les poids IGP ou les entrées de routage pour contourner ces routeurs  
  - [ ] Calculer les changements minimaux nécessaires et les appliquer
- [ ] Tester en créant une anomalie et en vérifiant que le méta-contrôleur redirige le trafic

## Optimisation et Améliorations

### Étape 8 : Optimiser la Plateforme

**Objectif :** Réduire les frais généraux tout en maintenant les capacités de détection.

- [ ] Ajuster la fréquence des sondes  
- [ ] Limiter la vérification des chemins aux routes critiques si nécessaire  
- [ ] Éventuellement compresser ou regrouper les sondes
- [ ] Évaluer l'impact sur les performances et documenter les compromis

## Tests et Intégration

### Étape 9 : Tests et Validation Complets

**Objectif :** Tests de bout en bout couvrant toutes les fonctionnalités.

- [ ] Tests automatisés pour :  
  - [ ] Connectivité de base  
  - [ ] Détection de panne de lien  
  - [ ] Détection de déviation de chemin  
  - [ ] Correction de la réaction (reroutage)
- [ ] Vérifier les résultats et s'assurer que toutes les fonctionnalités fonctionnent ensemble

## Documentation et Livraison

### Étape 10 : Finaliser la Documentation et la Soumission

**Objectif :** Produire les livrables requis.

- [ ] Rédiger le rapport final (PDF) expliquant l'architecture, les décisions de conception, les tests et les résultats  
- [ ] Mettre à jour ce README :  
  - [ ] Marquer le statut de chaque tâche  
- [ ] Fournir des instructions sur :  
  - [ ] Démarrer l'environnement Docker/VM  
  - [ ] Lancer le méta-contrôleur et les contrôleurs par switch  
  - [ ] Compiler et exécuter les programmes P4  
  - [ ] Exécuter les tests
- [ ] Soumettre via Moodle comme indiqué

---

**Si des détails ou des clarifications supplémentaires sont nécessaires, ajoutez-les ici ou dans la documentation complémentaire.**  
Au fur et à mesure que vous implémentez et testez chaque fonctionnalité, mettez à jour les marqueurs de statut (`[ ]`, `[x]`, `[🟧]`, `[✅]`).

