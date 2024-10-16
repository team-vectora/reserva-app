import reserva_app
from functools import wraps
from datetime import datetime
from reserva_app.models import Sala, Reserva, User
from flask import render_template, request, redirect, url_for, make_response

app = reserva_app.app


def login_required(f):
    @wraps(f)
    def funcao(*args, **kwargs):
        id_usuario = request.cookies.get("userid")

        if id_usuario is None:
            return redirect(url_for('login'))
        return f(*args, **kwargs)

    return funcao


def admin_required(f):
    @wraps(f)
    def funcao(*args, **kwargs):
        id_usuario = request.cookies.get("userid")
        user = User.objects().where("codigo", int(id_usuario))

        if id_usuario is None or not user or not user.get_admin():
            return redirect(url_for('login'))

        return f(*args, **kwargs)

    return funcao


def get_id_usuario() -> int:
    return int(request.cookies.get("userid"))


@app.route('/')
def home():
    return redirect(url_for("cadastro"))


@app.route('/cadastro', methods=["POST", "GET"])
def cadastro():
    if request.method == "POST":
        nome = request.form['nome'].strip()
        email = request.form['email'].strip()
        senha = request.form['password'].strip()
        if not all([nome, email, senha]):
            return render_template("cadastro.html", mensagem="Preencha todos os campos")

        objs = User.objects()
        if objs is not None:
            if objs.where("email", email):
                return render_template("cadastro.html", mensagem="Endereço de email já cadastrado.")

        usuario = User(nome, email, senha)
        usuario.save()
        return render_template("cadastro.html", mensagem="Usuário cadastrado com sucesso.", alert="success")

    return render_template("cadastro.html")


@app.route('/login', methods=["POST", "GET"])
def login():
    if request.method == "POST":
        email = request.form["email"].strip()
        senha = request.form["password"].strip()
        usuario = User.autenticate(email, senha)

        if not usuario:
            return render_template("login.html", mensagem="Email ou senha inválidos")

        response = make_response(redirect(url_for("reservas")))
        response.set_cookie("userid", str(usuario.get_codigo()))
        return response

    return render_template("login.html", mensagem="")


@app.route('/cadastrar-sala', methods=["POST", "GET"])
@admin_required
def cadastrar_sala():
    admin = User.objects().where("codigo", get_id_usuario())
    if request.method == "POST":
        tipo = int(request.form.get("tipo"))
        capacidade = int(request.form.get("capacidade"))
        descricao = request.form.get("descricao").strip()

        if not all([tipo, capacidade, descricao]):
            return render_template("cadastrar-sala.html", mensagem="Preencha todos os campos", admin=admin)
        if tipo == 0:
            return render_template("cadastrar-sala.html", mensagem="Selecione o tipo da sala", admin=admin)
        if int(capacidade) <= 0:
            return render_template("cadastrar-sala.html", mensagem="Adicione uma capacidade válida", admin=admin)

        sala = Sala(capacidade, tipo, descricao)
        sala.save()
        return redirect(url_for("cadastrar_sala"))

    return render_template("cadastrar-sala.html", admin=admin)


@app.route('/listar-salas')
@admin_required
def listar_salas():
    sala = Sala.objects().get_list()
    admin = User.objects().where("codigo", get_id_usuario())
    return render_template("listar-salas.html", salas=sala, admin=admin)


@app.route('/listar-salas/<sala_id>/editar', methods=["POST", "GET"])
@admin_required
def editar_sala(sala_id):
    admin = User.objects().where("codigo", get_id_usuario())
    sala = Sala.objects().where("codigo", int(sala_id))

    if request.method == "POST":

        tipo = int(request.form.get("tipo"))
        capacidade = int(request.form.get("capacidade"))
        descricao = request.form.get("descricao").strip()

        if not all([tipo, capacidade, descricao]):
            return render_template("editar-sala.html", mensagem="Preencha todos os campos", admin=admin)
        if int(capacidade) <= 0:
            return render_template("editar-sala.html", mensagem="Adicione uma capacidade válida", admin=admin)
        sala.set_tipo(tipo)
        sala.set_capacidade(capacidade)
        sala.set_descricao(descricao)
        sala.save()
        return redirect(url_for("listar_salas"))

    return render_template("editar-sala.html", sala=sala, admin=admin)


@app.route('/listar-salas/<sala_id>/excluir')
@admin_required
def excluir_sala(sala_id):
    sala = Sala.objects().where("codigo", int(sala_id))
    sala.exclude(sala_id)
    sala.save()
    return redirect(url_for("listar_salas"))


@app.route('/listar-salas/<sala_id>/desativar')
@admin_required
def desativar_sala(sala_id):
    sala = Sala.objects().where("codigo", int(sala_id))
    sala.set_ativo(False)
    sala.save()
    return redirect(url_for("listar_salas"))


@app.route('/listar-salas/<sala_id>/ativar')
@admin_required
def ativar_sala(sala_id):
    sala = Sala.objects().where("codigo", int(sala_id))
    sala.set_ativo(True)
    sala.save()
    return redirect(url_for("listar_salas"))


