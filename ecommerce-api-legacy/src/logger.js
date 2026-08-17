// Logger estruturado mínimo (sem dependência externa), substitui os
// console.log soltos e sem nível/timestamp espalhados pelo código legado.
function timestamp() {
  return new Date().toISOString();
}

module.exports = {
  info: (...args) => console.log(`[INFO] ${timestamp()}`, ...args),
  warn: (...args) => console.warn(`[WARN] ${timestamp()}`, ...args),
  error: (...args) => console.error(`[ERROR] ${timestamp()}`, ...args),
};
