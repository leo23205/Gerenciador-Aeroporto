# Importa funções necessárias de outros módulos
# 'chegada_automatica_dinamica' é usada para colocar o passageiro na fila após o check-in
# 'renovar_voo_se_cheio' verifica e renova voos lotados após uma compra
from fila_de_atendimento import chegada_automatica_dinamica
from dados_aeroporto import renovar_voo_se_cheio , ajustar_numero_de_filas

def realizar_compra(dados_aeroporto):
    """
    Permite que o usuário compre uma passagem manualmente, inserindo seus dados.
    
    Argumentos:
      - dados_aeroporto (dict): O dicionário mestre contendo voos e passageiros.
      
    Retorno:
      - None (A função modifica o dicionário mestre diretamente e exibe mensagens).
    """
    print("\n--- COMPRA DE PASSAGEM ---")
    
    # 1. Escolha do Voo
    # 'numero_voo' (str) -> Recebe o código do voo (ex: JJ3401)
    numero_voo = input("Digite o número do voo desejado (ex: JJ3401): ").upper()
    
    # 'voo_encontrado' (Tipo: dict ou None) -> Variável para armazenar o dicionário do voo, se achar
    voo_encontrado = None
    
    # Itera sobre a lista de voos dentro do dicionário mestre
    # 'voo' (Tipo: dict) -> Cada dicionário representando um voo
    for voo in dados_aeroporto['voos']:
        if voo['numero'] == numero_voo: # Compara a string do número
            voo_encontrado = voo # Armazena a referência ao dicionário do voo
            break #Para o loop assim que encontrar
    
    # Validações iniciais        
    if not voo_encontrado: # Se voo_encontrado continuar None
        print("Erro: Voo não encontrado.")
        return # Sai da função se o voo não existir
    
    # Verifica especificamente se está em Embarque para dar uma mensagem clara
    if voo_encontrado['status'] == 'Embarque':
        print(f" ERRO: Vendas encerradas! O Voo {numero_voo} já iniciou o embarque.")
        return
    
    # Impede compra se o voo não estiver em fase de Check-in (Decolou, Cancelado, etc.)
    # Acessa a chave 'status' (str) do dicionário do voo
    if voo_encontrado['status'] != 'Check-in':
        print(f"Erro: Voo indisponível para compra (Status: {voo_encontrado['status']}).")
        return
    
    # Verifica capacidade acessando as chaves (int) do dicionário
    if voo_encontrado['passageiros_alocados'] >= voo_encontrado['capacidade']:
        print("Erro: Voo lotado.")
        return

    # 2. Coleta de Dados do Usuário
    # 'nome' (Tipo: str) -> Nome do passageiro
    nome = input("Digite seu Nome completo: ")
    
    # Validação de CPF (Loop até digitar corretamente)
    while True:

        # 'cpf' (Tipo: str) -> Recebe a entrada do usuário
        cpf = input("Digite seu CPF (12 dígitos): ")
        
        # Verifica se a string contém apenas dígitos E se tem tamanho 12
        if cpf.isdigit() and len(cpf) == 12:
            break
        else:
            print("Erro: CPF inválido! Digite exatamente 12 números.")
   
    
    # 3. Criação do Passageiro (Dicionário)
    # 'novo_id' (Tipo: int) -> Pega o próximo ID disponível do contador mestre
    novo_id = dados_aeroporto['proximo_passageiro_id']
    
    # 'novo_passageiro' (Tipo: dict) -> Cria a estrutura de dados do passageiro
    novo_passageiro = {
        'id': novo_id,  #int
        'nome': nome,   #str
        'cpf': cpf,     #str
        'voo_numero': numero_voo,  # str
        'status_voo': 'Reservado', # str (Estado inicial)
        'checkin_status': False    # bool (Flag de controle)
    }
    
    # --- ATUALIZAÇÃO DOS DADOS MESTRES ---
    # Adiciona o dicionário do passageiro à lista geral (Histórico)
    dados_aeroporto['passageiros_geral'].append(novo_passageiro)

    # Incrementa o contador de IDs no dicionário mestre (int)
    dados_aeroporto['proximo_passageiro_id'] += 1
    
    # Atualiza a contagem (int) e a lista de IDs (list) DENTRO do voo específico
    voo_encontrado['passageiros_alocados'] += 1
    voo_encontrado['lista_passageiros'].append(novo_id)
    
    print(f"\n Compra realizada com sucesso! Seu ID de reserva é: {novo_id}")
    
    # Verifica se essa compra lotou o voo e, se sim, cria um voo substituto
    # Chama a função importada passando o dicionário mestre e o voo alterado
    renovar_voo_se_cheio(dados_aeroporto, voo_encontrado)
    
    print("Guarde este ID para fazer o check-in.")


