from fastapi import FastAPI, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from passlib.context import CryptContext
from datetime import timedelta, datetime
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from databases import Database
from jose import JWTError, jwt
from fastapi import Depends
from sqlalchemy.orm import Session
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional


# Настройки приложения
SECRET_KEY = "aba3a327e287babf18bec19cb6f4691c78b69ecdeb8860c42a296d2feb271955"  # Замените на свой секретный ключ
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Создание экземпляров FastAPI, SQLAlchemy и OAuth2PasswordBearer
app = FastAPI()

# Разрешить все источники (замените * на список доменов, с которых разрешены запросы)
origins = ["http://localhost:3000"]

# Добавить middleware для обработки CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Base = declarative_base()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Подключение к базе данных
DATABASE_URL = "postgresql://postgres:123123@localhost:5432/python_db"  # Замените на свои настройки
database = Database(DATABASE_URL)
metadata = Base.metadata
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# Модель Pydantic для пользователя
class UserBase(BaseModel):
    username: str


class UserCreate(UserBase):
    password: str


class User(BaseModel):
    id: Optional[int]
    username: str
    hashed_password: Optional[str]

    class Config:
        orm_mode = True
        exclude_unset = True



# Модель пользователя
class UserDB(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)


# Хэширование пароля
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# Функции для работы с пользователями
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


async def get_user(username: str):
    query = UserDB.__table__.select().where(UserDB.username == username)
    user = await database.fetch_one(query)
    return user


async def create_user(user: UserCreate):
    query = UserDB.__table__.insert().values(username=user.username, hashed_password=user.hashed_password)
    user_id = await database.execute(query)
    return user_id


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: timedelta):
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


# Регистрация пользователя
@app.post("/register", response_model=User)
async def register(user: UserCreate, db: Session = Depends(get_db)):
    existing_user = await get_user(user.username)
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    hashed_password = get_password_hash(user.password)
    new_user = UserDB(username=user.username, hashed_password=hashed_password)
    await create_user(new_user)
    return new_user


# Аутентификация и генерация токена доступа
@app.post("/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = await get_user(form_data.username)
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


# Защищенный маршрут
@app.get("/protected")
async def protected_route(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid authentication credentials")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid authentication credentials")
    return {"message": "You are authenticated"}


# Создание таблицы пользователей в базе данных
@app.on_event("startup")
async def startup():
    await database.connect()
    query = """
    CREATE TABLE IF NOT EXISTS users (
        id SERIAL PRIMARY KEY,
        username VARCHAR(50) UNIQUE NOT NULL,
        hashed_password VARCHAR(100) NOT NULL
    )
    """
    await database.execute(query)


@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()
