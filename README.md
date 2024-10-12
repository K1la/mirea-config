# ДЗ 1 / Вариант - 24
**ОБЯЗАТЕЛЬНО, перед каждым запуском нужно переименовывать архив RenameME.tar на archive.tar**
**Т.к архив меняется из-за воздействия команд**

# 1. Виртуальное окружение

```shell
python -m venv venv
venv/Scripts/activate
```

# 2. Установка библиотек

```shell
pip install unitest
```

# 3. Запуск программы

Запуск в режиме **CLI**:

```shell
py main.py "my-user" "start.txt"
```

# 4. Тестирование

# ОБЯЗАТЕЛЬНО перед каждым тестом, копировать архив RenameMe.tar и переименовывать его в 'archiveForTest.tar'

Для запуска тестирования необходимо запустить следующий скрипт:

```shell
python -m unittest tests.py
```