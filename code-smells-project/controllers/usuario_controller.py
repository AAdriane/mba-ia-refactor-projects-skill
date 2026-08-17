import logging

from flask import jsonify

from errors import NotFoundError, UnauthorizedError, ValidationError
from models.usuario import Usuario, UsuarioRepository

logger = logging.getLogger(__name__)


class UsuarioController:
    @staticmethod
    def listar():
        usuarios = UsuarioRepository.get_all()
        return jsonify({"dados": [u.to_dict() for u in usuarios], "sucesso": True}), 200

    @staticmethod
    def buscar_por_id(id):
        usuario = UsuarioRepository.get_by_id(id)
        if not usuario:
            raise NotFoundError("Usuário não encontrado")
        return jsonify({"dados": usuario.to_dict(), "sucesso": True}), 200

    @staticmethod
    def criar(dados):
        if not dados:
            raise ValidationError("Dados inválidos")
        Usuario.validar_cadastro(dados)

        usuario = Usuario(nome=dados["nome"], email=dados["email"])
        usuario.set_senha(dados["senha"])
        id = UsuarioRepository.create(usuario)
        logger.info("Usuário criado: %s", dados["email"])
        return jsonify({"dados": {"id": id}, "sucesso": True}), 201

    @staticmethod
    def login(dados):
        if not dados:
            raise ValidationError("Dados inválidos")

        email = dados.get("email", "")
        senha = dados.get("senha", "")
        if not email or not senha:
            raise ValidationError("Email e senha são obrigatórios")

        usuario = UsuarioRepository.get_by_email(email)
        if not usuario or not usuario.checar_senha(senha):
            logger.info("Login falhou: %s", email)
            raise UnauthorizedError("Email ou senha inválidos")

        logger.info("Login bem-sucedido: %s", email)
        return jsonify({"dados": usuario.to_dict(), "sucesso": True, "mensagem": "Login OK"}), 200
