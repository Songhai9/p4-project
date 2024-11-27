# README - Projet POKEMON

Ce fichier décrit les étapes du projet POKEMON et leurs sous-étapes. Chaque fonctionnalité est représentée par une case à cocher, dont l'état évolue comme suit :
- `[ ]` : Non implémentée.
- `[x]` : Implémentée mais non testée.
- `[🟧]` : Implémentée mais échoue certains tests.
- `[✅]` : Implémentée et validée avec succès.

---

## Étape 1 : Création des équipements de base
- [ ] **Développer simple_router**
  - [ ] Implémenter un plan de données en P4 pour le routage.
  - [ ] Implémenter un plan de contrôle en Python pour calculer et installer les tables.
  - [ ] Tester le routage sur des topologies simples.
- [ ] **Ajouter une fonctionnalité d'encapsulation**
  - [ ] Permettre d’imposer des points de passage intermédiaires.
  - [ ] Tester les chemins spécifiés avec des paquets.
- [ ] **Créer des équipements défaillants**
  - [ ] Implémenter `simple_router_loss` avec une probabilité de perte de 30%.
  - [ ] Implémenter `simple_router_stupid` avec des chemins aléatoires sauf si explicitement définis.
  - [ ] Tester et valider leurs comportements.

---

## Étape 2 : Création du méta-contrôleur
- [ ] Développer le méta-contrôleur pour gérer les équipements.
  - [ ] Implémenter `read_register_on` pour lire un registre spécifique.
  - [ ] Implémenter `write_register_on` pour écrire dans un registre spécifique.
  - [ ] Implémenter `install_entry_on` pour ajouter une entrée dans une table.
  - [ ] Implémenter `remove_entry_on` pour retirer une entrée d'une table.
- [ ] Tester la communication avec les équipements.

---

## Étape 3 : Supervision des liens
- [ ] Implémenter la supervision des pertes.
  - [ ] Envoyer des sondes pour chaque lien sortant.
  - [ ] Calculer et stocker le nombre de sondes reçues et manquantes.
  - [ ] Détecter et afficher les anomalies dans le méta-contrôleur.
- [ ] Implémenter la supervision des chemins.
  - [ ] Envoyer des sondes vers tous les commutateurs.
  - [ ] Enregistrer les sauts intermédiaires dans un en-tête dédié.
  - [ ] Identifier les chemins incorrects et les signaler.

---

## Étape 4 : Détection et réaction
- [ ] Implémenter la détection des anomalies par le méta-contrôleur.
- [ ] Modifier les poids IGP pour exclure les équipements défaillants.
- [ ] Valider les nouveaux comportements du réseau après modifications.

---

## Étape 5 : Optimisation
- [ ] Minimiser la surcharge réseau causée par les sondes.
- [ ] Optimiser les algorithmes de détection et de réaction.
- [ ] Tester les performances sur diverses topologies.

---

## Étape 6 : Rapport et documentation
- [ ] Rédiger un rapport expliquant les implémentations.
- [ ] Décrire les expériences et tests réalisés.
- [ ] Préparer un README détaillant l'architecture et l’utilisation.

---

