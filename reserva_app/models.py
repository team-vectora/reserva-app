from datetime import datetime

from reserva_app.static.db.model import Model, Column

'''

Salve salve meu grupo bonito, guia rápido de como usar os models
Para SALVAR alguma coisa no banco de dados, por exemplo um novo usuario

>>> usuario = User(nome, email, senha, ativo) # por padrao o ativo vem True, não precisa colocar
>>> usuario.save()

Pronto! ele vai até te retornar o id do usuario que ele gerou automaticamente tipo um auto_increment

>>> codigo = usuario.save()
>>> print(codigo)

Para ATUALIZAR é só mudar o que voce quer com os getters e setters e dar um .save() de novo

>>> usuario.set_ativo(False)
>>> usuario.save()

Para LER você pode usar o .objectes, que vai te retornar uma ListModel, voce pode usar o metodo .get_list
para mudar de ListModel para array normal

>>> objetos = User.objects() # é um método estático
>>> print(objetos)
maria,maria@email,maria123,True,1
joao,joao@email,joao123,True,2

>>> lista = objetos.get_list()
>>> print(lista)
[User.<xx5asd444gfeasd683613268>, User.<xx5asd444gfeasd683613268>]

E por ser um ListModel você pode usar o método .where para filtrar os resultados
para isso, coloque o método que voce quer utilizar para encontrar o resultado, e o resultado desejado
Exemplo:

>>> objetos.where("get_codigo", 1) # retorna um objeto User que tenha o id 1

Use uma tupla para mais de uma pesquisa

>>> reservas = Reservas.objects()
>>> reservas.where(("get_codigo_usuario", "get_ativo"), (1, True)) # Retorna todas as reservas do usuario 1, 
                                                                     ainda ativas
                                                                     
Por fim, para EXCLUIR basta usar o metodo .exclude, que também é estático

>>> User.exclude(2) #remove o usuario de codigo igual a 2

'''


class Reserva(Model):
    table_name = 'reserva.csv'

    def __init__(self, codigo_usuario: int = 0, codigo_sala: int = 0, datetime_start: datetime | str = None,
                 datetime_end: datetime | str = None, ativo: bool = True):
        super().__init__(Reserva)
        self.__codigo_usuario = Column.integer_field(codigo_usuario)
        self.__codigo_sala = Column.integer_field(codigo_sala)
        self.__datetime_start = Column.datetime_field(datetime_start)
        self.__datetime_end = Column.datetime_field(datetime_end)
        self.__ativo = Column.boolean_field(ativo)

    def set_codigo_usuario(self, codigo_usuario: int):
        self.__codigo_usuario.set_value(codigo_usuario)

    def get_codigo_usuario(self) -> int:
        return self.__codigo_usuario.get_value()

    def set_codigo_sala(self, codigo_sala: int):
        self.__codigo_sala.set_value(codigo_sala)

    def get_codigo_sala(self) -> int:
        return self.__codigo_sala.get_value()

    def set_datetime_start(self, datetime_start: datetime):
        self.__datetime_start.set_value(datetime_start)

    def get_datetime_start(self) -> datetime:

        return datetime.strptime(self.__datetime_start.get_value(), "%Y-%m-%d %H:%M:%S")

    def set_datetime_end(self, datetime_end: datetime):
        self.__datetime_end.set_value(datetime_end)

    def get_datetime_end(self) -> datetime:
        return datetime.strptime(self.__datetime_end.get_value(), "%Y-%m-%d %H:%M:%S")

    def set_ativo(self, ativo: bool):
        self.__ativo.set_value(ativo)

    def get_ativo(self) -> bool:
        return self.__ativo.get_value()

    @staticmethod
    def objects() -> Model.ListModel | Model:
        return Model._objects(Reserva)

    @staticmethod
    def exclude(id_to_exclude: int):
        Model._exclude(id_to_exclude, Reserva)


class User(Model):
    table_name = 'user.csv'

    def __init__(self, nome: str = '', email: str = '', senha: str = '', ativo: bool = True):
        super().__init__(User)
        self.__nome = Column.char_field(nome)
        self.__email = Column.char_field(email)
        self.__senha = Column.char_field(senha)
        self.__ativo = Column.boolean_field(ativo)

    def set_nome(self, nome: str):
        self.__nome.set_value(nome)

    def get_nome(self) -> str:
        return self.__nome.get_value()

    def set_email(self, email: str):
        self.__email.set_value(email)

    def get_email(self) -> str:
        return self.__email.get_value()

    def set_senha(self, senha: str):
        self.__senha.set_value(senha)

    def get_senha(self) -> str:
        return self.__senha.get_value()

    def set_ativo(self, ativo: bool):
        self.__ativo.set_value(ativo)

    def get_ativo(self) -> bool:
        return self.__ativo.get_value()

    @staticmethod
    def objects() -> Model.ListModel | Model:
        return User._objects(User)

    @staticmethod
    def exclude(id_to_exclude: int):
        User._exclude(id_to_exclude, User)


class Sala(Model):
    table_name = 'sala.csv'

    '''
        TIPOS DA SALA: 
            1 = LABORATORIO DE INFORMATICA
            2 = LABORATORIO DE QUIMICA
            3 = SALA DE AULA
    '''

    def __init__(self, capacidade: int = 0, tipo: int = 0, descricao: str = '', ativo:bool =True):
        super().__init__(Sala)
        self.__capacidade = Column.integer_field(capacidade)
        self.__ativo = Column.boolean_field(ativo)
        self.__tipo = Column.integer_field(tipo)
        self.__descricao = Column.char_field(descricao)

    def set_capacidade(self, capacidade: int):
        self.__capacidade.set_value(capacidade)

    def get_capacidade(self) -> int:
        return self.__capacidade.get_value()

    def set_tipo(self, tipo: int):
        self.__tipo.set_value(tipo)

    def get_tipo(self) -> int:
        return self.__tipo.get_value()

    def set_descricao(self, descricao: str):
        self.__descricao.set_value(descricao)

    def get_descricao(self) -> str:
        return self.__descricao.get_value()

    def set_ativo(self, ativo: bool):
        self.__ativo.set_value(ativo)

    def get_ativo(self) -> bool:
        return self.__ativo.get_value()

    @staticmethod
    def objects() -> Model.ListModel | Model:
        return Model._objects(Sala)

    @staticmethod
    def exclude(id_to_exclude: int):
        Model._exclude(id_to_exclude, Sala)

