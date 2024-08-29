from model import Base
from sqlalchemy import Column, Integer, DateTime, String, ForeignKey
from sqlalchemy.orm import relationship

class Agendamento(Base):
    __tablename__ = 'agendamento'

    id = Column(Integer, primary_key=True)
    medico_id = Column(Integer, ForeignKey('medico.id'), nullable=False)
    paciente_id = Column(Integer, ForeignKey('paciente.id'), nullable=False)
    inicio = Column(DateTime, nullable=False)
    fim = Column(DateTime, nullable=False)
    status = Column(String(50), default='confirmado')

    medico = relationship("Medico", back_populates="agendamentos")
    paciente = relationship("Paciente", back_populates="agendamentos")
