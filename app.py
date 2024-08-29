from flask_openapi3 import Info, OpenAPI, Tag
from flask_cors import CORS
from flask import jsonify, request
from schema import *
from model import *
from constants import ErrorMessages
from logger import logger
from sqlalchemy.exc import IntegrityError
from urllib.parse import unquote
from sqlalchemy import func
import calendar
import locale
from datetime import datetime, timedelta

info = Info(
    title="Med Meet API",
    version="1.0.0",
    description="API para o gerenciamento de médicos, pacientes e agendamentos. Permite cadastrar, visualizar, remover médicos e pacientes, além de gerenciar horários e agendamentos."
)

app = OpenAPI(__name__, info=info)
CORS(app)

medico_tag = Tag(name="Médico", description="Cadastro e visualização de médicos")
paciente_tag = Tag(name="Paciente", description="Cadastro e visualização de pacientes")
agendamento_tag = Tag(name="Agendamento", description="Cadastro e visualização de agendamentos")

@app.get('/medicos', tags=[medico_tag],
         responses={"200": ListagemMedicosSchema, "400": ErrorSchema})
def listar_medicos():
    """
    Obtenha a lista completa de médicos cadastrados

    Retorna informações como nome, especialidade, CRM, duração das consultas e horários de atendimento de todos os médicos cadastrados
    """
    session = Session()
    try:
        # Lista todos os médicos cadastrados
        medicos = session.query(Medico).all()

        # Converte a lista de médicos para DTO
        medicos_dto = [retornar_medico(medico) for medico in medicos]

        # Retorna em formato JSON a lista de médicos 
        return jsonify(medicos_dto), 200
    except Exception as e:
        logger.error(f"Erro ao listar médicos: {str(e)}")
        return jsonify({"message": str(e)}), 400
    finally:
        session.close()

@app.post('/medicos', tags=[medico_tag],
          responses={"200": VisualizarMedicoSchema, "400": ErrorSchema})
def cadastrar_medico(form: CadastrarMedicoSchema):
    """
    Cadastre um novo médico no sistema

    É necessário fornecer nome, email, especialidade, CRM e duração da consulta. O CRM e o email devem ser únicos
    """
    session = Session()
    try:
        # Verifica se o email já está em uso
        if session.query(Usuario).filter_by(email=form.email).first():
            logger.info(f"O email {form.email} já está em uso.")
            raise ValueError(ErrorMessages.ERRO_EMAIL_DUPLICADO)
        
        # Verifica se o CRM já está em uso
        if session.query(Medico).filter_by(crm=form.crm).first():
            logger.info(f"O CRM {form.crm} já está em uso.")
            raise ValueError(ErrorMessages.ERRO_CRM_DUPLICADO)

        # Cria um novo usuário
        usuario = Usuario(nome=form.nome, email=form.email)
        session.add(usuario)
        session.flush()

        # Cria um novo médico relacionando com o usuário
        medico = Medico(especialidade=form.especialidade, duracao_consulta=form.duracao_consulta, crm=form.crm, usuario_id=usuario.id)
        session.add(medico)
        session.flush()

        # Confirma as operações no banco
        session.commit()

        # Retorna em formato JSON os dados do médico cadastrado 
        return jsonify(retornar_medico(medico)), 200

    except IntegrityError as e:
        session.rollback()
        logger.error(f"Erro ao cadastrar médico: {e}")
        return jsonify({"message": ErrorMessages.ERRO_DADOS_INVALIDOS}), 400
    except ValueError as e:
        session.rollback()
        logger.error(f"Erro ao cadastrar médico: {str(e)}")
        return jsonify({"message": str(e)}), 400
    except Exception as e:
        session.rollback()
        logger.error(f"Erro inesperado ao cadastrar médico: {str(e)}")
        return jsonify({"message": str(e)}), 400
    finally:
        session.close()
        print("Sessão fechada.")

@app.post('/medicos/horarios', tags=[medico_tag], responses={"200": VisualizarHorarioSchema, "400": ErrorSchema})
def cadastrar_horario_medico(form: CadastrarHorarioSchema):
    """
    Cadastre horários de atendimento para um médico

    Associe os horários de atendimento ao médico com base no ID fornecido
    """
    session = Session()
    try:
        # Verifica se o médico existe no banco
        medico = session.query(Medico).filter_by(id=form.medico_id).first()
        if not medico:
            logger.info(f"Médico com o ID {form.medico_id} não existe.")
            raise ValueError("Médico não encontrado.")

        # Cria um novo horário para o médico com base nos dados do form
        horario_medico = HorarioMedico(
            dia_semana=form.dia_semana,
            hora_inicio_manha=form.hora_inicio_manha,
            hora_fim_manha=form.hora_fim_manha,
            hora_inicio_tarde=form.hora_inicio_tarde,
            hora_fim_tarde=form.hora_fim_tarde,
            medico_id=medico.id
        )

        # Adiciona e confirma as operações do horário do médico no banco 
        session.add(horario_medico)
        session.commit()

        # Retorna em formato JSON uma mensagem de sucesso
        return jsonify({"message": "Horário cadastrado com sucesso"}), 200

    except ValueError as e:
        session.rollback()
        logger.error(f"Erro ao cadastrar horário: {str(e)}")
        return jsonify({"message": str(e)}), 400
    except Exception as e:
        session.rollback()
        logger.error(f"Erro inesperado ao cadastrar horário: {str(e)}")
        return jsonify({"message": str(e)}), 400
    finally:
        session.close()
        print("Sessão fechada.")


