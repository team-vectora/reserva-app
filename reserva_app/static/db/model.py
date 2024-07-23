import os
from datetime import datetime
import reserva_app

app = reserva_app.init()


class Model:
    def __init__(self, child_class) -> None:
        target = os.path.join(app.static_folder, 'db', child_class.table_name)

        self.__codigo = 0
        self.__table_name = target
        self.__child_class = child_class

    def _generate_id(self) -> int:
        objects = self._objects(self.__child_class).get_list()
        return 1 if not objects else objects[-1].get_codigo() + 1

    def get_codigo(self):
        return self.__codigo

    def set_codigo(self, codigo):
        self.__codigo = int(codigo)

    def save(self) -> int:
        mode = "a" if self.__codigo == 0 else "r+"
        with open(self.__table_name, mode, encoding='latin-1') as file:
            if self.__codigo == 0:
                self.__codigo = self._generate_id()
                file.write(str(self))
            else:
                readline = file.readlines()
                new_lines = [str(self) if line.strip().endswith(str(self.__codigo)) else line for line in readline]
                file.seek(0)
                file.writelines(new_lines)
                file.truncate()

        return self.__codigo
    

    @staticmethod
    def _objects(child_class):
        target = os.path.join(app.static_folder, 'db', child_class.table_name)
        with open(target, "r", encoding='latin-1') as file:
            list_model = Model.ListModel()
            for line in file.readlines():
                attr_list = line.strip().split(",")
                model = child_class()
                for (dir_attr, attr) in zip(model.__dir__(), attr_list):
                    model.__getattribute__(dir_attr)(attr)
                list_model.append(model)
            return list_model

    @staticmethod
    def _exclude(id_to_exclude, child_class):
        target = os.path.join(app.static_folder, 'db', child_class.table_name)
        with open(target, "r+", encoding='latin-1') as file:
            readline = file.readlines()
            new_lines = [line for line in readline if not line.strip().endswith(str(id_to_exclude))]
            file.seek(0)
            file.writelines(new_lines)
            file.truncate()

    def __str__(self):
        return ",".join(map(str, [attr for attr in self.__dir__(get=True)])) + "\n"

    def __dir__(self, get=False):
        dir_attr = super().__dir__()
        if get:
            return [self.__getattribute__(attr)() for attr in dir_attr
                    if not any([
                    attr.startswith("_"),
                    attr.startswith("set"),
                    attr in ["table_name", "exclude", "save", "objects", "ListModel"]])]

        return [attr for attr in dir_attr
                if not any([
                attr.startswith("_"),
                attr.startswith("get"),
                attr in ["table_name", "exclude", "save", "objects", "ListModel"]])]

    class ListModel:
        def __init__(self, list_model=None):
            self.__list_model = list() if list_model is None else list_model

        def append(self, value):
            self.__list_model.append(value)

        def where(self, key=None, value=None):
            if type(key) is not str:
                list_model = [
                    item
                    for item in self.__list_model
                    if all(getattr(item, key_item)() == value_item for key_item, value_item in zip(key, value))
                ]

                return list_model

            list_model = [item for item in self.__list_model if getattr(item, key)() == value]
            return list_model if key != "get_codigo" else list_model[0]

        def get_list(self):
            return self.__list_model
        
        def get_dict(self):
            from reserva_app.models import Reserva, Sala, User

            arr = self.get_list()
            result_dict = {}

            if isinstance(arr[0], Reserva):
                for i, obj in enumerate(arr):
                    result_dict[i] = {
                        'codigo': obj.get_codigo(),
                        'codigo_usuario': obj.get_codigo_usuario(),
                        'datetime_start': obj.get_datetime_start().strftime("%Y-%m-%d %H:%M:%S"),
                        'datetime_end': obj.get_datetime_end().strftime("%Y-%m-%d %H:%M:%S"),
                        'duracao': str(obj.get_datetime_end() - obj.get_datetime_start()),
                        'falta':str(obj.get_datetime_start()-datetime.now()),
                        'ativo': obj.get_ativo()
                    }
            elif isinstance(arr[0], Sala):
                for i, obj in enumerate(arr):
                    result_dict[i] = {
                        'codigo': obj.get_codigo(),
                        'capacidade': obj.get_capacidade(),
                        'tipo': obj.get_tipo(),
                        'descricao': obj.get_descricao(),
                        'ativo': obj.get_ativo()
                    }
            elif isinstance(arr[0], User):
                for i, obj in enumerate(arr):
                    result_dict[i] = {
                        'nome': obj.get_nome(),
                        'email': obj.get_email(),
                        'ativo': obj.get_ativo()
                    }

            return result_dict


        def __str__(self):
            string_values = ''.join([str(item) for item in self.__list_model])
            return f"{string_values}"


class ColumnBase:
    def __init__(self, value, type_field):
        self.__value = value
        self.__type_field = type_field

    def get_value(self):
        return self.__value

    def set_value(self, value):
        self.__value = value


class Column:
    class char_field(ColumnBase):
        CHAR_REPLACE_COMMA = "///COMMA///"

        def __init__(self, value):
            super().__init__(self.__replace_comma(str(value)), 1)

        def set_value(self, value):
            super().set_value(self.__replace_comma(str(value)))

        def get_value(self):
            return self.__replace_comma(super().get_value())

        @staticmethod
        def __replace_comma(value):
            return value.replace(",", Column.char_field.CHAR_REPLACE_COMMA)

        @staticmethod
        def __replace_char_comma(value):
            return value.replace(Column.char_field.CHAR_REPLACE_COMMA, ",")

    class integer_field(ColumnBase):
        def __init__(self, value):
            super().__init__(int(value), 2)

        def set_value(self, value):
            super().set_value(int(value))

    class float_field(ColumnBase):
        def __init__(self, value):
            super().__init__(float(value), 3)

        def set_value(self, value):
            super().set_value(float(value))

    class boolean_field(ColumnBase):
        def __init__(self, value):
            value = value == 'True' if type(value) is str else value
            super().__init__(value, 4)

        def set_value(self, value: bool):
            value = value == 'True' if type(value) is str else value
            super().set_value(value)

    class datetime_field(ColumnBase):
        def __init__(self, value):
            value = datetime.strptime(value, "%Y-%m-%d %H:%M:%S") if type(value) is str \
                else value.strftime("%Y-%m-%d %H:%M:%S") if value \
                else value

            super().__init__(value, 4)

        def set_value(self, value):
            value = datetime.strptime(value, "%Y-%m-%d %H:%M:%S") if type(value) is str \
                else value.strftime("%Y-%m-%d %H:%M:%S")
            super().set_value(value)

        def get_value(self) -> str:
            value = super().get_value().strftime("%Y-%m-%d %H:%M:%S")
            return value
