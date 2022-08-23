import sqlite3
from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates

app = FastAPI()
templates = Jinja2Templates(directory="templates")

connection = sqlite3.connect('app.db')
connection.row_factory = sqlite3.Row
cursor = connection.cursor()

cursor.execute("SELECT * from crypto")
rows = cursor.fetchall()

@app.get("/")
def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request, "Cryptos": rows})