# Documentation détaillée des routes de l'API Pandémies

## Sommaire
- [Pays](#pays)
- [Indicateurs](#indicateurs)
- [Données Historiques](#donnees-historiques)

---

## Pays

### GET /api/pays
- **Description** : Liste tous les pays enregistrés dans la base.
- **Réponse** :
  - 200 : Tableau d'objets pays.
- **Exemple de réponse** :
```json
[
  { "id_pays": 1, "country": "France", "iso_code": "FRA", "population": 67000000 },
  { "id_pays": 2, "country": "Allemagne", "iso_code": "DEU", "population": 83000000 }
]
```

---

### GET /api/pays/:id
- **Description** : Récupère un pays par son identifiant unique.
- **Paramètres** :
  - `id` (path, integer) : Identifiant du pays
- **Réponse** :
  - 200 : Objet pays
  - 404 : Pays non trouvé

---

### GET /api/pays/iso/:code
- **Description** : Récupère un pays par son code ISO (3 lettres).
- **Paramètres** :
  - `code` (path, string) : Code ISO du pays
- **Réponse** :
  - 200 : Objet pays
  - 404 : Pays non trouvé

---

### POST /api/pays
- **Description** : Crée un nouveau pays.
- **Body attendu** :
```json
{
  "country": "France",
  "iso_code": "FRA",
  "population": 67000000
}
```
- **Réponse** :
  - 201 : Pays créé
  - 400 : Données manquantes ou invalides
  - 409 : Pays ou code ISO déjà existant

---

### PUT /api/pays/:id
- **Description** : Met à jour un pays existant.
- **Paramètres** :
  - `id` (path, integer)
- **Body attendu** :
```json
{
  "country": "France",
  "iso_code": "FRA",
  "population": 68000000
}
```
- **Réponse** :
  - 200 : Pays mis à jour
  - 400 : Données invalides
  - 404 : Pays non trouvé
  - 409 : Code ISO déjà utilisé

---

### DELETE /api/pays/:id
- **Description** : Supprime un pays par son identifiant.
- **Paramètres** :
  - `id` (path, integer)
- **Réponse** :
  - 204 : Pays supprimé
  - 404 : Pays non trouvé
  - 409 : Pays référencé dans d'autres données

---

## Indicateurs

### GET /api/indicateurs
- **Description** : Liste tous les indicateurs disponibles.
- **Réponse** :
  - 200 : Tableau d'objets indicateur

---

### GET /api/indicateurs/:id
- **Description** : Récupère un indicateur par son identifiant.
- **Paramètres** :
  - `id` (path, integer)
- **Réponse** :
  - 200 : Objet indicateur
  - 404 : Indicateur non trouvé

---

### GET /api/indicateurs/nom/:nom
- **Description** : Récupère un indicateur par son nom.
- **Paramètres** :
  - `nom` (path, string)
- **Réponse** :
  - 200 : Objet indicateur
  - 404 : Indicateur non trouvé

---

### POST /api/indicateurs
- **Description** : Crée un nouvel indicateur.
- **Body attendu** :
```json
{
  "indicator_name": "cases",
  "description": "Nombre de cas confirmés"
}
```
- **Réponse** :
  - 201 : Indicateur créé
  - 400 : Données manquantes ou invalides
  - 409 : Indicateur déjà existant

---

### PUT /api/indicateurs/:id
- **Description** : Met à jour un indicateur existant.
- **Paramètres** :
  - `id` (path, integer)
- **Body attendu** :
```json
{
  "indicator_name": "cases",
  "description": "Cas confirmés (mis à jour)"
}
```
- **Réponse** :
  - 200 : Indicateur mis à jour
  - 400 : Données invalides
  - 404 : Indicateur non trouvé
  - 409 : Nom d'indicateur déjà utilisé

---

### DELETE /api/indicateurs/:id
- **Description** : Supprime un indicateur par son identifiant.
- **Paramètres** :
  - `id` (path, integer)
- **Réponse** :
  - 204 : Indicateur supprimé
  - 404 : Indicateur non trouvé
  - 409 : Indicateur référencé dans d'autres données

---

## Données Historiques

### GET /api/donnees-historiques
- **Description** : Récupère la liste paginée des données historiques.
- **Paramètres** (query) :
  - `page` (integer, optionnel)
  - `limit` (integer, optionnel)
- **Réponse** :
  - 200 : Objet avec données et pagination
- **Exemple de réponse** :
```json
{
  "data": [
    { "id_donnee": 1, "date": "2023-01-01", "country": "France", ... }
  ],
  "pagination": { "page": 1, "limit": 100, "total": 1234, "pages": 13 }
}
```

---

### GET /api/donnees-historiques/filtre
- **Description** : Filtre les données historiques selon plusieurs critères.
- **Paramètres** (query) :
  - `pays`, `iso_code`, `indicator`, `dateDebut`, `dateFin`, `source`, `page`, `limit`
- **Réponse** :
  - 200 : Objet avec données filtrées et pagination

---

### GET /api/donnees-historiques/pays/:isoCode
- **Description** : Récupère les données historiques pour un pays donné.
- **Paramètres** :
  - `isoCode` (path, string)
  - `indicator`, `dateDebut`, `dateFin`, `page`, `limit` (query)
- **Réponse** :
  - 200 : Objet avec données et pagination

---

### GET /api/donnees-historiques/:id
- **Description** : Récupère une donnée historique par son identifiant.
- **Paramètres** :
  - `id` (path, integer)
- **Réponse** :
  - 200 : Objet donnée historique
  - 404 : Donnée non trouvée

---

### POST /api/donnees-historiques
- **Description** : Crée une nouvelle donnée historique.
- **Body attendu** :
```json
{
  "date": "2023-01-01",
  "country": "France",
  "indicator": "cases",
  "value": 1000,
  "iso_code": "FRA",
  "source": "OMS"
}
```
- **Réponse** :
  - 201 : Donnée créée
  - 400 : Données manquantes ou invalides

---

### PUT /api/donnees-historiques/:id
- **Description** : Met à jour une donnée historique existante.
- **Paramètres** :
  - `id` (path, integer)
- **Body attendu** :
```json
{
  "value": 1200,
  "cases_per_100k": 15.2
}
```
- **Réponse** :
  - 200 : Donnée mise à jour
  - 400 : Données invalides
  - 404 : Donnée non trouvée

---

### DELETE /api/donnees-historiques/:id
- **Description** : Supprime une donnée historique par son identifiant.
- **Paramètres** :
  - `id` (path, integer)
- **Réponse** :
  - 204 : Donnée supprimée
  - 404 : Donnée non trouvée 