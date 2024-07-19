import os

import reserva_app

app = reserva_app.init()


class Model:
    def __init__(self, primary_key: int, table_name: str, constructor) -> None:
        self.primary_key = primary_key or 0
        self.table_name = "reserva_app/db/" + table_name
        self.constructor = constructor

    def _generate_id(self) -> int:
        objects = self._objects(self.table_name, self.constructor)
        return 1 if not objects else objects[-1].primary_key + 1

    def save(self) -> int:
        mode = "a" if self.primary_key == 0 else "r+"
        with open(self.table_name, mode, encoding='latin-1') as file:
            if self.primary_key == 0:
                self.primary_key = self._generate_id()
                file.write(str(self))
            else:
                readline = file.readlines()
                new_lines = [str(self) if line.startswith(str(self.primary_key)) else line for line in readline]
                file.seek(0)
                file.writelines(new_lines)
                file.truncate()

        return self.primary_key

    @staticmethod
    def _objects(table_name, constructor) -> list:
        target = os.path.join(app.static_folder, 'db', table_name)
        with open(target, "w+", encoding='latin-1') as file:
            list_model = []
            for line in file.readlines():
                attr = line.strip().split(",")
                model = constructor(*attr)
                list_model.append(model)
            return list_model

    @staticmethod
    def _exclude(id_to_exclude, table_name):
        target = os.path.join(app.static_folder, 'db', table_name)
        with open(target, "r+", encoding='latin-1') as file:
            readline = file.readlines()
            new_lines = [line for line in readline if not line.startswith(id_to_exclude)]
            file.seek(0)
            file.writelines(new_lines)
            file.truncate()

    def __str__(self):
        return ",".join(map(str, [self.__getattribute__(attr) for attr in self.__dir__()])) + "\n"

    def __dir__(self):
        dir_attr = super().__dir__()
        return [attr for attr in dir_attr
                if not attr.startswith("_") and
                attr not in ["table_name", "constructor", "exclude", "save", "objects"]]
