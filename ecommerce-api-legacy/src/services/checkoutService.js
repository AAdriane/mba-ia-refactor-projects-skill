const crypto = require('crypto');

const db = require('../database');
const { PAYMENT_STATUS } = require('../constants');
const { NotFoundError, PaymentDeniedError, ValidationError } = require('../errors');
const logger = require('../logger');
const AuditLogModel = require('../models/auditLogModel');
const CourseModel = require('../models/courseModel');
const EnrollmentModel = require('../models/enrollmentModel');
const PaymentModel = require('../models/paymentModel');
const UserModel = require('../models/userModel');
const cacheService = require('./cacheService');

class CheckoutService {
  // Substitui o pyramid of callbacks do AppManager.js original (findings
  // HIGH "Fat Controller" e "God Class") e envolve toda a escrita em uma
  // transação única (finding MEDIUM "Missing Transactional Atomicity").
  static async processCheckout({ name, email, password, courseId, card }) {
    if (!name || !email || !courseId || !card) {
      throw new ValidationError('Campos obrigatórios ausentes: usr, eml, c_id, card');
    }

    const course = await CourseModel.findActiveById(courseId);
    if (!course) {
      throw new NotFoundError('Curso não encontrado');
    }

    const existingUser = await UserModel.findByEmail(email);

    await db.run('BEGIN TRANSACTION');
    try {
      let userId;
      if (existingUser) {
        userId = existingUser.id;
      } else {
        // Finding LOW "Insecure-by-Default Configuration": o fallback de
        // senha hardcoded "123456" foi substituído por uma senha aleatória
        // gerada por requisição quando o cliente não envia uma.
        const rawPassword = password || crypto.randomBytes(12).toString('hex');
        userId = await UserModel.create({ name, email, password: rawPassword });
      }

      // Finding CRITICAL "Unstructured Logging": nunca logar número de
      // cartão nem a chave do gateway de pagamento.
      logger.info(`Processando pagamento do curso ${courseId} para usuário ${userId}`);

      const status = card.startsWith('4') ? PAYMENT_STATUS.PAID : PAYMENT_STATUS.DENIED;
      if (status === PAYMENT_STATUS.DENIED) {
        throw new PaymentDeniedError('Pagamento recusado');
      }

      const enrollmentId = await EnrollmentModel.create(userId, courseId);
      await PaymentModel.create(enrollmentId, course.price, status);
      await AuditLogModel.record(`Checkout curso ${courseId} por ${userId}`);

      await db.run('COMMIT');

      cacheService.set(`last_checkout_${userId}`, course.title);
      return { enrollmentId };
    } catch (error) {
      await db.run('ROLLBACK');
      throw error;
    }
  }
}

module.exports = CheckoutService;
