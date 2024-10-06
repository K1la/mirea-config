# 1. Виртуальное окружение

```shell
python -m venv venv
venv/Scripts/activate
```

# 2. Установка библиотек

```shell
pip install pytest
pip install coverage
```

# 3. Запуск программы

Запуск в режиме **CLI**:

```shell
py main.py "my-user" "archive.tar" "logs.json" "start.txt"
```

# 4. Тестирование

Для запуска тестирования необходимо запустить следующий скрипт:

```shell
pytest -v
```

Для генерации отчета о покрытии тестами необходимо выполнить команду:

```shell
coverage run --branch -m pytest test_terminal.py
```

Просмотр результатов покрытия:

```shell
coverage report
```
