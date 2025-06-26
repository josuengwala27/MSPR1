# MSPR – COVID & MPOX

Projet complet d'intégration, d'analyse et d'exposition de données COVID-19 et MPOX, structuré en trois modules : **ETL**, **BDD**, **API**.

---

## 1. Architecture du projet

- **ETL/** : Extraction, transformation, profiling et nettoyage des données brutes (Python). Génère les fichiers CSV prêts à charger dans la base (`ETL/processed/`).
- **BDD/** : Schéma de base de données (Prisma/PostgreSQL), scripts de chargement Node.js, gestion de l'intégrité et de la performance.
- **API/** : API REST Express/Prisma pour exposer les données, avec documentation Swagger/OpenAPI.

---

## 2. Pipeline global

1. **Extraction & Transformation (ETL)**
   - Place les fichiers bruts dans `ETL/raw_data/`
   - Exécute les scripts Python pour générer les fichiers transformés dans `ETL/processed/`
2. **Chargement & Validation (BDD)**
   - Synchronise le schéma avec Prisma (`npx prisma db push`)
   - Charge les données CSV dans PostgreSQL (`npm run load`)
   - Valide l'intégrité et la qualité des données
3. **Exposition & Accès (API)**
   - Démarre l'API Node.js (`npm start`)
   - Accède à la documentation interactive sur `/api-docs`
   - Utilise les endpoints pour interroger, filtrer et manipuler les données

---

## 3. Documentation

- **ETL/** : Voir `ETL/README.md` et `ETL/docs/` pour la justification, le profiling, la transformation, l'orchestration, les tests, le benchmark.
- **BDD/** : Voir `BDD/README.md` et `BDD/docs/` pour la conception du schéma, l'initialisation, le chargement, la validation, l'optimisation.
- **API/** : Voir `API/README.md` et la documentation Swagger sur `/api-docs` pour la liste complète des routes et leur fonctionnement.

---

## 4. Prérequis

- Python 3.8+
- Node.js 18+
- PostgreSQL 15+

---

## 5. Installation rapide

```bash
# 1. Préparer l'ETL
cd ETL
python -m venv venv
venv\Scripts\activate  # ou source venv/bin/activate
pip install -r requirements.txt

# 2. Préparer la BDD
cd ../BDD
npm install

# 3. Préparer la base PostgreSQL et le .env
# (voir BDD/README.md)

# 4. Générer les données transformées
cd ../ETL
python scripts/01_extract.py
python scripts/02_profile.py
python scripts/03_transform.py

# 5. Charger les données dans la base
cd ../BDD
npx prisma db push
npm run load

# 6. Lancer l'API
cd ../API
npm install
npm start
```

---

## 6. Points forts du projet

- **Pipeline complet et automatisé** (ETL → BDD → API)
- **Documentation professionnelle** à chaque étape
- **Qualité, robustesse et traçabilité** des données
- **API RESTful** documentée et testable en direct

---

## 7. Ressources

- [Documentation ETL](ETL/README.md)
- [Documentation BDD](BDD/README.md)
- [Documentation API](API/README.md)
- [Swagger UI](http://localhost:3000/api-docs) (après lancement de l'API)
