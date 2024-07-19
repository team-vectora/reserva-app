import reserva_app
from flask import render_template, request, redirect, url_for
from reserva_app.models import Sala

app = reserva_app.init()

@app.route('/')
def home():
    return redirect('/cadastro')

@app.route('/cadastro')
def cadastro():
    return render_template("cadastro.html")

@app.route('/login')
def login():
    return render_template("login.html")

@app.route('/reservas')
def reservas():
    return render_template("reservas.html")

@app.route('/cadastrar-sala')
def cadastrar_sala():
    return render_template("cadastrar-sala.html")

@app.route('/listar-salas')
def listar_salas():
    salas = Sala.objects()
    return render_template("listar-salas.html", salas=salas)

@app.route('/reservar-sala')
def reservar_sala():
    return render_template("reservar-sala.html")

@app.route('/detalhe-reserva')
def detalhe_reserva():
    return render_template("detalhe-reserva.html")


