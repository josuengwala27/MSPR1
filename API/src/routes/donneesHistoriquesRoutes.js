const express = require('express');
const router = express.Router();
const { PrismaClient } = require('@prisma/client');
const prisma = new PrismaClient();

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