from datetime import datetime
import reserva_app
from functools import wraps
from flask import render_template, request, redirect, url_for, make_response
from reserva_app.models import Sala, Reserva, User

app = reserva_app.init()


def login_required(f):
    @wraps(f)
    def funcao(*args, **kwargs):
        id_usuario = request.cookies.get("userid")

        if id_usuario is None:
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
    mensagem = ""
    if request.method == "POST":
        nome = request.form['nome'].strip()
        email = request.form['email'].strip()
        senha = request.form['password'].strip()
        if not all([nome, email, senha]):
            mensagem = "Todos os campos são obrigatórios."
            return render_template("cadastro.html", mensagem=mensagem)

        usuario = User(nome, email, senha)
        objs = User.objects()
        if objs is not None:
            if objs.where("get_email", email):
                mensagem = "Endereço de email já cadastrado."
                return render_template("cadastro.html", mensagem=mensagem)

        usuario.save()
        return redirect(url_for("login"))

    return render_template("cadastro.html", mensagem=mensagem)


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
@login_required
def cadastrar_sala():
    if request.method == "POST":
        tipo = int(request.form.get("tipo"))
        capacidade = int(request.form.get("capacidade"))
        descricao = request.form.get("descricao").strip()

        if not all([tipo, capacidade, descricao]):
            return render_template("cadastrar-sala.html", mensagem="Preencha todos os campos")
        if tipo == 0:
            return render_template("cadastrar-sala.html", mensagem="Selecione o tipo da sala")
        if int(capacidade) <= 0:
            return render_template("cadastrar-sala.html", mensagem="Adicione uma capacidade válida")

        sala = Sala(capacidade, tipo, descricao)
        sala.save()
        return redirect(url_for("cadastrar_sala"))

    return render_template("cadastrar-sala.html")


@app.route('/listar-salas')
@login_required
def listar_salas():
    sala = Sala.objects().get_list()
    return render_template("listar-salas.html", salas=sala)


@app.route('/listar-salas/<sala_id>/editar')
@login_required
def editar_sala(sala_id):
    return render_template("listar-salas.html")

    


@app.route('/listar-salas/<sala_id>/excluir')
@login_required
def excluir_sala(sala_id):
    return render_template("listar-salas.html")


@app.route('/listar-salas/<sala_id>/desativar')
@login_required
def desativar_sala(sala_id):
    sala = Sala.objects().where("get_codigo", int(sala_id))
    sala.set_ativo(False)
    sala.save()
    return redirect(url_for("listar_salas"))


@app.route('/reservar-sala', methods=["POST", "GET"])
@login_required
def reservar_sala():
    salas = Sala.objects().get_list()

    if request.method == "POST":
        codigo_sala = int(request.form.get("sala"))
        inicio = request.form.get("inicio")
        fim = request.form.get("fim")

        if not all([inicio, fim]):
            return render_template("reservar-sala.html", salas=salas, mensagem="Preencha todos os campos")

        reservas_sala = Reserva.objects().where("get_codigo_sala", codigo_sala)
        if [reserva for reserva in reservas_sala
                if inicio <= reserva.get_datetime_start() <= fim
                or inicio <= reserva.get_datetime_end() <= fim]:
            return render_template("reservar-sala.html", salas=salas, mensagem="Essa sala já esta reservada nesse horário")

        reserva = Reserva(get_id_usuario(), codigo_sala, inicio, fim)

        if reserva.duracao().total_seconds() <= 0 or reserva.tempo_restante().total_seconds() <= 0:
            return render_template("reservar-sala.html", salas=salas, mensagem="Horário inválido")
        if reserva.duracao().total_seconds() > 28800:
            return render_template("reservar-sala.html", salas=salas,
                                   mensagem="O tempo de duração da sala não pode ser superior a oito horas")

        reserva.save()

        return redirect(url_for("reservas"))

    return render_template("reservar-sala.html", salas=salas)


@app.route('/reservas', methods=["POST", "GET"])
@login_required
def reservas():
    reservas_objects = Reserva.objects().where("get_codigo_usuario", get_id_usuario())

    if request.method == "POST":
        start = datetime.strptime(request.form.get("start"), "%Y-%m-%dT%H:%M")
        end = datetime.strptime(request.form.get("end"), "%Y-%m-%dT%H:%M")

        if not all([start, end]):
            return render_template("reservas.html", mensagem="Preencha todos os campos")

        objects = Reserva.objects().where("get_codigo_usuario", get_id_usuario())
        reservas_objects = [reserva for reserva in objects
                            if start <= reserva.get_datetime_start() <= end
                            and start <= reserva.get_datetime_end() <= end]

    return render_template("reservas.html", reservas=reservas_objects)


@app.route('/detalhe-reserva')
def detalhe_reserva():
    return render_template("detalhe-reserva.html")


@app.route('/detalhe_reserva/<id>', methods=["GET"])
@login_required
def detalhe_reserva_id(id):
    arr_reserva = str(Reserva.objects().where("get_codigo", int(id))).split(',')
    arr_user = str(User.objects().where("get_codigo", int(arr_reserva[0]))).split(',')
    arr_sala = str(Sala.objects().where("get_codigo", int(arr_reserva[1]))).split(',')

    incio_time = datetime.strptime(arr_reserva[2], '%Y-%m-%d %H:%M:%S')
    fim_time = datetime.strptime(arr_reserva[3], '%Y-%m-%d %H:%M:%S')
    duracao = fim_time - incio_time

    tipos = {
        1: "Laboratório de Informática",
        2: "Laboratório de Química",
        3: "Sala de Aula"
    }

    return render_template("detalhe-reserva.html",
                           reserva=id,
                           duracao=duracao,
                           tipo_sala=tipos[int(arr_sala[1])],
                           id_criador=arr_user[4],
                           descricao=arr_sala[2],
                           professor=arr_user[0],
                           sala=arr_reserva[4],
                           inicio=arr_reserva[2],
                           fim=arr_reserva[3])


@app.route('/deletar-reserva/<id_reserva>/<id_criador_reserva>', methods=['POST'])
def deletar_reserva(id_reserva, id_criador_reserva):
    id_usuario = request.cookies.get("userid")
    if id_criador_reserva == id_usuario:
        Reserva.exclude(id_reserva)
        return redirect(url_for('reservas'))
    return None


if __name__ == '__main__':
    app.run(debug=True)
