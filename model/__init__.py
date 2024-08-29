from sqlalchemy_utils import database_exists, create_database
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
import os

from model.base import Base
from model.usuario import Usuario
from model.medico import Medico
from model.horario_medico import HorarioMedico
from model.paciente import Paciente
from model.agendamento import Agendamento

db_path = "database/"

if not os.path.exists(db_path):
   # Cria o diretório
   os.makedirs(db_path)

db_url = 'sqlite:///%s/med_meet.sqlite3' % db_path

engine = create_engine(db_url, echo=False)

Session = sessionmaker(bind=engine)

Base.metadata.create_all(engine)
