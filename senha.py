import secrets
import hashlib
import pickle
import time 

#Nome do arquivo onde os dados do administrador serão armazenados
# tipo: str
ARQUIVO_DADOS = 'admin_data.pkl'
# Tempo(em segundos) para o qual o token de 2FA é válido
# tipo: int
TEMPO_EXPIRACAO_TOKEN = 60 # Token expira em 60 segundos (constante)


def criar_hash_senha(senha):
    """
    Recebe uma senha em texto e retorna o hash SHA-256 em hexadecimal.

    Args:
        senha (str): senha em texto puro.

    Returns:
        str: hash hexadecimal SHA-256 da senha.
    """
    senha_em_bytes = senha.encode('utf-8') # converte string para bytes
    hash_senha = hashlib.sha256(senha_em_bytes).hexdigest()
    return hash_senha


def carregar_dados():
    """
    Carrega os dados do arquivo pickle. Se não existir, retorna dados padrão.

    Returns:
        dict: dicionário com a estrutura do administrador:
            {
                'usuario': str,
                'senha_hash': str,
                'token_temp': Optional[str],
                'token_expira_em': float (timestamp)
            }
    """
    try:
        with open(ARQUIVO_DADOS, 'rb') as f:
            dados = pickle.load(f)

            # Assegura que os campos de token existam (compatibilidade/atualização)
            dados.setdefault('token_temp', None)
            dados.setdefault('token_expira_em', 0.0)
            return dados
    except FileNotFoundError:
        
        # Se não houver arquivo, inicializa dados padrão com senha padrão (hash)
        senha_padrao = "admin123"
        return {
            'usuario': 'admin',
            'senha_hash': criar_hash_senha(senha_padrao),
            'token_temp': None,
            'token_expira_em': 0.0 # Campo para armazenar o momento de expiração
        }

def salvar_dados(admin_data):
    """
    Persiste o dicionário admin_data no arquivo ARQUIVO_DADOS usando pickle.

    Args:
        admin_data (dict): dicionário com os dados do administrador a serem salvos.

    Returns:
        None
    """
    with open(ARQUIVO_DADOS, 'wb') as f:
        pickle.dump(admin_data, f)
    print("Dados salvos com sucesso.")


def gerar_token_temporario(admin_data):
    """
    Gera um token temporário (hex de 3 bytes, 6 caracteres hexadecimais),
    armazena o token e o timestamp de expiração em admin_data, e retorna o token.

    Args:
        admin_data (dict): dicionário do administrador onde o token será gravado.

    Returns:
        str: token gerado (hexadecimal).
    """
    token = secrets.token_hex(3) 
    
    # Armazena o token e o momento de expiração no dicionário
    admin_data['token_temp'] = token            # tipo: str
    admin_data['token_expira_em'] = time.time() + TEMPO_EXPIRACAO_TOKEN # tipo: float (timestamp)
    
    return token

def autenticacao_token(admin_data):
    """
    Realiza a autenticação de 2 fatores baseada em token temporário.

    Fluxo resumido:
    - Gera um token novo a cada tentativa.
    - Mostra o token (simulação de envio).
    - Verifica se token informado bate com o gerado e ainda não expirou.
    - Limita o número de tentativas.

    Args:
        admin_data (dict): dicionário com estado atual do administrador.

    Locais/Tipos usados internamente:
        MAX_TENTATIVAS_TOKEN (int)
        tentativas (int)
        token_gerado (str)
        token_input (str)
        tempo_atual (float)

    Returns:
        tuple[bool, dict]:
            - bool: True se autenticação de 2FA bem-sucedida, False caso contrário.
            - dict: admin_data possivelmente atualizado (token e expiração).
    """
    MAX_TENTATIVAS_TOKEN = 3 # Define o número máximo de tentativas
    tentativas = 0

    while tentativas < MAX_TENTATIVAS_TOKEN:
        
        # 1. Gera e exibe um novo token a cada tentativa
        token_gerado = gerar_token_temporario(admin_data)
        print(f"\n--- TENTATIVA {tentativas + 1}/{MAX_TENTATIVAS_TOKEN} ---")
        print(f"Token de 2 Fatores (válido por {TEMPO_EXPIRACAO_TOKEN} segundos): {token_gerado}")

        token_input = input("Digite o token recebido: ") # tipo: str
        
        # Captura o tempo no momento da verificação
        tempo_atual = time.time() # tipo: float (timestamp)
        
        # 2. Verifica a validade (token correto E não expirado)
        if token_input == token_gerado and tempo_atual < admin_data['token_expira_em']:
            print("Autenticação de 2 Fatores bem-sucedida.")
            return True, admin_data
        
        # 3. Lógica de Falha: Incrementa a tentativa e notifica o motivo
        else:
            tentativas += 1
            
            if tempo_atual >= admin_data['token_expira_em']:
                
                # Token expirou antes do usuário digitar
                print("Token inválido. O tempo de validade expirou. Gerando novo token...")
            else:
                
                # Token informado não corresponde ao gerado
                print("Token incorreto. Gerando novo token...")
    
    # Excedeu tentativas permitidas
    print("Acesso negado por tentativas excessivas no token.")
    return False, admin_data


def login_administracao():
    """
    Gerencia o fluxo de login principal + 2FA.

    Fluxo:
    - Carrega os dados do admin (carregar_dados).
    - Solicita usuário e senha principal (até 3 tentativas).
    - Se a senha principal estiver correta, chama autenticacao_token para 2FA.

    Variáveis locais:
        admin_data (dict)
        tentativas (int)
        usuario_input (str)
        senha_input (str)
        senha_input_hash (str)

    Returns:
        tuple[bool, dict]:
            - bool: True se todo o processo (senha + 2FA) for bem-sucedido, False caso contrário.
            - dict: admin_data atualizado.
    """
    
    admin_data = carregar_dados()
    tentativas = 3

    while tentativas > 0:
        usuario_input = input("Digite o nome de usuário do administrador: ") # tipo: str
        senha_input = input("Digite a senha do administrador: ") # tipo: str

        senha_input_hash = criar_hash_senha(senha_input) # tipo: str

        if (usuario_input == admin_data['usuario'] and
                senha_input_hash == admin_data['senha_hash']):
            
            print("Senha principal verificada. Próxima etapa: Autenticação de 2 Fatores.")
            
            # SEGUNDA ETAPA: Autenticação de 2 Fatores
            acesso_permitido, admin_data_atualizado = autenticacao_token(admin_data) 

            if acesso_permitido:
                
                # Retorna True para acesso liberado e os dados atualizados
                return True, admin_data_atualizado 
            else:
                
                # Falha no 2FA
                return False, admin_data_atualizado
        
        else:
            
            # Credenciais principais incorretas: reduz contador de tentativas
            tentativas -= 1
            print(f"Credenciais inválidas. Tentativas restantes: {tentativas}")

    print("Número máximo de tentativas atingido. Acesso negado.")
    return False, admin_data


    

