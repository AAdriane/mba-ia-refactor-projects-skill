// Configuração central lida de variáveis de ambiente. Nenhum segredo real
// vive aqui — apenas defaults seguros para desenvolvimento local. Em
// produção, todas essas variáveis devem ser definidas no ambiente (ver
// .env.example).
module.exports = {
  port: process.env.PORT || 3000,
  dbFile: process.env.DB_FILE || ':memory:',
  paymentGatewayKey: process.env.PAYMENT_GATEWAY_KEY || 'dev-payment-gateway-key',
  smtpUser: process.env.SMTP_USER || 'no-reply@example.com',
};
