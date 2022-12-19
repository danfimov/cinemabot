# Cinemabot

Проект бота, предназначенного для поиска фильмов по названию. 

Бот доступен в Telegram под ником [@anfimov_cinema_bot](https://t.me/anfimov_cinema_bot).


## Run Locally

Склонируйте код проекта

```bash
  git clone https://gitlab.manytask.org/python/students-fall-2022/danfimov.git
```

Перейдите в директорию с проектом

```bash
  cd 13.3.HW3/cinemabot
```

Установите [Poetry](https://python-poetry.org/). Подробнее об установке можно почитать в [официальной документации Poetry](https://python-poetry.org/docs/#installation).

```bash
  curl -sSL https://install.python-poetry.org | python3 -
```

Установите зависимости

```bash
  poetry install 
```

Создайте файл `.env` с необходимыми переменными для работы бота и базы данных

```bash
# Env variables example
BOT_TOKEN="<your_bot_token>"  # from BotFather
KINOPOISK_API_KEY="<your_token>"  # from kinopoiskapiunofficial.tech/
POSTGRES_USER="cinemabot_admin"
POSTGRES_PASSWORD="password"
POSTGRES_DB="cinemabot_db"
```

Запустите базу данных с помощью [docker-compose](https://docs.docker.com/compose/)

```bash
  make db
```

Запустите миграции, чтобы создать в базе необходимые сущности

```bash
  make migrate
```

Запустите бота

```bash
  make run
```


## Roadmap

- [] Поддержка стандартного флоу: поиск фильма - далее/подробнее/стоп, история поиска и статистика показов фильмов;
- [x] Внедрение alembic для комфортной работы с изменениями в базе данных;
- [] Замена MemoryStorage на Redis;
- [] Деплой робота в Yandex Cloud;
- [] Ориентирование на язык пользователя: поддержка вывода описания на русском или английском языках в зависимости от языка в приложении;
- [] Добавление дополнительных источников информации о фильмах помимо неофициального API Кинопоиска;
- [] Настройка полей в выдаче поиска для каждого пользователя через хранение информации в State;
