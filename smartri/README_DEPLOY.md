# Déploiement SmartRI Web

## 1. Lancer le backend (API Python)

Ouvrez un terminal dans le dossier `smartri` et lancez :

    start_backend.bat

Cela démarre le serveur FastAPI sur http://localhost:8000

## 2. Lancer le frontend (interface web)

Ouvrez le fichier :

    frontend/index.html

…dans votre navigateur web (double-cliquez ou faites clic droit > ouvrir avec Chrome/Edge/Firefox).

## 3. Utilisation

- Cliquez sur "Sélectionnez un fichier Excel" puis "Analyser"
- Les résultats s’affichent dans le tableau, colorés selon le risque

## 4. Déploiement sur un serveur

- Backend : déployez `main.py` (FastAPI) sur un serveur (Heroku, Azure, etc.)
- Frontend : hébergez le dossier `frontend/` sur Netlify, Vercel, ou le même serveur (en statique)

---

**Tout est prêt pour une utilisation web collaborative et moderne !**
