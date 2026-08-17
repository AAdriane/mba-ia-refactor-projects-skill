const CheckoutService = require('../services/checkoutService');

class CheckoutController {
  static async checkout(req, res) {
    const { usr, eml, pwd, c_id: courseId, card } = req.body;
    const result = await CheckoutService.processCheckout({
      name: usr, email: eml, password: pwd, courseId, card,
    });
    res.status(200).json({ msg: 'Sucesso', enrollment_id: result.enrollmentId });
  }
}

module.exports = CheckoutController;
