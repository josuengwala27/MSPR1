# Modélisation simplifiée du projet ETL Pandémies (alignée sur les fichiers CSV)

## 1. Modèle Conceptuel de Données (MCD)

```
+----------------+         +------------------+
|     Pays       |         |   Indicateur     |
+----------------+         +------------------+
| id_pays PK     |         | id_indicateur PK |
| country        |         | indicator_name   |
| iso_code       |         | description      |
| population     |         +------------------+
+----------------+
        | 1
        |-------------------+
        |                   |
        | N                 | N
+-------------------+       |
| DonneeHistorique  |<------+
+-------------------+
| id_donnee PK      |
| date              |
| country           |
| value             |
| indicator         |
| source            |
| iso_code          |
| population        |
| unit              |
| cases_per_100k    |
| deaths_per_100k   |
| incidence_7j      |
| growth_rate       |
+-------------------+
```

---

## 2. Tables (alignées sur les CSV)

- **pays** (id_pays PK, country, iso_code, population)
- **indicateur** (id_indicateur PK, indicator_name, description)
- **donnee_historique** (id_donnee PK, date, country, value, indicator, source, iso_code, population, unit, cases_per_100k, deaths_per_100k, incidence_7j, growth_rate)

---

## 3. Script SQL PostgreSQL (exemple)

```sql
CREATE TABLE pays (
  id_pays SERIAL PRIMARY KEY,
  country VARCHAR(100) NOT NULL,
  iso_code CHAR(3) NOT NULL UNIQUE,
  population BIGINT
);

CREATE TABLE indicateur (
  id_indicateur SERIAL PRIMARY KEY,
  indicator_name VARCHAR(50) NOT NULL UNIQUE,
  description TEXT
);

CREATE TABLE donnee_historique (
  id_donnee SERIAL PRIMARY KEY,
  date DATE NOT NULL,
  country VARCHAR(100) NOT NULL,
  value DOUBLE PRECISION,
  indicator VARCHAR(50) NOT NULL,
  source VARCHAR(100),
  iso_code CHAR(3),
  population BIGINT,
  unit VARCHAR(20),
  cases_per_100k DOUBLE PRECISION,
  deaths_per_100k DOUBLE PRECISION,
  incidence_7j DOUBLE PRECISION,
  growth_rate DOUBLE PRECISION
);
```

---

## 4. Remarques

- La colonne `region` n'existe pas dans les CSV, elle est donc supprimée.
- Les tables sont alignées sur les fichiers générés par l'ETL.
- Les faits (donnee_historique) sont stockés dans deux fichiers (covid et mpox) mais ont la même structure.
- Les dimensions sont réduites à l'essentiel (pays, indicateur).

---

**Ce document est la référence pour la modélisation et l'implémentation de ta base analytique ETL Pandémies, alignée sur les fichiers CSV réels.** 