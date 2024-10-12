import unittest
from terminal import MyTerminal

class TestTerminalCommands(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        cls.terminal = MyTerminal(user_name="test_user", start_script='start.txt')
        cls.terminal.fs = 'archiveForTest.tar'

    def test_cd_valid_directory(self):
        """Проверка перехода в допустимый каталог"""
        self.terminal.cur_d = ''
        result = self.terminal.cd(['desktop'])
        self.assertEqual(self.terminal.cur_d, 'desktop')
        self.assertEqual(result, 'change to desktop')

    def test_cd_invalid_directory(self):
        """Проверка перехода в недопустимый каталог"""
        result = self.terminal.cd(['invalid_dir'])
        self.assertIn("cd: invalid_dir: No such file or directory", result)

    def test_ls_root(self):
        """Проверка команды ls для корневого каталога"""
        self.terminal.cur_d = ''
        result = self.terminal.ls([])
        self.assertIn("desktop", result)
        self.assertIn("users", result)
        self.assertIn("hello.txt", result)

    def test_ls_desktop(self):
        """Проверка команды ls для каталога desktop"""
        self.terminal.cur_d = 'desktop'
        result = self.terminal.ls([])
        self.assertIn("folder", result)
        self.assertIn("more_textes.txt", result)

    def test_tree_current_directory(self):
        """Проверка команды tree для текущего каталога"""
        self.terminal.cur_d = 'desktop/folder'
        result = self.terminal.tree([])
        self.assertIn("|-- bin", result)
        self.assertIn("|-- more_textes.txt", result)
        self.assertIn("|__ world", result)

    def test_tree_invalid_directory(self):
        """Проверка команды tree для несуществующего каталога"""
        result = self.terminal.tree(['invalid_dir'])
        self.assertIn("tree: 'invalid_dir': No such file or directory", result)

    def test_mv_valid(self):
        """Проверка перемещения файла"""
        self.terminal.cur_d = 'desktop'
        result = self.terminal.mv(['more_textes.txt', 'desktop/folder/more_textes.txt'])
        self.assertIn("'desktop/more_textes.txt' -> 'desktop/folder/more_textes.txt'", result)

    def test_mv_invalid_source(self):
        """Проверка команды mv с недопустимым исходным файлом"""
        result = self.terminal.mv(['invalid_file', 'users/new_file.txt'])
        self.assertIn("mv: can't stat 'invalid_file': No such file or directory", result)

    def test_uname_default(self):
        """Проверка команды uname без аргументов"""
        result = self.terminal.uname([])
        self.assertIn("CLI_UNIX", result)

    def test_uname_with_flags(self):
        """Проверка команды uname с различными флагами"""
        result = self.terminal.uname(['-s', '-r', '-v', '-m'])
        self.assertIn("CLI_UNIX", result)
        self.assertIn("CLI_UNIX by Salakhaddin 1.0.0", result)
        self.assertIn("1.0", result)
        self.assertIn("x86_64", result)

    def test_invalid_command(self):
        """Проверка ввода несуществующей команды"""
        result = self.terminal.command_dispatcher("invalidcommand")
        self.assertIn("Command not found", result)

if __name__ == "__main__":
    unittest.main()
