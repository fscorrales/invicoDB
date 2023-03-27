import os
import inspect


class HanglingPath():
    # --------------------------------------------------
    def get_invicodb_path(self):
        dir_path = os.path.dirname(
            os.path.abspath(
                inspect.getfile(
                    inspect.currentframe())))
        return dir_path

    # --------------------------------------------------
    def get_src_path(self):
        dir_path = self.get_invicodb_path()
        dir_path = os.path.dirname(dir_path)
        return dir_path

    # --------------------------------------------------
    def get_update_path_input(self):
        dir_path = os.path.join(
            os.path.dirname(self.get_src_path()),'Base de Datos'
        )
        return dir_path

    # --------------------------------------------------
    def get_outside_path(self):
        dir_path = os.path.dirname(os.path.dirname(self.get_src_path()))
        return dir_path

    # --------------------------------------------------
    def get_db_path(self):
        self.db_path = os.path.join(self.get_outside_path() ,'Python Output')
        self.db_path = os.path.join(self.db_path, 'SQLite Files')
        return self.db_path

    # --------------------------------------------------
    def get_exequiel_path(self):
        dir_path = r'\\192.168.0.149\Compartida CONTABLE\R Apps (Compartida)\R Output\SQLite Files'
        return dir_path