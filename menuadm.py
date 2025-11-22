# Importa a função de segurança para troca de senha (gera o hash SHA-256)
from senha import criar_hash_senha 

# Importa funções do simulador de filas para integração com o menu
from fila_de_atendimento import fila_principal, chegada_automatica_dinamica 

# Importa funções do módulo de dados central para gerenciamento de voos, passageiros e clima
from dados_aeroporto import (
    gerar_passageiro_aleatorio,
    DADOS_AEROPORTO,
    ajustar_numero_de_filas, 
    verificar_condicoes_climaticas, 
    simular_avanco_tempo,
    salvar_dados_aeroporto
)

def menu_gerenciamento_passageiros(dados_aeroporto):
    """
    Sub-menu para gerar novos passageiros e visualizar o status atual.
    
    Argumentos:
      - dados_aeroporto (dict): O dicionário mestre com os dados.
      
    Retorno:
      - dict: O dicionário de dados atualizado.
    """
    while True:
        # Chama a função para ajustar as filas dinamicamente antes de mostrar o menu
        # Isso garante que exista pelo menos 1 fila aberta se houver demanda
        ajustar_numero_de_filas(dados_aeroporto)
        
        # 'total_passageiros' (Tipo: int) -> Conta o histórico total de passageiros
        total_passageiros = len(dados_aeroporto['passageiros_geral'])
        
        print("\n--- SUB-MENU: PASSAGEIROS ---")
        print(f"Total de Passageiros Gerados: {total_passageiros}")
        print("1. Gerar Novo Passageiro Automático (e simular check-in)")
        print("2. Visualizar Voos Ativos")
        print("3. Voltar")
        
        # 'escolha' (Tipo: str) -> Captura a opção do usuário
        escolha = input("Escolha uma opção: ")
        
        if escolha == '1':
            # GERAÇÃO E CHECK-IN AUTOMÁTICO
            # 'novo_passageiro' (Tipo: dict) -> Recebe o dicionário do passageiro criado
            novo_passageiro = gerar_passageiro_aleatorio(dados_aeroporto)
            
            # Se o passageiro foi criado com sucesso (não retornou None)
            if novo_passageiro:
                # Chama a função de fila para alocar o passageiro
                # Como chamamos ajustar_numero_de_filas acima, garantimos que existe fila
                chegada_automatica_dinamica(dados_aeroporto, novo_passageiro)
            
        elif escolha == '2':
            # Visualiza os dados de todos os voos ativos
            print("\n--- STATUS DOS VOOS ---")
            # 'voo' (Tipo: dict) -> Itera sobre cada voo na lista para exibir status
            for voo in dados_aeroporto['voos']:
                print(f"Voo {voo['numero']} ({voo['origem']}->{voo['destino']}): Status={voo['status']}, Alocados={voo['passageiros_alocados']}/{voo['capacidade']}")
        
        elif escolha == '3':
            # Sai do loop e volta para o menu anterior
            break 
            
        else:
            print("Opção inválida.")
    
    return dados_aeroporto # Retorna os dados atualizados

