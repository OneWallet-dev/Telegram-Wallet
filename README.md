<hr/>

![Typing SVG](https://readme-typing-svg.herokuapp.com?font=Fira+Code&size=40&pause=1000&color=373737&background=91C5F4&center=true&vCenter=true&multiline=true&width=1080&height=80&lines=Telegram+Crypto+WAllet+(TCW))
<hr/>

## Технологии
- Python 3.10-buster;
- Aiogram ( Telegram framework  );
- Docker and Docker Compose ( containerization );
- PostgreSQL ( database );
- Redis ( cache, database )
- SQLAlchemy ( working with database from Python );
- Alembic ( database migrations made easy );
- Pydantic ( models )


## Установка и запуск

1. Клонировать проект в удобное место:

```sh
git clone https://github.com/OneWallet-dev/Telegram-Wallet.git
```

2. Собрать и запустить контейнеры:
```sh
docker-compose up -d --build
```
<hr/>

## Дополнительные команды

1. Создание файла миграций:
```sh
docker-compose exec backend alembic revision --autogenerate -m "revision_name"
```

2. Обновление базы данных:
```sh
docker-compose exec app alembic upgrade head
```

3. Остановка контейнеров:
```sh
docker-compose down
```

4. Запуск контейнеров:
```sh
docker-compose up
```

<hr/>
