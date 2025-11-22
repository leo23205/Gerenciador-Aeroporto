import random
import math 
import pickle 
import os

# Constante com o nome do arquivo de banco de dados
ARQUIVO_BD_AEROPORTO = 'aeroporto_dados.pkl'

# Dicionário mestre com a estrutura inicial padrão do aeroporto
# Lista de dicionários, cada um representando um voo
DADOS_AEROPORTO = {
    'voos': [
        {'numero': 'JJ3401', 'origem': 'GRU', 'destino': 'GIG', 'status': 'Check-in', 'capacidade': 150, 'passageiros_alocados': 0, 'lista_passageiros': []},
        {'numero': 'LA8002', 'origem': 'BSB', 'destino': 'POA', 'status': 'Check-in', 'capacidade': 100, 'passageiros_alocados': 0, 'lista_passageiros': []},
        {'numero': 'G37856', 'origem': 'FOR', 'destino': 'REC', 'status': 'Embarque', 'capacidade': 120, 'passageiros_alocados': 0, 'lista_passageiros': []},
    ],
    'passageiros_geral': [], # Lista para armazenar todos os passageiros (histórico)
    'filas_atendimento': [], # Lista de listas para as filas dinâmicas
    'proximo_passageiro_id': 1000 # Contador inteiro para gerar IDs únicos
}

def salvar_dados_aeroporto(dados):
    """
    Salva o dicionário completo do aeroporto em um arquivo binário.
    Argumentos:
      - dados (dict): O dicionário mestre do aeroporto.
    Retorno: None
    """
    try:
        # Abre o arquivo em modo de escrita binária ('wb')
        with open(ARQUIVO_BD_AEROPORTO, 'wb') as f:
            pickle.dump(dados, f) # Serializa e salva o dicionário
        print(" Dados do aeroporto salvos com sucesso!")
    except Exception as e:
        print(f"Erro ao salvar dados: {e}")

def carregar_dados_aeroporto():
    """
    Carrega os dados do arquivo. Se não existir, retorna os dados padrão.
    Retorno: dict (O dicionário com os dados do aeroporto)
    """
    # Verifica se o arquivo existe no sistema
    if not os.path.exists(ARQUIVO_BD_AEROPORTO):
        return DADOS_AEROPORTO # Retorna a estrutura padrão se for a primeira vez
    
    try:
        # Abre o arquivo em modo de leitura binária ('rb')
        with open(ARQUIVO_BD_AEROPORTO, 'rb') as f:
            return pickle.load(f) # Deserializa e retorna os dados salvos
    except Exception as e:
        print(f"Erro ao carregar dados (iniciando com padrão): {e}")
        return DADOS_AEROPORTO # Retorna padrão em caso de erro de leitura
    
def encontrar_fila_mais_curta(filas):
    """
    Retorna a sublista (fila) com o menor número de clientes.
    Argumentos:
      - filas (list): Lista de listas contendo as filas de atendimento.
    Retorno: list (A sublista que representa a fila mais vazia)
    """
    if not filas:
        return [] # Retorna lista vazia se não houver filas
    
    #'fila_curta' (Tipo: list) -> Assume que a primeira fila é a menor inicialmente
    fila_curta = filas[0] 

    # Itera sobre cada sublista (fila) dentro da lista principal
    for fila in filas:

        # Compara o tamanho (len) da fila atual com a menor encontrada
        if len(fila) < len(fila_curta):
            fila_curta = fila # Atualiza a referência se achar uma menor
    return fila_curta

def renovar_voo_se_cheio(dados_aeroporto, voo):
    """
    Verifica se o voo lotou. Se sim, remove-o e cria um novo na mesma rota.
    Argumentos:
      - dados_aeroporto (dict): Dicionário mestre.
      - voo (dict): O dicionário do voo específico a verificar.
    Retorno: bool (True se o voo foi renovado, False caso contrário)
    """
    
    # Verifica capacidade (passageiros atuais >= capacidade total)
    if voo['passageiros_alocados'] >= voo['capacidade']:
        print(f"\n ALERTA: O Voo {voo['numero']} atingiu a capacidade máxima e DECOLOU!")
        
        # Remove o dicionário do voo antigo da lista de voos
        dados_aeroporto['voos'].remove(voo)
        
        # Gera um novo número (ex: mantem 'JJ', muda '1234')
        sigla = voo['numero'][:2] 
        novo_numero = f"{sigla}{random.randint(1000, 9999)}"
        
        # Cria um novo dicionário para o voo substituto
        novo_voo = {
            'numero': novo_numero,
            'origem': voo['origem'],
            'destino': voo['destino'],
            'status': 'Check-in', # Novo voo começa vazio e disponível
            'capacidade': voo['capacidade'], # Mantém a mesma capacidade
            'passageiros_alocados': 0,
            'lista_passageiros': []
        }
        
        # Adiciona o novo voo à lista
        dados_aeroporto['voos'].append(novo_voo)
        print(f" Um novo voo foi aberto para substituir: {novo_numero} ({novo_voo['origem']} -> {novo_voo['destino']})")
        return True
    return False

