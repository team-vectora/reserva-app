import os
from datetime import datetime
import reserva_app

app = reserva_app.app


class Model:
    def __init__(self, child_class) -> None:
        target = os.path.join(app.static_folder, 'db', child_class.table_name)  # Nome do arquivo CSV

        self.__codigo = 0  # Codigo é comum para todos os models
        self.__table_name = target  # Nome do arquivo
        self.__child_class = child_class  # Instancia da classe filha que vai herdar o Model

    def _generate_id(self) -> int:
        objects = self._objects(self.__child_class).get_list()  # Lista dos objetos
        return 1 if not objects else objects[-1].get_codigo() + 1  # Cria o id sendo o id do ultimo da lista +1

    """
        GETTER SETTER
    """

    def get_codigo(self):
        return self.__codigo

    def set_codigo(self, codigo):
        self.__codigo = int(codigo)

    def save(self) -> int:
        mode = "a" if self.__codigo == 0 else "r+"  # Se o codigo for zero quer dizer que é um Model novo, então o
                                                    # modo é de A, pra criar o adicionar, se não (se ja ta criado) então
                                                    # é R+ (read e edit) pra dar o update
        with open(self.__table_name, mode, encoding='latin-1') as file:
            if self.__codigo == 0:  # Se o model é novo
                self.__codigo = self._generate_id()  # Gera um novo ID
                file.write(str(self))  # Adiciona no arquivo
            else:  # Se o model ja existe
                readline = file.readlines()
                new_lines = [str(self) if line.strip().endswith(str(self.__codigo)) else line for line in readline]  #
                                                    # Troca toda a linha pela linha atual
                file.seek(0)
                file.writelines(new_lines)  # Reescreve todo_ o arquivo
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
                for (dir_attr, attr) in zip(model.__dir__(set=True), attr_list):
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
        return ",".join(map(self.__format_to_csv, [attr for attr in self.__dir__(get=True)])) + "\n"

    @staticmethod
    def __format_to_csv(value):
        return str(value).replace(",", Column.char_field.CHAR_REPLACE_COMMA)

    def __dir__(self, get=False, set=False):
        dir_attr = super().__dir__()

        if get:
            for attr in dir_attr:
                if attr.startswith("get"):
                    print(attr)
                    print(self.__getattribute__(attr)())

            return [self.__getattribute__(attr)() for attr in dir_attr
                    if attr.startswith("get")]
        if set:
            return [attr for attr in dir_attr
                    if attr.startswith("set")]

        return dir_attr

    class ListModel:
        def __init__(self, list_model=None):
            self.__list_model = list() if list_model is None else list_model

        def append(self, value):
            self.__list_model.append(value)

        def where(self, key=None, value=None) -> list | super:
            sorted_list = sorted(self.__list_model, key=lambda x: getattr(x, key)())

            if key == "get_codigo" or key == "get_email":
                return self._binary_search(sorted_list, key, value)

            if isinstance(key, str):
                return self._binary_search_filter(sorted_list, key, value)
            else:
                return self._binary_search_multiple_filter(sorted_list, key, value)

        def get_list(self):
            return self.__list_model

        @staticmethod
        def _binary_search(sorted_list, key, value):
            start = 0
            end = len(sorted_list) - 1

            while start <= end:
                mid = (start + end) // 2
                current_value = getattr(sorted_list[mid], key)()

                if current_value == value:
                    return sorted_list[mid]
                elif current_value < value:
                    start = mid + 1
                else:
                    end = mid - 1

            return None

        @staticmethod
        def _binary_search_filter(sorted_list, key, value):
            start = 0
            end = len(sorted_list) - 1
            found_index = -1

            while start <= end:
                mid = (start + end) // 2
                current_value = getattr(sorted_list[mid], key)()

                if current_value == value:
                    found_index = mid
                    break
                elif current_value < value:
                    start = mid + 1
                else:
                    end = mid - 1

            if found_index == -1:
                return []

            results = [sorted_list[found_index]]

            left = found_index - 1
            while left >= 0 and getattr(sorted_list[left], key)() == value:
                results.insert(0, sorted_list[left])
                left -= 1

            right = found_index + 1
            while right < len(sorted_list) and getattr(sorted_list[right], key)() == value:
                results.append(sorted_list[right])
                right += 1

            return results

        @staticmethod
        def _binary_search_multiple_filter(sorted_list, key_list, value_list):

            aux_list_results = []

            for key, value in zip(key_list, value_list):
                result_filter_list = Model.ListModel._binary_search_filter(sorted_list, key, value)
                aux_list_results.append(result_filter_list)

            if len(aux_list_results) > 1:
                final_results = aux_list_results[0]
                for result_filter_list in aux_list_results:
                    final_results = [item for item in final_results if item in result_filter_list]

                return final_results
            else:
                return aux_list_results[0]

        def print_(self):
            string_values = ''.join([str(item) for item in self.__list_model])
            return f"{string_values}"

        def __str__(self):
            return ",".join(map(self.__format_to_csv, [attr for attr in self.__dir__(get=True)])) + "\n"

        @staticmethod
        def __format_to_csv(value):
            return str(value).replace(",", Column.char_field.CHAR_REPLACE_COMMA)


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
            super().__init__(self.__replace_char_comma(str(value)), 1)

        def set_value(self, value):
            super().set_value(self.__replace_char_comma(str(value)))

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
        format = "%d/%m/%Y %H:%M"

        def __init__(self, value):
            if type(value) is datetime:
                value = value.strftime(self.format)

            super().__init__(value, 4)

        def set_value(self, value):
            if type(value) is datetime:
                value = value.strftime(self.format)

            super().set_value(value)

        def get_value(self) -> str:
            value = super().get_value()
            print(value)
            return value

