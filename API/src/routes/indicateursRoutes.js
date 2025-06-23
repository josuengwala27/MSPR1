const express = require('express');
const router = express.Router();
const { PrismaClient } = require('@prisma/client');
const prisma = new PrismaClient();

// GET tous les indicateurs
router.get('/', async (req, res) => {
  try {
    const indicateurs = await prisma.indicateur.findMany();
    res.json(indicateurs);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// GET un indicateur par ID
router.get('/:id', async (req, res) => {
  try {
    const id = parseInt(req.params.id);
    const indicateur = await prisma.indicateur.findUnique({
      where: { id_indicateur: id }
    });
    
    if (!indicateur) {
      return res.status(404).json({ error: 'Indicateur non trouvé' });
    }
    
    res.json(indicateur);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// GET un indicateur par nom
router.get('/nom/:nom', async (req, res) => {
  try {
    const nom = req.params.nom;
    const indicateur = await prisma.indicateur.findUnique({
      where: { indicator_name: nom }
    });
    
    if (!indicateur) {
      return res.status(404).json({ error: 'Indicateur non trouvé' });
    }
    
    res.json(indicateur);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// POST créer un indicateur
router.post('/', async (req, res) => {
  try {
    const { indicator_name, description } = req.body;
    
    if (!indicator_name) {
      return res.status(400).json({ error: 'Le nom de l\'indicateur est requis' });
    }
    
    const nouvelIndicateur = await prisma.indicateur.create({
      data: {
        indicator_name,
        description: description || null
      }
    });
    
    res.status(201).json(nouvelIndicateur);
  } catch (error) {
    if (error.code === 'P2002') {
      return res.status(409).json({ error: 'Cet indicateur existe déjà' });
    }
    res.status(500).json({ error: error.message });
  }
});

// PUT mettre à jour un indicateur
router.put('/:id', async (req, res) => {
  try {
    const id = parseInt(req.params.id);
    const { indicator_name, description } = req.body;
    
    const indicateurExiste = await prisma.indicateur.findUnique({
      where: { id_indicateur: id }
    });
    
    if (!indicateurExiste) {
      return res.status(404).json({ error: 'Indicateur non trouvé' });
    }
    
    const indicateurModifie = await prisma.indicateur.update({
      where: { id_indicateur: id },
      data: {
        indicator_name: indicator_name || undefined,
        description: description !== undefined ? description : undefined
      }
    });
    
    res.json(indicateurModifie);
  } catch (error) {
    if (error.code === 'P2002') {
      return res.status(409).json({ error: 'Ce nom d\'indicateur est déjà utilisé' });
    }
    res.status(500).json({ error: error.message });
  }
});

// DELETE supprimer un indicateur
router.delete('/:id', async (req, res) => {
  try {
    const id = parseInt(req.params.id);
    
    const indicateurExiste = await prisma.indicateur.findUnique({
      where: { id_indicateur: id }
    });
    
    if (!indicateurExiste) {
      return res.status(404).json({ error: 'Indicateur non trouvé' });
    }
    
    await prisma.indicateur.delete({
      where: { id_indicateur: id }
    });
    
    res.status(204).send();
  } catch (error) {
    if (error.code === 'P2003') {
      return res.status(409).json({ 
        error: 'Impossible de supprimer cet indicateur car il est référencé dans d\'autres données' 
      });
    }
    res.status(500).json({ error: error.message });
  }
});

module.exports = router; 