@app.get('/medicos/agenda', tags=[medico_tag],
         responses={"200": VisualizarAgendamentoSchema, "400": ErrorSchema})
def visualizar_agenda_medico(query: MedicoBuscaSchema):
    """
    Visualize a agenda de um médico para um dia específico

    Retorna a agenda completa, mostrando horários disponíveis e ocupados.
    """
    try:
        # Define a formatação de datas em português
        locale.setlocale(locale.LC_TIME, 'pt_BR.utf8')
    except locale.Error:
        # Retorna em formato JSON um erro caso a localidade não seja suportada
        return jsonify({"error": "Locale pt_BR.utf8 não suportado no sistema."}), 500
    
    # Descodifica e formata o ID do médico e a data
    medico_id = unquote(unquote(query.medico_id))
    data = unquote(unquote(query.data))
    data_obj = datetime.strptime(data, '%Y-%m-%d')
    dia_semana = calendar.day_name[data_obj.weekday()]

    session = Session()

    try:
        # Verifica se o médico existe no banco
        medico = session.query(Medico).filter_by(id=medico_id).one()

        # Busca os horários disponíveis do médico para o dia específico
        horarios_medico = session.query(HorarioMedico).filter(
            HorarioMedico.medico_id == medico_id,
            func.lower(HorarioMedico.dia_semana).like(f"%{dia_semana.lower()}%")
        ).all()

        logger.info(f"horarios_medico: {horarios_medico}")

        # Busca os agendamentos do médico para a data específica
        agendamentos = session.query(Agendamento).filter(
            Agendamento.medico_id == medico_id,
            func.date(Agendamento.inicio) == data_obj.date()
        ).all()

        # Gera a agenda completa do médico, combinando horários e agendamentos
        agenda = gerar_agenda(horarios_medico, agendamentos, medico.duracao_consulta, data_obj)

        # Retorna em formato JSON a agenda completa 
        return jsonify(agenda), 200
    except Exception as e:
        logger.error(f"Erro ao visualizar agenda: {str(e)}")
        return jsonify({"error": str(e)}), 500
    finally:
        session.close()

def gerar_agenda(horarios_medico, agendamentos, duracao_consulta, data_obj):
    agenda = []
    for horario in horarios_medico:
         # Gera slots para o período da manhã
        inicio = datetime.combine(data_obj.date(), horario.hora_inicio_manha)
        fim = datetime.combine(data_obj.date(), horario.hora_fim_manha)
        agenda += gerar_slots_agenda(inicio, fim, duracao_consulta, agendamentos)

        # Gera slots para o período da tarde
        inicio = datetime.combine(data_obj.date(), horario.hora_inicio_tarde)
        fim = datetime.combine(data_obj.date(), horario.hora_fim_tarde)
        agenda += gerar_slots_agenda(inicio, fim, duracao_consulta, agendamentos)

    return agenda

def gerar_slots_agenda(inicio, fim, duracao_consulta, agendamentos):
    """
    Gera os slots de horários para consultas.

    Cria slots de tempo para consultas médicas e verifica se estão disponíveis ou ocupados.
    """
    slots = []
    while inicio + timedelta(minutes=duracao_consulta) <= fim:
        slot_inicio = inicio
        slot_fim = inicio + timedelta(minutes=duracao_consulta)

        slot = {
            "inicio": slot_inicio.time().strftime('%H:%M'),
            "fim": slot_fim.time().strftime('%H:%M'),
            "ocupado": False,
            "agendamentoId": None
        }

        for agendamento in agendamentos:
            agendamento_inicio = agendamento.inicio
            agendamento_fim = agendamento.fim

            if agendamento_inicio <= slot_inicio and agendamento_fim >= slot_fim:
                slot['ocupado'] = True
                slot['agendamentoId'] = agendamento.id
                break

        slots.append(slot)
        inicio += timedelta(minutes=duracao_consulta)
    
    return slots

