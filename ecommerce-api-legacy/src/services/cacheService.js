const logger = require('../logger');

// Substitui `globalCache`/`totalRevenue` (finding HIGH "Uncontrolled Global
// Mutable State" em utils.js): estado encapsulado em uma instância única e
// controlada, em vez de variáveis de módulo mutáveis acessadas diretamente.
class CacheService {
  constructor() {
    this._store = new Map();
  }

  set(key, value) {
    logger.info(`Salvando no cache: ${key}`);
    this._store.set(key, value);
  }

  get(key) {
    return this._store.get(key);
  }
}

module.exports = new CacheService();
