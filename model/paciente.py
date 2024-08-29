from model import Base
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

class Paciente(Base):
    __tablename__ = 'paciente'

    id = Column(Integer, primary_key=True)
    cpf = Column(String(255), nullable=False, unique=True)
    endereco = Column(String(50), nullable=False)    
    usuario_id = Column(Integer, ForeignKey("usuario.id"), nullable=False)

    usuario = relationship("Usuario")
    agendamentos = relationship("Agendamento", back_populates="paciente")