@app.get('/pacientes', tags=[paciente_tag],
         responses={"200": ListagemPacientesSchema, "400": ErrorSchema})
def listar_pacientes():
    """
    Obtenha a lista completa de pacientes cadastrados

    Retorna informações como nome, CPF e endereço de todos os pacientes cadastrados
    """
    session = Session()
    try:
        # Lista todos os pacientes cadastrados
        pacientes = session.query(Paciente).all()

        # Converte a lista de pacientes para DTO
        pacientes_dto = [retornar_paciente(paciente) for paciente in pacientes]

        # Retorna em formato JSON a lista de pacientes 
        return jsonify(pacientes_dto), 200
    except Exception as e:
        return jsonify({"message": str(e)}), 400
    finally:
        session.close()

@app.post('/pacientes', tags=[paciente_tag],
          responses={"200": VisualizarPacienteSchema, "400": ErrorSchema})
def cadastrar_paciente(form: CadastrarPacienteSchema):
    """
    Cadastre um novo paciente no sistema

    É necessário fornecer nome, email, CPF e endereço. O CPF e o email devem ser únicos
    """
    session = Session()
    try:
        # Verifica se o email já está em uso
        if session.query(Usuario).filter_by(email=form.email).first():
            logger.info(f"O email {form.email} já está em uso.")
            raise ValueError(ErrorMessages.ERRO_EMAIL_DUPLICADO)
        
        # Verifica se o CPF já está em uso
        if session.query(Paciente).filter_by(cpf=form.cpf).first():
            logger.info(f"O CPF {form.cpf} já está em uso.")
            raise ValueError(ErrorMessages.ERRO_CPF_DUPLICADO)

        # Cria um novo usuário
        usuario = Usuario(nome=form.nome, email=form.email)
        session.add(usuario)
        session.flush()
        print("Usuário criado com sucesso:", usuario)

        # Cria um novo paciente relacionando com o usuário
        paciente = Paciente(cpf=form.cpf, endereco=form.endereco, usuario_id=usuario.id)
        session.add(paciente)

        # Confirma as operações no banco
        session.commit()

        # Retorna em formato JSON os dados do paciente cadastrado 
        return retornar_paciente(paciente), 200
    
    except IntegrityError as e:
        session.rollback()
        logger.error(f"Erro ao cadastrar paciente: {ErrorMessages.ERRO_DADOS_INVALIDOS}")
        return jsonify({"message": ErrorMessages.ERRO_DADOS_INVALIDOS}), 400
    except ValueError as e:
        session.rollback()
        logger.error(f"Erro ao cadastrar paciente: {str(e)}")
        return jsonify({"message": str(e)}), 400
    except Exception as e:
        session.rollback()
        logger.error(f"Erro inesperado ao cadastrar paciente: {str(e)}")
        return jsonify({"message": str(e)}), 400
    finally:
        session.close()
        print("Sessão fechada.")


@app.get('/pacientes/buscar', tags=[paciente_tag],
         responses={"200": VisualizarPacienteSchema, "400": ErrorSchema})
def buscar_paciente_por_nome():
    """
    Busca paciente por nome.
    
    Permite buscar pacientes cadastrados no sistema com através do nome
    """

    # Extrai o nome do paciente a partir do parâmetros da requisição
    nome = request.args.get('nome', '').strip()
    
    # Retorna uma lista vazia se o nome não for fornecido
    if len(nome) < 1:
        return jsonify([]), 200 

    session = Session()

    try:
        # Busca pacientes por nome
        pacientes = session.query(Paciente).join(Usuario).filter(
            Usuario.nome.ilike(f"%{nome}%")
        ).limit(10).all()
        
        # Verifica se algum paciente foi encontrado
        if not pacientes:
            logger.info(f"Nenhum paciente encontrado com o nome: {nome}")
        
        # Converte os resultados em uma lista de dicionários para retorno
        resultados = [retornar_paciente(paciente) for paciente in pacientes]

        # Retorna em formato JSON a lista de pacientes encontrados 
        return jsonify(resultados), 200
    
    except Exception as e:
        logger.error(f"Erro ao buscar pacientes: {str(e)}")
        return jsonify({"message": str(e)}), 400
    finally:
        session.close()

@app.post('/agendamentos', tags=[agendamento_tag],
          responses={"200": VisualizarAgendamentoSchema, "400": ErrorSchema})
