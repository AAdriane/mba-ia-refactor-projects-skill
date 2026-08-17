const express = require('express');

const CheckoutController = require('../controllers/checkoutController');
const { asyncHandler } = require('../middlewares/errorHandler');

const router = express.Router();

router.post('/checkout', asyncHandler(CheckoutController.checkout));

module.exports = router;