import mysql.connector
from mysql.connector import Error
from datetime import datetime
import reserva_app

app = reserva_app.app


class Model:
    def __init__(self, child_class) -> None:
        self.__codigo = 0  # Código é comum para todos os models
        self.__child_class = child_class  # Instância da classe filha que vai herdar o Model

    @staticmethod
    def _get_connection():
        try:
            connection = mysql.connector.connect(
                host='localhost',
                database='your_database',
                user='your_user',
                password='your_password'
            )
            return connection
        except Error as e:
            print(f"Error: {e}")
            return None

    def save(self) -> int:
        connection = self._get_connection()
        if not connection:
            return 0

        cursor = connection.cursor()

        if self.__codigo == 0:  # Novo registro
            self.__codigo = self._generate_id()
            columns = ', '.join([attr for attr in self.__dir__(get=True)])
            values = ', '.join(['%s'] * len(self.__dir__(get=True)))
            query = f"INSERT INTO {self.__child_class.table_name} ({columns}) VALUES ({values})"
            cursor.execute(query, [self.__getattribute__(attr)() for attr in self.__dir__(get=True)])
        else:  # Atualizar registro existente
            set_clause = ', '.join([f"{attr} = %s" for attr in self.__dir__(get=True)])
            query = f"UPDATE {self.__child_class.table_name} SET {set_clause} WHERE codigo = %s"
            cursor.execute(query, [self.__getattribute__(attr)() for attr in self.__dir__(get=True)] + [self.__codigo])

        connection.commit()
        cursor.close()
        connection.close()
        return self.__codigo

    @staticmethod
    def _objects(child_class):
        connection = mysql.connector.connect(
            host='localhost',
            database='your_database',
            user='your_user',
            password='your_password'
        )
        cursor = connection.cursor()
        query = f"SELECT * FROM {child_class.table_name}"
        cursor.execute(query)

        list_model = Model.ListModel()
        for row in cursor.fetchall():
            model = child_class()
            for (attr, value) in zip(model.__dir__(set=True), row):
                model.__getattribute__(attr)(value)
            list_model.append(model)

        cursor.close()
        connection.close()
        return list_model

    @staticmethod
    def _exclude(id_to_exclude, child_class):
        connection = mysql.connector.connect(
            host='localhost',
            database='your_database',
            user='your_user',
            password='your_password'
        )
        cursor = connection.cursor()
        query = f"DELETE FROM {child_class.table_name} WHERE codigo = %s"
        cursor.execute(query, (id_to_exclude,))
        connection.commit()

        cursor.close()
        connection.close()

    def __str__(self):
        return ",".join(map(self.__format_to_csv, [attr for attr in self.__dir__(get=True)])) + "\n"

    @staticmethod
    def __format_to_csv(value):
        return str(value).replace(",", Column.char_field.CHAR_REPLACE_COMMA)

    def __dir__(self, get=False, set=False):
        dir_attr = super().__dir__()

        if get:
            return [self.__getattribute__(attr)() for attr in dir_attr
                    if attr.startswith("get")]
        if set:
            return [attr for attr in dir_attr
                    if attr.startswith("set")]

        return dir_attr

    class ListModel:
        def __init__(self, list_model=None):
            self.__list_model = list() if list_model is None else list_model

        def append(self, value):
            self.__list_model.append(value)

        def where(self, key=None, value=None) -> list | super:
            return [obj for obj in self.__list_model if getattr(obj, key)() == value]

        def get_list(self):
            return self.__list_model

        def print_(self):
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
            super().__init__(self.__replace_char_comma(str(value)), 1)

        def set_value(self, value):
            super().set_value(self.__replace_char_comma(str(value)))

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
            value = value == 'True' if isinstance(value, str) else value
            super().__init__(value, 4)

        def set_value(self, value: bool):
            value = value == 'True' if isinstance(value, str) else value
            super().set_value(value)

    class datetime_field(ColumnBase):
        format = "%d/%m/%Y %H:%M"

        def __init__(self, value):
            if isinstance(value, datetime):
                value = value.strftime(self.format)
            super().__init__(value, 5)

        def set_value(self, value):
            if isinstance(value, datetime):
                value = value.strftime(self.format)
            super().set_value(value)

        def get_value(self) -> str:
            value = super().get_value()
            return value