def gerar_passageiro_aleatorio(dados_aeroporto):
    """
    Gera um passageiro fictício e o aloca em um voo disponível.
    
    Retorno:
      - dict: O dicionário do novo passageiro criado.
      - None: Se não houver voos disponíveis.
    """
    nomes = ['Ana', 'Bruno', 'Carla', 'David', 'Elena', 'Felipe', 'Izac', 'Cassio', 'Davi', 'Felipe', 'Caio', 'Gabriel'] 
    sobrenomes = ['Silva', 'Santos', 'Oliveira', 'Pereira']
    
    # 'voos_checkin' (Tipo: list) -> Lista temporária para filtrar voos válidos
    voos_checkin = []
    # Filtra voos elegíveis (Status Check-in e com vagas)
    for voo in dados_aeroporto['voos']:
        if voo['status'] == 'Check-in' and voo['passageiros_alocados'] < voo['capacidade']:
            voos_checkin.append(voo)
    
    if not voos_checkin:
        print("Erro: Nenhum voo ativo disponível.")
        return None

    # Escolhe um voo aleatoriamente da lista filtrada    
    voo_destino = random.choice(voos_checkin)
    
    # Cria o dicionário do passageiro
    novo_passageiro = {
        'id': dados_aeroporto['proximo_passageiro_id'],
        'nome': f"{random.choice(nomes)} {random.choice(sobrenomes)}",
        'cpf': f"{random.randint(100, 999)}.{random.randint(100, 999)}.{random.randint(100, 999)}-{random.randint(10, 99)}",
        'voo_numero': voo_destino['numero'],
        'status_voo': 'Reservado',
        'checkin_status': False
    }
    
    # Atualiza o estado global (banco de dados)
    dados_aeroporto['proximo_passageiro_id'] += 1 # Prepara ID para o próximo
    dados_aeroporto['passageiros_geral'].append(novo_passageiro) # Salva no histórico

    # Atualiza o voo específico
    voo_destino['passageiros_alocados'] += 1
    voo_destino['lista_passageiros'].append(novo_passageiro['id'])
    print(f"Novo passageiro ({novo_passageiro['nome']}) gerado e alocado no Voo {voo_destino['numero']}.")
    
    # Checa se lotou
    renovar_voo_se_cheio(dados_aeroporto, voo_destino)
    
    return novo_passageiro # Retorna o objeto criado

def calcular_filas_necessarias(dados_aeroporto):
    """
    Calcula o número de filas com base nos passageiros em check-in.
    Retorno: int (Número de filas ideal)
    """
    passageiros_em_checkin = 0

    # Soma a demanda total (vagas ocupadas em voos de check-in)
    for voo in dados_aeroporto['voos']:
        if voo['status'] == 'Check-in':
            passageiros_em_checkin += (voo['capacidade'] - voo['passageiros_alocados'])
            
    if passageiros_em_checkin == 0:
        return 1 # Mínimo de 1 fila sempre
    
    # Regra de negócio: 1 fila para cada 100 passageiros
    filas_necessarias = math.ceil(passageiros_em_checkin / 100)
    # 1. Limite Máximo: Não permite mais que 5 filas
    if filas_necessarias > 5:
        return 5
        
    # 2. Limite Mínimo: Não permite menos que 1 fila
    elif filas_necessarias < 1:
        return 1
        
    # 3. Se estiver entre 1 e 5, retorna o valor calculado
    else:
        return filas_necessarias

