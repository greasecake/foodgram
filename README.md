# Foodgram

### Описание
Foodgram - сайт для хранения рецептов пользователей. Для проекта реализована система подписок, фильтрации рецептов, а также возможность добавлять рецепты в избранное и список покупок.

Проект развёрнут на удаленном сервере и доступен по адресу http://51.250.2.248/

### Начало работы
Пособие по установке Docker: https://docs.docker.com/engine/install/

И docker-compose: https://docs.docker.com/compose/install/

Для развертывания приложения, после клонирования репозитория нужно выполнить следующие команды
- cd foodgram-project-react/infra
- docker-compose up -d --build
- docker-compose exec backend python3 foodgram/manage.py migrate --no-input
- docker-compose exec web python3 project/manage.py createsuperuser
- docker-compose exec web python3 project/manage.py loaddata fixtures/ingredients_prepared.json

Автор<br>
Вадим Кужель
