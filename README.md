# Социальная сеть блогеров “Yatube”.

### Разработан fullstack сайт, в котором реализован функционал регистрации пользователей, публикации и редактирования постов (с изображениями), подписки на других авторов и комментирования публикаций.
___
Для развёртывания проекта необходимо выполнить следующие команды:
 ```
git clone https://github.com/altvik2503/hw05_final.git
cd hw05_final/
python -m venv venv
. venv/scripts/activate
pip install -r requirements.txt
python yatube/manage.py migrate
python yatube/manage.py runserver
```
После этого сайт будет доступен по локальному адресу 127.0.0.1
___
### Действующий сайт развёрнут по адресу http://altvik.pythonanywhere.com/
___
Приложение написано на языке Python версии 3.7.9 и имеет следующе зависимости:
```
Django==2.2.19
Pillow==8.3.1
pytz==2022.7
sorl-thumbnail==12.7.0
sqlparse==0.4.3
python-dotenv-0.21.0
```
___
В проекте используются технологии

*Django ORM, Bootstrap, CSS*
