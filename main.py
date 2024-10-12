from sys import argv
from os.path import exists
from terminal import MyTerminal


def main():
    if len(argv) >= 3:
        user_name = argv[1]
        start_script = argv[2]
    else:
        print('Введены не все ключи для корректного запуска')
        return

    terminal = MyTerminal(user_name, start_script)
    terminal.exec_start_script()
    terminal.start_polling()


if __name__ == '__main__':
    main()
