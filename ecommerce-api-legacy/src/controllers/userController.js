const UserModel = require('../models/userModel');

class UserController {
  static async deleteUser(req, res) {
    const { id } = req.params;
    await UserModel.deleteCascade(id);
    res.send('Usuário deletado, matrículas e pagamentos relacionados também foram removidos.');
  }
}

module.exports = UserController;
