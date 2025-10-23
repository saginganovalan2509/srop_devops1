from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse, JSONResponse
from pymongo import MongoClient

# Подключение к MongoDB
client = MongoClient("mongodb://admin:adminpass@mongo:27017/")
db = client["srop_db"]
users = db["users"]

app = FastAPI(title="SROP DevOps Project")

#  Единый стиль
STYLE = """
    <style>
        body { font-family: 'Segoe UI', Tahoma, sans-serif; background-color: #f4f6f8; color: #333; margin: 0; padding: 0; }
        header { background-color: #2c3e50; color: white; padding: 15px; text-align: center; }
        main { padding: 20px; max-width: 700px; margin: auto; }
        a { color: #3498db; text-decoration: none; }
        a:hover { text-decoration: underline; }
        .button { display: inline-block; padding: 8px 14px; margin: 6px 4px; background-color: #3498db; color: white; border-radius: 5px; text-decoration: none; }
        .button:hover { background-color: #2980b9; }
        .delete-btn { background-color: #e74c3c; }
        .delete-btn:hover { background-color: #c0392b; }
        .card { background: white; padding: 15px; margin-top: 10px; border-radius: 10px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }
        input[type="text"], input[type="number"] { width: 100%; padding: 8px; margin-top: 5px; border-radius: 5px; border: 1px solid #ccc; }
        input[type="submit"] { background-color: #2ecc71; color: white; border: none; padding: 10px 16px; border-radius: 5px; margin-top: 10px; cursor: pointer; }
        input[type="submit"]:hover { background-color: #27ae60; }
        form.delete-form { margin-top: 15px; }
        input[type="checkbox"] { margin-right: 8px; }
    </style>
"""

# Главная
@app.get("/", response_class=HTMLResponse)
def home():
    return f"""
    <html><head><title>Главная</title>{STYLE}</head>
    <body>
        <header><h1>SROP DevOps Project</h1></header>
        <main>
            <p>Учебное приложение на FastAPI и MongoDB.</p>
            <a class="button" href="/about">О проекте</a>
            <a class="button" href="/users">Пользователи</a>
            <a class="button" href="/add">Добавить</a>
        </main>
    </body></html>
    """

#  О проекте
@app.get("/about", response_class=HTMLResponse)
def about():
    return f"""
    <html><head><title>О проекте</title>{STYLE}</head>
    <body>
        <header><h1>О проекте</h1></header>
        <main>
            <div class="card">
                <p>Проект srop1</p>
                <p>FastAPI + MongoDB в Docker Compose.</p>
                <a href="/" class="button">Назад</a>
            </div>
        </main>
    </body></html>
    """

# Список пользователей
@app.get("/users", response_class=HTMLResponse)
def get_users():
    all_users = list(users.find({}, {"_id": 0}))
    if not all_users:
        content = "<p>Пока нет пользователей.</p>"
    else:
        content = """
        <form method="post" action="/delete_selected" class="delete-form">
        """
        for u in all_users:
            content += f"""
            <div class="card">
                <input type="checkbox" name="names" value="{u['name']}">
                <strong>{u['name']}</strong> — {u['age']} лет
            </div>
            """
        content += """
            <input type="submit" value="Удалить выбранных" class="delete-btn button">
        </form>
        """

    return f"""
    <html><head><title>Пользователи</title>{STYLE}</head>
    <body>
        <header><h1>Список пользователей</h1></header>
        <main>
            {content}
            <a href="/" class="button">На главную</a>
        </main>
    </body></html>
    """

# Добавление
@app.get("/add", response_class=HTMLResponse)
def add_form():
    return f"""
    <html><head><title>Добавление</title>{STYLE}</head>
    <body>
        <header><h1>Добавить пользователя</h1></header>
        <main>
            <form action="/add" method="post" class="card">
                <label>Имя:</label>
                <input type="text" name="name" required>
                <label>Возраст:</label>
                <input type="number" name="age" required>
                <input type="submit" value="Добавить">
            </form>
            <a href="/" class="button">Назад</a>
        </main>
    </body></html>
    """

# POST: Добавление пользователя
@app.post("/add", response_class=HTMLResponse)
def add_user(name: str = Form(...), age: int = Form(...)):
    users.insert_one({"name": name, "age": age})
    return f"""
    <html><head><title>Добавлен</title>{STYLE}</head>
    <body>
        <header><h1>Успех!</h1></header>
        <main>
            <div class="card">
                <p>Пользователь <strong>{name}</strong> добавлен!</p>
                <a href="/users" class="button">Посмотреть всех</a>
                <a href="/" class="button">На главную</a>
            </div>
        </main>
    </body></html>
    """

# POST: Удаление выбранных пользователей
@app.post("/delete_selected", response_class=HTMLResponse)
async def delete_selected(request: Request):
    form = await request.form()
    selected_names = form.getlist("names")

    if not selected_names:
        message = "Вы не выбрали пользователей для удаления."
    else:
        result = users.delete_many({"name": {"$in": selected_names}})
        message = f"Удалено {result.deleted_count} пользователей."

    return f"""
    <html><head><title>Удаление</title>{STYLE}</head>
    <body>
        <header><h1>Удаление завершено</h1></header>
        <main>
            <div class="card">
                <p>{message}</p>
                <a href="/users" class="button">Назад</a>
                <a href="/" class="button">Главная</a>
            </div>
        </main>
    </body></html>
    """
