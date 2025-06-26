const express = require('express');
const router = express.Router();
const { PrismaClient } = require('@prisma/client');
const prisma = new PrismaClient();

/**
 * @swagger
 * tags:
 *   name: Pays
 *   description: Gestion des pays
 */

/**
 * @swagger
 * /api/pays:
 *   get:
 *     summary: Liste tous les pays
 *     tags: [Pays]
 *     responses:
 *       200:
 *         description: Liste des pays
 */
// GET tous les pays
router.get('/', async (req, res) => {
  try {
    const pays = await prisma.pays.findMany();
    res.json(pays);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

/**
 * @swagger
 * /api/pays/{id}:
 *   get:
 *     summary: Récupère un pays par ID
 *     tags: [Pays]
 *     parameters:
 *       - in: path
 *         name: id
 *         required: true
 *         schema:
 *           type: integer
 *         description: ID du pays
 *     responses:
 *       200:
 *         description: Pays trouvé
 *       404:
 *         description: Pays non trouvé
 */
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

/**
 * @swagger
 * /api/pays/iso/{code}:
 *   get:
 *     summary: Récupère un pays par code ISO
 *     tags: [Pays]
 *     parameters:
 *       - in: path
 *         name: code
 *         required: true
 *         schema:
 *           type: string
 *         description: Code ISO du pays
 *     responses:
 *       200:
 *         description: Pays trouvé
 *       404:
 *         description: Pays non trouvé
 */
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

/**
 * @swagger
 * /api/pays:
 *   post:
 *     summary: Crée un nouveau pays
 *     tags: [Pays]
 *     requestBody:
 *       required: true
 *       content:
 *         application/json:
 *           schema:
 *             type: object
 *             required:
 *               - country
 *               - iso_code
 *             properties:
 *               country:
 *                 type: string
 *               iso_code:
 *                 type: string
 *               population:
 *                 type: integer
 *     responses:
 *       201:
 *         description: Pays créé
 *       400:
 *         description: Données invalides
 *       409:
 *         description: Pays ou code ISO existe déjà
 */
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

/**
 * @swagger
 * /api/pays/{id}:
 *   put:
 *     summary: Met à jour un pays
 *     tags: [Pays]
 *     parameters:
 *       - in: path
 *         name: id
 *         required: true
 *         schema:
 *           type: integer
 *         description: ID du pays
 *     requestBody:
 *       required: true
 *       content:
 *         application/json:
 *           schema:
 *             type: object
 *             properties:
 *               country:
 *                 type: string
 *               iso_code:
 *                 type: string
 *               population:
 *                 type: integer
 *     responses:
 *       200:
 *         description: Pays mis à jour
 *       400:
 *         description: Données invalides
 *       404:
 *         description: Pays non trouvé
 *       409:
 *         description: Code ISO déjà utilisé
 */
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

/**
 * @swagger
 * /api/pays/{id}:
 *   delete:
 *     summary: Supprime un pays
 *     tags: [Pays]
 *     parameters:
 *       - in: path
 *         name: id
 *         required: true
 *         schema:
 *           type: integer
 *         description: ID du pays
 *     responses:
 *       204:
 *         description: Pays supprimé
 *       404:
 *         description: Pays non trouvé
 *       409:
 *         description: Pays référencé dans d'autres données
 */
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