def menu_administrador_acoes(dados_admin, dados_aeroporto): 
    """
    Função principal que gerencia as ações do admin, incluindo troca de senha e simuladores.
    
    Argumentos:
      - dados_admin (dict): Dados de login do administrador (senha hash).
      - dados_aeroporto (dict): Dicionário mestre do aeroporto.
      
    Retorno:
      - tuple: (dados_admin atualizados, bool senha_alterada)
    """
    
    # 'senha_alterada' (Tipo: bool) -> Flag para indicar se a senha mudou (para salvar depois)
    senha_alterada = False # Inicializa fora do loop

    while True: # Loop principal do menu do administrador
        print("\n--- MENU DO ADMINISTRADOR ---")
        print("1. Gerenciamento de Passageiros") 
        print("2. Gerenciamento de Voos / Clima") 
        print("3. Gerenciar Simulação de Filas") 
        print("4. Avançar Tempo (Mudar Status dos Voos)") 
        print("5. Trocar Senha")
        print("6. Sair e Salvar")
        
        escolha = input("Escolha uma opção: ")

        if escolha == '1':
            # Opção 1: Passageiros
            dados_aeroporto = menu_gerenciamento_passageiros(dados_aeroporto)
            
        elif escolha == '2':
            # Opção 2: Voos e Clima (O clima deve estar dentro deste submenu)
            dados_aeroporto = menu_gerenciamento_voos(dados_aeroporto)

        elif escolha == '3':
            # Opção 3: Filas (
            print("Iniciando o sistema de filas...")
            dados_aeroporto = fila_principal(dados_aeroporto) 
            print("Voltando ao Menu do Administrador.")
        
        elif escolha == '4':
            # Opção 4: Avançar Tempo
            dados_aeroporto = simular_avanco_tempo(dados_aeroporto)

        elif escolha == '5':
            # Opção 5: Trocar Senha
            nova_senha = input("Digite a nova senha: ")
            dados_admin['senha_hash'] = criar_hash_senha(nova_senha) 
            print("A senha foi alterada na memória. Será salva ao sair.")
            senha_alterada = True
            
        elif escolha == '6':
            # Opção 6: Sair
            print("Saindo do menu do administrador.")
            break 
            
        else:
            print("Opção inválida.")
    
    # Retorna os dados do admin e a flag para o menu principal saber se deve salvar
    return dados_admin, senha_alterada

def menu_gerenciamento_voos(dados_aeroporto):
    """
    Sub-menu para Adicionar e Remover voos manualmente (CRUD).
    
    Argumentos:
      - dados_aeroporto (dict): Dicionário mestre.
      
    Retorno:
      - dict: Dicionário mestre atualizado.
    """
    while True:
        print("\n--- GESTÃO DE VOOS / CLIMA ---")
        print("1. Adicionar Novo Voo")
        print("2. Cancelar/Remover Voo")
        print("3. Verificar Clima (Simulação API)") #
        print("4. Listar Voos")
        print("5. Voltar")
        
        escolha = input("Escolha uma opção: ")
        
        if escolha == '1':
            # ADICIONAR VOO
            print("\n--- NOVO VOO ---")
            # Coleta dados do novo voo
            numero = input("Número do Voo (ex: AB1234): ").upper()
            origem = input("Origem (sigla): ").upper()
            destino = input("Destino (sigla): ").upper()
            try:
                # Validação de entrada para garantir que capacidade seja número inteiro
                capacidade = int(input("Capacidade: "))
            except ValueError:
                print("Capacidade inválida.")
                continue # Volta para o início do loop se der erro
            
            # Cria o dicionário do novo voo
            novo_voo = {
                'numero': numero,
                'origem': origem,
                'destino': destino,
                'status': 'Check-in', # Status inicial padrão
                'capacidade': capacidade,
                'passageiros_alocados': 0,
                'lista_passageiros': []
            }
            # Adiciona à lista de voos no dicionário mestre
            dados_aeroporto['voos'].append(novo_voo)
            print(f" Voo {numero} criado com sucesso!")
            
        elif escolha == '2':
            # REMOVER VOO
            numero_alvo = input("Digite o número do voo para cancelar: ").upper()
            encontrado = False
            
            # Itera para encontrar o voo pelo número
            for voo in dados_aeroporto['voos']:
                if voo['numero'] == numero_alvo:
                    # Remove o dicionário do voo da lista
                    dados_aeroporto['voos'].remove(voo)
                    print(f" Voo {numero_alvo} cancelado e removido do sistema.")
                    encontrado = True
                    break # Para a busca após encontrar
            
            if not encontrado:
                print("Voo não encontrado.")
        
        elif escolha == '3':
            # Chama a verificação de clima AQUI
            dados_aeroporto = verificar_condicoes_climaticas(dados_aeroporto)

        elif escolha == '4':
            # LISTAR VOOS
            # Formata a saída em colunas alinhadas para melhor visualização
            print("\n{:<10} {:<10} {:<10} {:<15}".format("VOO", "ORIGEM", "DESTINO", "STATUS"))
            for voo in dados_aeroporto['voos']:
                print(f"{voo['numero']:<10} {voo['origem']:<10} {voo['destino']:<10} {voo['status']:<15}")

        elif escolha == '5':
            break # Sai do sub-menu
        else:
            print("Opção inválida.")
            
    return dados_aeroporto

