# Importa as funções utilitárias e de dados do módulo central 'dados_aeroporto'
from dados_aeroporto import ajustar_numero_de_filas, gerar_passageiro_aleatorio , encontrar_fila_mais_curta

def chegada_automatica_dinamica(dados_aeroporto, passageiro_data): 
    """
    Adiciona um dicionário de passageiro à fila mais curta disponível.
    
    Argumentos:
      - dados_aeroporto (dict): O dicionário mestre contendo todo o estado do sistema.
      - passageiro_data (dict): O dicionário representando o passageiro a ser adicionado.
      
    Retorno:
      - None (A função não retorna valor, apenas modifica a lista de filas ).
    """
    
    #'filas' (Tipo: list) -> Acessa a lista de listas que representa as filas de atendimento
    filas = dados_aeroporto['filas_atendimento']
    
    # Verifica se a lista de filas está vazia
    if not filas:
        print("Erro: Nenhuma fila disponível para atendimento.")
        return # Sai da função se não houver filas (Retorno implícito: None)
    
    # 'fila_destino' (Tipo: list) -> Recebe a referência da sublista (fila) com menos pessoas
    fila_destino = encontrar_fila_mais_curta(filas)
    
    # Adiciona o dicionário do passageiro na fila encontrada!
    # .append() altera a lista original diretamente na memória
    fila_destino.append(passageiro_data) 
    
    # 'numero_fila' (Tipo: int) -> Calcula o índice da fila e soma 1 para exibir (Fila 1, Fila 2...)
    numero_fila = dados_aeroporto['filas_atendimento'].index(fila_destino) + 1
    
    # Exibe mensagem acessando as chaves 'nome' e 'id' do dicionário do passageiro
    print(f"Passageiro {passageiro_data['nome']} (ID: {passageiro_data['id']}) chegou na Fila {numero_fila}.")
    
    # Não retorna mais o ID, pois ele já foi atualizado na função gerar_passageiro_aleatorio.


def atendimento_automatico_total(dados_aeroporto):
    """
    Percorre todas as filas e atende 1 cliente de cada fila simultaneamente (Simulação de guichês).
    
    Argumentos:
      - dados_aeroporto (dict): O dicionário mestre.
      
    Retorno:
      - int: O número total de clientes que foram atendidos nesta rodada.
    """
    
    # 'filas' (Tipo: list) -> Referência à lista de listas de atendimento
    filas = dados_aeroporto['filas_atendimento']
    
    # 'clientes_atendidos' (Tipo: int) -> Contador para rastrear quantos atendimentos ocorreram
    clientes_atendidos = 0
    
    # Itera sobre todas as filas dinamicamente usando enumerate
    # 'i' (Tipo: int) -> Índice da fila atual
    # 'fila' (Tipo: list) -> A sublista contendo os passageiros naquela fila
    for i, fila in enumerate(filas):
        
        # 'numero_fila' (Tipo: int) -> Ajusta o índice para começar em 1 na exibição
        numero_fila = i + 1
        
        # Verifica se a fila atual tem passageiros (Lógica FIFO)
        if len(fila) > 0:
            
            # 'atendido' (Tipo: dict) -> Remove e retorna o primeiro passageiro da lista (pop(0))
            atendido = fila.pop(0) # 'atendido' agora é o dicionário do passageiro
            
            # Acessar o ID e o NOME dentro do dicionário atendido para exibição
            # 'passageiro_id' (Tipo: int) -> Extrai o valor da chave 'id'
            passageiro_id = atendido['id']
            
            # 'passageiro_nome' (Tipo: str) -> Extrai o valor da chave 'nome'
            passageiro_nome = atendido['nome']
            
            # Imprime os dados do passageiro atendido
            print(f"Sistema: Cliente {passageiro_nome} (ID: {passageiro_id}) atendido automaticamente na Fila {numero_fila}.")
            
            # Incrementa o contador de atendimentos
            clientes_atendidos += 1
        else:
            # Caso a fila esteja vazia
            print(f"Sistema: Fila {numero_fila} estava vazia. Nenhum atendimento.")
    
    # Verifica se o contador permaneceu zerado (nenhuma fila tinha gente)
    if clientes_atendidos == 0:
        print("Nenhuma fila ativa tinha clientes para atender.")
        
    return clientes_atendidos # Retorna o total (int)

def fila_principal(dados_aeroporto):
    """
    Função principal do simulador de filas (Menu de Simulação).
    
    Argumentos:
      - dados_aeroporto (dict): O estado atual do aeroporto.
      
    Retorno:
      - dict: O dicionário 'dados_aeroporto' atualizado após as simulações.
    """
    
    # Loop infinito para manter o menu rodando até o usuário sair
    while True:
        
        # Ajustar o número de filas no início de cada loop
        # Chama a função importada que calcula demanda e abre/fecha filas
        # 'dados_aeroporto' (Tipo: dict) -> É atualizado com o retorno da função
        dados_aeroporto = ajustar_numero_de_filas(dados_aeroporto)

        # 'filas' (Tipo: list) -> Atualiza a referência local para exibição
        filas = dados_aeroporto['filas_atendimento']
        
        print("\n--- Sistema de Filas Dinâmicas ---")
        
        # Exibe o status de todas as filas dinamicamente
        # 'i' (Tipo: int), 'fila' (Tipo: list)
        for i, fila in enumerate(filas):
            # Mostra o número da fila e quantos dicionários (clientes) tem dentro
            print(f"Fila {i+1} ({len(fila)} clientes): {fila}")
            
        print("Comandos:")
        print("N - Chegada Automática de Passageiro")
        print("T - Atendimento Automático Total") 
        print("S - Sair")
        
        # 'operacoes' (Tipo: str) -> Lê a entrada do usuário e converte para maiúsculas
        operacoes = input("Digite as operações: ").upper()
        
        # 'sair' (Tipo: bool) -> Flag de controle para encerrar o loop
        sair = False

        # Itera sobre a string de entrada (permite comandos em lote ex: "NT")
        # 'op' (Tipo: str) -> Caractere atual da iteração
        for op in operacoes:
            if op == "N": # CHEGADA AUTOMÁTICA
                
                # 'novo_passageiro' (Tipo: dict ou None) -> Chama a função para criar um passageiro
                novo_passageiro = gerar_passageiro_aleatorio(dados_aeroporto)

                # Se o passageiro foi criado com sucesso (não é None)
                if novo_passageiro:
                    # Chama a função para colocar o dicionário na fila correta
                    chegada_automatica_dinamica(dados_aeroporto, novo_passageiro)
            
            elif op == "T": # ATENDIMENTO AUTOMÁTICO TOTAL
                # Chama a função que atende um cliente de cada fila
                atendimento_automatico_total(dados_aeroporto)    
            elif op == "S":
                sair = True # Define a flag como verdadeira
                break # Quebra o loop 'for'
            else:
                print(f"Operação inválida: {op}")
        
        # Verifica se a flag de saída foi ativada para quebrar o while True
        if sair:
            print("Encerrando programa.")
            # Retorna o dicionário mestre atualizado para quem chamou (menu adm)
            return dados_aeroporto
        
