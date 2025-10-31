# HCI-Project : Implémentation du $1 Gesture Recognizer

## 🎯 Objectif du projet
L’objectif de ce projet est d’implémenter un système complet de reconnaissance de gestes basé sur l’algorithme **$1 Recognizer**, puis de développer une interface graphique permettant :
- de visualiser une galerie de gestes (templates),
- de dessiner un geste à la souris,
- de reconnaître ce geste en temps réel,
- et d’afficher un feedback visuel dynamique.

Ce projet est réalisé en **Python** avec **PySide6** pour l’interface graphique et **NumPy** pour les calculs géométriques.

---

## 🧱 Structure du projet

Le projet est composé des principaux fichiers suivants :

- `MainWindow.py` — point d’entrée de l’application (classe principale et interface générale)
- `Canvas.py` — gestion du tracé utilisateur, affichage du feedback et interaction avec le recognizer
- `onedollar.py` — implémentation de l’algorithme de reconnaissance de gestes ($1 Recognizer)
- `onedol_ds.pkl` — jeu de données contenant les templates de gestes (16 classes)
- `resources/` — icônes, éventuels fichiers annexes
- `README.md` — documentation du projet

---

## ⚙️ Installation

### 1. Créer un environnement virtuel (recommandé)
```bash
python -m venv venv
source venv/bin/activate      # sous Linux / macOS
venv\Scripts\activate         # sous Windows
````

### 2. Installer les dépendances

```bash
pip install numpy PySide6
```

### 3. Lancer l’application

```bash
python MainWindow.py
```

---

## 🚀 Fonctionnalités implémentées

### 🧩 Partie 1 – Interface et galerie de templates

* **Étape 1 à 3 :**

  * Chargement du squelette de l’application (`MainWindow.py`)
  * Création d’une galerie d’icônes via `QListWidget`
  * Chargement des templates depuis `onedol_ds.pkl`
  * Affichage de chaque template sous forme de vignette avec icône et label

### 🧠 Partie 2 – Implémentation du $1 Recognizer

* **Étape 4 :** Ajout des templates au système de reconnaissance (`addTemplate()` dans `OneDollar`)
* **Étape 5 à 8 :** Implémentation complète des étapes de normalisation :

  * Rééchantillonnage des points (`resample()`)
  * Rotation vers l’axe horizontal (`rotateToZero()`, `rotateBy()`)
  * Mise à l’échelle et translation à l’origine (`scaleToSquare()`)
  * Reconnaissance du geste (`recognize()`) avec calcul de la distance minimale entre le geste et chaque template

Résultat : le système affiche en console le label du geste reconnu avec son score de similarité.

### 💬 Partie 3 – Feedback visuel et interaction utilisateur

* **Étape 9 :** Ajout d’un **signal PySide6** émis lors de la reconnaissance d’un geste (`selected_template`)

  * Connexion du signal à `set_action_on_gesture()` pour surligner automatiquement le template reconnu dans la galerie
* **Étape 10 :** Affichage d’un **feedback statique** du template reconnu à proximité du geste de l’utilisateur
* **Étape 11 :** Ajout d’un **feedback dynamique** avec animation grâce à un `QTimer`, interpolant entre le geste dessiné et le template reconnu.

Ces fonctionnalités offrent une interaction fluide et intuitive.

---

## 🔄 Partie 4 – Octopocus (non réalisée)

* **Étape 12 (en cours / non implémentée) :**
  L’objectif de cette étape est d’ajouter une interaction de type **Octopocus**, permettant :

  * Un **mode expert** (reconnaissance rapide classique),
  * Un **mode novice** (affichage progressif de tous les gestes disponibles après 500 ms d’attente).

Cette amélioration n’a pas encore été développée dans la version actuelle.

---

## 🧪 Résultats

À ce stade :

* Le système reconnaît correctement les gestes parmi les 16 classes disponibles.
* L’utilisateur reçoit un retour visuel (statique et dynamique).
* L’interface est entièrement fonctionnelle et stable.

---

## 👤 Auteur

Projet réalisé par **Antony MANUEL** à partir d'une base de code fournit par le professeur **Sylvain Malacria**, dans le cadre du cours de **3DTechnology**
IMT Nord Europe — **2025–2026**

```

---

Souhaites-tu que je te personnalise ce `README.md` avec ton **nom**, ton **établissement**, et éventuellement **des captures d’écran** (je peux ajouter des sections d’images si tu veux) ?
```