def realizar_checkin(dados_aeroporto):
    """
    Realiza o check-in de um passageiro existente e o envia para a fila de atendimento.
    
    Argumentos:
      - dados_aeroporto (dict): O dicionário mestre.
      
    Retorno:
      - None
    """
    print("\n--- CHECK-IN ---")
    
    try:
        # 'id_input' (Tipo: int) -> Solicita o ID numérico gerado na compra
        id_input = int(input("Digite seu ID de reserva: "))
    except ValueError:
        print("ID inválido.")
        return

    # 'passageiro_encontrado' (Tipo: dict ou None) -> Variável de busca

    passageiro_encontrado = None

    # Itera sobre a lista de todos os passageiros
    for p in dados_aeroporto['passageiros_geral']:
        if p['id'] == id_input: # Compara inteiros
            passageiro_encontrado = p # Armazena a referência ao dicionário
            break

    # Validações        
    if not passageiro_encontrado:
        print("Erro: Reserva não encontrada.")
        return

    # Verifica a flag booleana 'checkin_status'   
    if passageiro_encontrado['checkin_status']:
        print("Aviso: Você já fez check-in e já está na fila/embarcado.")
        return

    # Confirmação visual acessando chaves do dicionário
    print(f"Passageiro: {passageiro_encontrado['nome']} - Voo: {passageiro_encontrado['voo_numero']}")
    
    # 'confirmar' (Tipo: str)
    confirmar = input("Confirmar check-in? (S/N): ").upper()
    
    if confirmar == 'S':
        # Atualiza status no dicionário do passageiro (reflete no banco de dados mestre)
        passageiro_encontrado['checkin_status'] = True
        passageiro_encontrado['status_voo'] = 'Check-in Realizado'
        
        print("Check-in confirmado! Redirecionando para as filas de atendimento...")
        
        # --- INTEGRAÇÃO COM FILAS ---
        # Chama a função do módulo de filas para alocar o passageiro na fila mais curta
        # Passa o dicionário 'passageiro_encontrado' inteiro
        chegada_automatica_dinamica(dados_aeroporto, passageiro_encontrado)
    else:
        print("Check-in cancelado.")


def menu_passageiro_acoes(dados_aeroporto):
    """
    Exibe o menu principal do passageiro e gerencia as escolhas.
    
    Argumentos:
      - dados_aeroporto (dict): O estado atual do aeroporto.
      
    Retorno:
      - None (O menu roda em loop até o usuário escolher sair).
    """
    
    while True:
        # Garante que as filas sejam criadas/ajustadas antes de qualquer ação
        ajustar_numero_de_filas(dados_aeroporto)

        print("\n--- ÁREA DO PASSAGEIRO ---")
        print("1. Ver Painel de Voos")
        print("2. Comprar Passagem")
        print("3. Fazer Check-in")
        print("4. Voltar ao Menu Principal")
        
        # 'escolha' (Tipo: str) -> Captura a opção do usuário)
        escolha = input("Escolha uma opção: ")
        
        if escolha == '1':
            # Visualização Simples (Painel de Aeroporto)
            # Formata a saída como uma tabela alinhada usando formatação de strings
            print("\n{:<10} {:<10} {:<10} {:<15}".format("VOO", "ORIGEM", "DESTINO", "STATUS"))
            print("-" * 50)

            # Itera sobre a lista de voos para exibir cada um
            for voo in dados_aeroporto['voos']:
                print(f"{voo['numero']:<10} {voo['origem']:<10} {voo['destino']:<10} {voo['status']:<15}")
                
        elif escolha == '2':
            # Chama a função de compra passando os dados
            realizar_compra(dados_aeroporto)
            
        elif escolha == '3':
            # Chama a função de check-in passando os dados
            realizar_checkin(dados_aeroporto)
            
        elif escolha == '4':
            print("Saindo da área do passageiro...")
            break
            
        else:
            print("Opção inválida.")