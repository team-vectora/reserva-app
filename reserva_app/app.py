import reserva_app
from flask import render_template, request, redirect, url_for
from reserva_app.models import Reserva, Sala, User

app = reserva_app.init()


@app.route('/')
def home():
    return redirect('/cadastro')


@app.route('/cadastro', methods=['POST'])
def cadastro():
    nome = request.form['nome']
    email = request.form['email']
    senha = request.form['password']
    usuario = User(nome, email, senha)
    usuario.save()
    return render_template("cadastro.html")


@app.route('/cadastro', methods=['GET'])
def cadastro_get():
    return render_template("cadastro.html")



@app.route('/login')
def login():
    return render_template("login.html")


@app.route('/reservas', methods=["GET"])
def reservas():
    objs = Reserva.objects()
    lista = objs.get_dict()
    return render_template("reservas.html", reservas=lista)

@app.route('/reservas', methods=["POST"])
def reservas_post():
    objs = Reserva.objects()
    lista = objs.get_dict()
    return render_template("reservas.html", reservas=lista)

@app.route('/cadastrar-sala')
def cadastrar_sala():
    return render_template("cadastrar-sala.html")


@app.route('/listar-salas')
def listar_salas():
    return render_template("listar-salas.html")


@app.route('/reservar-sala', methods=['GET'])
def reservar_sala_get():
    salas = Sala.objects()
    arr_salas = salas.get_dict()
    return render_template("reservar-sala.html", salas=arr_salas)

@app.route('/reservar-sala', methods=['POST'])
def reservar_sala_post():
    sala_cod = request.form['sala']
    inicio = request.form['inicio']
    fim = request.form['fim']
    nova_reserva = Reserva(datetime_end=fim, datetime_start=inicio, codigo_sala=sala_cod)
    nova_reserva.save()
    return render_template("reservar-sala.html")




@app.route('/detalhe_reserva/<id>')
def detalhe_reserva(id):
    reserva = Reserva.objects()
    print(reserva)
    reserva.where('get_codigo',id)
    return render_template("detalhe_reserva.html", reserva=reserva)
    


if __name__ == '__main__':
    app.run(debug=True)
