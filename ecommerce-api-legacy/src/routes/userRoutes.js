const express = require('express');

const UserController = require('../controllers/userController');
const { asyncHandler } = require('../middlewares/errorHandler');

const router = express.Router();

router.delete('/users/:id', asyncHandler(UserController.deleteUser));

module.exports = router;
