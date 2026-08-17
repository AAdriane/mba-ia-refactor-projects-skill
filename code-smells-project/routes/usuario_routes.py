from flask import Blueprint, request

from controllers.usuario_controller import UsuarioController

usuario_bp = Blueprint("usuarios", __name__)


@usuario_bp.route("/usuarios", methods=["GET"])
def listar_usuarios():
    return UsuarioController.listar()


@usuario_bp.route("/usuarios/<int:id>", methods=["GET"])
def buscar_usuario(id):
    return UsuarioController.buscar_por_id(id)


@usuario_bp.route("/usuarios", methods=["POST"])
def criar_usuario():
    return UsuarioController.criar(request.get_json())


@usuario_bp.route("/login", methods=["POST"])
def login():
    return UsuarioController.login(request.get_json())
