from datetime import datetime
import reserva_app
from functools import wraps
from flask import render_template, request, redirect, url_for
from reserva_app.models import Reserva, Sala, User
from reserva_app.static.db.model import Model

app = reserva_app.init()

nome_usuario = None
id_usuario = None

def login_required(f):
    @wraps(f)
    def funcao(*args, **kwargs):
        if nome_usuario is None or id_usuario is None:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return funcao

@app.route('/')
def home():
    return redirect('/cadastro')


@app.route('/cadastro', methods=['POST'])
def cadastro():
    mensagem = ""
    
    nome = request.form['nome']
    email = request.form['email']
    senha = request.form['password']
    if not nome or not email or not senha:
        mensagem = "Todos os campos são obrigatórios."
        return render_template("cadastro.html", mensagem=mensagem)
    
    usuario = User(nome, email, senha)
    objs = User.objects()
    if objs is not None:
        if str(Model.ListModel(objs.where("get_email", email))):
            mensagem = "Endereço de email já cadastrado."
            return render_template("cadastro.html", mensagem=mensagem)
        if str(Model.ListModel(objs.where("get_nome", nome))):
            mensagem = "Nome de usuário já cadastrado."
            return render_template("cadastro.html", mensagem=mensagem)  

    usuario.save()
    return redirect(url_for('login'))

@app.route('/cadastro', methods=['GET'])
def cadastro_get():
    mensagem = ""
    return render_template("cadastro.html", mensagem=mensagem)  

@app.route('/login', methods=["GET"])
def login_get():
    global nome_usuario, id_usuario
    nome_usuario = None
    id_usuario = None
    return render_template("login.html")


@app.route('/login', methods=["POST"])
def login():
    global nome_usuario, id_usuario
    objs = User.objects()
    email = request.form["email"]
    senha = request.form["password"]
    
    user = str(Model.ListModel(objs.where(("get_email", "get_senha"), (email, senha))))
    print(user)
    if user.strip() != "":
        nome_usuario = user.split(",")[0]
        id_usuario = user.split(",")[4]
        return redirect(url_for('reservas'))
    return render_template("login.html")
    


@app.route('/reservas', methods=["GET"])
@login_required
def reservas():
    objs = Reserva.objects()
    lista = objs.get_dict()
    return render_template("reservas.html", reservas=lista)

@app.route('/reservas', methods=["POST"])
@login_required
def reservas_post():
    objs = Reserva.objects()
    lista = objs.get_dict()
    return render_template("reservas.html", reservas=lista)

@app.route('/cadastrar-sala')
@login_required
def cadastrar_sala():
    return render_template("cadastrar-sala.html")


@app.route('/listar-salas')
@login_required
def listar_salas():
    return render_template("listar-salas.html")


@app.route('/reservar-sala', methods=['GET'])
@login_required
def reservar_sala_get():
    salas = Sala.objects()
    arr_salas = salas.get_dict()
    return render_template("reservar-sala.html", salas=arr_salas)

@app.route('/reservar-sala', methods=['POST'])
@login_required
def reservar_sala_post():
    
    sala = request.form['sala']
    inicio = request.form['inicio']
    fim = request.form['fim']


    try:
        datetime_start = datetime.strptime(inicio, '%Y-%m-%dT%H:%M').strftime('%Y-%m-%d %H:%M:%S')
        datetime_end = datetime.strptime(fim, '%Y-%m-%dT%H:%M').strftime('%Y-%m-%d %H:%M:%S')
    except ValueError as e:
        return str(e), 400

    nova_reserva = Reserva(datetime_end=datetime_end, datetime_start=datetime_start, codigo_sala=sala, codigo_usuario=id_usuario)
    nova_reserva.save()

    return redirect(url_for('reservas'))


@app.route('/detalhe_reserva/<id>', methods=["GET"])
@login_required
def detalhe_reserva(id):
    arr_reserva=str(Reserva.objects().where("get_codigo",int(id))).split(',')
    arr_user=str(User.objects().where("get_codigo",int(arr_reserva[0]))).split(',')
    arr_sala=str(Sala.objects().where("get_codigo",int(arr_reserva[1]))).split(',')

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
                           tipo_sala= tipos[int(arr_sala[1])],
                           id_criador=arr_user[4],
                           descricao=arr_sala[2],
                           professor=arr_user[0],
                           sala=arr_reserva[4],
                           inicio=arr_reserva[2],
                           fim=arr_reserva[3])

@app.route('/deletar-reserva/<id_reserva>/<id_criador_reserva>', methods=['POST'])
def deletar_reserva(id_reserva, id_criador_reserva):
    if id_criador_reserva == id_usuario:
        Reserva.exclude(id_reserva)
        return redirect(url_for('reservas'))
    return None


if __name__ == '__main__':
    app.run(debug=True)
