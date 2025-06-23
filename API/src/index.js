const express = require('express');
const cors = require('cors');
const { PrismaClient } = require('@prisma/client');
require('dotenv').config();

// Import du middleware de sérialisation BigInt
const bigIntSerializer = require('./middleware/bigIntSerializer');

const app = express();
const prisma = new PrismaClient();
const PORT = process.env.PORT || 3000;

// Middleware
app.use(cors());
app.use(express.json());

// Middleware pour gérer la sérialisation des BigInt
app.use(bigIntSerializer);

// Routes
app.use('/api/pays', require('./routes/paysRoutes'));
app.use('/api/indicateurs', require('./routes/indicateursRoutes'));
app.use('/api/donnees-historiques', require('./routes/donneesHistoriquesRoutes'));

// Route de base
app.get('/', (req, res) => {
  res.json({ message: 'Bienvenue sur l\'API Pandémies' });
});

// Gestion des erreurs
app.use((err, req, res, next) => {
  console.error(err.stack);
  res.status(500).json({
    error: 'Une erreur est survenue',
    message: process.env.NODE_ENV === 'development' ? err.message : 'Erreur serveur'
  });
});

// Démarrer le serveur
app.listen(PORT, () => {
  console.log(`Serveur démarré sur le port ${PORT}`);
}); 