def realocar_clientes(dados_aeroporto, fila_a_fechar):
    """
    Move todos os clientes da fila_a_fechar para a fila mais curta restante.
    Argumentos:
      - dados_aeroporto (dict): Dicionário mestre.
      - fila_a_fechar (list): A lista de passageiros que será removida.
    Retorno: None
    """

    # 'filas_ativas' (Tipo: list) -> Referência à lista de filas
    filas_ativas = dados_aeroporto['filas_atendimento']
    clientes_realocados = 0

    # 'clientes_a_mover' (Tipo: list) -> Cópia da lista para iterar com segurança
    clientes_a_mover = list(fila_a_fechar) 
    
    if len(filas_ativas) <= 1:
        print("Sistema: Impossível realocar (apenas 1 fila).")
        return 

    for cliente in clientes_a_mover:
        # Encontra a melhor fila entre as restantes (excluindo a última)
        fila_destino = encontrar_fila_mais_curta(filas_ativas[:-1]) 
        fila_destino.append(cliente) # Adiciona o cliente na nova fila
        clientes_realocados += 1
        
    fila_a_fechar.clear() # Limpa a fila original antes de remover
    print(f"Sistema: {clientes_realocados} clientes realocados.")

def ajustar_numero_de_filas(dados_aeroporto):
    """
    Ajusta o tamanho da lista 'filas_atendimento' dinamicamente.
    Retorno: dict (O dicionário de dados atualizado)
    """

    # 'num_necessario' (Tipo: int) -> Cálculo de demanda
    num_necessario = calcular_filas_necessarias(dados_aeroporto)

    # 'num_atual' (Tipo: int) -> Quantas filas existem agora
    num_atual = len(dados_aeroporto['filas_atendimento'])
    
    if num_necessario > num_atual:
        # Abre novas filas se necessário
        for _ in range(num_necessario - num_atual):
            dados_aeroporto['filas_atendimento'].append([]) 
            print(f"Sistema: Nova fila aberta! Total: {len(dados_aeroporto['filas_atendimento'])}")
         
    elif num_necessario < num_atual:
        # Fecha filas excedentes
        for _ in range(num_atual - num_necessario):
            fila_a_fechar = dados_aeroporto['filas_atendimento'][-1] # Pega a última

            if not fila_a_fechar: 
                # Se vazia, apenas remove
                dados_aeroporto['filas_atendimento'].pop()
                print("Sistema: Fila vazia fechada.")
            else:
                # Se cheia, realoca antes de remover
                print("Sistema: Realocando clientes para fechar fila...")
                realocar_clientes(dados_aeroporto, fila_a_fechar)
                dados_aeroporto['filas_atendimento'].pop() # Remove após esvaziar
                print("Sistema: Fila fechada após realocação.")
                break 
    return dados_aeroporto  


def verificar_condicoes_climaticas(dados_aeroporto):
    """
    Simula uma API de clima e gerencia cancelamentos e restaurações.
    Retorno: dict (Dados atualizados)
    """
    print("\n VERIFICANDO CONDIÇÕES METEOROLÓGICAS (SIMULAÇÃO)...")
    
    condicoes = ['Céu Limpo', 'Nublado', 'Chuva Leve', 'Tempestade', 'Neve']
    
    
    voos_alterados = 0
    
    for voo in dados_aeroporto['voos']:

        # Escolhe uma condição climática aleatória da lista
        clima_atual = random.choice(condicoes)
        print(f"-> Voo {voo['numero']} (Destino: {voo['destino']}): {clima_atual}")
        
        # --- LÓGICA DE CANCELAMENTO ---
        # Regra: Cancela se for Tempestade ou Neve
        if clima_atual in ['Tempestade', 'Neve']:
            if voo['status'] != 'CANCELADO':
                # Salva o status atual antes de cancelar para poder restaurar
                voo['status_anterior'] = voo['status'] # Salva backup do status
                voo['status'] = 'CANCELADO'
                print(f"     ALERTA: Voo {voo['numero']} CANCELADO devido ao mau tempo!")
                voos_alterados += 1
                realocar_passageiros_voo_cancelado(dados_aeroporto, voo)
                
        # --- LÓGICA DE RESTAURAÇÃO (Se o tempo estiver bom) ---
        else:
            if voo['status'] == 'CANCELADO':
                #  Restaura o status anterior
                # O .get garante que, se não tiver histórico, volta para 'Check-in'
                status_original = voo.get('status_anterior', 'Check-in')
                voo['status'] = status_original
                print(f"   AVISO: Clima normalizou. Voo {voo['numero']} reativado para '{status_original}'.")
                voos_alterados += 1
            
    if voos_alterados == 0:
        print("\nNenhuma alteração de status necessária.")
    else:
        print(f"\nTotal de alterações (Cancelamentos/Restaurações): {voos_alterados}")
        
    input("\nPressione Enter para continuar...")
    return dados_aeroporto

