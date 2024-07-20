from reserva_app.models import User, Sala, Reserva
from reserva_app.static.db.model import Model

maria = User("maria", "maria@email", "maria123")
joao = User("joao", "joao@email", "joao123")

maria.save()
joao.save()
print("João salvo:\n" + str(User.objects()))

joao.set_ativo(False)
joao.save()
print("João atualizado:\n" + str(User.objects()))


sala1 = Sala(30, 2, "Sala com 4 professores para venda")
sala2 = Sala(10, 1, "Sala com trez computadors, uma cama e duaokas -m e,,,da das escada")

sala1.save()
sala2.save()
print("Sala salva:\n" + str(Sala.objects()))

sala2.set_ativo(False)
sala2.save()
print("Sala atualizada:\n" + str(Sala.objects()))


reserva1 = Reserva(1, 1, "2024-07-21 15:00:00", "2024-07-22 16:00:00")
reserva2 = Reserva(1, 2, "2024-07-22 16:00:00", "2024-07-22 17:00:00")
reserva3 = Reserva(2, 1, "2024-07-21 17:00:00", "2024-07-22 18:00:00")
reserva4 = Reserva(2, 2, "2024-07-22 18:00:00", "2024-07-22 19:00:00")

reserva1.save()
reserva2.save()
reserva3.save()
reserva4.save()
print("Reserva salva:\n" + str(Reserva.objects()))

reserva1.set_ativo(False)
reserva1.save()
print("Reserva atualizada:\n" + str(Reserva.objects()))


reservas_de_joao = Reserva.objects().where("get_codigo_usuario", 1)
print("Reservas de Joao:\n" + str(Model.ListModel(reservas_de_joao)))

reservas_de_maria = Reserva.objects().where("get_codigo_usuario", 2)
print("Reservas de Maria:\n" + str(Model.ListModel(reservas_de_maria)))

reservas_de_joao_na_sala_um = Reserva.objects().where(("get_codigo_usuario", "get_codigo_sala"), (1, 1))
print("Reservas de Joao na sala um:\n" + str(Model.ListModel(reservas_de_joao_na_sala_um)))

reservas_de_maria_na_sala_dois = Reserva.objects().where(("get_codigo_usuario", "get_codigo_sala"), (2, 2))
print("Reservas de Maria na sala dois:\n" + str(Model.ListModel(reservas_de_maria_na_sala_dois)))

User.exclude(joao.get_codigo())
User.exclude(maria.get_codigo())

Sala.exclude(sala1.get_codigo())
Sala.exclude(sala2.get_codigo())

Reserva.exclude(reserva1.get_codigo())
Reserva.exclude(reserva2.get_codigo())
Reserva.exclude(reserva3.get_codigo())
Reserva.exclude(reserva4.get_codigo())



