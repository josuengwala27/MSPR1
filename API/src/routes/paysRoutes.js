const express = require('express');
const router = express.Router();
const { PrismaClient } = require('@prisma/client');
const prisma = new PrismaClient();

// GET tous les pays
router.get('/', async (req, res) => {
  try {
    const pays = await prisma.pays.findMany();
    res.json(pays);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// GET un pays par ID
router.get('/:id', async (req, res) => {
  try {
    const id = parseInt(req.params.id);
    const pays = await prisma.pays.findUnique({
      where: { id_pays: id }
    });
    
    if (!pays) {
      return res.status(404).json({ error: 'Pays non trouvé' });
    }
    
    res.json(pays);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// GET un pays par code ISO
router.get('/iso/:code', async (req, res) => {
  try {
    const code = req.params.code;
    const pays = await prisma.pays.findUnique({
      where: { iso_code: code }
    });
    
    if (!pays) {
      return res.status(404).json({ error: 'Pays non trouvé' });
    }
    
    res.json(pays);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// POST créer un pays
router.post('/', async (req, res) => {
  try {
    const { country, iso_code, population } = req.body;
    
    if (!country || !iso_code) {
      return res.status(400).json({ error: 'Le nom du pays et le code ISO sont requis' });
    }
    
    const nouveauPays = await prisma.pays.create({
      data: {
        country,
        iso_code,
        population: population ? BigInt(population) : null
      }
    });
    
    res.status(201).json(nouveauPays);
  } catch (error) {
    if (error.code === 'P2002') {
      return res.status(409).json({ error: 'Ce pays ou code ISO existe déjà' });
    }
    res.status(500).json({ error: error.message });
  }
});

// PUT mettre à jour un pays
router.put('/:id', async (req, res) => {
  try {
    const id = parseInt(req.params.id);
    const { country, iso_code, population } = req.body;
    
    const paysExiste = await prisma.pays.findUnique({
      where: { id_pays: id }
    });
    
    if (!paysExiste) {
      return res.status(404).json({ error: 'Pays non trouvé' });
    }
    
    const paysModifie = await prisma.pays.update({
      where: { id_pays: id },
      data: {
        country: country || undefined,
        iso_code: iso_code || undefined,
        population: population ? BigInt(population) : undefined
      }
    });
    
    res.json(paysModifie);
  } catch (error) {
    if (error.code === 'P2002') {
      return res.status(409).json({ error: 'Ce code ISO est déjà utilisé par un autre pays' });
    }
    res.status(500).json({ error: error.message });
  }
});

// DELETE supprimer un pays
router.delete('/:id', async (req, res) => {
  try {
    const id = parseInt(req.params.id);
    
    const paysExiste = await prisma.pays.findUnique({
      where: { id_pays: id }
    });
    
    if (!paysExiste) {
      return res.status(404).json({ error: 'Pays non trouvé' });
    }
    
    await prisma.pays.delete({
      where: { id_pays: id }
    });
    
    res.status(204).send();
  } catch (error) {
    if (error.code === 'P2003') {
      return res.status(409).json({ 
        error: 'Impossible de supprimer ce pays car il est référencé dans d\'autres données' 
      });
    }
    res.status(500).json({ error: error.message });
  }
});

module.exports = router; 