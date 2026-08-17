const express = require('express');

const config = require('./config');
const database = require('./database');
const logger = require('./logger');
const { errorHandler } = require('./middlewares/errorHandler');
const adminRoutes = require('./routes/adminRoutes');
const checkoutRoutes = require('./routes/checkoutRoutes');
const userRoutes = require('./routes/userRoutes');

const app = express();
app.use(express.json());

app.use('/api', checkoutRoutes);
app.use('/api', adminRoutes);
app.use('/api', userRoutes);

app.use(errorHandler);

async function start() {
  await database.initSchema();
  await database.seed();
  app.listen(config.port, () => {
    logger.info(`Frankenstein LMS rodando na porta ${config.port}...`);
  });
}

if (require.main === module) {
  start();
}

module.exports = app;
