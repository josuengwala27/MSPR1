/**
 * Middleware pour convertir les BigInt en chaînes de caractères lors de la sérialisation JSON
 * Résout l'erreur "Do not know how to serialize a BigInt"
 */
const bigIntSerializer = (req, res, next) => {
  // Sauvegarde de la méthode json originale
  const originalJson = res.json;
  
  // Redéfinition de la méthode json
  res.json = function(body) {
    // Fonction récursive pour parcourir et convertir les BigInt
    const replaceBigInt = (data) => {
      if (data === null || data === undefined) {
        return data;
      }
      
      // Si c'est un BigInt, conversion en chaîne
      if (typeof data === 'bigint') {
        return data.toString();
      }
      
      // Si c'est un tableau, application sur chaque élément
      if (Array.isArray(data)) {
        return data.map(item => replaceBigInt(item));
      }
      
      // Si c'est un objet, application sur chaque propriété
      if (typeof data === 'object') {
        Object.keys(data).forEach(key => {
          data[key] = replaceBigInt(data[key]);
        });
      }
      
      return data;
    };
    
    // Application du remplacement sur le corps de la réponse
    body = replaceBigInt(body);
    
    // Appel de la méthode originale avec le corps transformé
    return originalJson.call(this, body);
  };
  
  next();
};

module.exports = bigIntSerializer; 