from model import Base
from sqlalchemy import Column, String, Integer, DateTime
from sqlalchemy.sql import func

class Usuario(Base):
    __tablename__ = 'usuario'

    id = Column(Integer, primary_key=True)
    nome = Column(String(255), nullable=False)
    email = Column(String(255), nullable=False, unique=True)
    data_cadastro = Column(DateTime, default=func.now())

    @classmethod
    def criar_usuario(cls, nome: str, email: str) -> 'Usuario':
        novo_usuario = cls(nome=nome, email=email)
        return novo_usuario