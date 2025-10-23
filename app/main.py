from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse, JSONResponse
from pymongo import MongoClient

# Подключаемся к MongoDB (имя хоста совпадает с docker-compose)
client = MongoClient("mongodb://admin:adminpass@mongo:27017/")
db = client["srop_db"]
users = db["users"]

app = FastAPI(title="SROP DevOps Project")

# Главная страница
@app.get("/", response_class=HTMLResponse)
def home():
    return """
    <html>
        <head><title>Главная страница</title></head>
        <body style='font-family:Arial; background-color:#f2f2f2;'>
            <h1 style='color:#2c3e50;'>Добро пожаловать в проект SROP DevOps!</h1>
            <p>Это учебное приложение на FastAPI и MongoDB.</p>
            <a href='/about'>О проекте</a> |
            <a href='/users'>Пользователи</a> |
            <a href='/add'>Добавить</a>
        </body>
    </html>
    """

# Страница "О проекте"
@app.get("/about", response_class=HTMLResponse)
def about():
    return """
    <html>
        <body style='font-family:Arial'>
            <h2>О проекте</h2>
            <p>Данный проект создан для СРОП №1: развертывание Python-приложения в Docker.</p>
            <a href='/'>Назад</a>
        </body>
    </html>
    """

# Получение списка пользователей
@app.get("/users")
def get_users():
    result = list(users.find({}, {"_id": 0}))
    return JSONResponse(content=result)

# HTML-форма добавления пользователя
@app.get("/add", response_class=HTMLResponse)
def add_form():
    return """
    <html>
        <body style='font-family:Arial'>
            <h2>Добавить пользователя</h2>
            <form action="/add" method="post">
                Имя: <input type="text" name="name"><br><br>
                Возраст: <input type="number" name="age"><br><br>
                <input type="submit" value="Добавить">
            </form>
            <a href='/'>Назад</a>
        </body>
    </html>
    """

# POST-запрос для добавления
@app.post("/add")
def add_user(name: str = Form(...), age: int = Form(...)):
    users.insert_one({"name": name, "age": age})
    return HTMLResponse(f"""
    <html><body>
        <p>Пользователь {name} добавлен!</p>
        <a href='/users'>Посмотреть всех</a>
    </body></html>
    """)

# Удаление всех пользователей
@app.get("/delete")
def delete_all():
    count = users.delete_many({}).deleted_count
    return {"message": f"Удалено {count} пользователей."}
