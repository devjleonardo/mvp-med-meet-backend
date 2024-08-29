from pydantic import BaseModel, EmailStr
from typing import List
from model.paciente import Paciente

class CadastrarPacienteSchema(BaseModel):
    """Define os dados necessários para cadastrar um novo paciente"""
    nome: str = "Rodrigo Thales de Brito"
    email: EmailStr = "rodrigo.thales@gmail.com"
    cpf: str = "625.267.307-24"
    endereco: str = "Rua Brandão Borges, 689, Londrina - PR"

class ListagemPacientesSchema(BaseModel):
    """Define como uma listagem de pacientes será retornada"""
    pacientes:List[CadastrarPacienteSchema]

class VisualizarPacienteSchema(BaseModel):
    """Define como um paciente será retornado"""
    id: int = 1
    nome: str = "Rodrigo Thales de Brito"
    email: EmailStr = "rodrigo.thales@gmail.com"
    cpf: str = "625.267.307-24"
    endereco: str = "Rua Brandão Borges, 689, Londrina - PR"

class VisualizarContagemPacientesSchema(BaseModel):
    """Define como a contagem de pacientes será retornada."""
    contagem: int = 0

def retornar_paciente(paciente: Paciente):
    """Retorna uma representação do paciente seguindo o schema definido"""
    return {
        "id": paciente.id,
        "nome": paciente.usuario.nome,
        "email": paciente.usuario.email,
        "cpf": paciente.cpf,
        "endereco": paciente.endereco
    }
