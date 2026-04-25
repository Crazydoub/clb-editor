# 🔥 LightBurn CLB Editor

Un éditeur graphique avancé pour les fichiers de matériaux **LightBurn (.clb)**.

---

## 🎯 Objectif du projet

LightBurn propose un système de bibliothèque de matériaux puissant, mais **complexe à éditer** :

* navigation peu intuitive
* modification lente
* duplication difficile
* gestion des paramètres peu flexible

👉 **LightBurn CLB Editor** a été créé pour résoudre ces problèmes.

---

## 💡 Pourquoi cet outil ?

Ce projet permet de :

* ⚡ **éditer rapidement les profils matériaux**
* 🎯 ajuster précisément les paramètres laser
* 🔄 dupliquer et organiser facilement les profils
* 🧠 éviter les erreurs liées à l’édition XML manuelle
* 🚀 gagner un temps considérable dans la calibration laser

---

## 🧰 Fonctionnalités principales

### 🧱 Gestion des matériaux

* création / suppression
* renommage (double clic)
* organisation simple

### 📄 Gestion des profils (Entry)

* ajout / duplication / suppression
* tri manuel
* affichage clair (Type | Épaisseur | Description)

### 🎛️ Édition avancée

* paramètres :

  * Vitesse (Speed)
  * Puissance min / max
  * Intervalle (Scan/Image)
* sliders dynamiques selon le type :

  * Cut
  * Scan
  * Image

### 🔄 Undo / Redo

* historique complet des actions
* modifications non destructives

### 📂 Fichiers

* ouverture `.clb`
* sauvegarde directe
* compatibilité LightBurn

---

## 🧠 Cas d’usage

Cet outil est idéal pour :

* 🪵 tests matériaux (bois, MDF, acrylique…)
* 🔥 calibration laser
* 🧪 création de presets
* 📚 gestion de bibliothèques de découpe/gravure
* ⚙️ optimisation de workflow CNC / laser

---

## 🚀 Installation

### Option 1 — Utilisation directe

👉 Télécharger le `.exe` dans **Releases**

* aucun besoin d’installer Python
* lancement en double clic

---

### Option 2 — Depuis le code source

```bash
git clone https://github.com/Crazydoub/clb-editor.git
cd clb-editor
python src/editor.pyw
```

---

## 🏗️ Build (création du .exe)

```bash
pyinstaller --onefile --noconsole src/editor.pyw
```

---

## 📁 Structure du projet

```
clb-editor/
├── src/            # code source
├── assets/         # icônes
├── dist/           # build (ignoré)
├── build/          # temporaire
├── README.md
├── LICENSE
```

---

## ⚠️ Licence

Ce projet est **strictement non-commercial**.

✔️ Autorisé :

* usage personnel
* modification
* partage

❌ Interdit :

* usage commercial
* revente
* intégration dans un produit payant

---

## 🧠 Pourquoi ne pas utiliser LightBurn directement ?

| Fonction             | LightBurn | CLB Editor |
| -------------------- | --------- | ---------- |
| édition rapide       | ❌         | ✔️         |
| duplication profils  | ❌         | ✔️         |
| vue globale          | ❌         | ✔️         |
| manipulation massive | ❌         | ✔️         |

---

## 🚀 Roadmap

* 🎨 UI améliorée
* 📊 génération automatique de tests laser
* 🧠 presets matériaux intelligents
* 🔄 auto-update
* 🌙 dark mode

---

## 🤝 Contribution

Projet ouvert aux améliorations 👍

---

## 👨‍💻 Auteur

Crazydoub

---

## ⭐ Support

Si ce projet t’aide :

👉 laisse une étoile ⭐ sur GitHub