def simular_avanco_tempo(dados_aeroporto):
    """
    Avança o status dos voos para simular a passagem do tempo.
    Check-in -> Embarque -> Decolou (Renova)
    Retorno: dict (Dados atualizados)
    """
    print("\n SIMULANDO PASSAGEM DE TEMPO...")
    
    # Cria uma cópia da lista para poder modificar a original sem erro de loop
    # Slice [:] cria uma cópia superficial
    for voo in dados_aeroporto['voos'][:]: 
        
        status_antigo = voo['status']
        mudou = False

        # Lógica de Mudança de Status
        if voo['status'] == 'Check-in':
            # Regra: Avança se tiver passageiros ou sorteio (70% chance)
            if voo['passageiros_alocados'] > 0 or random.random() > 0.7:
                voo['status'] = 'Embarque'
                mudou = True
                
        elif voo['status'] == 'Embarque':
            # De Embarque vai para Decolou
            voo['status'] = 'Decolou'
            mudou = True
            
        elif voo['status'] == 'Decolou' or voo['status'] == 'CANCELADO':
            # Se decolou ou foi cancelado, removemos e criamos um novo
            print(f"  Voo {voo['numero']} saiu do pátio ({voo['status']}). Gerando substituto...")
            dados_aeroporto['voos'].remove(voo)
            
            # Gera substituto (lógica similar à renovação)
            sigla = voo['numero'][:2]
            novo_numero = f"{sigla}{random.randint(1000, 9999)}"
            novo_voo = {
                'numero': novo_numero,
                'origem': voo['origem'],
                'destino': voo['destino'],
                'status': 'Check-in', # Começa sempre no Check-in
                'capacidade': voo['capacidade'],
                'passageiros_alocados': 0,
                'lista_passageiros': []
            }
            dados_aeroporto['voos'].append(novo_voo)
            
        if mudou:
            print(f"-> Voo {voo['numero']}: {status_antigo} >>> {voo['status']}")
            
    print("Atualização de status concluída.")
    return dados_aeroporto


def realocar_passageiros_voo_cancelado(dados_aeroporto, voo_cancelado):
    """
    Procura passageiros do voo cancelado e tenta movê-los para o próximo voo disponível.
    """
    print(f" Iniciando realocação automática para passageiros do voo {voo_cancelado['numero']}...")
    
    # 1. Encontrar um voo substituto (Mesma rota, Status Check-in, Com vagas)
    voo_substituto = None
    for voo in dados_aeroporto['voos']:
        # Verifica se é a mesma rota, se não é o mesmo voo cancelado, e se está aceitando gente
        if (voo['origem'] == voo_cancelado['origem'] and 
            voo['destino'] == voo_cancelado['destino'] and
            voo['status'] == 'Check-in' and 
            voo['numero'] != voo_cancelado['numero']):
            
            voo_substituto = voo
            break # Achou o primeiro disponível
            
    if not voo_substituto:
        print(" Não há voos disponíveis para realocação imediata. Passageiros ficarão em espera.")
        # Atualiza o status dos passageiros para avisar que deu ruim
        for passageiro in dados_aeroporto['passageiros_geral']:
            if passageiro['voo_numero'] == voo_cancelado['numero']:
                passageiro['status_voo'] = 'CANCELADO - Aguardando Solução'
        return

    print(f" Voo substituto encontrado: {voo_substituto['numero']} ({voo_substituto['origem']}->{voo_substituto['destino']})")

    # 2. Mover os passageiros
    passageiros_movidos = 0
    
    # Itera sobre todos os passageiros do sistema
    for passageiro in dados_aeroporto['passageiros_geral']:
        if passageiro['voo_numero'] == voo_cancelado['numero']:
            
            # Verifica se cabe no novo voo
            if voo_substituto['passageiros_alocados'] < voo_substituto['capacidade']:
                
                # Atualiza o passageiro
                passageiro['voo_numero'] = voo_substituto['numero']
                passageiro['status_voo'] = 'Realocado'
                
                # Atualiza o voo substituto
                voo_substituto['passageiros_alocados'] += 1
                voo_substituto['lista_passageiros'].append(passageiro['id'])
                
                passageiros_movidos += 1
            else:
                print(f" Voo substituto lotou! Passageiro {passageiro['nome']} ficou de fora.")
                passageiro['status_voo'] = 'CANCELADO - Sem Vaga'

    # Limpa a lista do voo cancelado (já que movemos ou tratamos todos)
    voo_cancelado['passageiros_alocados'] = 0
    voo_cancelado['lista_passageiros'] = []
    
    print(f" Total de passageiros realocados: {passageiros_movidos}")