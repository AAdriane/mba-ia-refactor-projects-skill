const { AppError } = require('../errors');
const logger = require('../logger');

// eslint-disable-next-line no-unused-vars
function errorHandler(err, req, res, next) {
  if (err instanceof AppError) {
    return res.status(err.statusCode).json({ erro: err.message, sucesso: false });
  }
  logger.error('Erro não tratado', err);
  return res.status(500).json({ erro: 'Erro interno', sucesso: false });
}

function asyncHandler(fn) {
  return (req, res, next) => Promise.resolve(fn(req, res, next)).catch(next);
}

module.exports = { errorHandler, asyncHandler };
