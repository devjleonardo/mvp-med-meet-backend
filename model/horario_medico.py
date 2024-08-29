from model import Base
from sqlalchemy import Column, Integer, String, ForeignKey, Time
from sqlalchemy.orm import relationship

class HorarioMedico(Base):
    __tablename__ = 'horario_medico'

    id = Column(Integer, primary_key=True)
    dia_semana = Column(String(50))
    hora_inicio_manha = Column(Time)
    hora_fim_manha = Column(Time)
    hora_inicio_tarde = Column(Time)
    hora_fim_tarde = Column(Time)
    medico_id = Column(Integer, ForeignKey('medico.id'))

    medico = relationship("Medico", back_populates="horarios")
