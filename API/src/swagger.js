const swaggerJsdoc = require('swagger-jsdoc');
const swaggerUi = require('swagger-ui-express');

const options = {
  definition: {
    openapi: '3.0.0',
    info: {
      title: 'API Pandémies',
      version: '1.0.0',
      description: "Documentation auto-générée avec Swagger pour l'API COVID-19 et MPOX",
    },
    servers: [
      { url: 'http://localhost:3000', description: 'Développement local' }
    ],
  },
  apis: ['./src/routes/*.js'], // Toutes les routes documentées
};

const specs = swaggerJsdoc(options);

module.exports = { swaggerUi, specs }; 