const crypto = require('crypto');

// Substitui badCrypto() (finding CRITICAL "Insecure Credential Storage"):
// hash real com salt aleatório por senha e comparação em tempo constante,
// usando apenas o módulo `crypto` nativo do Node (sem dependência externa).
const KEY_LENGTH = 64;

function hashPassword(password) {
  const salt = crypto.randomBytes(16).toString('hex');
  const hash = crypto.scryptSync(password, salt, KEY_LENGTH).toString('hex');
  return `${salt}:${hash}`;
}

function verifyPassword(password, storedHash) {
  const [salt, hash] = storedHash.split(':');
  if (!salt || !hash) return false;
  const hashBuffer = Buffer.from(hash, 'hex');
  const derivedBuffer = crypto.scryptSync(password, salt, KEY_LENGTH);
  return hashBuffer.length === derivedBuffer.length && crypto.timingSafeEqual(hashBuffer, derivedBuffer);
}

module.exports = { hashPassword, verifyPassword };