def cadastrar_agendamento(form: CadastrarAgendamentoSchema):
    """
    Cadastre um novo agendamento
    
    Forneça o nome do paciente, nome do médico, data e horário do agendamento
    """
    session = Session()
    try:
        # Verifica se o paciente existe
        paciente = session.query(Paciente).join(Usuario).filter(Usuario.nome == form.paciente_nome).first()
        if not paciente:
            logger.info(f"Paciente com o nome {form.paciente_nome} não existe.")
            raise ValueError(f"Paciente '{form.paciente_nome}' não encontrado.")

        # Verifica se o médico existe
        medico = session.query(Medico).join(Usuario).filter(Usuario.nome == form.medico_nome).first()
        if not medico:
            logger.info(f"Médico com o nome {form.medico_nome} não existe.")
            raise ValueError(f"Médico '{form.medico_nome}' não encontrado.")

        # Converte data e horário em um objeto datetime
        data_hora = datetime.strptime(f"{form.data} {form.horario}", "%Y-%m-%d %H:%M")

        # Cria um novo agendamento relacionando médico e paciente
        agendamento = Agendamento(
            inicio=data_hora,
            fim=data_hora + timedelta(minutes=medico.duracao_consulta),
            medico_id=medico.id,
            paciente_id=paciente.id
        )

        # Adiciona e confirma as operações do agendamento no banco 
        session.add(agendamento)
        session.commit()

        # Retorna em formato JSON uma mensagem de sucesso
        return jsonify({"message": "Agendamento realizado com sucesso."}), 200

    except ValueError as ve:
        session.rollback()
        print(f"Erro ao cadastrar agendamento: {str(ve)}")
        return jsonify({"message": str(ve)}), 400
    except Exception as e:
        session.rollback()
        return jsonify({"message": f"Erro ao criar agendamento: {str(e)}"}), 400
    finally:
        session.close()


@app.post('/agendamentos/ver', tags=[agendamento_tag], responses={"200": VisualizarAgendamentoSchema, "400": ErrorSchema})
def ver_agendamento():
    """
    Veja detalhes de um agendamento.

    Retorna os detalhes de um agendamento específico, incluindo o nome do paciente, nome do médico e horário.
    """
    data = request.json
    agendamento_id = data.get('agendamento_id')
    
    # Verifica se o ID do agendamento foi passaddo
    if not agendamento_id:
        return jsonify({"message": "ID do agendamento não fornecido"}), 400

    session = Session()
    try:
        # Busca o agendamento no banco de dados pelo ID
        agendamento = session.query(Agendamento).filter_by(id=agendamento_id).first()
        if not agendamento:
            return jsonify({"message": "Agendamento não encontrado"}), 404

        # Retorna em formato JSON os detalhes do agendamento 
        return jsonify({
            "paciente_nome": agendamento.paciente.usuario.nome,
            "medico_nome": agendamento.medico.usuario.nome,
            "inicio": agendamento.inicio.isoformat(),
            "fim": agendamento.fim.isoformat(),
        }), 200
    except Exception as e:
        session.rollback()
        return jsonify({"message": f"Erro ao obter agendamento: {str(e)}"}), 500
    finally:
        session.close()

@app.get('/medicos/contagem', tags=[medico_tag], responses={"200": VisualizarContagemMedicosSchema, "400": ErrorSchema})
def contagem_medicos():
    """
    Obtenha o número total de médicos cadastrados

    Retorna a contagem total de médicos registrados no sistema
    """
    session = Session()
    try:
        # Consulta o total de médicos cadastrados no banco
        total_medicos = session.query(Medico).count()

        # Retorna em formato JSON a contagem de médicos 
        return jsonify({"contagem": total_medicos})
    finally:
        session.close()

@app.get('/pacientes/contagem', tags=[paciente_tag], responses={"200": VisualizarContagemPacientesSchema, "400": ErrorSchema})
def contagem_pacientes():
    """
    Obtenha o número total de pacientes cadastrados

    Retorna a contagem total de pacientes registrados no sistema
    """
    session = Session()
    try:
        # Consulta o total de pacientes cadastrados no banco
        total_pacientes = session.query(Paciente).count()

        # Retorna em formato JSON a contagem de pacientes 
        return jsonify({"contagem": total_pacientes})
    finally:
        session.close()

@app.get('/agendamentos/hoje/contagem', tags=[agendamento_tag], responses={"200": VisualizarContagemAgendamentosSchema, "400": ErrorSchema})
def contagem_agendamentos_hoje():
    """
    Obtenha o número total de agendamentos para hoje

    Retorna a contagem de agendamentos realizados para o dia atual
    """
    session = Session()
    try:
        # Pega a data atual
        today = datetime.today().date()

        # Consulta o total de agendamentos para a data de hoje no banco de dados
        total_agendamentos = session.query(Agendamento).filter(func.date(Agendamento.inicio) == today).count()

        # Retorna em formato JSON a contagem de agendamentos
        return jsonify({"contagem": total_agendamentos})
    finally:
        session.close()
