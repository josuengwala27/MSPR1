/**
 * Utilitaires pour le parsing et la validation des données
 * Fonctions communes utilisées par les scripts de chargement et de test
 */

// Fonctions utilitaires pour la conversion sécurisée des types
function safeParseInt(value) {
  if (!value || value === '' || value === 'null' || value === 'undefined') {
    return null;
  }
  const parsed = parseInt(value);
  return isNaN(parsed) ? null : parsed;
}

function safeParseFloat(value) {
  if (!value || value === '' || value === 'null' || value === 'undefined') {
    return null;
  }
  const parsed = parseFloat(value);
  return isNaN(parsed) ? null : parsed;
}

function safeParseBigInt(value) {
  if (!value || value === '' || value === 'null' || value === 'undefined') {
    return null;
  }
  try {
    // Convertir d'abord en string, puis en BigInt
    const cleanValue = String(value).replace(/\.0+$/, ''); // Enlever les .0 finaux
    return BigInt(cleanValue);
  } catch (error) {
    console.warn(`Impossible de convertir en BigInt: ${value}`);
    return null;
  }
}

function safeParseDate(value) {
  if (!value || value === '' || value === 'null' || value === 'undefined') {
    return null;
  }
  try {
    const date = new Date(value);
    return isNaN(date.getTime()) ? null : date;
  } catch (error) {
    console.warn(`Impossible de convertir en Date: ${value}`);
    return null;
  }
}

function validateString(value, maxLength, fieldName) {
  if (!value || typeof value !== 'string') {
    return null;
  }
  const trimmed = value.trim();
  if (trimmed.length > maxLength) {
    console.warn(`${fieldName} trop long (${trimmed.length} > ${maxLength}): ${trimmed.substring(0, 50)}...`);
    return trimmed.substring(0, maxLength);
  }
  return trimmed;
}

// Configuration par défaut
const DEFAULT_CONFIG = {
  BATCH_SIZE: 1000,
  ETL_PROCESSED_DIR: '../ETL/processed'
};

module.exports = {
  safeParseInt,
  safeParseFloat,
  safeParseBigInt,
  safeParseDate,
  validateString,
  DEFAULT_CONFIG
}; 