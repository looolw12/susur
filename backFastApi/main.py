from fastapi import FastAPI, HTTPException, Response
from pydantic import BaseModel
import psycopg2
from urllib import parse
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI()

db_url = "postgresql://postgres:123123@localhost:5432/python_db"

# Разбор DATABASE_URL
result = parse.urlparse(db_url)
db_config = {
    "user": result.username,
    "password": result.password,
    "host": result.hostname,
    "port": result.port,
    "database": result.path[1:],
}

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)

class User(BaseModel):
    username: str
    password: str


def create_user_table():
    conn = psycopg2.connect(**db_config)
    cursor = conn.cursor()
    cursor.execute(
        '''
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            username TEXT NOT NULL,
            password TEXT NOT NULL
        );
        '''
    )
    conn.commit()
    cursor.close()
    conn.close()


def get_user(username):
    conn = psycopg2.connect(**db_config)
    cursor = conn.cursor()
    cursor.execute(
        '''
        SELECT * FROM users WHERE username = %s;
        ''', (username,)
    )
    user = cursor.fetchone()
    cursor.close()
    conn.close()
    return user


@app.post('/register')
def register(user: User):
    existing_user = get_user(user.username)
    if existing_user:
        raise HTTPException(status_code=400, detail='User already exists')

    conn = psycopg2.connect(**db_config)
    cursor = conn.cursor()
    cursor.execute(
        '''
        INSERT INTO users (username, password) VALUES (%s, %s);
        ''', (user.username, user.password)
    )
    conn.commit()
    cursor.close()
    conn.close()
    return {'message': 'User registered successfully'}


@app.post('/login')
def login(user: User):
    stored_user = get_user(user.username)
    if not stored_user or stored_user[2] != user.password:
        raise HTTPException(status_code=401, detail='Invalid username or password')

    return {'message': 'Login successful'}

@app.options("/login")
def login_options(response: Response):
    response.headers["Allow"] = "POST, OPTIONS"
    return response

if __name__ == '__main__':
    create_user_table()
    # uvicorn.run(app, host='0.0.0.0', port=8000)
