# Importa funções de segurança (login e salvamento de dados do admin)
from senha import login_administracao, salvar_dados
# Importa a função principal do menu de administrador
from menuadm import menu_administrador_acoes
# Importa funções para carregar/salvar o estado completo do aeroporto (persistência)
from dados_aeroporto import carregar_dados_aeroporto, salvar_dados_aeroporto
# Importa a função do menu de passageiros
from menu_passageiros import menu_passageiro_acoes

def menu_principal_adm_user(dados_do_aeroporto):
    """
    Exibe o menu principal e redireciona o fluxo para Admin ou Usuário.
    Recebe os dados por parâmetro para manter as alterações na memória.
    
    Argumentos:
      - dados_do_aeroporto (dict): O dicionário mestre com todo o estado atual do sistema.
      
    Retorno:
      - None (A função executa ações e modificações 'in-place', mas não retorna valor direto).
    """
    
    print("\n--- MENU PRINCIPAL ---")
    print("Selecione o tipo de acesso:")
    print("1 - Acesso para Administrador")
    print("2 - Acesso para Usuário (Painel de Voos)")
    
    # 'operacoes' (Tipo: str) -> Recebe a escolha do usuário
    operacoes = input("Digite 1 ou 2: ")
    
    if operacoes == "1": # CAMINHO DO ADMINISTRADOR
        print("Você escolheu entrar como administrador.")
        
        # Chama a função de login. Retorna sucesso (bool) e os dados do admin (dict)
        # 'sucesso' (Tipo: bool), 'dados_admin' (Tipo: dict)
        sucesso, dados_admin = login_administracao()
        
        if sucesso:
            print("\nLogin completo! Iniciando o Menu do Administrador...")
            
            # Passa os dados da memória para o admin
            # O admin vai modificar esses dados (criar voos, mudar status) e retornar
            # 'dados_admin_final' (Tipo: dict) -> Dados do admin atualizados
            # 'senha_alterada' (Tipo: bool) -> Flag indicando se houve troca de senha
            dados_admin_final, senha_alterada = menu_administrador_acoes(dados_admin, dados_do_aeroporto)
            
            # Se a senha foi alterada dentro do menu, salva os dados de segurança no arquivo .pkl
            if senha_alterada:
                salvar_dados(dados_admin_final)
                print("Status: Nova senha salva permanentemente.")
            
            # Ao sair do admin, os dados em 'dados_do_aeroporto' já estão alterados na memória.
            # Não precisamos carregar de novo, nem salvar imediatamente (salvamos ao sair do programa).
            
        else:
            print("Retornando ao Menu Principal.")
            
    elif operacoes == "2": # CAMINHO DO PASSAGEIRO
        print("Acessando painel de voos...")
        
        # Passa os MESMOS dados da memória para o passageiro
        # Assim ele vê exatamente o que o admin acabou de mudar/criar
        menu_passageiro_acoes(dados_do_aeroporto)
        
    
        
    else:
        print("Opção inválida.")

def iniciar_sistema():
    """
    Função loop principal. Carrega os dados UMA VEZ no início e salva no final.
    """
    
    # --- CARREGAMENTO ÚNICO  ---
    print("Carregando sistema...")
    # 'dados_gerais' (Tipo: dict) -> Carrega o estado inicial do arquivo ou cria padrão
    dados_gerais = carregar_dados_aeroporto()
    
    while True: # Loop infinito do programa
        # Passa os dados carregados para o menu, mantendo o estado na memória
        menu_principal_adm_user(dados_gerais)
        
        # Pergunta se quer continuar ou sair
        continuar = input("\nPressione ENTER para voltar ao Menu Principal ou digite 'S' para sair: ").upper()
        
        if continuar == 'S':
            print("Salvando dados e encerrando...")
            # --- SALVAMENTO FINAL  ---
            # Salva todo o estado (voos, passageiros, filas) no arquivo .pkl antes de fechar
            salvar_dados_aeroporto(dados_gerais)
            break # Encerra o loop e o programa

# Garante que o sistema só inicie se este arquivo for executado diretamente
if __name__ == "__main__":
    iniciar_sistema()
    
