from fastapi import FastAPI, HTTPException, Response, Depends
from pydantic import BaseModel
import psycopg2
from urllib import parse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer
import secrets
from datetime import datetime, timedelta
import jwt

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
    allow_origins=["http://localhost:3000"],  # Замените на URL вашего React-приложения
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")

class User(BaseModel):
    username: str
    password: str

class Category(BaseModel):
    name: str
    description: str

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
    cursor.execute(
        '''
        CREATE TABLE IF NOT EXISTS categories (
            id SERIAL PRIMARY KEY,
            name TEXT NOT NULL,
            description TEXT NOT NULL,
            user_id INTEGER REFERENCES users (id) ON DELETE CASCADE
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


def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, 'be5d4b96e6cbd07b9e78ce0290f6bf06327dccc82fa066b3eeb9a8e49478d53f', algorithms=['HS256'])
        username = payload.get('username')
        user = get_user(username)
        if user is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return user
    except jwt.exceptions.DecodeError:
        raise HTTPException(status_code=401, detail="Invalid token")



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

    # Generate JWT token
    token_data = {
        'username': user.username,
        'exp': datetime.utcnow() + timedelta(hours=1)  # Token expiration time
    }
    token = jwt.encode(token_data, 'be5d4b96e6cbd07b9e78ce0290f6bf06327dccc82fa066b3eeb9a8e49478d53f', algorithm='HS256')

    return {'access_token': token, 'token_type': 'bearer'}


@app.post('/categories')
def create_category(category: Category, current_user: User = Depends(get_current_user)):
    conn = psycopg2.connect(**db_config)
    cursor = conn.cursor()
    cursor.execute(
        '''
        INSERT INTO categories (name, description, user_id) VALUES (%s, %s, %s);
        ''', (category.name, category.description, current_user[0])
    )
    conn.commit()
    cursor.close()
    conn.close()
    return {'message': 'Category created successfully'}

@app.get('/categories')
def get_categories(current_user: User = Depends(get_current_user)):
    conn = psycopg2.connect(**db_config)
    cursor = conn.cursor()
    cursor.execute(
        '''
        SELECT * FROM categories WHERE user_id = %s;
        ''', (current_user[0],)
    )
    categories = cursor.fetchall()
    cursor.close()
    conn.close()

    categories_list = []
    for category in categories:
        category_dict = {
            'id': category[0],
            'name': category[1],
            'description': category[2]
        }
        categories_list.append(category_dict)

    return {'categories': categories_list}



@app.options("/login")
def login_options(response: Response):
    response.headers["Allow"] = "POST, OPTIONS"
    return response


if __name__ == '__main__':
    # create_user_table()
    secret_key = secrets.token_hex(32)  # Генерирует случайную строку из 32 байт в шестнадцатеричном формате
    print (secret_key)

    # Здесь вы можете выбрать способ запуска сервера, например, использовать uvicorn:
    # uvicorn.run(app, host='0.0.0.0', port=8000)
