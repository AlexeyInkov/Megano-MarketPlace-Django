# Итоговая аттестация по курсу

## Установка
#### Установка зависимостей
```pip install -r requirements.txt```

#### Подключение frondend
1. Собрать пакет: в директории diploma-frontend выполнить команду
   - ```python setup.py sdist```
2. Установить полученный пакет в виртуальное окружение:
   - ```pip install diploma-frontend-X.Y.tar.gz```
   - X и Y - числа, они могут изменяться в зависимости от текущей версии пакета.

#### Выполнение миграций
```python manage.py migrate```

#### создание суперпользователя
```python manage.py createsuperuser```

#### Заполнение БД
```python manage.py loaddata api.json```


