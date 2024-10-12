import json
import tarfile
from datetime import datetime


class MyTerminal:
    def __init__(self, user_name, start_script):
        self.us_name = user_name
        self.st_script = start_script

        with open('logs.json', 'r') as config_path:
            config = json.load(config_path)
        self.fs = config['filesystem']

        self.cur_d = ''
        self.polling = False
        self.deleted = set()

    def output(self, message, end='\n'):
        print(message)
        return message

    def start_polling(self):
        self.polling = True
        while self.polling:
            message = f'{self.us_name}:~{self.cur_d}$ '
            enter = input(message).strip()
            if len(enter) > 0:
                self.command_dispatcher(enter)
        self.output('stop polling...')

    def command_dispatcher(self, command):

        params = command.split()
        if params[0] == 'exit':
            self.polling = False
        elif params[0] == 'cd':
            self.cd(params[1:])
        elif params[0] == 'ls':
            self.ls(params[1:])
        elif params[0] == 'mv':
            self.mv(params[1:])
        elif params[0] == 'tree':
            self.tree(params[1:])
        elif params[0] == 'uname':
            self.uname(params[1:])
        elif params[0] == 'uname':
            self.uname(params[1:])
        else:
            return self.output("Command not found")

    def exec_start_script(self):
        try:
            with open(self.st_script, 'rt') as f:
                for s in f:
                    s = s.strip()
                    if len(s) > 0:
                        self.command_dispatcher(s)
        except:
            self.output('Failed opening start script')

    def find_path(self, path):
        current_path = self.cur_d

        while '//' in path:
            path = path.replace('//', '/')
        if path[-1] == '/':
            path = path[:-1]

        path = path.split('/')
        if path[0] == '/':
            current_path = ''
            path.pop(0)

        while path:
            name = path.pop(0)
            if name == '.':
                current_path = self.cur_d
            elif name == '..':
                index = current_path.rfind('/')
                if index > -1:
                    current_path = current_path[:index]
                else:
                    current_path = ''
            else:
                if current_path:
                    current_path += '/' + name
                else:
                    current_path += name
                with tarfile.open(self.fs, 'r') as tar:
                    paths = [member.name for member in tar]
                    if current_path not in paths:
                        return None

        if current_path in self.deleted:
            current_path = None
        return current_path

    def ls(self, prmtrs):
        message = ""

        def ls_names(c_directory):
            m_names = set()
            with tarfile.open(self.fs, 'r') as tar:
                for member in tar:
                    m_name = member.name
                    if m_name.find(c_directory) > -1 and m_name not in self.deleted:
                        if m_name == c_directory:
                            if member.type == tarfile.DIRTYPE:
                                continue
                            return (c_directory[c_directory.rfind('/') + 1:],)

                        m_name = m_name[len(c_directory):]
                        if m_name[0] == '/':
                            m_name = m_name[1:]
                        erase = m_name.find('/')
                        if erase > -1:
                            m_name = m_name[:m_name.find('/')]
                        m_names.add(m_name)
            return sorted(m_names)

        if len(prmtrs) > 1:
            prmtrs.sort()
            while prmtrs:
                directory = self.find_path(prmtrs[0])
                name = prmtrs.pop(0)
                if directory is None:
                    self.output(f"ls: cannot access '{name}': No such file or directory")
                    continue

                message += self.output(f'{name}:') + '\n'
                names = ls_names(directory)
                if names:
                    message += self.output(' '.join(names)) + '\n'
                if prmtrs:
                    message += self.output('') + '\n'

            return message

        directory = self.cur_d
        if len(prmtrs) == 1:
            directory = self.find_path(prmtrs[0])
            if directory is None:
                message += self.output(f"ls: cannot access '{prmtrs[0]}': No such file or directory") + '\n'
                return message

        names = ls_names(directory)
        if names:
            message += self.output('\n'.join(names)) + '\n'
        return message

    def cd(self, prmtrs):
        if not prmtrs:
            self.cur_d = ''
            return 'root directory'

        if len(prmtrs) > 1:
            return self.output("cd: too many arguments")

        new_directory = self.find_path(prmtrs[0])
        if new_directory is None:
            return self.output(f"cd: {prmtrs[0]}: No such file or directory")
        if new_directory == '':
            self.cur_d = new_directory
            return f"change to " + new_directory

        with tarfile.open(self.fs, 'r') as tar:
            for member in tar:
                if member.name == new_directory and member.name not in self.deleted:
                    if member.type != tarfile.DIRTYPE:
                        return self.output(f"cd: {prmtrs[0]}: Not a directory")
                    self.cur_d = new_directory
                    return f"change to " + new_directory

    def mv(self, prmtrs):
        if len(prmtrs) != 2:
            return self.output("mv: missing file operand or target")

        src_path = self.find_path(prmtrs[0])  # Исходный файл или директория
        dest_path = self.find_path(prmtrs[1])  # Целевая директория или имя

        if src_path is None:
            return self.output(f"mv: can't stat '{prmtrs[0]}': No such file or directory")

        with tarfile.open(self.fs, 'r') as tar:
            files_in_tar = [member.name for member in tar.getmembers()]
            
            # Если целевой путь — это существующий файл, то перемещаем внутрь
            if dest_path is None:
                # Определяем целевой путь
                if prmtrs[1].endswith('/'):
                    dest_path = prmtrs[1].rstrip('/')
                else:
                    dest_path = prmtrs[1]
            else:
                # Если dest_path — существующая директория, перемещаем внутрь нее
                if dest_path in files_in_tar and tar.getmember(dest_path).isdir():
                    src_name = src_path.split('/')[-1]  # Имя исходного файла
                    dest_path = f"{dest_path}/{src_name}"  # Перемещение в целевую директорию

            if dest_path in files_in_tar:
                return self.output(f"mv: cannot move '{prmtrs[0]}' to '{prmtrs[1]}': File or directory exists")

            self.deleted.add(src_path)  # Помечаем исходный файл как удаленный

            for member in tar.getmembers():
                if member.name == src_path:
                    with tarfile.open(self.fs, 'a') as tar_add:
                        member.name = dest_path  # Изменяем путь
                        tar_add.addfile(member)
        
        return self.output(f"'{src_path}' -> '{dest_path}'")


    def tree(self, prmtrs):
        #если ничего не указано - это текущая директория
        start_path = self.cur_d
        if len(prmtrs) == 1:
            start_path = self.find_path(prmtrs[0])
            if start_path is None:
                return self.output(f"tree: '{prmtrs[0]}': No such file or directory")
        
        def generate_tree(directory, prefix=""):
            tree_str=""
            entries = []

            with tarfile.open(self.fs, 'r') as tar:
                for member in tar.getmembers():
                    #файл/папка не удалена
                    if member.name.startswith(directory) and member.name != directory and member.name not in self.deleted:
                        #отрезаем текущий путь, чтобы получить имя
                        rel_path = member.name[len(directory):].lstrip('/')
                        if '/' not in rel_path or rel_path.endswith('/'):
                            entries.append((rel_path, member))

            entries = sorted(entries, key=lambda x: x[0])

            for i, (entry_name, member) in enumerate(entries):
                connector = "|__ " if i == len(entries) - 1 else "|-- "
                tree_str += f"{prefix}{connector}{entry_name}\n"
                
                if member.isdir():
                    sub_dir = f"{directory}/{entry_name}".rstrip('/')
                    new_prefix = f"{prefix}{'    ' if i == len(entries)-1 else '|   '}"
                    tree_str += generate_tree(sub_dir, new_prefix)
            return tree_str
        
        #если директория пустая
        with tarfile.open(self.fs, 'r') as tar:
            paths = [member.name for member in tar.getmembers() if member.name.startswith(start_path) and member.name not in self.deleted]
            if len(paths) == 0:
                return self.output(f"tree: {start_path}: [empty directory]")
        
        tree_structure = generate_tree(start_path)
        self.output(tree_structure)

        return tree_structure

    def uname(self, prmtrs):
        sys_name = "CLI_UNIX"
        version = "1.0"
        release = "CLI_UNIX by Salakhaddin 1.0.0"
        machine = "x86_64"

        if not prmtrs:
            return self.output(sys_name)

        # Опции команды uname:
        output = []
        for param in prmtrs:
            if param == "-s":  # Вывод имени системы
                output.append(sys_name)
            elif param == "-r":  # Вывод релиза/версии ядра
                output.append(release)
            elif param == "-v":  # Вывод версии ОС
                output.append(version)
            elif param == "-m":  # Вывод архитектуры
                output.append(machine)
            else:
                return self.output(f"uname: invalid option - '{param}'")

        return self.output(" ".join(output))