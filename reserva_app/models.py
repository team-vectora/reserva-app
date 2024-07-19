from reserva_app.static.db.model import Model


class Reserva(Model):
    table_name = 'sala.csv'

    def __init__(self, codigo, codigo_usuario, codigo_sala, datetime_start, datetime_end, ativa):
        super().__init__(codigo, Reserva.table_name, self.__init__)
        self.codigo = super().primary_key
        self.codigo_usuario = codigo_usuario
        self.codigo_sala = codigo_sala
        self.datetime_start = datetime_start
        self.datetime_end = datetime_end
        self.ativa = ativa

    @staticmethod
    def objects() -> list:
        return Model._objects(Reserva.table_name, Reserva.__init__)

    @staticmethod
    def exclude(id_to_exclude):
        Model._exclude(id_to_exclude, Reserva.table_name)


class User(Model):
    table_name = 'sala.csv'

    def __init__(self, codigo, nome, email, senha, ativo):
        super().__init__(codigo, User.table_name, self.__init__)
        self.codigo = super().primary_key
        self.nome = nome
        self.email = email
        self.senha = senha
        self.ativo = ativo

    @staticmethod
    def objects() -> list:
        return super()._objects(User.table_name, User.__init__)

    @staticmethod
    def exclude(id_to_exclude):
        super()._exclude(id_to_exclude, User.table_name)


class Sala(Model):
    table_name = 'sala.csv'

    def __init__(self, codigo, capacidade, ativo, tipo, descricao):
        super().__init__(codigo, Sala.table_name, self.__init__)
        self.codigo = super().primary_key
        self.capacidade = capacidade
        self.ativo = ativo
        self.tipo = tipo
        self.descricao = descricao

    @staticmethod
    def objects() -> list:
        return Model._objects(Sala.table_name, Sala.__init__)

    @staticmethod
    def exclude(id_to_exclude):
        Model._exclude(id_to_exclude, Sala.table_name)