@app.route('/reservar-sala', methods=["POST", "GET"])
@login_required
def reservar_sala():
    admin = User.objects().where("codigo", get_id_usuario())
    salas_nao_ordenadas = Sala.objects().get_list()
    salas = sorted(salas_nao_ordenadas, key=lambda item: item.nome_sala())
    # Para ficar ordenado por ordem alfabética as salas

    if request.method == "POST":
        codigo_sala = int(request.form.get("sala"))
        inicio = request.form.get("inicio")
        fim = request.form.get("fim")

        if not all([inicio, fim]):
            return render_template(
                "reservar-sala.html",
                salas=salas,
                mensagem="Preencha todos os campos",
                admin=admin
            )

        inicio = datetime.strptime(inicio, "%Y-%m-%dT%H:%M")
        fim = datetime.strptime(fim, "%Y-%m-%dT%H:%M")

        reservas_sala = Reserva.objects().where("codigo_sala", codigo_sala)
        if [reserva for reserva in reservas_sala
                if inicio <= reserva.get_datetime_start(False) <= fim
                or inicio <= reserva.get_datetime_end(False) <= fim]:
            return render_template(
                "reservar-sala.html",
                salas=salas,
                mensagem="Essa sala já esta reservada nesse horário",
                admin=admin
            )

        reserva = Reserva(get_id_usuario(), codigo_sala, inicio, fim)

        if 0 > reserva.tempo_restante().total_seconds() > (-6 * 3600):
            return render_template(
                "reservar-sala.html",
                salas=salas,
                mensagem="A sala deve ser reservada com 6 horas de antecedência",
                admin=admin
            )
        if reserva.duracao().total_seconds() <= 0 or reserva.tempo_restante().total_seconds() >= 0:
            return render_template("reservar-sala.html", salas=salas, mensagem="Horário inválido", admin=admin)
        if reserva.duracao().total_seconds() > 28800:
            return render_template("reservar-sala.html", salas=salas,
                                   mensagem="O tempo de duração da sala não pode ser superior a oito horas", admin=admin)

        reserva.save()

        return redirect(url_for("reservas"))

    return render_template("reservar-sala.html", salas=salas, admin=admin)


@app.route('/reservas', methods=["POST", "GET"])
@login_required
def reservas():
    admin = User.objects().where("codigo", get_id_usuario())
    reservas_objects = Reserva.objects().where("codigo_usuario", get_id_usuario())

    if request.method == "POST":
        start = datetime.strptime(request.form.get("start"), "%Y-%m-%dT%H:%M")
        end = datetime.strptime(request.form.get("end"), "%Y-%m-%dT%H:%M")

        if not all([start, end]):
            return render_template("reservas.html", mensagem="Preencha todos os campos", admin=admin)

        objects = Reserva.objects().where("codigo_usuario", get_id_usuario())
        reservas_objects = [reserva for reserva in objects
                            if start <= reserva.get_datetime_start(False) <= end
                            and start <= reserva.get_datetime_end(False) <= end]

    mensagem = request.cookies.get("mensagem")
    if mensagem:
        alert = request.cookies.get("alert")
        response = make_response(
            render_template(
                "reservas.html",
                reservas=reservas_objects,
                mensagem=mensagem,
                alert=alert,
                admin=admin
            )
        )
        response.delete_cookie("mensagem")
        if alert:
            response.delete_cookie("alert")

        return response

    return render_template("reservas.html", reservas=reservas_objects, admin=admin)


@app.route('/detalhe_reserva/<reserva_id>', methods=["GET"])
@login_required
def detalhe_reserva(reserva_id):
    admin = User.objects().where("codigo", get_id_usuario())
    reserva = Reserva.objects().where("codigo", int(reserva_id))
    usuario = User.objects().where("codigo", reserva.get_codigo_usuario())
    sala = Sala.objects().where("codigo", reserva.get_codigo_sala())

    return render_template("detalhe-reserva.html", reserva=reserva, usuario=usuario, sala=sala, admin=admin)


@app.route('/cancelar-reserva/<reserva_id>', methods=['POST'])
def cancelar_reserva(reserva_id):
    reserva = Reserva.objects().where("codigo", int(reserva_id))
    response = make_response(redirect(url_for('reservas')))

    if 0 > reserva.tempo_restante().total_seconds() >= (-43200):
        response.set_cookie("mensagem", "A reserva só pode ser cancelada com 12 horas de antecedência")

        return response

    if get_id_usuario() == reserva.get_codigo_usuario():
        Reserva.exclude(reserva_id)
        response.set_cookie("mensagem", "Reserva cancelada com sucesso")
        response.set_cookie("alert", "success")

        return response

    response.set_cookie("mensagem", "O ocorreu um erro")
    response.set_cookie("alert", "danger")

    return response


@app.route('/logout')
def logout():
    response = make_response(redirect(url_for("login")))
    response.delete_cookie("userid")

    return response
    

if __name__ == '__main__':
    app.run(debug=True)
