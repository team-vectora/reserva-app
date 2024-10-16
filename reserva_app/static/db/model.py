import os
import pymysql
from pymysql.cursors import DictCursor
from mysql.connector import Error
from datetime import datetime
import reserva_app

app = reserva_app.app


class Model:
    def __init__(self, child_class) -> None:
        self.__codigo = 0  # Código é comum para todos os models
        self.__child_class = child_class  # Instância da classe filha que vai herdar o Model

    def get_codigo(self):
        return self.__codigo

    def set_codigo(self, codigo):
        self.__codigo = codigo

    @staticmethod
    def _get_connection():
        try:
            connection = pymysql.connect(
                host='localhost',
                database='reservaappdb',
                user='root',
                password="1234",
                port=3306,
                #cursorclass=DictCursor,
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
            columns = ', '.join([attr for attr in self.__dir__(db=True)])
            values = ', '.join(['%s'] * len(self.__dir__(db=True)))
            query = f"INSERT INTO {self.__child_class.table_name} ({columns}) VALUES ({values})"
            print(f"query: {cursor.mogrify(query, [attr for attr in self.__dir__(get=True)])}")
            cursor.execute(query, [attr for attr in self.__dir__(get=True)])
            self.__codigo = cursor.lastrowid
        else:  # Atualizar registro existente
            set_clause = ', '.join([f"{attr} = %s" for attr in self.__dir__(db=True)[:-1]])
            query = f"UPDATE {self.__child_class.table_name} SET {set_clause} WHERE codigo = %s"
            print(f"query: {cursor.mogrify(query, [attr for attr in self.__dir__(get=True)])}")
            cursor.execute(query, [attr for attr in self.__dir__(get=True)])

        connection.commit()
        cursor.close()
        connection.close()
        return self.__codigo

    @staticmethod
    def _objects(child_class):
        connection = Model._get_connection()
        cursor = connection.cursor()
        query = f"SELECT * FROM {child_class.table_name}"
        cursor.execute(query)

        print(f"query: {cursor.mogrify(query)}")

        list_model = Model.ListModel()
        list_model.set_child_class(child_class)
        for row in cursor.fetchall():
            model = child_class()
            model.set_codigo(row[0])  # o primeiro sempre vai ser o codigo
            for (attr, value) in zip(model.__dir__(set=True), row[1:]):  # precisa pular se nao ele quebra
                model.__getattribute__(attr)(value)
            list_model.append(model)

        cursor.close()
        connection.close()
        return list_model

    @staticmethod
    def _exclude(id_to_exclude, child_class):
        connection = Model._get_connection()
        cursor = connection.cursor()
        query = f"DELETE FROM {child_class.table_name} WHERE codigo = %s"
        cursor.execute(query, id_to_exclude)

        print(f"query: {cursor.mogrify(query, id_to_exclude)}")
        connection.commit()

        cursor.close()
        connection.close()

    def __str__(self):
        return ",".join([str(attr) for attr in self.__dir__(get=True)]) + "\n"

    def __dir__(self, get=False, set=False, db=False):
        dir_attr = super().__dir__()

        if get:
            return [self.__getattribute__(attr)() for attr in dir_attr
                    if attr.startswith("get")]
        if set:
            return [attr for attr in dir_attr
                    if attr.startswith("set")]
        if db:
            return [attr[4:] for attr in dir_attr
                    if attr.startswith("get")]

        return dir_attr

    class ListModel:
        def __init__(self, list_model=None, child_class=None):
            self.__list_model = list() if list_model is None else list_model
            self.__child_class = child_class

        def append(self, value):
            self.__list_model.append(value)

        def where(self, key=None, value=None) -> list | super:

            cursor = Model._get_connection().cursor()

            if isinstance(key, tuple) and isinstance(value, tuple):
                # Se ambos são tuplas, construa uma consulta com múltiplas condições
                conditions = ' AND '.join([f"{k} = %s" for k in key])
                query = f"SELECT * FROM {self.__child_class.table_name} WHERE {conditions}"
                cursor.execute(query, value)
            elif key and value:
                # Se ambos são parâmetros normais
                query = f"SELECT * FROM {self.__child_class.table_name} WHERE {key} = %s"
                cursor.execute(query, value)
            else:
                # Se não forem fornecidos parâmetros, retorna todos os registros
                query = f"SELECT * FROM {self.__child_class.table_name}"
                cursor.execute(query)

            print(f"query: {cursor.mogrify(query, value)}")

            results = cursor.fetchall()
            print(f"resultados: {results}")
            if len(results) == 0:
                return []

            cursor.close()
            # Criar objetos da classe filha a partir dos resultados
            models = []
            for row in results:
                model = self.__child_class()
                model.set_codigo(row[0])  # o primeiro sempre vai ser o codigo e da ruim se nao excluir ele antes
                for attr, value in zip(model.__dir__(set=True), row[1:]):
                    model.__getattribute__(attr)(value)
                models.append(model)

            return models if len(models) > 1 else models[0]

        def get_list(self):
            return self.__list_model

        def print_(self):
            cursor = Model._get_connection().cursor()

            # Executar uma consulta para obter o cabeçalho
            cursor.execute(f"SELECT * FROM {self.__child_class.table_name} LIMIT 0")  # Consulta apenas para cabeçalho
            columns = [col[0] for col in cursor.description]  # Obter cabeçalho

            # Imprimir cabeçalho
            header = '| ' + ' | '.join(columns) + ' |'
            print(header)
            print('-' * len(header))  # Linhas divisórias

            # Consultar todos os dados para imprimir
            cursor.execute(f"SELECT * FROM {self.__child_class.table_name}")
            results = cursor.fetchall()
            cursor.close()

            # Imprimir cada linha formatada
            for row in results:
                formatted_row = '| ' + ' | '.join(str(value) for value in row) + ' |'
                print(formatted_row)

        def set_child_class(self, child_class):
            self.__child_class = child_class

    """
    LIST MODEL antigo com a implementação da BUSCA BINÁRIA
    
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
    """


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

        def __init__(self, value):
            super().__init__(str(value), 1)

        def set_value(self, value):
            super().set_value(str(value))

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
        format = '%Y-%m-%d %H:%M:%S'

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
