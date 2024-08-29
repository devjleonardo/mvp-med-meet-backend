from pydantic import BaseModel
from datetime import datetime
from typing import List
from model.agendamento import Agendamento

class CadastrarAgendamentoSchema(BaseModel):
    """Define como um novo agendamento deve ser cadastrado"""
    paciente_nome: str = "Rodrigo Thales de Brito"
    medico_nome: str = "Hillary Lopez Stafford"
    data: str = "2024-08-25"
    horario: str = "14:30"

class VisualizarAgendamentoSchema(BaseModel):
    """Define como um agendamento será retornado"""
    id: int = 1
    paciente_nome: str = "Rodrigo Thales de Brito"
    medico_nome: str = "Hillary Lopez Stafford"
    inicio: datetime = "2024-08-25T14:30:00"
    fim: datetime = "2024-08-25T15:00:00"

class ListagemAgendamentosSchema(BaseModel):
    """Define como uma listagem de agendamentos será retornada"""
    agendamentos: List[VisualizarAgendamentoSchema]

class VisualizarContagemAgendamentosSchema(BaseModel):
    """Define como a contagem de agendamentos será retornada."""
    contagem: int = 0

def retornar_agendamento(agendamento: Agendamento):
    """Retorna uma representação do agendamento seguindo o schema definido"""
    return {
        "id": agendamento.id,
        "paciente_nome": agendamento.paciente.usuario.nome,
        "medico_nome": agendamento.medico.usuario.nome,
        "inicio": agendamento.inicio,
        "fim": agendamento.fim,
    }
