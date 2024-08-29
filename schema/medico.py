from pydantic import BaseModel, EmailStr
from datetime import time
from typing import List
from model.medico import Medico
from model.horario_medico import HorarioMedico

class CadastrarMedicoSchema(BaseModel):
    """Define os dados necessários para cadastrar um novo médico"""
    nome: str = "Hillary Lopez Stafford"
    email: EmailStr = "hillary.stafford@gmail.com"
    especialidade: str = "Dermatologia"
    crm: str = "206704"
    duracao_consulta: int = 30

class CadastrarHorarioSchema(BaseModel):
    """Define os dados para cadastrar os horários de um médico"""
    medico_id: int = 1
    dia_semana: str = "Segunda-feira"
    hora_inicio_manha: time = time(8, 0)
    hora_fim_manha: time = time(12, 0)
    hora_inicio_tarde: time = time(13, 0)
    hora_fim_tarde: time = time(17, 0)

class MedicoBuscaSchema(BaseModel):
    """Define como deve ser a estrutura que representa a busca"""
    medico_id: str = "1"
    data: str = "2024-08-25"

class ListagemMedicosSchema(BaseModel):
    """Define como uma listagem de médicos será retornada"""
    medicos:List[CadastrarMedicoSchema]

class VisualizarMedicoSchema(BaseModel):
    """Define como um médico será retornado"""
    id: int = 1
    nome: str = "Hillary Lopez Stafford"
    email: EmailStr = "hillary.stafford@gmail.com"
    especialidade: str = "Dermatologia"
    crm: str = "206704"
    duracao_consulta: int = 30

class VisualizarHorarioSchema(BaseModel):
    """Define como um horário será retornado"""
    dia_semana: str = "Segunda-feira"
    hora_inicio_manha: str = "08:00"
    hora_fim_manha: str = "12:00"
    hora_inicio_tarde: str = "13:00"
    hora_fim_tarde: str = "17:00"

class VisualizarContagemMedicosSchema(BaseModel):
    """Define como a contagem de médicos será retornada"""
    contagem: int = 0 

def retornar_medico(medico: Medico):
    """Retorna uma representação do médico seguindo o schema definido"""
    return {
        "id": medico.id,
        "nome": medico.usuario.nome,
        "email": medico.usuario.email,
        "especialidade": medico.especialidade,
        "crm": medico.crm
    }

def retornar_horario(horario: HorarioMedico):
    """Retorna uma representação do horário do médico"""
    return {
        "dia_semana": horario.dia_semana,
        "hora_inicio_manha": horario.hora_inicio_manha.strftime('%H:%M'),
        "hora_fim_manha": horario.hora_fim_manha.strftime('%H:%M'),
        "hora_inicio_tarde": horario.hora_inicio_tarde.strftime('%H:%M'),
        "hora_fim_tarde": horario.hora_fim_tarde.strftime('%H:%M')
    }

def retornar_agendamento(agendamento):
    """Retorna uma representação do agendamento seguindo o schema definido"""
    return {
        "id": agendamento.id,
        "inicio": agendamento.inicio.strftime("%Y-%m-%d %H:%M:%S"),
        "fim": agendamento.fim.strftime("%Y-%m-%d %H:%M:%S"),
        "status": agendamento.status,
        "paciente": {
            "id": agendamento.paciente.id,
            "nome": agendamento.paciente.usuario.nome,
            "email": agendamento.paciente.usuario.email
        }
    }
