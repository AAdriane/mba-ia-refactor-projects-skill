const express = require('express');

const AdminController = require('../controllers/adminController');
const { asyncHandler } = require('../middlewares/errorHandler');

const router = express.Router();

router.get('/admin/financial-report', asyncHandler(AdminController.financialReport));

module.exports = router;
