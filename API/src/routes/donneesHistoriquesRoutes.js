const express = require('express');
const router = express.Router();
const { PrismaClient } = require('@prisma/client');
const prisma = new PrismaClient();

/**
 * @swagger
 * tags:
 *   name: DonneesHistoriques
 *   description: Gestion des données historiques
 */

/**
 * @swagger
 * /api/donnees-historiques:
 *   get:
 *     summary: Récupère les données historiques (pagination)
 *     tags: [DonneesHistoriques]
 *     parameters:
 *       - in: query
 *         name: page
 *         schema:
 *           type: integer
 *         description: Numéro de page
 *       - in: query
 *         name: limit
 *         schema:
 *           type: integer
 *         description: Nombre d'éléments par page
 *     responses:
 *       200:
 *         description: Liste paginée des données historiques
 */
// GET toutes les données historiques (avec pagination)
router.get('/', async (req, res) => {
  try {
    const page = parseInt(req.query.page) || 1;
    const limit = parseInt(req.query.limit) || 100;
    const skip = (page - 1) * limit;
    
    const donnees = await prisma.donneeHistorique.findMany({
      skip,
      take: limit,
      orderBy: {
        date: 'desc'
      }
    });
    
    const total = await prisma.donneeHistorique.count();
    
    res.json({
      data: donnees,
      pagination: {
        page,
        limit,
        total,
        pages: Math.ceil(total / limit)
      }
    });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

/**
 * @swagger
 * /api/donnees-historiques/filtre:
 *   get:
 *     summary: Filtre les données historiques
 *     tags: [DonneesHistoriques]
 *     parameters:
 *       - in: query
 *         name: pays
 *         schema:
 *           type: string
 *         description: Nom du pays
 *       - in: query
 *         name: iso_code
 *         schema:
 *           type: string
 *         description: Code ISO
 *       - in: query
 *         name: indicator
 *         schema:
 *           type: string
 *         description: Indicateur
 *       - in: query
 *         name: dateDebut
 *         schema:
 *           type: string
 *           format: date
 *         description: Date de début
 *       - in: query
 *         name: dateFin
 *         schema:
 *           type: string
 *           format: date
 *         description: Date de fin
 *       - in: query
 *         name: source
 *         schema:
 *           type: string
 *         description: Source
 *       - in: query
 *         name: page
 *         schema:
 *           type: integer
 *         description: Numéro de page
 *       - in: query
 *         name: limit
 *         schema:
 *           type: integer
 *         description: Nombre d'éléments par page
 *     responses:
 *       200:
 *         description: Liste filtrée des données historiques
 */
// GET données historiques filtrées
router.get('/filtre', async (req, res) => {
  try {
    const {
      pays,
      iso_code,
      indicator,
      dateDebut,
      dateFin,
      source,
      page = 1,
      limit = 100
    } = req.query;
    
    const skip = (parseInt(page) - 1) * parseInt(limit);
    
    let where = {};
    
    // Construction des filtres
    if (pays) where.country = pays;
    if (iso_code) where.iso_code = iso_code;
    if (indicator) where.indicator = indicator;
    if (source) where.source = source;
    
    // Filtre de date
    if (dateDebut || dateFin) {
      where.date = {};
      if (dateDebut) where.date.gte = new Date(dateDebut);
      if (dateFin) where.date.lte = new Date(dateFin);
    }
    
    const donnees = await prisma.donneeHistorique.findMany({
      where,
      skip,
      take: parseInt(limit),
      orderBy: {
        date: 'desc'
      }
    });
    
    const total = await prisma.donneeHistorique.count({ where });
    
    res.json({
      data: donnees,
      pagination: {
        page: parseInt(page),
        limit: parseInt(limit),
        total,
        pages: Math.ceil(total / parseInt(limit))
      }
    });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

/**
 * @swagger
 * /api/donnees-historiques/pays/{isoCode}:
 *   get:
 *     summary: Récupère les données par pays
 *     tags: [DonneesHistoriques]
 *     parameters:
 *       - in: path
 *         name: isoCode
 *         required: true
 *         schema:
 *           type: string
 *         description: Code ISO du pays
 *       - in: query
 *         name: indicator
 *         schema:
 *           type: string
 *         description: Indicateur
 *       - in: query
 *         name: dateDebut
 *         schema:
 *           type: string
 *           format: date
 *         description: Date de début
 *       - in: query
 *         name: dateFin
 *         schema:
 *           type: string
 *           format: date
 *         description: Date de fin
 *       - in: query
 *         name: page
 *         schema:
 *           type: integer
 *         description: Numéro de page
 *       - in: query
 *         name: limit
 *         schema:
 *           type: integer
 *         description: Nombre d'éléments par page
 *     responses:
 *       200:
 *         description: Liste des données historiques pour un pays
 */
// GET données historiques par pays
router.get('/pays/:isoCode', async (req, res) => {
  try {
    const isoCode = req.params.isoCode;
    const {
      indicator,
      dateDebut,
      dateFin,
      page = 1,
      limit = 100
    } = req.query;
    
    const skip = (parseInt(page) - 1) * parseInt(limit);
    
    let where = { iso_code: isoCode };
    
    if (indicator) where.indicator = indicator;
    
    // Filtre de date
    if (dateDebut || dateFin) {
      where.date = {};
      if (dateDebut) where.date.gte = new Date(dateDebut);
      if (dateFin) where.date.lte = new Date(dateFin);
    }
    
    const donnees = await prisma.donneeHistorique.findMany({
      where,
      skip,
      take: parseInt(limit),
      orderBy: {
        date: 'desc'
      }
    });
    
    const total = await prisma.donneeHistorique.count({ where });
    
    res.json({
      data: donnees,
      pagination: {
        page: parseInt(page),
        limit: parseInt(limit),
        total,
        pages: Math.ceil(total / parseInt(limit))
      }
    });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

/**
 * @swagger
 * /api/donnees-historiques/{id}:
 *   get:
 *     summary: Récupère une donnée par ID
 *     tags: [DonneesHistoriques]
 *     parameters:
 *       - in: path
 *         name: id
 *         required: true
 *         schema:
 *           type: integer
 *         description: ID de la donnée
 *     responses:
 *       200:
 *         description: Donnée trouvée
 *       404:
 *         description: Donnée non trouvée
 */
// GET une donnée historique par ID
router.get('/:id', async (req, res) => {
  try {
    const id = parseInt(req.params.id);
    const donnee = await prisma.donneeHistorique.findUnique({
      where: { id_donnee: id }
    });
    
    if (!donnee) {
      return res.status(404).json({ error: 'Donnée historique non trouvée' });
    }
    
    res.json(donnee);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

/**
 * @swagger
 * /api/donnees-historiques:
 *   post:
 *     summary: Crée une nouvelle donnée historique
 *     tags: [DonneesHistoriques]
 *     requestBody:
 *       required: true
 *       content:
 *         application/json:
 *           schema:
 *             type: object
 *             required:
 *               - date
 *               - country
 *               - indicator
 *             properties:
 *               date:
 *                 type: string
 *                 format: date
 *               country:
 *                 type: string
 *               value:
 *                 type: number
 *               indicator:
 *                 type: string
 *               source:
 *                 type: string
 *               iso_code:
 *                 type: string
 *               population:
 *                 type: integer
 *               unit:
 *                 type: string
 *               cases_per_100k:
 *                 type: number
 *               deaths_per_100k:
 *                 type: number
 *               incidence_7j:
 *                 type: number
 *               growth_rate:
 *                 type: number
 *     responses:
 *       201:
 *         description: Donnée créée
 *       400:
 *         description: Données invalides
 */
// POST créer une donnée historique
router.post('/', async (req, res) => {
  try {
    const {
      date,
      country,
      value,
      indicator,
      source,
      iso_code,
      population,
      unit,
      cases_per_100k,
      deaths_per_100k,
      incidence_7j,
      growth_rate
    } = req.body;
    
    if (!date || !country || !indicator) {
      return res.status(400).json({ 
        error: 'La date, le pays et l\'indicateur sont requis' 
      });
    }
    
    const nouvelleDonnee = await prisma.donneeHistorique.create({
      data: {
        date: new Date(date),
        country,
        value: value || null,
        indicator,
        source: source || null,
        iso_code: iso_code || null,
        population: population ? BigInt(population) : null,
        unit: unit || null,
        cases_per_100k: cases_per_100k || null,
        deaths_per_100k: deaths_per_100k || null,
        incidence_7j: incidence_7j || null,
        growth_rate: growth_rate || null
      }
    });
    
    res.status(201).json(nouvelleDonnee);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

/**
 * @swagger
 * /api/donnees-historiques/{id}:
 *   put:
 *     summary: Met à jour une donnée historique
 *     tags: [DonneesHistoriques]
 *     parameters:
 *       - in: path
 *         name: id
 *         required: true
 *         schema:
 *           type: integer
 *         description: ID de la donnée
 *     requestBody:
 *       required: true
 *       content:
 *         application/json:
 *           schema:
 *             type: object
 *             properties:
 *               date:
 *                 type: string
 *                 format: date
 *               country:
 *                 type: string
 *               value:
 *                 type: number
 *               indicator:
 *                 type: string
 *               source:
 *                 type: string
 *               iso_code:
 *                 type: string
 *               population:
 *                 type: integer
 *               unit:
 *                 type: string
 *               cases_per_100k:
 *                 type: number
 *               deaths_per_100k:
 *                 type: number
 *               incidence_7j:
 *                 type: number
 *               growth_rate:
 *                 type: number
 *     responses:
 *       200:
 *         description: Donnée mise à jour
 *       400:
 *         description: Données invalides
 *       404:
 *         description: Donnée non trouvée
 */
// PUT mettre à jour une donnée historique
router.put('/:id', async (req, res) => {
  try {
    const id = parseInt(req.params.id);
    const {
      date,
      country,
      value,
      indicator,
      source,
      iso_code,
      population,
      unit,
      cases_per_100k,
      deaths_per_100k,
      incidence_7j,
      growth_rate
    } = req.body;
    
    const donneeExiste = await prisma.donneeHistorique.findUnique({
      where: { id_donnee: id }
    });
    
    if (!donneeExiste) {
      return res.status(404).json({ error: 'Donnée historique non trouvée' });
    }
    
    const donneeModifiee = await prisma.donneeHistorique.update({
      where: { id_donnee: id },
      data: {
        date: date ? new Date(date) : undefined,
        country: country || undefined,
        value: value !== undefined ? value : undefined,
        indicator: indicator || undefined,
        source: source !== undefined ? source : undefined,
        iso_code: iso_code !== undefined ? iso_code : undefined,
        population: population !== undefined ? BigInt(population) : undefined,
        unit: unit !== undefined ? unit : undefined,
        cases_per_100k: cases_per_100k !== undefined ? cases_per_100k : undefined,
        deaths_per_100k: deaths_per_100k !== undefined ? deaths_per_100k : undefined,
        incidence_7j: incidence_7j !== undefined ? incidence_7j : undefined,
        growth_rate: growth_rate !== undefined ? growth_rate : undefined
      }
    });
    
    res.json(donneeModifiee);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

/**
 * @swagger
 * /api/donnees-historiques/{id}:
 *   delete:
 *     summary: Supprime une donnée historique
 *     tags: [DonneesHistoriques]
 *     parameters:
 *       - in: path
 *         name: id
 *         required: true
 *         schema:
 *           type: integer
 *         description: ID de la donnée
 *     responses:
 *       204:
 *         description: Donnée supprimée
 *       404:
 *         description: Donnée non trouvée
 */
// DELETE supprimer une donnée historique
router.delete('/:id', async (req, res) => {
  try {
    const id = parseInt(req.params.id);
    
    const donneeExiste = await prisma.donneeHistorique.findUnique({
      where: { id_donnee: id }
    });
    
    if (!donneeExiste) {
      return res.status(404).json({ error: 'Donnée historique non trouvée' });
    }
    
    await prisma.donneeHistorique.delete({
      where: { id_donnee: id }
    });
    
    res.status(204).send();
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

module.exports = router; 