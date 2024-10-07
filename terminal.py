import json
import tarfile
from datetime import datetime


class MyTerminal:
    def __init__(self, user_name, file_system, log_file, start_script):
        self.us_name = user_name
        self.fs = file_system
        self.log_f = log_file
        self.st_script = start_script

        self.cur_d = ''
        self.polling = False
        self.log = dict()
        self.log['id'] = dict()
        self.cnt = 0

        self.deleted = set()

    def make_log(self):
        with open(self.log_f, 'w') as f:
            json.dump(self.log, f)

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
        self.log['id'][self.cnt] = {'user': self.us_name, 'time': str(datetime.now()), 'command': command}
        self.cnt += 1

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
        else:
            self.output("Command not found")

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
            return self.output("mv: missing file operand")
        
        source_path = self.find_path(prmtrs[0])
        if source_path is None:
            return self.output(f"mv: can't stat '{prmtrs[0]}': No such file or directory")
        
        destination_path = self.find_path(prmtrs[1])
        if destination_path is None:
            destination_path = prmtrs[1]
            if destination_path[-1] == '/':
                destination_path = destination_path[:-1]
        
        #если путь - это директория
        with tarfile.open(self.fs, 'r') as tar:
            for member in tar.getmembers():
                if member.name == destination_path and member.isdir():
                    destination_path = f"{destination_path}/{source_path.split('/')[-1]}"
                    break
        
        #обновляем переменные удаленных файлов
        self.deleted.add(source_path)

        #переименование/ перемещаем файл
        with tarfile.open(self.fs, 'r') as tar:
            new_members = []
            for member in tar.getmembers():
                if member.name != source_path:
                    new_members.append(member)
                else:
                    member.name = destination_path
                    new_members.append(member)

            with tarfile.open(self.fs, 'w') as new_tar:
                for member in new_members:
                    new_tar.addfile(member)
        
        self.output(f"'{prmtrs[0]}' -> '{prmtrs[1]}'")

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
    
    def uname(self, prmtrs):
        sys_name = "CLI_Terminal"

        version = "1.0"
        release = "CLI_Treminal by Salakhaddin 1.0"
        machine = "x86_64"

        if not prmtrs:
            return self.output(sys_name)

        output = []
        for param in prmtrs:
            if param == "-s":
                output.append(sys_name)
            elif param == "-r":
                output.append(release)
            elif param == "-v":
                output.append(version)
            elif param == "-m":
                output.append(machine)
            else:
                return self.output(f"uname: invalid option -- '{param}'")
        
        return self.output(" ".join(output))
            
