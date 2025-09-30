# Importação das bibliotecas necessárias para a interface gráfica, lógica do jogo,
# manipulação de áudio, reconhecimento de voz e processamento de texto.
import tkinter as tk  # Importa a biblioteca Tkinter para criar a interface gráfica, com o alias 'tk'.
from tkinter import messagebox, font, ttk  # Importa componentes específicos do Tkinter: caixas de mensagem, fontes e widgets temáticos.
import heapq  # Importa a biblioteca para implementar filas de prioridade (min-heap), usada no algoritmo A*.
import random  # Importa a biblioteca para gerar números aleatórios.
import time  # Importa a biblioteca para funções relacionadas a tempo (não usada diretamente, mas pode ser útil).
import threading  # Importa a biblioteca para executar tarefas em paralelo (threads), como falar e ouvir sem travar a interface.
import os  # Importa a biblioteca para interagir com o sistema operacional, como remover arquivos.
from gtts import gTTS  # Importa a classe gTTS da biblioteca Google Text-to-Speech para converter texto em fala.
from playsound import playsound  # Importa a função playsound para tocar arquivos de áudio.
import speech_recognition as sr  # Importa a biblioteca de reconhecimento de voz, com o alias 'sr'.
from thefuzz import process  # Importa a função 'process' da thefuzz para encontrar strings parecidas (fuzzy string matching).
from unidecode import unidecode # Importa a função unidecode para remover acentos de strings.

