from model import Base
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

class Medico(Base):
    __tablename__ = 'medico'

    id = Column(Integer, primary_key=True)
    especialidade = Column(String(255), nullable=False)
    crm = Column(String(50), nullable=False, unique=True)    
    duracao_consulta = Column(Integer)
    usuario_id = Column(Integer, ForeignKey("usuario.id"), nullable=False)

    usuario = relationship("Usuario")
    horarios = relationship("HorarioMedico", back_populates="medico")
    agendamentos = relationship("Agendamento", back_populates="medico")



    