# Classe principal que encapsula toda a lógica e a interface do jogo.
class JogoSupermercado:
    # Constante para balancear o peso da heurística no cálculo do A* e na Busca Gulosa.
    FATOR_HEURISTICA = 100 # Define um multiplicador para a heurística, para que ela tenha um peso comparável ao custo do caminho (g).

    # O método __init__ é o construtor da classe. Ele é chamado quando um novo objeto JogoSupermercado é criado.
    def __init__(self, master):
        # 'master' é a janela principal do Tkinter.
        self.master = master # Armazena a referência da janela principal na variável de instância 'self.master'.
        master.configure(bg="#f5f5f5")  # Define a cor de fundo padrão da janela.
        
        # Inicia a janela maximizada para uma melhor experiência do usuário.
        master.state('zoomed') # Configura o estado inicial da janela para 'zoomed' (maximizada).
        master.minsize(1200, 700) # Define um tamanho mínimo para a janela, caso o usuário a redimensione.
        
        # Define o título que aparecerá na barra superior da janela.
        master.title("Jogo do Supermercado (Baseado em Turnos)")

        # Inicializa o objeto para reconhecimento de voz.
        self.recognizer = sr.Recognizer() # Cria uma instância do reconhecedor de voz.

        # --- Variáveis de Estado do Jogo ---
        self.cesta_jogador = []  # Lista para armazenar os itens (nome, preço) do jogador.
        self.total_jogador = 0.0  # Soma dos preços na cesta do jogador.
        self.cesta_robo = []  # Lista para os itens do robo (IA).
        self.total_robo = 0.0  # Soma dos preços na cesta do robo.
        self.jogo_ativo = False  # Flag (sinalizador) para controlar se o jogo está em andamento.
        
        # --- Controle de Turno ---
        self.turno_do_jogador = True  # Começa com o turno do jogador.
        self.botoes_produtos = [] # Lista para guardar as referências dos botões de produtos para poder habilitá-los/desabilitá-los.

        # Dicionário que armazenará todos os produtos disponíveis, com seus preços e estoque.
        self.produtos_com_estoque = {} # Inicializa o dicionário de produtos.

        # Exibe a tela inicial de boas-vindas.
        self.mostrar_tela_bem_vindo() # Chama o método que constrói a primeira tela do jogo.

    # Função para converter uma string de texto em fala usando a API do Google.
    def falar_texto(self, texto_para_falar):
        try: # Inicia um bloco de tratamento de exceções, para o caso de falha (ex: sem internet).
            # Cria um objeto gTTS com o texto, definindo o idioma para português do Brasil e velocidade normal.
            tts = gTTS(text=texto_para_falar, lang='pt-br', slow=False)
            arquivo_audio_temporario = "temp_fala.mp3"  # Nome do arquivo de áudio temporário.
            tts.save(arquivo_audio_temporario)  # Salva o áudio gerado no arquivo temporário.
            playsound(arquivo_audio_temporario) # Toca o arquivo de áudio.
            os.remove(arquivo_audio_temporario) # Remove o arquivo temporário após tocar para não ocupar espaço.
        except Exception as e: # Captura qualquer exceção que possa ocorrer.
            # Informa no console caso ocorra um erro.
            print(f"Erro ao tentar falar o texto com gTTS: {e}")
            print("Verifique sua conexão com a internet ou se a biblioteca playsound está funcionando corretamente.")

    # Configura e exibe a tela inicial do jogo.
    def mostrar_tela_bem_vindo(self):
        # Limpa todos os widgets (elementos gráficos) da tela anterior.
        for widget in self.master.winfo_children(): # Itera sobre todos os widgets filhos da janela principal.
            widget.destroy() # Destrói (remove) cada widget.

        # Configura a cor de fundo para a tela de boas-vindas.
        self.master.configure(bg="#ff6b00") # Altera a cor de fundo da janela principal.

        # Cria um frame (container) central para alinhar todos os elementos.
        frame_bem_vindo = tk.Frame(self.master, bg="#ff6b00") # Cria o frame, filho da janela principal.
        frame_bem_vindo.place(relx=0.5, rely=0.5, anchor="center") # Centraliza o frame na janela usando posicionamento relativo.

        # Título principal da tela.
        label_titulo = tk.Label(frame_bem_vindo, text="Olá, seja bem-vindo!", # Cria um widget de texto (Label).
                                 font=("Arial", 48, "bold"), fg="white", bg="#ff6b00") # Define a fonte, cor do texto (fg) e cor de fundo (bg).
        label_titulo.pack(pady=(0, 40)) # Adiciona o label ao frame com um espaçamento vertical (padding).

        # Frame para os desenhos dos carrinhos de compras.
        frame_carrinhos = tk.Frame(frame_bem_vindo, bg="#ff6b00") # Cria um frame para os ícones decorativos.
        frame_carrinhos.pack(pady=(0, 40)) # Adiciona o frame à tela.

        # Desenha três carrinhos decorativos.
        self.desenhar_carrinho_compras(frame_carrinhos, 0) # Chama a função para desenhar o primeiro carrinho.
        self.desenhar_carrinho_compras(frame_carrinhos, 1) # Chama a função para desenhar o segundo carrinho.
        self.desenhar_carrinho_compras(frame_carrinhos, 2) # Chama a função para desenhar o terceiro carrinho.

        # Texto explicando as regras do jogo por turnos.
        texto_mensagem = "O jogo agora é por turnos! Você adiciona um item, depois o robo.\nO estoque é compartilhado. Use sua estratégia para vencer!" # Define o texto.
        label_mensagem = tk.Label(frame_bem_vindo, text=texto_mensagem, # Cria o label com o texto.
                                   font=("Arial", 16), fg="white", bg="#ff6b00", # Define a formatação.
                                   justify="center") # Centraliza o texto de múltiplas linhas.
        label_mensagem.pack(pady=(0, 60)) # Adiciona o label à tela.

        # Frame para a seleção do algoritmo da IA.
        frame_algoritmo = tk.Frame(frame_bem_vindo, bg="#ff6b00") # Cria um frame para os botões de rádio.
        frame_algoritmo.pack(pady=(0, 40)) # Adiciona o frame à tela.

        # Cria um label para o seletor de algoritmo.
        tk.Label(frame_algoritmo, text="Escolha o algoritmo do robo:",
                 font=("Arial", 18, "bold"), fg="white", bg="#ff6b00").pack() # Adiciona o label ao frame de algoritmo.

        # Variável para armazenar a escolha do algoritmo (A* ou Gulosa).
        self.variavel_algoritmo = tk.StringVar(value="A*") # Cria uma variável especial do Tkinter para guardar a opção selecionada. Padrão é A*.
        # Cria o botão de rádio para a opção "A*".
        tk.Radiobutton(frame_algoritmo, text="Algoritmo A*", variable=self.variavel_algoritmo,
                                     value="A*", font=("Arial", 16), fg="white", bg="#ff6b00",
                                     selectcolor="#ff6b00").pack() # Adiciona o botão de rádio à tela.
        # Cria o botão de rádio para a opção "Busca Gulosa".
        tk.Radiobutton(frame_algoritmo, text="Busca Gulosa", variable=self.variavel_algoritmo,
                                     value="Gulosa", font=("Arial", 16), fg="white", bg="#ff6b00",
                                     selectcolor="#ff6b00").pack() # Adiciona o botão de rádio à tela.

        # Botão para começar o jogo.
        botao_iniciar = tk.Button(frame_bem_vindo, text="INICIAR JOGO", # Cria o botão.
                                   font=("Arial", 26, "bold"), bg="white", fg="#ff6b00", # Define a formatação.
                                   relief="flat", padx=40, pady=20, # Define o estilo e espaçamento interno.
                                   command=self.inicializar_jogo) # Define a função que será chamada ao clicar.
        botao_iniciar.pack(pady=(0, 40)) # Adiciona o botão à tela.

        # Cria um label de rodapé com uma instrução.
        label_rodape = tk.Label(frame_bem_vindo, text="Clique em 'INICIAR JOGO' para começar",
                                     font=("Arial", 14), fg="white", bg="#ff6b00")
        label_rodape.pack() # Adiciona o label à tela.

    # Função auxiliar para desenhar carrinhos de compras decorativos na tela de boas-vindas.
    def desenhar_carrinho_compras(self, parent, position):
        w, h = 100, 100 # Define a largura (width) e altura (height) do canvas.
        canvas = tk.Canvas(parent, width=w, height=h, bg="#ff6b00", highlightthickness=0) # Cria uma área de desenho (Canvas).
        canvas.grid(row=0, column=position, padx=15) # Posiciona o canvas em uma grade (grid) dentro do frame pai.

        # Desenha as partes do carrinho (cesto, rodas, alça) usando formas geométricas.
        canvas.create_rectangle(w*0.125, h*0.375, w*0.875, h*0.75, fill="#e0e0e0", outline="#c0c0c0", width=2) # Corpo do cesto.
        canvas.create_rectangle(w*0.0625, h*0.3125, w*0.9375, h*0.375, fill="#e0e0e0", outline="#c0c0c0", width=2) # Borda superior do cesto.
        canvas.create_oval(w*0.1875, h*0.6875, w*0.3125, h*0.8125, fill="#555555", outline="#333333", width=1) # Roda 1.
        canvas.create_oval(w*0.6875, h*0.6875, w*0.8125, h*0.8125, fill="#555555", outline="#333333", width=1) # Roda 2.
        canvas.create_line(w*0.8125, h*0.3125, w*0.9375, h*0.1875, fill="#c0c0c0", width=3) # Parte da alça.
        canvas.create_line(w*0.9375, h*0.1875, w*0.6875, h*0.1875, fill="#c0c0c0", width=3) # Parte da alça.
        canvas.create_line(w*0.6875, h*0.1875, w*0.5625, h*0.3125, fill="#c0c0c0", width=3) # Parte da alça.
        
        # Adiciona itens decorativos no carrinho do meio.
        if position == 1: # Verifica se é o carrinho central.
            canvas.create_oval(w*0.3125, h*0.4375, w*0.4375, h*0.5625, fill="#ff9999", outline="#ff6666", width=1) # Item 1 (círculo).
            canvas.create_rectangle(w*0.5, h*0.5, w*0.625, h*0.625, fill="#99ccff", outline="#6699ff", width=1) # Item 2 (quadrado).
            canvas.create_rectangle(w*0.6875, h*0.4375, w*0.8125, h*0.5625, fill="#ffcc99", outline="#ff9966", width=1) # Item 3 (retângulo).

    # Função principal que configura a tela do jogo e reinicia as variáveis.
    def inicializar_jogo(self):
        # Limpa a tela de boas-vindas.
        for widget in self.master.winfo_children(): # Itera sobre todos os widgets na janela.
            widget.destroy() # Remove cada widget.
        
        self.master.configure(bg="#f5f5f5") # Define a cor de fundo do jogo.
        
        # --- CONFIGURAÇÕES DA RODADA ---
        # Reseta as variáveis de estado do jogo.
        self.jogo_ativo = True # Define o jogo como ativo.
        self.turno_do_jogador = True # Define o turno inicial como do jogador.
        self.valor_alvo = round(random.uniform(25.0, 70.0), 2) # Sorteia um novo valor-alvo entre 25.0 e 70.0, arredondado para 2 casas decimais.
        self.cesta_jogador = [] # Esvazia a cesta do jogador.
        self.total_jogador = 0.0 # Zera o total do jogador.
        self.cesta_robo = [] # Esvazia a cesta do robô.
        self.total_robo = 0.0 # Zera o total do robô.
        
        # Base de dados de produtos, separados por departamento.
        produtos_base = {
            "Alimentos": {
                "Ketchup": 2.49, "Maçã": 1.50, "Pão": 2.20, "Queijo": 5.50, "Arroz": 7.00,
                "Chocolate": 3.50, "Biscoitos": 2.80, "Azeite de Oliva": 22.50, "Macarrão": 4.20,
                "Molho de Tomate": 3.80, "Atum em Lata": 6.50, "Ovos (dúzia)": 9.00,
            },
            "Bebidas": {
                "Leite": 3.00, "Iogurte": 1.80, "Refrigerante": 8.50, "Suco de Laranja": 6.00,
                "Água Mineral": 2.00, "Café": 12.00, "Cerveja (lata)": 3.50, "Vinho": 35.00,
            },
            "Limpeza": {
                "Sabonete Líquido": 2.09, "Detergente": 2.50, "Sabão em Pó": 15.00,
                "Desinfetante": 8.00, "Água Sanitária": 5.00, "Esponja de Aço": 1.50,
                "Papel Toalha": 4.50, "Amaciante de Roupas": 11.00, "Limpador Multiuso": 7.50,
                "Saco de Lixo": 5.50, "Papel Higiênico": 10.00,
            }
        }
        
        # Cria a estrutura de dados de produtos com estoque para cada item.
        self.produtos_com_estoque = {"Todos": {}} # Inicializa o dicionário, começando com a categoria "Todos".
        for depto, produtos in produtos_base.items(): # Itera sobre cada departamento e seus produtos.
            self.produtos_com_estoque[depto] = {} # Cria uma entrada para o departamento específico.
            for nome, preco in produtos.items(): # Itera sobre cada produto no departamento.
                estoque = random.randint(1, 3) # Sorteia um estoque inicial entre 1 e 3 para cada produto.
                produto_data = {"preco": preco, "estoque": estoque} # Cria um dicionário com os dados do produto.
                self.produtos_com_estoque[depto][nome] = produto_data # Adiciona o produto ao seu departamento.
                self.produtos_com_estoque["Todos"][nome] = produto_data # Adiciona também à lista "Todos" para visualização geral.
        
        self.departamento_atual = "Todos" # Define o departamento inicial a ser exibido.

        # --- Criação da Interface Gráfica do Jogo ---

        # Cabeçalho da loja.
        frame_cabecalho = tk.Frame(self.master, bg="#ff6b00", height=120) # Cria um frame para o cabeçalho.
        frame_cabecalho.pack(fill="x") # Adiciona o frame à janela, fazendo-o preencher toda a largura ('x').
        frame_cabecalho.pack_propagate(False) # Impede que o frame mude de tamanho para se ajustar aos seus filhos.
        tk.Label(frame_cabecalho, text="Mais por Menos", # Cria o título da loja.
                 font=("Arial", 36, "bold"), fg="white", bg="#ff6b00").pack(pady=25) # Adiciona o título ao cabeçalho.

        # Frame principal que conterá as 3 colunas (Jogador, Produtos, Robo).
        frame_principal = tk.Frame(self.master, bg="#f5f5f5") # Cria o frame principal.
        frame_principal.pack(fill="both", expand=True, padx=25, pady=25) # Adiciona à janela, preenchendo todo o espaço disponível.

        # Configura as colunas para se expandirem igualmente.
        frame_principal.columnconfigure(0, weight=1) # A coluna 0 (Jogador) irá expandir com a janela.
        frame_principal.columnconfigure(1, weight=1) # A coluna 1 (Produtos) irá expandir com a janela.
        frame_principal.columnconfigure(2, weight=1) # A coluna 2 (Robo) irá expandir com a janela.
        frame_principal.rowconfigure(0, weight=1) # A linha 0 irá expandir com a janela.

        # --- Coluna do Jogador (Esquerda) ---
        frame_jogador = tk.LabelFrame(frame_principal, text="👤 JOGADOR", # Cria um frame com título para o jogador.
                                      font=("Arial", 18, "bold"), bg="#f5f5f5")
        frame_jogador.grid(row=0, column=0, sticky="nsew", padx=(0, 10)) # Posiciona o frame na grade (coluna 0).

        # Frame para as informações do alvo e total.
        frame_alvo = tk.Frame(frame_jogador, bg="#f5f5f5") 
        frame_alvo.pack(fill="x", pady=15) # Adiciona o frame à coluna do jogador.
        
        # Mostra o valor-alvo da rodada.
        label_valor_alvo = tk.Label(frame_alvo, text=f"🎯 VALOR-ALVO: R$ {self.valor_alvo:.2f}",
                                     font=("Arial", 18, "bold"), bg="#f5f5f5")
        label_valor_alvo.pack() # Adiciona o label ao frame de alvo.

        # Mostra o total atual da cesta do jogador.
        self.label_total_jogador = tk.Label(frame_alvo, text=f"💰 SEU TOTAL: R$ {self.total_jogador:.2f}",
                                            font=("Arial", 17), bg="#f5f5f5")
        self.label_total_jogador.pack(pady=8) # Adiciona o label.

        # Frame para exibir o saldo.
        frame_saldo = tk.Frame(frame_alvo, bg="#f5f5f5")
        frame_saldo.pack(fill="x", pady=(15, 0), padx=20) # Adiciona o frame.

        # Mostra quanto dinheiro o jogador ainda tem para gastar.
        saldo_restante = self.valor_alvo - self.total_jogador # Calcula o saldo.
        self.label_saldo_restante = tk.Label(frame_saldo, text=f"SALDO: R$ {saldo_restante:.2f}",
                                             font=("Arial", 18, "bold"), bg="#f5f5f5", fg="#17a2b8")
        self.label_saldo_restante.pack(side="left", expand=True) # Adiciona o label, alinhado à esquerda.
        
        # Botão para ouvir o saldo em voz alta.
        self.botao_ouvir_saldo = tk.Button(frame_saldo, text="🔊 Ouvir Saldo",
                                           font=("Arial", 14), bg="#17a2b8", fg="white", relief="flat",
                                           command=self.falar_saldo_restante, padx=15, pady=5)
        self.botao_ouvir_saldo.pack(side="right", expand=True) # Adiciona o botão, alinhado à direita.
        
        # Frame para exibir a cesta do jogador usando Canvas.
        self.frame_cesta_jogador = tk.LabelFrame(frame_jogador, text="Sua Cesta",
                                                     font=("Arial", 15, "bold"), bg="#f5f5f5")
        self.frame_cesta_jogador.pack(fill="both", expand=True, pady=15, padx=10) # Adiciona o frame.
        
        # Canvas onde o desenho da cesta é feito.
        self.canvas_cesta_jogador = tk.Canvas(self.frame_cesta_jogador, bg="white", highlightthickness=0)
        self.canvas_cesta_jogador.pack(fill="both", expand=True) # Adiciona o canvas.
        
        # Listbox que mostra os itens e é colocada dentro do canvas.
        self.display_cesta_jogador = tk.Listbox(self.canvas_cesta_jogador, font=("Arial", 14),
                                                   bg="white", selectbackground="#ff6b00",
                                                   bd=0, highlightthickness=0)
        
        # Chama a função de redesenho sempre que a janela for redimensionada.
        self.canvas_cesta_jogador.bind("<Configure>", self.redesenhar_cesta_jogador) # Associa o evento de redimensionamento à função.

        # Frame para os botões de ação do jogador.
        frame_botoes_jogador = tk.Frame(frame_jogador, bg="#f5f5f5")
        frame_botoes_jogador.pack(fill="x", pady=15) # Adiciona o frame.

        # Botão para remover um item selecionado da cesta.
        self.botao_remover_jogador = tk.Button(frame_botoes_jogador, text="Remover Item",
                                               font=("Arial", 15, "bold"), bg="#e74c3c", fg="white",
                                               command=self.remover_da_cesta, pady=8) # Define a função a ser chamada ao clicar.
        self.botao_remover_jogador.pack(side="left", fill="x", expand=True, padx=10) # Adiciona o botão.
        
        # Botão para o jogador finalizar sua compra (terminar a rodada).
        self.botao_finalizar_jogador = tk.Button(frame_botoes_jogador, text="Finalizar Compra",
                                                 font=("Arial", 15, "bold"), bg="#27ae60", fg="white",
                                                 command=self.finalizar_compra, pady=8)
        self.botao_finalizar_jogador.pack(side="right", fill="x", expand=True, padx=10) # Adiciona o botão.
        
        # --- Coluna do Meio (Produtos) ---
        frame_meio = tk.Frame(frame_principal, bg="#f5f5f5") # Cria o frame da coluna central.
        frame_meio.grid(row=0, column=1, sticky="nsew", padx=10) # Posiciona o frame na grade (coluna 1).

        # Frame com botões de rádio para filtrar por departamento.
        frame_depto = tk.LabelFrame(frame_meio, text="Departamentos",
                                     font=("Arial", 16, "bold"), bg="#f5f5f5")
        frame_depto.pack(fill="x", pady=(0, 15)) # Adiciona o frame.

        departamentos = list(self.produtos_com_estoque.keys()) # Pega a lista de nomes dos departamentos.
        self.variavel_depto = tk.StringVar(value="Todos") # Cria uma variável do Tkinter para o departamento selecionado.

        for depto in departamentos: # Itera sobre os nomes dos departamentos.
            # Cria um botão de rádio para cada departamento.
            tk.Radiobutton(frame_depto, text=depto, variable=self.variavel_depto, value=depto,
                           command=self.exibir_produtos, font=("Arial", 14),
                           bg="#f5f5f5").pack(side="left", padx=20, expand=True) # Adiciona o botão.

        # Frame para os controles de voz.
        frame_voz = tk.Frame(frame_meio, bg="#f5f5f5")
        frame_voz.pack(fill="x", pady=10) # Adiciona o frame.
        
        # Label para mostrar o status do reconhecimento de voz.
        self.label_status_voz = tk.Label(frame_voz, text="Diga 'adicionar' ou 'remover' [produto]", font=("Arial", 12), fg="#555555", bg="#f5f5f5")
        self.label_status_voz.pack() # Adiciona o label.

        # Botão do microfone para iniciar o reconhecimento de voz.
        self.botao_microfone = tk.Button(frame_voz, text="🎤", font=("Arial", 25),
                                         command=self.iniciar_escuta_produto, # Define a função a ser chamada.
                                         bg="#8e44ad", fg="white", relief="flat", width=4)
        self.botao_microfone.pack(pady=5) # Adiciona o botão.

        # Frame que conterá a lista rolável de produtos.
        frame_exibicao_produtos = tk.Frame(frame_meio, bg="#f5f5f5")
        frame_exibicao_produtos.pack(fill="both", expand=True) # Adiciona o frame.

        self.canvas_produtos = tk.Canvas(frame_exibicao_produtos, bg="#f5f5f5", highlightthickness=0) # Cria um canvas para a área rolável.
        scrollbar = tk.Scrollbar(frame_exibicao_produtos, orient="vertical", command=self.canvas_produtos.yview) # Cria a barra de rolagem.
        self.frame_rolavel_produtos = tk.Frame(self.canvas_produtos, bg="#f5f5f5") # Cria o frame que conterá os produtos.

        # Configura o canvas para atualizar a região de rolagem quando o frame de produtos mudar de tamanho.
        self.frame_rolavel_produtos.bind("<Configure>", lambda e: self.canvas_produtos.configure(scrollregion=self.canvas_produtos.bbox("all")))

        self.canvas_produtos.create_window((0, 0), window=self.frame_rolavel_produtos, anchor="nw") # Coloca o frame rolável dentro do canvas.
        self.canvas_produtos.configure(yscrollcommand=scrollbar.set) # Conecta a barra de rolagem ao canvas.

        self.canvas_produtos.pack(side="left", fill="both", expand=True) # Adiciona o canvas.
        scrollbar.pack(side="right", fill="y") # Adiciona a barra de rolagem.
        
        # --- Coluna do Robo (Direita) ---
        frame_robo = tk.LabelFrame(frame_principal, text="🤖 ROBO", # Cria o frame com título para o robô.
                                   font=("Arial", 18, "bold"), bg="#f5f5f5")
        frame_robo.grid(row=0, column=2, sticky="nsew", padx=(10, 0)) # Posiciona o frame na grade (coluna 2).

        # Frame para as informações do robô.
        frame_info_robo = tk.Frame(frame_robo, bg="#f5f5f5")
        frame_info_robo.pack(fill="x", pady=15) # Adiciona o frame.

        # Label para mostrar o valor-alvo (igual ao do jogador).
        label_valor_alvo_robo = tk.Label(frame_info_robo, text=f"🎯 VALOR-ALVO: R$ {self.valor_alvo:.2f}",
                                         font=("Arial", 18, "bold"), bg="#f5f5f5")
        label_valor_alvo_robo.pack() # Adiciona o label.

        # Label para mostrar o total da cesta do robô.
        self.label_total_robo = tk.Label(frame_info_robo, text=f"💰 TOTAL ROBO: R$ {self.total_robo:.2f}",
                                         font=("Arial", 17), bg="#f5f5f5")
        self.label_total_robo.pack(pady=8) # Adiciona o label.
        
        # Frame para o saldo do robô.
        frame_saldo_robo = tk.Frame(frame_info_robo, bg="#f5f5f5")
        frame_saldo_robo.pack(fill="x", pady=(15, 0), padx=20) # Adiciona o frame.

        saldo_restante_robo = self.valor_alvo - self.total_robo # Calcula o saldo.
        self.label_saldo_restante_robo = tk.Label(frame_saldo_robo, text=f"SALDO: R$ {saldo_restante_robo:.2f}",
                                                  font=("Arial", 18, "bold"), bg="#f5f5f5", fg="#17a2b8")
        self.label_saldo_restante_robo.pack(side="left", expand=True) # Adiciona o label.

        # Botão para ouvir o saldo do robô.
        self.botao_ouvir_saldo_robo = tk.Button(frame_saldo_robo, text="🔊 Ouvir Saldo",
                                                font=("Arial", 14), bg="#17a2b8", fg="white", relief="flat",
                                                command=self.falar_saldo_restante_robo, padx=15, pady=5)
        self.botao_ouvir_saldo_robo.pack(side="right", expand=True) # Adiciona o botão.

        # Mostra qual algoritmo o robo está usando.
        self.label_algoritmo_robo = tk.Label(frame_info_robo, text=f"Algoritmo: {self.variavel_algoritmo.get()}",
                                             font=("Arial", 17), bg="#f5f5f5")
        self.label_algoritmo_robo.pack(pady=(20, 0)) # Adiciona o label.

        # Label de status para indicar de quem é o turno.
        self.label_robo_status = tk.Label(frame_info_robo, text="É a sua vez de jogar!",
                                           font=("Arial", 15, "bold"), bg="#f5f5f5", fg="#27ae60")
        self.label_robo_status.pack() # Adiciona o label.
        
        # Estrutura da cesta do robô com Canvas.
        frame_cesta_robo = tk.LabelFrame(frame_robo, text="Cesta do Robo",
                                             font=("Arial", 15, "bold"), bg="#f5f5f5", bd=2)
        frame_cesta_robo.pack(fill="both", expand=True, pady=15, padx=10) # Adiciona o frame.

        # Canvas para desenhar a cesta do robô.
        self.canvas_cesta_robo = tk.Canvas(frame_cesta_robo, bg="white", highlightthickness=0)
        self.canvas_cesta_robo.pack(fill="both", expand=True) # Adiciona o canvas.
        
        # Listbox para mostrar os itens na cesta do robô, posicionada sobre o canvas.
        self.display_cesta_robo = tk.Listbox(self.canvas_cesta_robo, font=("Arial", 14),
                                                bg="white", selectbackground="#3498db",
                                                bd=0, highlightthickness=0)
        
        # Vincula o evento de redimensionamento à função de redesenho.
        self.canvas_cesta_robo.bind("<Configure>", self.redesenhar_cesta_robo)
        
        # Frame para os botões de "Voltar ao Menu" e "Nova Rodada".
        frame_novo_jogo = tk.Frame(self.master, bg="#f5f5f5")
        frame_novo_jogo.pack(fill="x", pady=20) # Adiciona o frame na parte inferior da janela.
        frame_botoes_finais = tk.Frame(frame_novo_jogo, bg="#f5f5f5")
        frame_botoes_finais.pack() # Centraliza os botões dentro do frame.
        tk.Button(frame_botoes_finais, text="Voltar ao Menu", # Cria o botão de voltar.
                  font=("Arial", 16, "bold"), bg="#6c757d", fg="white",
                  command=self.mostrar_tela_bem_vindo, padx=20, pady=10).pack(side="left", padx=15) # Adiciona o botão.
        tk.Button(frame_botoes_finais, text="Nova Rodada", # Cria o botão de nova rodada.
                  font=("Arial", 16, "bold"), bg="#ff6b00", fg="white",
                  command=self.iniciar_nova_rodada, padx=20, pady=10).pack(side="left", padx=15) # Adiciona o botão.

        # Exibe os produtos pela primeira vez e redesenha as cestas vazias.
        self.exibir_produtos() # Chama a função para popular a lista de produtos.
        self.master.update_idletasks() # Força a interface a se atualizar para garantir que os widgets tenham tamanho antes de desenhar.
        self.redesenhar_cesta_jogador() # Desenha a cesta do jogador.
        self.redesenhar_cesta_robo() # Desenha a cesta do robô.

    # Função para desenhar a cesta de compras do jogador.
    def redesenhar_cesta_jogador(self, event=None):
        self.canvas_cesta_jogador.delete("all") # Apaga todos os desenhos anteriores no canvas.
        width = self.canvas_cesta_jogador.winfo_width() # Pega a largura atual do canvas.
        height = self.canvas_cesta_jogador.winfo_height() # Pega a altura atual do canvas.

        if width < 50 or height < 50: return # Se o canvas for muito pequeno, não desenha nada.

        # Cores.
        cor_cesta_verde = "#009933" # Define a cor de preenchimento da cesta.
        cor_borda_verde = "#006622" # Define a cor da borda da cesta.
        cor_alca_preta = "#1a1a1a" # Define a cor da alça.

        # Proporções da cesta.
        x_center, y_center = width / 2, height / 2 # Calcula o centro do canvas.
        cesta_w = width * 0.85 # Define a largura da cesta como 85% da largura do canvas.
        cesta_h = height * 0.5 # Define a altura da cesta como 50% da altura do canvas.
        
        # Pontos do corpo da cesta (trapézio).
        x1 = x_center - cesta_w / 2 # Ponto superior esquerdo.
        y1 = y_center - cesta_h / 2 + 20 # Ponto superior esquerdo (com um deslocamento para baixo).
        x2 = x_center + cesta_w / 2 # Ponto superior direito.
        y2 = y1 # Mesma altura do ponto y1.
        x3 = x_center + cesta_w / 2.5 # Ponto inferior direito (mais estreito).
        y3 = y_center + cesta_h / 2 + 20 # Ponto inferior direito.
        x4 = x_center - cesta_w / 2.5 # Ponto inferior esquerdo (mais estreito).
        y4 = y3 # Mesma altura do ponto y3.
        self.canvas_cesta_jogador.create_polygon(x1, y1, x2, y2, x3, y3, x4, y4, fill=cor_cesta_verde, outline=cor_borda_verde, width=2) # Desenha o polígono.
        
        # Borda superior da cesta.
        self.canvas_cesta_jogador.create_rectangle(x1 - 2, y1 - 10, x2 + 2, y2, fill=cor_cesta_verde, outline=cor_borda_verde, width=2) # Desenha um retângulo para a borda.

        # Linhas verticais para simular as frestas.
        num_linhas = 8 # Define o número de linhas a serem desenhadas.
        for i in range(num_linhas + 1): # Itera para criar cada linha.
            percent = i / num_linhas # Calcula a porcentagem do caminho percorrido.
            top_x = x1 + percent * (x2 - x1) # Calcula a coordenada X superior da linha (interpolação linear).
            bottom_x = x4 + percent * (x3 - x4) # Calcula a coordenada X inferior da linha (interpolação linear).
            top_y = y1 # A coordenada Y superior é constante.
            bottom_y = y3 # A coordenada Y inferior é constante.
            self.canvas_cesta_jogador.create_line(top_x, top_y, bottom_x, bottom_y, fill=cor_borda_verde, width=1) # Desenha a linha.

        # Alças da cesta.
        alca_h = cesta_h * 0.7 # Define a altura da alça.
        alca_w_top = cesta_w * 0.7 # Define a largura da parte superior da alça.
        alca_w_bottom = cesta_w * 0.9 # Define a largura da base da alça.
        
        # Pontos da alça.
        p1 = (x_center - alca_w_bottom / 2, y1 - 5) # Ponto 1.
        p2 = (x_center - alca_w_top / 2, y1 - alca_h) # Ponto 2.
        p3 = (x_center + alca_w_top / 2, y1 - alca_h) # Ponto 3.
        p4 = (x_center + alca_w_bottom / 2, y1 - 5) # Ponto 4.
        self.canvas_cesta_jogador.create_polygon(p1, p2, p3, p4, fill="", outline=cor_alca_preta, width=12, joinstyle=tk.ROUND) # Desenha a alça como um polígono sem preenchimento.

        # Se a cesta estiver vazia, exibe uma mensagem.
        if self.display_cesta_jogador.size() == 0: # Verifica o número de itens na Listbox.
            self.canvas_cesta_jogador.create_text(width / 2, height - 20, text="Seus itens aparecerão aqui!", font=("Arial", 14), fill="#888888") # Desenha o texto.

        # Posiciona a Listbox dentro do desenho da cesta.
        padding = 15 # Define um espaçamento interno.
        listbox_x = x4 + padding # Calcula a posição X da Listbox.
        listbox_y = y1 + padding / 2 # Calcula a posição Y da Listbox.
        listbox_width = (x3 - x4) - (padding * 2) # Calcula a largura da Listbox.
        listbox_height = (y3 - y1) - padding # Calcula a altura da Listbox.

        # Adiciona a Listbox ao canvas como uma "janela".
        self.canvas_cesta_jogador.create_window(listbox_x, listbox_y, anchor="nw", window=self.display_cesta_jogador, width=max(10, listbox_width), height=max(10, listbox_height))

    # Função para desenhar a cesta de compras do robô.
    def redesenhar_cesta_robo(self, event=None):
        self.canvas_cesta_robo.delete("all") # Apaga todos os desenhos anteriores no canvas.
        width = self.canvas_cesta_robo.winfo_width() # Pega a largura atual do canvas.
        height = self.canvas_cesta_robo.winfo_height() # Pega a altura atual do canvas.

        if width < 50 or height < 50: return # Se o canvas for muito pequeno, não desenha nada.

        # Cores (as mesmas da cesta do jogador).
        cor_cesta_verde = "#009933"
        cor_borda_verde = "#006622"
        cor_alca_preta = "#1a1a1a"

        # Proporções da cesta.
        x_center, y_center = width / 2, height / 2
        cesta_w = width * 0.85
        cesta_h = height * 0.5

        # Pontos do corpo da cesta (trapézio).
        x1 = x_center - cesta_w / 2
        y1 = y_center - cesta_h / 2 + 20
        x2 = x_center + cesta_w / 2
        y2 = y1
        x3 = x_center + cesta_w / 2.5
        y3 = y_center + cesta_h / 2 + 20
        x4 = x_center - cesta_w / 2.5
        y4 = y3
        self.canvas_cesta_robo.create_polygon(x1, y1, x2, y2, x3, y3, x4, y4, fill=cor_cesta_verde, outline=cor_borda_verde, width=2) # Desenha o corpo da cesta.

        # Borda superior da cesta.
        self.canvas_cesta_robo.create_rectangle(x1 - 2, y1 - 10, x2 + 2, y2, fill=cor_cesta_verde, outline=cor_borda_verde, width=2) # Desenha a borda.
        
        # Linhas verticais para simular as frestas.
        num_linhas = 8
        for i in range(num_linhas + 1):
            percent = i / num_linhas
            top_x = x1 + percent * (x2 - x1)
            bottom_x = x4 + percent * (x3 - x4)
            top_y = y1
            bottom_y = y3
            self.canvas_cesta_robo.create_line(top_x, top_y, bottom_x, bottom_y, fill=cor_borda_verde, width=1) # Desenha cada linha.

        # Alças da cesta.
        alca_h = cesta_h * 0.7
        alca_w_top = cesta_w * 0.7
        alca_w_bottom = cesta_w * 0.9
        
        p1 = (x_center - alca_w_bottom / 2, y1 - 5)
        p2 = (x_center - alca_w_top / 2, y1 - alca_h)
        p3 = (x_center + alca_w_top / 2, y1 - alca_h)
        p4 = (x_center + alca_w_bottom / 2, y1 - 5)
        self.canvas_cesta_robo.create_polygon(p1, p2, p3, p4, fill="", outline=cor_alca_preta, width=12, joinstyle=tk.ROUND) # Desenha a alça.

        # Se a cesta do robô estiver vazia, exibe uma mensagem.
        if self.display_cesta_robo.size() == 0:
            self.canvas_cesta_robo.create_text(width / 2, height - 20, text="Cesta do Robô", font=("Arial", 14), fill="#888888") # Desenha o texto.

        # Posiciona a Listbox do robô dentro do desenho.
        padding = 15
        listbox_x = x4 + padding
        listbox_y = y1 + padding / 2
        listbox_width = (x3 - x4) - (padding * 2)
        listbox_height = (y3 - y1) - padding

        # Adiciona a Listbox do robô ao canvas.
        self.canvas_cesta_robo.create_window(listbox_x, listbox_y, anchor="nw", window=self.display_cesta_robo, width=max(10, listbox_width), height=max(10, listbox_height))

    # Função auxiliar para habilitar ou desabilitar todos os controles do jogador.
    def _definir_estado_controles_jogador(self, state):
        # Altera o estado (NORMAL ou DISABLED) dos botões do jogador.
        self.botao_remover_jogador.config(state=state) # Altera o estado do botão de remover.
        self.botao_finalizar_jogador.config(state=state) # Altera o estado do botão de finalizar.
        self.botao_microfone.config(state=state) # Altera o estado do botão de microfone.
        self.botao_ouvir_saldo.config(state=state) # Altera o estado do botão de ouvir saldo.
        
        # Percorre os botões de adicionar produto.
        for botao in self.botoes_produtos: # Itera sobre a lista de botões de produtos.
            # Só reabilita o botão se ele não estiver "Fora de Estoque".
            if state == tk.NORMAL and botao.cget('text') != "Fora de Estoque": # Verifica se o estado é para habilitar e se há estoque.
                botao.config(state=tk.NORMAL) # Habilita o botão.
            # Desabilita todos se o estado for DISABLED.
            elif state == tk.DISABLED: # Se o estado for para desabilitar.
                botao.config(state=tk.DISABLED) # Desabilita o botão.

    # Lógica para passar o turno do jogador para o robo.
    def _passar_turno_para_robo(self):
        if not self.jogo_ativo: return # Se o jogo não estiver ativo, não faz nada.
        
        self.turno_do_jogador = False # Muda o turno para o robô.
        self._definir_estado_controles_jogador(tk.DISABLED) # Desabilita os controles do jogador.
        self.label_robo_status.config(text="🤔 Robo pensando...", fg="#e67e22") # Atualiza o status para "pensando".
        # Espera 1 segundo (1000 ms) antes de executar o turno do robo, para dar um efeito de "pensamento".
        self.master.after(1000, self.executar_turno_robo) # Agenda a execução do turno do robô.
    
    # Lógica para passar o turno do robo de volta para o jogador.
    def _passar_turno_para_jogador(self):
        if not self.jogo_ativo: return # Se o jogo não estiver ativo, não faz nada.

        self.turno_do_jogador = True # Muda o turno para o jogador.
        self._definir_estado_controles_jogador(tk.NORMAL) # Habilita os controles do jogador.
        self.label_robo_status.config(text="É a sua vez de jogar!", fg="#27ae60") # Atualiza o status para a vez do jogador.

    # Inicia o processo de escuta do comando de voz em uma thread separada para não travar a interface.
    def iniciar_escuta_produto(self):
        self.botao_microfone.config(state=tk.DISABLED, bg="#c0392b") # Desabilita o botão do microfone e muda a cor para indicar que está ouvindo.
        thread = threading.Thread(target=self.processar_comando_de_voz, daemon=True) # Cria uma nova thread para o processo de voz.
        thread.start() # Inicia a thread.
    
    # Prepara o texto para comparação: converte para minúsculas e remove acentos.
    def _preprocessar_texto(self, text):
        return unidecode(text.lower()) # Retorna o texto sem acentos e em letras minúsculas.

    # Usa 'thefuzz' para encontrar o produto mais parecido com o que foi falado.
    def _encontrar_melhor_produto_correspondente(self, spoken_text):
        product_names = list(self.produtos_com_estoque["Todos"].keys()) # Pega uma lista com todos os nomes de produtos.
        # Cria um dicionário que mapeia nomes processados para nomes originais, para facilitar a busca.
        processed_names = {self._preprocessar_texto(name): name for name in product_names}
        # Encontra a melhor correspondência entre o texto falado (processado) e a lista de nomes (processados).
        result = process.extractOne(self._preprocessar_texto(spoken_text), processed_names.keys())
        # Retorna o nome original do produto e a pontuação de similaridade (0 a 100).
        return (processed_names[result[0]], result[1]) if result else (None, 0)

    # Encontra o item mais parecido com o que foi falado, mas buscando apenas na cesta do jogador.
    def _encontrar_melhor_correspondencia_na_cesta(self, spoken_text):
        if not self.cesta_jogador: return None, 0, -1 # Se a cesta estiver vazia, retorna sem fazer nada.
        
        cart_names = [item[0] for item in self.cesta_jogador] # Cria uma lista com os nomes dos itens na cesta.
        result = process.extractOne(self._preprocessar_texto(spoken_text), cart_names) # Encontra a melhor correspondência.
        
        if result: # Se encontrou um resultado.
            best_match, score = result # Pega o nome e a pontuação.
            # Encontra o índice do item na cesta para poder removê-lo.
            for i, item in enumerate(self.cesta_jogador): # Itera sobre a cesta.
                if item[0] == best_match: return best_match, score, i # Retorna o nome, a pontuação e o índice.
        return None, 0, -1 # Se não encontrou, retorna valores padrão.
        
    # Função principal que gerencia o reconhecimento de voz.
    def processar_comando_de_voz(self):
        if not self.turno_do_jogador: # Verifica se é o turno do jogador.
            self.master.after(0, self.label_status_voz.config, {'text': 'Aguarde seu turno.'}) # Atualiza o status na thread principal.
            self.master.after(1000, self.reativar_microfone) # Reativa o microfone depois de um tempo.
            return # Sai da função.
            
        self.master.after(0, self.label_status_voz.config, {'text': 'Ouvindo...'}) # Atualiza o status para "Ouvindo...".
        try: # Inicia o bloco de tratamento de exceções.
            with sr.Microphone() as source: # Usa o microfone como fonte de áudio.
                self.recognizer.adjust_for_ambient_noise(source, duration=1) # Ajusta o reconhecedor ao ruído ambiente.
                audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=5) # Ouve o áudio por até 5 segundos.
            
            self.master.after(0, self.label_status_voz.config, {'text': 'Processando...'}) # Atualiza o status para "Processando...".
            # Usa a API de reconhecimento do Google para converter o áudio em texto.
            texto_falado = self.recognizer.recognize_google(audio, language='pt-BR').lower() # Converte para texto em português e minúsculas.
            self.master.after(0, self.label_status_voz.config, {'text': f'Você disse: "{texto_falado}"'}) # Mostra o texto reconhecido.

            # Verifica se o comando é para adicionar ou remover um item.
            if "adicionar" in texto_falado: self._adicionar_produto_por_voz(texto_falado) # Chama a função de adicionar.
            elif "remover" in texto_falado: self._remover_produto_por_voz(texto_falado) # Chama a função de remover.
            else: self.master.after(0, self.label_status_voz.config, {'text': "Comando não reconhecido."}) # Informa que o comando é inválido.
        
        # Tratamento de erros comuns do reconhecimento de voz.
        except sr.WaitTimeoutError: # Se não detectar fala.
            self.master.after(0, self.label_status_voz.config, {'text': 'Nenhuma fala detectada.'})
        except sr.UnknownValueError: # Se não entender o que foi dito.
            self.master.after(0, self.label_status_voz.config, {'text': 'Não consegui entender.'})
        except sr.RequestError as e: # Se houver um erro de conexão com a API do Google.
            self.master.after(0, self.label_status_voz.config, {'text': f"Erro na API; {e}"})
        finally: # Executa este bloco independentemente de ter ocorrido erro ou não.
            # Reativa o microfone após um tempo.
            self.master.after(2000, self.reativar_microfone) # Agenda a reativação do microfone.

    # Processa o comando de voz para adicionar um item.
    def _adicionar_produto_por_voz(self, texto_falado):
        # Extrai o nome do produto da frase falada (pega tudo que vem depois de "adicionar").
        nome_produto_falado = texto_falado.split("adicionar", 1)[1].strip()
        if not nome_produto_falado: # Se não houver nome de produto.
            self.master.after(0, self.label_status_voz.config, {'text': 'Diga o nome do produto.'}) # Pede o nome.
            return # Sai da função.
        
        produto_nome, pontuacao = self._encontrar_melhor_produto_correspondente(nome_produto_falado) # Procura o produto mais parecido.
        
        # Se a similaridade for alta (75% ou mais), adiciona o produto.
        if pontuacao >= 75:
            # Chama a função de adicionar à cesta. 'master.after' garante que seja na thread principal da GUI.
            self.master.after(0, self.adicionar_a_cesta_jogador, produto_nome, True)
            self.master.after(0, self.label_status_voz.config, {'text': f'"{produto_nome}" adicionado!'}) # Confirma a adição.
        else: # Se a similaridade for baixa.
            feedback = f'Produto "{nome_produto_falado}" não encontrado.' # Monta a mensagem de erro.
            # Se a pontuação for razoável, sugere o produto mais próximo.
            if produto_nome and pontuacao > 50:
                feedback += f'\nVocê quis dizer "{produto_nome}"?' # Adiciona a sugestão.
            self.master.after(0, self.label_status_voz.config, {'text': feedback}) # Mostra o feedback.

    # Processa o comando de voz para remover um item.
    def _remover_produto_por_voz(self, texto_falado):
        nome_produto_falado = texto_falado.split("remover", 1)[1].strip() # Pega o nome do produto.
        if not nome_produto_falado: # Se não houver nome.
            self.master.after(0, self.label_status_voz.config, {'text': 'Diga o nome do produto.'}) # Pede o nome.
            return # Sai da função.
        
        produto_nome, pontuacao, indice = self._encontrar_melhor_correspondencia_na_cesta(nome_produto_falado) # Procura o produto na cesta.

        # Se encontrou um item similar na cesta, remove-o.
        if pontuacao >= 75:
            self.master.after(0, self.remover_da_cesta, indice) # Chama a função de remover, passando o índice do item.
        else: # Se não encontrou.
            feedback = f'"{nome_produto_falado}" não está na cesta.' # Monta a mensagem de erro.
            if produto_nome and pontuacao > 50: # Se houver uma sugestão razoável.
                feedback += f'\nVocê quis dizer "{produto_nome}"?' # Adiciona a sugestão.
            self.master.after(0, self.label_status_voz.config, {'text': feedback}) # Mostra o feedback.

    # Reativa o botão do microfone e reseta o texto de status.
    def reativar_microfone(self):
        if self.jogo_ativo: # Se o jogo ainda estiver rolando.
            # Define o estado e a cor do botão com base no turno atual.
            state, bg_color = (tk.NORMAL, "#8e44ad") if self.turno_do_jogador else (tk.DISABLED, "#c0392b")
            self.botao_microfone.config(state=state, bg=bg_color) # Aplica as configurações.
            if self.turno_do_jogador: # Se for a vez do jogador.
                self.label_status_voz.config(text="Diga 'adicionar' ou 'remover' [produto]") # Reseta o texto de instrução.

    # Converte o saldo do jogador em texto e o fala.
    def falar_saldo_restante(self):
        saldo = self.valor_alvo - self.total_jogador # Calcula o saldo.
        reais, centavos = int(saldo), int(round((saldo - int(saldo)) * 100)) # Separa reais e centavos.
        texto = f"Seu saldo restante é de {reais} reais" + (f" e {centavos} centavos." if centavos > 0 else ".") # Monta a frase.
        # Usa uma thread para falar, evitando que a interface congele.
        threading.Thread(target=self.falar_texto, args=(texto,), daemon=True).start()

    # Converte o saldo do robo em texto e o fala.
    def falar_saldo_restante_robo(self):
        saldo = self.valor_alvo - self.total_robo # Calcula o saldo.
        reais, centavos = int(saldo), int(round((saldo - int(saldo)) * 100)) # Separa reais e centavos.
        texto = f"O saldo restante do robo é de {reais} reais" + (f" e {centavos} centavos." if centavos > 0 else ".") # Monta a frase.
        threading.Thread(target=self.falar_texto, args=(texto,), daemon=True).start() # Inicia a fala em uma thread.

    # Atualiza a exibição dos produtos na tela do meio.
    def exibir_produtos(self):
        # Limpa os produtos antigos.
        for widget in self.frame_rolavel_produtos.winfo_children(): widget.destroy() # Remove todos os widgets do frame de produtos.
        
        self.botoes_produtos = [] # Reseta a lista de referências dos botões.
        produtos = self.produtos_com_estoque[self.variavel_depto.get()] # Pega a lista de produtos do departamento selecionado.
        
        # Cria um card para cada produto.
        for i, (produto, dados) in enumerate(produtos.items()): # Itera sobre os produtos.
            # Cria um frame para o card do produto.
            frame_produto = tk.Frame(self.frame_rolavel_produtos, bd=1, relief="solid", bg="white", padx=15, pady=15)
            frame_produto.grid(row=i // 3, column=i % 3, padx=12, pady=12, sticky="nsew") # Posiciona o card em uma grade de 3 colunas.
            tk.Label(frame_produto, text=produto[:20], font=("Arial", 12), bg="white").pack(anchor="w") # Adiciona o nome do produto.
            tk.Label(frame_produto, text=f"R${dados['preco']:.2f}", font=("Arial", 16, "bold"), fg="#e74c3c", bg="white").pack(anchor="w") # Adiciona o preço.
            tk.Label(frame_produto, text=f"Estoque: {dados['estoque']}", font=("Arial", 11, "italic"), fg="#555", bg="white").pack(anchor="w") # Adiciona o estoque.
            
            # Define a aparência do botão com base no estoque e no turno.
            state, text, color = (tk.DISABLED, "Fora de Estoque", "#95a5a6") if dados['estoque'] <= 0 else (tk.NORMAL, "Adicionar", "#27ae60")
            if not self.turno_do_jogador: state = tk.DISABLED # Se não for o turno do jogador, desabilita o botão.

            # A função lambda é usada para passar o nome do produto correto para a função de adicionar.
            botao = tk.Button(frame_produto, text=text, font=("Arial", 12, "bold"), fg="white", relief="flat", pady=5, bg=color, state=state,
                              command=lambda p=produto: self.adicionar_a_cesta_jogador(p))
            botao.pack(side="bottom", fill="x") # Adiciona o botão ao card.
            self.botoes_produtos.append(botao) # Adiciona a referência do botão à lista de botões.
            
    # Lógica para adicionar um produto à cesta do jogador.
    def adicionar_a_cesta_jogador(self, nome_produto, falar_nome=True):
        if not self.jogo_ativo or not self.turno_do_jogador: return # Verifica se o jogo está ativo e se é o turno do jogador.
        
        dados = self.produtos_com_estoque["Todos"][nome_produto] # Pega os dados do produto.
        
        # Verifica se há estoque.
        if dados["estoque"] <= 0:
            messagebox.showwarning("Sem Estoque", f"'{nome_produto}' está fora de estoque!") # Mostra um aviso.
            return # Sai da função.
            
        # Verifica se o preço não excede o valor-alvo.
        if self.total_jogador + dados["preco"] <= self.valor_alvo:
            self.cesta_jogador.append((nome_produto, dados["preco"])) # Adiciona o item à lista da cesta.
            self.total_jogador += dados["preco"] # Atualiza o total.
            dados["estoque"] -= 1 # Decrementa o estoque.
            
            # Atualiza a interface.
            self.display_cesta_jogador.insert(tk.END, f"{nome_produto} - R$ {dados['preco']:.2f}") # Adiciona o item na Listbox.
            self.atualizar_saldo_jogador() # Atualiza os labels de total e saldo.
            
            # Redesenha a cesta para remover a mensagem de "vazio", se for o primeiro item.
            self.redesenhar_cesta_jogador()
            
            if falar_nome: # Se a adição não foi por clique (foi por voz).
                threading.Thread(target=self.falar_texto, args=(f"{nome_produto} adicionado",), daemon=True).start() # Fala o nome do produto.
            
            self.exibir_produtos() # Atualiza os produtos para mostrar o novo estoque.
            
            # Verifica se o jogador atingiu o valor exato.
            if round(self.total_jogador, 2) == self.valor_alvo:
                messagebox.showinfo("Parabéns!", "🎉 Você atingiu o valor exato!") # Mostra uma mensagem de parabéns.
                self.finalizar_compra() # Finaliza o jogo.
            else:
                self._passar_turno_para_robo() # Passa o turno para o robô.
        else: # Se o orçamento for excedido.
            messagebox.showwarning("Orçamento Excedido", f"Não é possível adicionar '{nome_produto}'.") # Mostra um aviso.

    # Lógica para remover um item da cesta do jogador.
    def remover_da_cesta(self, index=None):
        if not self.jogo_ativo or not self.turno_do_jogador: return # Verifica as condições do jogo.
        
        # Se um índice não foi passado (pelo clique), pega o item selecionado na Listbox.
        if index is None:
            selection = self.display_cesta_jogador.curselection() # Pega a seleção atual.
            if not selection: return # Se nada estiver selecionado, sai.
            index = selection[0] # Pega o índice do item selecionado.
            
        if 0 <= index < len(self.cesta_jogador): # Verifica se o índice é válido.
            nome, preco = self.cesta_jogador.pop(index) # Remove o item da lista e pega seus dados.
            self.total_jogador -= preco # Subtrai o preço do total.
            self.produtos_com_estoque["Todos"][nome]["estoque"] += 1 # Devolve o item ao estoque.
            
            # Atualiza a interface.
            self.display_cesta_jogador.delete(index) # Remove o item da Listbox.
            self.atualizar_saldo_jogador() # Atualiza os labels de saldo.
            
            # Redesenha a cesta para mostrar a mensagem de "vazio", se for o caso.
            self.redesenhar_cesta_jogador()
            
            self.exibir_produtos() # Atualiza a exibição de produtos (estoque).
            threading.Thread(target=self.falar_texto, args=(f"{nome} removido",), daemon=True).start() # Fala o nome do item removido.
    
    # Atualiza os labels de total e saldo do jogador.
    def atualizar_saldo_jogador(self):
        self.label_total_jogador.config(text=f"💰 SEU TOTAL: R$ {self.total_jogador:.2f}") # Atualiza o label do total.
        saldo = self.valor_alvo - self.total_jogador # Calcula o novo saldo.
        self.label_saldo_restante.config(text=f"SALDO: R$ {saldo:.2f}") # Atualiza o label do saldo.

    # Lógica do turno do robo (IA).
    def executar_turno_robo(self):
        # Encontra o melhor item para adicionar com base no algoritmo escolhido.
        melhor_item = self._encontrar_melhor_proximo_item()
        
        if melhor_item: # Se encontrou um item.
            nome, preco = melhor_item # Desempacota o nome e o preço.
            # Adiciona o item à cesta do robo.
            self.cesta_robo.append((nome, preco)) # Adiciona à lista da cesta.
            self.total_robo += preco # Atualiza o total do robô.
            self.produtos_com_estoque["Todos"][nome]["estoque"] -= 1 # Remove do estoque compartilhado.
            self.atualizar_display_robo() # Atualiza a interface do robo.
        else: # Se não encontrou nenhum item válido.
            # Se não encontrou nenhum item válido, o robo passa a vez.
            print("Robo passou a vez.") # Imprime uma mensagem no console.
        
        self.exibir_produtos() # Atualiza a exibição de produtos para refletir a mudança no estoque.
        
        self._passar_turno_para_jogador() # Devolve o turno para o jogador.
    
    # Função heurística para os algoritmos. Calcula a diferença absoluta até o valor-alvo
    # e multiplica por um fator para dar peso equivalente ao custo do passo (g).
    def heuristica(self, total):
        return abs(self.valor_alvo - total) * self.FATOR_HEURISTICA # Retorna o valor da heurística.

    # Implementação do algoritmo A* para encontrar a melhor combinação de produtos.
    def busca_a_estrela(self):
        # 1. Cria uma lista de produtos disponíveis com base no estoque.
        disponiveis = [(n, d["preco"]) for n, d in self.produtos_com_estoque["Todos"].items() if d["estoque"] > 0]
        # 2. Inicializa a fronteira (fila de prioridade) e o conjunto de visitados.
        fronteira, visitados = [], set()
        # 3. O estado inicial é a cesta atual do robo.
        h_inicial = self.heuristica(self.total_robo) # Calcula a heurística inicial.
        # A fronteira armazena uma tupla: (f_score, h_score, total_monetario, caminho_da_cesta)
        heapq.heappush(fronteira, (len(self.cesta_robo) + h_inicial, h_inicial, self.total_robo, self.cesta_robo.copy()))
        # Guarda a melhor solução encontrada até agora como fallback, caso não encontre a solução exata.
        melhor_solucao, melhor_h = (self.cesta_robo.copy(), self.total_robo), h_inicial
        
        limite, passo = 2000, 0 # Limite de segurança para evitar loops infinitos em casos complexos.
        while fronteira and passo < limite: # Enquanto houver estados na fronteira e não atingir o limite.
            passo += 1 # Incrementa o contador de passos.
            _, h_atual, total, cesta = heapq.heappop(fronteira) # Pega o estado com o menor f_score.
            
            # Cria um identificador único para o estado atual (total e itens na cesta).
            estado = (round(total, 2), tuple(sorted(p[0] for p in cesta)))
            if estado in visitados: continue # Se já visitou este estado, pula.
            visitados.add(estado) # Adiciona o estado ao conjunto de visitados.
            
            # Se o estado atual é o mais próximo do alvo que já vimos, salvamos.
            if h_atual < melhor_h: melhor_solucao, melhor_h = (cesta.copy(), total), h_atual
            
            # Se encontramos a solução exata (ou muito próxima), retornamos.
            if abs(total - self.valor_alvo) < 0.01: return cesta
            
            # 4. Expande para os próximos estados possíveis.
            itens_na_cesta = {p[0] for p in cesta} # Cria um conjunto com os nomes dos itens na cesta atual.
            for produto, preco in disponiveis: # Itera sobre todos os produtos disponíveis.
                if total + preco <= self.valor_alvo and produto not in itens_na_cesta: # Verifica se o produto cabe no orçamento e não está na cesta.
                    nova_cesta = cesta + [(produto, preco)] # Cria uma nova cesta com o produto adicionado.
                    # Calcula os custos para o novo estado.
                    h_novo = self.heuristica(total + preco) # Custo estimado para o futuro (heurística).
                    g_novo = len(nova_cesta) # Custo do caminho percorrido (número de itens).
                    f_novo = g_novo + h_novo # Custo total (f = g + h).
                    heapq.heappush(fronteira, (f_novo, h_novo, total + preco, nova_cesta)) # Adiciona o novo estado à fronteira.
                    
        # Se o loop terminar sem encontrar a solução exata, retorna a melhor solução parcial encontrada.
        return melhor_solucao[0]

    # Estratégia do robo para escolher o próximo item.
    def _encontrar_melhor_proximo_item(self):
        # --- Lógica da Busca Gulosa (com Heurística) ---
        if self.variavel_algoritmo.get() == "Gulosa":
            # Pega todos os itens que cabem no orçamento.
            disponiveis = [(n, d["preco"]) for n, d in self.produtos_com_estoque["Todos"].items() 
                           if d["estoque"] > 0 and self.total_robo + d["preco"] <= self.valor_alvo]
            
            if not disponiveis: # Se não houver itens disponíveis que caibam no orçamento.
                return None # Retorna nada.
            
            # Escolhe o item que, ao ser adicionado, resulta no menor valor heurístico (mais perto do alvo).
            melhor_escolha = min(
                disponiveis,
                key=lambda item: self.heuristica(self.total_robo + item[1]) # A chave para a minimização é o valor da heurística.
            )
            return melhor_escolha # Retorna o melhor item encontrado.
        
        # --- Lógica do Algoritmo A* ---
        else: # Se o algoritmo for A*.
            # 1. Roda a busca A* para encontrar a cesta final ideal a partir do estado atual.
            cesta_ideal = self.busca_a_estrela()
            if not cesta_ideal: return None # Se não encontrou um caminho, não faz nada.
            
            # 2. Descobre qual o próximo item do caminho ideal que o robo deve pegar.
            itens_atuais = {item[0] for item in self.cesta_robo} # Pega os itens que o robô já tem.
            for item in cesta_ideal: # Itera sobre os itens da cesta ideal encontrada pelo A*.
                if item[0] not in itens_atuais: # Encontra o primeiro item que o robô ainda não tem.
                    # Verifica se o item ainda está em estoque (pode ter sido pego pelo jogador).
                    dados = self.produtos_com_estoque["Todos"].get(item[0]) # Pega os dados do produto.
                    if dados and dados["estoque"] > 0: # Confirma se ainda há estoque.
                        return item # Retorna este item como o próximo melhor passo.
            return None # Se todos os itens da cesta ideal já foram pegos ou estão sem estoque, não faz nada.
            
    # Atualiza a interface do robo (cesta, total, saldo).
    def atualizar_display_robo(self):
        self.display_cesta_robo.delete(0, tk.END) # Limpa a Listbox do robô.
        for produto, preco in self.cesta_robo: # Itera sobre os itens na cesta do robô.
            self.display_cesta_robo.insert(tk.END, f"{produto} - R$ {preco:.2f}") # Adiciona cada item à Listbox.
        
        # Redesenha a cesta do robô.
        self.redesenhar_cesta_robo()
        
        self.label_total_robo.config(text=f"💰 TOTAL ROBO: R$ {self.total_robo:.2f}") # Atualiza o label do total.
        saldo = self.valor_alvo - self.total_robo # Calcula o novo saldo.
        self.label_saldo_restante_robo.config(text=f"SALDO: R$ {saldo:.2f}") # Atualiza o label do saldo.

    # Finalização e resultado do jogo.
    def finalizar_compra(self):
        if not self.jogo_ativo: return # Se o jogo já foi finalizado, não faz nada.
        self.jogo_ativo = False # Marca o jogo como inativo.
        
        # Calcula a diferença de cada jogador para o valor-alvo.
        diff_jogador = abs(self.valor_alvo - self.total_jogador)
        diff_robo = abs(self.valor_alvo - self.total_robo)
        
        # Determina o vencedor.
        vencedor = "EMPATE" # Assume empate como padrão.
        # Critério 1: Menor diferença.
        if diff_jogador < diff_robo: # Se o jogador está mais perto.
            vencedor = "JOGADOR"
        elif diff_robo < diff_jogador: # Se o robô está mais perto.
            vencedor = "ROBO"
        # Critério 2 (desempate): Menos itens na cesta.
        elif len(self.cesta_jogador) < len(self.cesta_robo): # Se o jogador tem menos itens.
            vencedor = "JOGADOR"
        elif len(self.cesta_robo) < len(self.cesta_jogador): # Se o robô tem menos itens.
            vencedor = "ROBO"

        # Monta a mensagem de resultado.
        msg = f"🎯 VALOR-ALVO: R$ {self.valor_alvo:.2f}\n\n"
        msg += f"👤 JOGADOR: R$ {self.total_jogador:.2f} ({len(self.cesta_jogador)} itens)\n"
        msg += f"🤖 ROBO: R$ {self.total_robo:.2f} ({len(self.cesta_robo)} itens)\n\n"
        msg += {"JOGADOR": "🎉 VOCÊ VENCEU!", "ROBO": "🤖 O ROBO VENCEU!", "EMPATE": "⚖️ EMPATE!"}[vencedor]
        
        messagebox.showinfo("Resultado Final", msg) # Exibe a mensagem de resultado.
        
        # Se o jogador comprou algo, mostra a nota fiscal.
        if self.cesta_jogador: self.mostrar_nota_fiscal()

    # Cria uma nova janela (Toplevel) para mostrar a nota fiscal da compra do jogador.
    def mostrar_nota_fiscal(self):
        nota_window = tk.Toplevel(self.master) # Cria uma nova janela filha.
        nota_window.title("Nota da Sua Compra") # Define o título da janela.
        nota_window.geometry("450x550") # Define o tamanho da janela.
        nota_window.configure(bg="#ffffff") # Define a cor de fundo.
        nota_window.resizable(False, False) # Impede que a janela seja redimensionada.

        # Centraliza a janela da nota fiscal em relação à janela principal.
        x = self.master.winfo_x() + (self.master.winfo_width() // 2) - 225
        y = self.master.winfo_y() + (self.master.winfo_height() // 2) - 275
        nota_window.geometry(f'+{x}+{y}') # Define a posição da janela.

        # --- Cabeçalho ---
        frame_header = tk.Frame(nota_window, bg="#ffffff")
        frame_header.pack(pady=(20, 10)) # Adiciona o frame do cabeçalho.
        
        tk.Label(frame_header, text="MAIS POR MENOS", font=("Arial", 22, "bold"), bg="white").pack() # Nome da loja.
        tk.Label(frame_header, text="SUPERMERCADO", font=("Arial", 14), bg="white").pack() # Tipo de estabelecimento.
        tk.Label(frame_header, text="CUPOM FISCAL", font=("Arial", 12, "italic"), fg="#555", bg="white").pack(pady=(10,0)) # Título do cupom.
        
        ttk.Separator(nota_window, orient='horizontal').pack(fill='x', padx=20, pady=5) # Adiciona uma linha separadora.

        # --- Tabela de Itens (usando Treeview para um visual de tabela) ---
        frame_itens = tk.Frame(nota_window, bg="white")
        frame_itens.pack(fill="both", expand=True, padx=20, pady=5) # Adiciona o frame dos itens.

        # Estilo para o Treeview para deixá-lo com aparência limpa.
        style = ttk.Style() # Cria um objeto de estilo.
        style.theme_use("clam") # Usa um tema base.
        style.configure("Treeview", background="white", foreground="black", rowheight=25, fieldbackground="white", bordercolor="#ffffff", borderwidth=0)
        style.map('Treeview', background=[('selected', '#ff6b00')]) # Define a cor de seleção.
        style.configure("Treeview.Heading", font=("Arial", 10, 'bold'), background="#f0f0f0", borderwidth=0) # Estiliza o cabeçalho.
        style.layout("Treeview", [('Treeview.treearea', {'sticky': 'nswe'})]) # Remove as bordas da área da tabela.

        # Criação do Treeview com barra de rolagem.
        tree_frame = tk.Frame(frame_itens, bg="white")
        tree_frame.pack(fill='both', expand=True) # Frame para a tabela e a barra de rolagem.

        cols = ('#', 'Descrição', 'Valor') # Define as colunas.
        tree = ttk.Treeview(tree_frame, columns=cols, show='headings', height=10) # Cria o widget Treeview, mostrando apenas os cabeçalhos.
        
        # Define os cabeçalhos.
        tree.heading('#', text='ITEM') # Cabeçalho da coluna 1.
        tree.heading('Descrição', text='DESCRIÇÃO') # Cabeçalho da coluna 2.
        tree.heading('Valor', text='VALOR (R$)') # Cabeçalho da coluna 3.

        # Define as colunas e seu alinhamento.
        tree.column('#', width=50, anchor=tk.CENTER) # Coluna de item (centralizada).
        tree.column('Descrição', width=250, anchor=tk.W) # Coluna de descrição (alinhada à esquerda).
        tree.column('Valor', width=100, anchor=tk.E) # Coluna de valor (alinhada à direita).

        # Adiciona os itens da compra à tabela.
        for i, (prod, preco) in enumerate(self.cesta_jogador, 1): # Itera sobre os itens da cesta do jogador.
            tree.insert("", "end", values=(f"{i:03d}", prod, f"{preco:.2f}")) # Insere uma nova linha na tabela.

        # Barra de rolagem.
        scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=tree.yview) # Cria a barra de rolagem.
        tree.configure(yscrollcommand=scrollbar.set) # Conecta a barra de rolagem à tabela.
        
        tree.grid(row=0, column=0, sticky='nsew') # Posiciona a tabela na grade.
        scrollbar.grid(row=0, column=1, sticky='ns') # Posiciona a barra de rolagem na grade.
        tree_frame.grid_rowconfigure(0, weight=1) # Faz a linha da grade expandir verticalmente.
        tree_frame.grid_columnconfigure(0, weight=1) # Faz a coluna da grade expandir horizontalmente.

        # --- Total ---
        ttk.Separator(nota_window, orient='horizontal').pack(fill='x', padx=20, pady=(10, 5)) # Adiciona outra linha separadora.
        frame_total = tk.Frame(nota_window, bg="white")
        frame_total.pack(fill='x', padx=25, pady=5) # Adiciona o frame do total.

        tk.Label(frame_total, text="TOTAL", font=("Arial", 14, "bold"), bg="white").pack(side="left") # Label "TOTAL".
        tk.Label(frame_total, text=f"R$ {self.total_jogador:.2f}", font=("Arial", 14, "bold"), bg="white").pack(side="right") # Valor total.

        # --- Botão Fechar ---
        botao_fechar = tk.Button(nota_window, text="Fechar",
                                 font=("Arial", 14, "bold"),
                                 bg="#ff6b00", fg="white",
                                 relief="flat",
                                 command=nota_window.destroy, # Define que o botão fechará a janela da nota.
                                 padx=20, pady=8)
        botao_fechar.pack(pady=20) # Adiciona o botão.
        
        # Configura a janela da nota como modal (bloqueia a interação com a janela principal).
        nota_window.transient(self.master) # Define a janela principal como "mãe".
        nota_window.grab_set() # Captura todos os eventos para esta janela.
        self.master.wait_window(nota_window) # Pausa a execução até que a janela da nota seja fechada.


    # Inicia uma nova rodada do jogo.
    def iniciar_nova_rodada(self):
        self.inicializar_jogo() # Simplesmente chama a função de inicialização novamente.

# Ponto de entrada do programa. Este bloco só é executado quando o arquivo é rodado diretamente.
if __name__ == "__main__":
    root = tk.Tk()  # Cria a janela principal do Tkinter.
    app = JogoSupermercado(root) # Cria uma instância da nossa classe de jogo, passando a janela principal.
    root.mainloop() # Inicia o loop principal da interface gráfica, que aguarda por eventos (cliques, etc.).