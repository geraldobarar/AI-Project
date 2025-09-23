# Importação das bibliotecas necessárias para a interface gráfica, lógica do jogo,
# manipulação de áudio, reconhecimento de voz e processamento de texto.
import tkinter as tk
from tkinter import messagebox, font, ttk
import heapq
import random
import time
import threading
import os
from gtts import gTTS
from playsound import playsound
import speech_recognition as sr
from thefuzz import process
from unidecode import unidecode

# Classe principal que encapsula toda a lógica e a interface do jogo.
class JogoSupermercado:
    # O método __init__ é o construtor da classe. Ele é chamado quando um novo objeto JogoSupermercado é criado.
    def __init__(self, master):
        # 'master' é a janela principal do Tkinter.
        self.master = master
        master.configure(bg="#f5f5f5")  # Define a cor de fundo padrão da janela.
        
        # Inicia a janela maximizada ('zoomed') para uma melhor experiência do usuário.
        master.state('zoomed') 
        master.minsize(1200, 700) # Define um tamanho mínimo para a janela.
        
        master.title("Jogo do Supermercado (Baseado em Turnos)")

        # Inicializa o objeto para reconhecimento de voz.
        self.recognizer = sr.Recognizer()

        # --- Variáveis de Estado do Jogo ---
        self.carrinho_jogador = []  # Lista para armazenar os itens (nome, preço) do jogador.
        self.total_jogador = 0.0  # Soma dos preços no carrinho do jogador.
        self.carrinho_robo = []  # Lista para os itens do robo (IA).
        self.total_robo = 0.0  # Soma dos preços no carrinho do robo.
        self.jogo_ativo = False  # Flag para controlar se o jogo está em andamento.
        
        # --- Controle de Turno ---
        self.turno_do_jogador = True  # Começa com o turno do jogador.
        self.botoes_produtos = [] # Lista para guardar os botões de produtos e poder habilitá-los/desabilitá-los.

        # Dicionário que armazenará todos os produtos disponíveis, com seus preços e estoque.
        self.produtos_com_estoque = {}

        # Exibe a tela inicial de boas-vindas.
        self.mostrar_tela_bem_vindo()

    # Função para converter uma string de texto em fala usando a API do Google.
    def falar_texto(self, texto_para_falar):
        try:
            # Cria um objeto gTTS com o texto, definindo o idioma para português do Brasil.
            tts = gTTS(text=texto_para_falar, lang='pt-br', slow=False)
            arquivo_audio_temporario = "temp_fala.mp3"  # Nome do arquivo de áudio temporário.
            tts.save(arquivo_audio_temporario)  # Salva o áudio gerado.
            playsound(arquivo_audio_temporario) # Toca o arquivo de áudio.
            os.remove(arquivo_audio_temporario) # Remove o arquivo temporário após tocar.
        except Exception as e:
            # Informa no console caso ocorra um erro (ex: falta de internet).
            print(f"Erro ao tentar falar o texto com gTTS: {e}")
            print("Verifique sua conexão com a internet ou se a biblioteca playsound está funcionando corretamente.")

    # Configura e exibe a tela inicial do jogo.
    def mostrar_tela_bem_vindo(self):
        # Limpa todos os widgets da tela anterior.
        for widget in self.master.winfo_children():
            widget.destroy()

        # Configura a cor de fundo para a tela de boas-vindas.
        self.master.configure(bg="#ff6b00")

        # Cria um frame central para alinhar todos os elementos.
        frame_bem_vindo = tk.Frame(self.master, bg="#ff6b00")
        frame_bem_vindo.place(relx=0.5, rely=0.5, anchor="center") # Centraliza o frame na janela.

        # Título principal da tela.
        label_titulo = tk.Label(frame_bem_vindo, text="Olá, seja bem-vindo!",
                                font=("Arial", 48, "bold"), fg="white", bg="#ff6b00") 
        label_titulo.pack(pady=(0, 40)) 

        # Frame para os desenhos dos carrinhos de compras.
        frame_carrinhos = tk.Frame(frame_bem_vindo, bg="#ff6b00")
        frame_carrinhos.pack(pady=(0, 40)) 

        # Desenha três carrinhos decorativos.
        self.desenhar_carrinho_compras(frame_carrinhos, 0)
        self.desenhar_carrinho_compras(frame_carrinhos, 1)
        self.desenhar_carrinho_compras(frame_carrinhos, 2)

        # Texto explicando as regras do jogo por turnos.
        texto_mensagem = "O jogo agora é por turnos! Você adiciona um item, depois o robo.\nO estoque é compartilhado. Use sua estratégia para vencer!"
        label_mensagem = tk.Label(frame_bem_vindo, text=texto_mensagem,
                                  font=("Arial", 16), fg="white", bg="#ff6b00", 
                                  justify="center")
        label_mensagem.pack(pady=(0, 60)) 

        # Frame para a seleção do algoritmo da IA.
        frame_algoritmo = tk.Frame(frame_bem_vindo, bg="#ff6b00")
        frame_algoritmo.pack(pady=(0, 40)) 

        tk.Label(frame_algoritmo, text="Escolha o algoritmo do robo:",
                 font=("Arial", 18, "bold"), fg="white", bg="#ff6b00").pack() 

        # Variável para armazenar a escolha do algoritmo (A* ou Gulosa).
        self.variavel_algoritmo = tk.StringVar(value="A*") # Padrão é A*.
        tk.Radiobutton(frame_algoritmo, text="Algoritmo A*", variable=self.variavel_algoritmo,
                                      value="A*", font=("Arial", 16), fg="white", bg="#ff6b00", 
                                      selectcolor="#ff6b00").pack()
        tk.Radiobutton(frame_algoritmo, text="Busca Gulosa", variable=self.variavel_algoritmo,
                                      value="Gulosa", font=("Arial", 16), fg="white", bg="#ff6b00", 
                                      selectcolor="#ff6b00").pack()

        # Botão para começar o jogo.
        botao_iniciar = tk.Button(frame_bem_vindo, text="INICIAR JOGO",
                                  font=("Arial", 26, "bold"), bg="white", fg="#ff6b00", 
                                  relief="flat", padx=40, pady=20, 
                                  command=self.inicializar_jogo) # Chama a função que prepara o jogo.
        botao_iniciar.pack(pady=(0, 40)) 

        label_rodape = tk.Label(frame_bem_vindo, text="Clique em 'INICIAR JOGO' para começar",
                                      font=("Arial", 14), fg="white", bg="#ff6b00") 
        label_rodape.pack()

    # Função auxiliar para desenhar carrinhos de compras decorativos na tela de boas-vindas.
    def desenhar_carrinho_compras(self, parent, position):
        w, h = 100, 100 
        canvas = tk.Canvas(parent, width=w, height=h, bg="#ff6b00", highlightthickness=0)
        canvas.grid(row=0, column=position, padx=15) 

        # Desenha as partes do carrinho (cesto, rodas, alça) usando formas geométricas.
        canvas.create_rectangle(w*0.125, h*0.375, w*0.875, h*0.75, fill="#e0e0e0", outline="#c0c0c0", width=2)
        canvas.create_rectangle(w*0.0625, h*0.3125, w*0.9375, h*0.375, fill="#e0e0e0", outline="#c0c0c0", width=2)
        canvas.create_oval(w*0.1875, h*0.6875, w*0.3125, h*0.8125, fill="#555555", outline="#333333", width=1)
        canvas.create_oval(w*0.6875, h*0.6875, w*0.8125, h*0.8125, fill="#555555", outline="#333333", width=1)
        canvas.create_line(w*0.8125, h*0.3125, w*0.9375, h*0.1875, fill="#c0c0c0", width=3)
        canvas.create_line(w*0.9375, h*0.1875, w*0.6875, h*0.1875, fill="#c0c0c0", width=3)
        canvas.create_line(w*0.6875, h*0.1875, w*0.5625, h*0.3125, fill="#c0c0c0", width=3)
        
        # Adiciona itens decorativos no carrinho do meio.
        if position == 1:
            canvas.create_oval(w*0.3125, h*0.4375, w*0.4375, h*0.5625, fill="#ff9999", outline="#ff6666", width=1)
            canvas.create_rectangle(w*0.5, h*0.5, w*0.625, h*0.625, fill="#99ccff", outline="#6699ff", width=1)
            canvas.create_rectangle(w*0.6875, h*0.4375, w*0.8125, h*0.5625, fill="#ffcc99", outline="#ff9966", width=1)

    # Desenha o carrinho de compras do jogador na tela principal.
    def redesenhar_carrinho_jogador(self, event=None):
        self.canvas_carrinho_vazio.delete("all") # Limpa o canvas.
        width = self.canvas_carrinho_vazio.winfo_width()
        height = self.canvas_carrinho_vazio.winfo_height()

        # Evita erros se a janela ainda não tiver sido desenhada.
        if width < 2 or height < 2:
            return

        # Cores para o desenho do carrinho.
        cor_cesto = "#d0d0d0"
        cor_contorno = "#888888"
        cor_rodas = "#444444"
        cor_alca = "#666666"

        # Calcula as dimensões do carrinho com base no tamanho do canvas.
        carrinho_w = width * 0.75
        carrinho_h = height * 0.7
        x0 = (width - carrinho_w) / 2
        y0 = (height - carrinho_h) / 2

        # Desenha as partes do carrinho.
        cesto_y_fim = y0 + carrinho_h * 0.8
        self.canvas_carrinho_vazio.create_rectangle(x0, y0, x0 + carrinho_w, cesto_y_fim,
                                                  fill=cor_cesto, outline=cor_contorno, width=2)
        # Linhas decorativas no cesto.
        for i in range(1, 4):
            self.canvas_carrinho_vazio.create_line(x0, y0 + i * (carrinho_h * 0.8) / 4,
                                                 x0 + carrinho_w, y0 + i * (carrinho_h * 0.8) / 4,
                                                 fill=cor_contorno, width=1)
        
        y_rodas = y0 + carrinho_h
        self.canvas_carrinho_vazio.create_line(x0, cesto_y_fim, x0 + carrinho_w * 0.2, y_rodas, fill=cor_contorno, width=2)
        self.canvas_carrinho_vazio.create_line(x0 + carrinho_w, cesto_y_fim, x0 + carrinho_w * 0.8, y_rodas, fill=cor_contorno, width=2)
        raio_roda = carrinho_h * 0.08
        self.canvas_carrinho_vazio.create_oval(x0 + carrinho_w * 0.2 - raio_roda, y_rodas - raio_roda,
                                                 x0 + carrinho_w * 0.2 + raio_roda, y_rodas + raio_roda,
                                                 fill=cor_rodas, outline=cor_rodas)
        self.canvas_carrinho_vazio.create_oval(x0 + carrinho_w * 0.8 - raio_roda, y_rodas - raio_roda,
                                                 x0 + carrinho_w * 0.8 + raio_roda, y_rodas + raio_roda,
                                                 fill=cor_rodas, outline=cor_rodas)
        alca_x = x0 + carrinho_w + 10
        self.canvas_carrinho_vazio.create_line(x0 + carrinho_w, y0, alca_x, y0 - 10, fill=cor_alca, width=3)
        self.canvas_carrinho_vazio.create_line(alca_x, y0 - 10, alca_x, y0 + 10, fill=cor_alca, width=3)
        self.canvas_carrinho_vazio.create_rectangle(alca_x - 3, y0 - 12, alca_x + 3, y0 + 12, fill="#555555", outline="")
        
        # Se o carrinho estiver vazio, exibe uma mensagem.
        if self.display_carrinho_jogador.size() == 0:
            self.canvas_carrinho_vazio.create_text(width / 2, height - 20, text="Seus itens aparecerão aqui!",
                                                 font=("Arial", 14), fill="#888888")

        # Posiciona a Listbox (que mostra os itens) dentro do desenho do cesto do carrinho.
        padding = 4
        listbox_x = x0 + padding
        listbox_y = y0 + padding
        listbox_width = carrinho_w - (padding * 2)
        listbox_height = (cesto_y_fim - y0) - (padding * 2)
        
        self.canvas_carrinho_vazio.create_window(listbox_x, listbox_y,
                                                 anchor="nw",
                                                 window=self.display_carrinho_jogador,
                                                 width=max(10, listbox_width),
                                                 height=max(10, listbox_height))

    # Função principal que configura a tela do jogo e reinicia as variáveis.
    def inicializar_jogo(self):
        # Limpa a tela de boas-vindas.
        for widget in self.master.winfo_children():
            widget.destroy()
        
        self.master.configure(bg="#f5f5f5") # Define a cor de fundo do jogo.
        
        # Reseta as variáveis de estado do jogo.
        self.jogo_ativo = True
        self.turno_do_jogador = True
        self.valor_alvo = round(random.uniform(25.0, 70.0), 2) # Sorteia um novo valor-alvo.
        self.carrinho_jogador = []
        self.total_jogador = 0.0
        self.carrinho_robo = []
        self.total_robo = 0.0
        
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
        
        # Cria a estrutura de dados de produtos com estoque aleatório para cada item.
        self.produtos_com_estoque = {"Todos": {}}
        for depto, produtos in produtos_base.items():
            self.produtos_com_estoque[depto] = {}
            for nome, preco in produtos.items():
                estoque = random.randint(1, 3) # Cada produto terá entre 1 e 3 unidades no estoque.
                produto_data = {"preco": preco, "estoque": estoque}
                self.produtos_com_estoque[depto][nome] = produto_data
                self.produtos_com_estoque["Todos"][nome] = produto_data # Adiciona também à lista "Todos".
        
        self.departamento_atual = "Todos"

        # --- Criação da Interface Gráfica do Jogo ---

        # Cabeçalho da loja.
        frame_cabecalho = tk.Frame(self.master, bg="#ff6b00", height=120) 
        frame_cabecalho.pack(fill="x")
        frame_cabecalho.pack_propagate(False)
        tk.Label(frame_cabecalho, text="Mais por Menos",
                 font=("Arial", 36, "bold"), fg="white", bg="#ff6b00").pack(pady=25) 

        # Frame principal que conterá as 3 colunas (Jogador, Produtos, Robo).
        frame_principal = tk.Frame(self.master, bg="#f5f5f5")
        frame_principal.pack(fill="both", expand=True, padx=25, pady=25)

        # Configura as colunas para se expandirem igualmente.
        frame_principal.columnconfigure(0, weight=1)
        frame_principal.columnconfigure(1, weight=1)
        frame_principal.columnconfigure(2, weight=1)
        frame_principal.rowconfigure(0, weight=1)

        # --- Coluna do Jogador (Esquerda) ---
        frame_jogador = tk.LabelFrame(frame_principal, text="👤 JOGADOR",
                                      font=("Arial", 18, "bold"), bg="#f5f5f5") 
        frame_jogador.grid(row=0, column=0, sticky="nsew", padx=(0, 10))

        frame_alvo = tk.Frame(frame_jogador, bg="#f5f5f5")
        frame_alvo.pack(fill="x", pady=15)
        
        # Mostra o valor-alvo da rodada.
        label_valor_alvo = tk.Label(frame_alvo, text=f"🎯 VALOR-ALVO: R$ {self.valor_alvo:.2f}",
                                  font=("Arial", 18, "bold"), bg="#f5f5f5") 
        label_valor_alvo.pack()

        # Mostra o total atual do carrinho do jogador.
        self.label_total_jogador = tk.Label(frame_alvo, text=f"💰 SEU TOTAL: R$ {self.total_jogador:.2f}",
                                            font=("Arial", 17), bg="#f5f5f5") 
        self.label_total_jogador.pack(pady=8) 

        frame_saldo = tk.Frame(frame_alvo, bg="#f5f5f5")
        frame_saldo.pack(fill="x", pady=(15, 0), padx=20) 

        # Mostra quanto dinheiro o jogador ainda tem para gastar.
        saldo_restante = self.valor_alvo - self.total_jogador
        self.label_saldo_restante = tk.Label(frame_saldo, text=f"SALDO: R$ {saldo_restante:.2f}",
                                             font=("Arial", 18, "bold"), bg="#f5f5f5", fg="#17a2b8") 
        self.label_saldo_restante.pack(side="left", expand=True)
        
        # Botão para ouvir o saldo em voz alta.
        self.botao_ouvir_saldo = tk.Button(frame_saldo, text="🔊 Ouvir Saldo",
                                           font=("Arial", 14), bg="#17a2b8", fg="white", relief="flat", 
                                           command=self.falar_saldo_restante, padx=15, pady=5) 
        self.botao_ouvir_saldo.pack(side="right", expand=True)

        # Frame para exibir o carrinho do jogador.
        self.frame_carrinho_jogador = tk.LabelFrame(frame_jogador, text="Seu Carrinho",
                                                    font=("Arial", 15, "bold"), bg="#f5f5f5") 
        self.frame_carrinho_jogador.pack(fill="both", expand=True, pady=15)

        # Canvas onde o desenho do carrinho é feito.
        self.canvas_carrinho_vazio = tk.Canvas(self.frame_carrinho_jogador, bg="white", highlightthickness=0)
        self.canvas_carrinho_vazio.pack(fill="both", expand=True)
        
        # Listbox que mostra os itens e é colocada dentro do canvas.
        self.display_carrinho_jogador = tk.Listbox(self.canvas_carrinho_vazio, font=("Arial", 14), 
                                                 bg="white", selectbackground="#ff6b00",
                                                 bd=0, highlightthickness=0)

        # Chama a função de redesenho sempre que a janela for redimensionada.
        self.canvas_carrinho_vazio.bind("<Configure>", self.redesenhar_carrinho_jogador)

        frame_botoes_jogador = tk.Frame(frame_jogador, bg="#f5f5f5")
        frame_botoes_jogador.pack(fill="x", pady=15)

        # Botão para remover um item selecionado do carrinho.
        self.botao_remover_jogador = tk.Button(frame_botoes_jogador, text="Remover Item",
                                               font=("Arial", 15, "bold"), bg="#e74c3c", fg="white", 
                                               command=self.remover_do_carrinho, pady=8)
        self.botao_remover_jogador.pack(side="left", fill="x", expand=True, padx=10) 

        # Botão para o jogador finalizar sua compra (terminar a rodada).
        self.botao_finalizar_jogador = tk.Button(frame_botoes_jogador, text="Finalizar Compra",
                                                 font=("Arial", 15, "bold"), bg="#27ae60", fg="white", 
                                                 command=self.finalizar_compra, pady=8)
        self.botao_finalizar_jogador.pack(side="right", fill="x", expand=True, padx=10) 
        
        # --- Coluna do Meio (Produtos) ---
        frame_meio = tk.Frame(frame_principal, bg="#f5f5f5")
        frame_meio.grid(row=0, column=1, sticky="nsew", padx=10)

        # Frame com botões de rádio para filtrar por departamento.
        frame_depto = tk.LabelFrame(frame_meio, text="Departamentos",
                                    font=("Arial", 16, "bold"), bg="#f5f5f5")
        frame_depto.pack(fill="x", pady=(0, 15))

        departamentos = list(self.produtos_com_estoque.keys())
        self.variavel_depto = tk.StringVar(value="Todos") # Padrão é "Todos".
        
        for depto in departamentos:
            tk.Radiobutton(frame_depto, text=depto, variable=self.variavel_depto, value=depto,
                         command=self.exibir_produtos, font=("Arial", 14), 
                         bg="#f5f5f5").pack(side="left", padx=20, expand=True)

        # Frame para os controles de voz.
        frame_voz = tk.Frame(frame_meio, bg="#f5f5f5")
        frame_voz.pack(fill="x", pady=10)
        
        self.label_status_voz = tk.Label(frame_voz, text="Diga 'adicionar' ou 'remover' [produto]", font=("Arial", 12), fg="#555555", bg="#f5f5f5")
        self.label_status_voz.pack()

        # Botão do microfone para iniciar o reconhecimento de voz.
        self.botao_microfone = tk.Button(frame_voz, text="🎤", font=("Arial", 25), 
                                         command=self.iniciar_escuta_produto,
                                         bg="#8e44ad", fg="white", relief="flat", width=4)
        self.botao_microfone.pack(pady=5)

        # Frame que conterá a lista rolável de produtos.
        frame_exibicao_produtos = tk.Frame(frame_meio, bg="#f5f5f5")
        frame_exibicao_produtos.pack(fill="both", expand=True)

        self.canvas_produtos = tk.Canvas(frame_exibicao_produtos, bg="#f5f5f5", highlightthickness=0)
        scrollbar = tk.Scrollbar(frame_exibicao_produtos, orient="vertical", command=self.canvas_produtos.yview)
        self.frame_rolavel_produtos = tk.Frame(self.canvas_produtos, bg="#f5f5f5")

        self.frame_rolavel_produtos.bind("<Configure>", lambda e: self.canvas_produtos.configure(scrollregion=self.canvas_produtos.bbox("all")))

        self.canvas_produtos.create_window((0, 0), window=self.frame_rolavel_produtos, anchor="nw")
        self.canvas_produtos.configure(yscrollcommand=scrollbar.set)

        self.canvas_produtos.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # --- Coluna do Robo (Direita) ---
        frame_robo = tk.LabelFrame(frame_principal, text="🤖 ROBO",
                                      font=("Arial", 18, "bold"), bg="#f5f5f5") 
        frame_robo.grid(row=0, column=2, sticky="nsew", padx=(10, 0))

        frame_info_robo = tk.Frame(frame_robo, bg="#f5f5f5")
        frame_info_robo.pack(fill="x", pady=15)

        label_valor_alvo_robo = tk.Label(frame_info_robo, text=f"🎯 VALOR-ALVO: R$ {self.valor_alvo:.2f}",
                                            font=("Arial", 18, "bold"), bg="#f5f5f5")
        label_valor_alvo_robo.pack()

        self.label_total_robo = tk.Label(frame_info_robo, text=f"💰 TOTAL ROBO: R$ {self.total_robo:.2f}",
                                            font=("Arial", 17), bg="#f5f5f5") 
        self.label_total_robo.pack(pady=8)
        
        frame_saldo_robo = tk.Frame(frame_info_robo, bg="#f5f5f5")
        frame_saldo_robo.pack(fill="x", pady=(15, 0), padx=20)

        saldo_restante_robo = self.valor_alvo - self.total_robo
        self.label_saldo_restante_robo = tk.Label(frame_saldo_robo, text=f"SALDO: R$ {saldo_restante_robo:.2f}",
                                                      font=("Arial", 18, "bold"), bg="#f5f5f5", fg="#17a2b8")
        self.label_saldo_restante_robo.pack(side="left", expand=True)

        self.botao_ouvir_saldo_robo = tk.Button(frame_saldo_robo, text="🔊 Ouvir Saldo",
                                                    font=("Arial", 14), bg="#17a2b8", fg="white", relief="flat",
                                                    command=self.falar_saldo_restante_robo, padx=15, pady=5)
        self.botao_ouvir_saldo_robo.pack(side="right", expand=True)

        # Mostra qual algoritmo o robo está usando.
        self.label_algoritmo_robo = tk.Label(frame_info_robo, text=f"Algoritmo: {self.variavel_algoritmo.get()}",
                                                font=("Arial", 17), bg="#f5f5f5") 
        self.label_algoritmo_robo.pack(pady=(20, 0))

        # Label de status para indicar de quem é o turno.
        self.label_robo_status = tk.Label(frame_info_robo, text="É a sua vez de jogar!",
                                              font=("Arial", 15, "bold"), bg="#f5f5f5", fg="#27ae60") 
        self.label_robo_status.pack()
        
        frame_carrinho_robo = tk.LabelFrame(frame_robo, text="Carrinho do Robo",
                                                font=("Arial", 15, "bold"), bg="#f5f5f5") 
        frame_carrinho_robo.pack(fill="both", expand=True, pady=15)

        # Listbox para mostrar os itens no carrinho do robo.
        self.display_carrinho_robo = tk.Listbox(frame_carrinho_robo, font=("Arial", 14), 
                                                  bg="white", selectbackground="#3498db")
        self.display_carrinho_robo.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Frame para o botão de "Nova Rodada".
        frame_novo_jogo = tk.Frame(self.master, bg="#f5f5f5")
        frame_novo_jogo.pack(fill="x", pady=20)

        tk.Button(frame_novo_jogo, text="Nova Rodada",
                  font=("Arial", 16, "bold"), bg="#ff6b00", fg="white", 
                  command=self.iniciar_nova_rodada, padx=20, pady=10).pack() 

        # Exibe os produtos pela primeira vez.
        self.exibir_produtos()

    # Função auxiliar para habilitar ou desabilitar todos os controles do jogador.
    def _set_player_controls_state(self, state):
        # Altera o estado (NORMAL ou DISABLED) dos botões do jogador.
        self.botao_remover_jogador.config(state=state)
        self.botao_finalizar_jogador.config(state=state)
        self.botao_microfone.config(state=state)
        self.botao_ouvir_saldo.config(state=state)
        
        # Percorre os botões de adicionar produto.
        for botao in self.botoes_produtos:
            # Só reabilita o botão se ele não estiver "Fora de Estoque".
            if state == tk.NORMAL and botao.cget('text') != "Fora de Estoque":
                botao.config(state=tk.NORMAL)
            # Desabilita todos se o estado for DISABLED.
            elif state == tk.DISABLED:
                botao.config(state=tk.DISABLED)

    # Lógica para passar o turno do jogador para o robo.
    def _passar_turno_para_robo(self):
        if not self.jogo_ativo:
            return
            
        self.turno_do_jogador = False
        self._set_player_controls_state(tk.DISABLED) # Desabilita controles do jogador.
        self.label_robo_status.config(text="🤔 Robo pensando...", fg="#e67e22")
        # Espera 1 segundo (1000 ms) antes de executar o turno do robo, para dar um efeito de "pensamento".
        self.master.after(1000, self.executar_turno_robo)
    
    # Lógica para passar o turno do robo de volta para o jogador.
    def _passar_turno_para_jogador(self):
        if not self.jogo_ativo:
            return

        self.turno_do_jogador = True
        self._set_player_controls_state(tk.NORMAL) # Habilita os controles do jogador.
        self.label_robo_status.config(text="É a sua vez de jogar!", fg="#27ae60")


    # Inicia o processo de escuta do comando de voz em uma thread separada para não travar a interface.
    def iniciar_escuta_produto(self):
        self.botao_microfone.config(state=tk.DISABLED, bg="#c0392b") # Desabilita o botão enquanto ouve.
        thread = threading.Thread(target=self.processar_comando_de_voz, daemon=True)
        thread.start()
    
    # Prepara o texto para comparação: converte para minúsculas e remove acentos.
    def _preprocess_text(self, text):
        return unidecode(text.lower())

    # Usa 'thefuzz' para encontrar o produto mais parecido com o que foi falado.
    def _find_best_product_match(self, spoken_text):
        todos_produtos = self.produtos_com_estoque["Todos"]
        product_names = list(todos_produtos.keys())
        # Cria um dicionário que mapeia nomes processados para nomes originais.
        processed_product_names = {self._preprocess_text(name): name for name in product_names}
        # Encontra a melhor correspondência.
        result = process.extractOne(self._preprocess_text(spoken_text), processed_product_names.keys())
        
        if result:
            best_match_processed, score = result
            original_product_name = processed_product_names[best_match_processed]
            return (original_product_name, score) # Retorna o nome original e a pontuação de similaridade.
        return (None, 0)

    # Encontra o item mais parecido com o que foi falado, mas buscando apenas no carrinho do jogador.
    def _find_best_match_in_cart(self, spoken_text):
        if not self.carrinho_jogador:
            return None, 0, -1

        cart_product_names = [item[0] for item in self.carrinho_jogador]
        result = process.extractOne(self._preprocess_text(spoken_text), cart_product_names)
        
        if result:
            best_match, score = result
            # Encontra o índice do item no carrinho.
            for i, item in enumerate(self.carrinho_jogador):
                if item[0] == best_match:
                    return best_match, score, i
        return None, 0, -1
        
    # Função principal que gerencia o reconhecimento de voz.
    def processar_comando_de_voz(self):
        if not self.turno_do_jogador:
            self.master.after(0, self.label_status_voz.config, {'text': 'Aguarde seu turno.'})
            self.master.after(1000, self.reativar_microfone)
            return

        self.master.after(0, self.label_status_voz.config, {'text': 'Ouvindo...'})
        try:
            with sr.Microphone() as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=1) # Ajusta ao ruído ambiente.
                audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=5)
            
            self.master.after(0, self.label_status_voz.config, {'text': 'Processando...'})
            # Usa a API de reconhecimento do Google para converter o áudio em texto.
            texto_falado = self.recognizer.recognize_google(audio, language='pt-BR').lower()
            self.master.after(0, self.label_status_voz.config, {'text': f'Você disse: "{texto_falado}"'})

            # Verifica se o comando é para adicionar ou remover um item.
            if "adicionar" in texto_falado:
                self._adicionar_produto_por_voz(texto_falado)
            elif "remover" in texto_falado:
                self._remover_produto_por_voz(texto_falado)
            else:
                self.master.after(0, self.label_status_voz.config, {'text': "Comando não reconhecido."})

        # Tratamento de erros comuns do reconhecimento de voz.
        except sr.WaitTimeoutError:
            self.master.after(0, self.label_status_voz.config, {'text': 'Nenhuma fala detectada.'})
        except sr.UnknownValueError:
            self.master.after(0, self.label_status_voz.config, {'text': 'Não consegui entender.'})
        except sr.RequestError as e:
            self.master.after(0, self.label_status_voz.config, {'text': f"Erro na API; {e}"})
        finally:
            # Reativa o microfone após um tempo.
            self.master.after(2000, self.reativar_microfone)

    # Processa o comando de voz para adicionar um item.
    def _adicionar_produto_por_voz(self, texto_falado):
        # Extrai o nome do produto da frase falada.
        nome_produto_falado = texto_falado.split("adicionar", 1)[1].strip()
        if not nome_produto_falado:
            self.master.after(0, self.label_status_voz.config, {'text': 'Diga o nome do produto para adicionar.'})
            return

        produto_nome, pontuacao = self._find_best_product_match(nome_produto_falado)
        
        # Se a similaridade for alta (75% ou mais), adiciona o produto.
        if pontuacao >= 75:
            # Chama a função de adicionar ao carrinho. 'master.after' garante que seja na thread principal da GUI.
            self.master.after(0, self.adicionar_ao_carrinho_jogador, produto_nome, True)
            self.master.after(0, self.label_status_voz.config, {'text': f'"{produto_nome}" adicionado!'})
        else:
            feedback_msg = f'Produto "{nome_produto_falado}" não encontrado.'
            # Se a pontuação for razoável, sugere o produto mais próximo.
            if produto_nome and pontuacao > 50:
                feedback_msg += f'\nVocê quis dizer "{produto_nome}"?'
            self.master.after(0, self.label_status_voz.config, {'text': feedback_msg})

    # Processa o comando de voz para remover um item.
    def _remover_produto_por_voz(self, texto_falado):
        nome_produto_falado = texto_falado.split("remover", 1)[1].strip()
        if not nome_produto_falado:
            self.master.after(0, self.label_status_voz.config, {'text': 'Diga o nome do produto para remover.'})
            return
        
        produto_nome, pontuacao, indice = self._find_best_match_in_cart(nome_produto_falado)

        # Se encontrou um item similar no carrinho, remove-o.
        if pontuacao >= 75:
            self.master.after(0, self.remover_do_carrinho, indice)
        else:
            feedback_msg = f'"{nome_produto_falado}" não está no seu carrinho.'
            if produto_nome and pontuacao > 50:
                feedback_msg += f'\nVocê quis dizer "{produto_nome}"?'
            self.master.after(0, self.label_status_voz.config, {'text': feedback_msg})

    # Reativa o botão do microfone e reseta o texto de status.
    def reativar_microfone(self):
        if self.jogo_ativo and self.turno_do_jogador:
            self.botao_microfone.config(state=tk.NORMAL, bg="#8e44ad")
            self.label_status_voz.config(text="Diga 'adicionar' ou 'remover' [produto]")
        elif self.jogo_ativo and not self.turno_do_jogador:
            self.botao_microfone.config(state=tk.DISABLED, bg="#c0392b")

    # Converte o saldo do jogador em texto e o fala.
    def falar_saldo_restante(self):
        if not self.jogo_ativo: return
        saldo = self.valor_alvo - self.total_jogador
        reais = int(saldo)
        centavos = int(round((saldo - reais) * 100))
        texto_saldo = f"Seu saldo restante é de {reais} reais"
        texto_saldo += f" e {centavos} centavos." if centavos > 0 else "."
        # Usa uma thread para falar, evitando que a interface congele.
        threading.Thread(target=self.falar_texto, args=(texto_saldo,), daemon=True).start()

    # Converte o saldo do robo em texto e o fala.
    def falar_saldo_restante_robo(self):
        if not self.jogo_ativo: return
        saldo = self.valor_alvo - self.total_robo
        reais = int(saldo)
        centavos = int(round((saldo - reais) * 100))
        texto_saldo = f"O saldo restante do robo é de {reais} reais"
        texto_saldo += f" e {centavos} centavos." if centavos > 0 else "."
        threading.Thread(target=self.falar_texto, args=(texto_saldo,), daemon=True).start()

    # Atualiza a exibição dos produtos na tela do meio.
    def exibir_produtos(self):
        # Limpa os produtos antigos.
        for widget in self.frame_rolavel_produtos.winfo_children():
            widget.destroy()
        
        self.botoes_produtos = [] # Reseta a lista de botões.
        self.departamento_atual = self.variavel_depto.get() # Pega o departamento selecionado.
        produtos = self.produtos_com_estoque[self.departamento_atual]
        
        linha, coluna = 0, 0
        num_colunas = 3 # Exibe os produtos em 3 colunas.
        for produto, dados_produto in produtos.items():
            preco = dados_produto["preco"]
            estoque = dados_produto["estoque"]
            nome_produto_exibicao = produto[:20] + "..." if len(produto) > 20 else produto
            
            # Cria um card para cada produto.
            frame_produto = tk.Frame(self.frame_rolavel_produtos, bd=1, relief="solid",
                                  bg="white", padx=15, pady=15)
            frame_produto.grid(row=linha, column=coluna, padx=12, pady=12, sticky="nsew") 
            
            label_nome = tk.Label(frame_produto, text=nome_produto_exibicao, font=("Arial", 12), 
                                bg="white", wraplength=180, justify="left")
            label_nome.pack(anchor="w", pady=(0, 5))

            label_preco = tk.Label(frame_produto, text=f"R${preco:.2f}", font=("Arial", 16, "bold"), 
                                 fg="#e74c3c", bg="white")
            label_preco.pack(anchor="w", pady=(0, 10))
            
            label_estoque = tk.Label(frame_produto, text=f"Estoque: {estoque}", font=("Arial", 11, "italic"),
                                   fg="#555", bg="white")
            label_estoque.pack(anchor="w", pady=(0, 10))

            # Botão para adicionar o produto ao carrinho.
            botao_adicionar = tk.Button(frame_produto, font=("Arial", 12, "bold"), fg="white", 
                                       relief="flat", cursor="hand2", pady=5, 
                                       # A função lambda é usada para passar o nome do produto correto para a função.
                                       command=lambda p=produto: self.adicionar_ao_carrinho_jogador(p))
            
            # Muda a aparência do botão com base no estoque.
            if estoque > 0:
                botao_adicionar.config(text="Adicionar ao Carrinho", state=tk.NORMAL, bg="#27ae60")
            else:
                botao_adicionar.config(text="Fora de Estoque", state=tk.DISABLED, bg="#95a5a6")

            # Desabilita o botão se não for o turno do jogador.
            if not self.turno_do_jogador:
                botao_adicionar.config(state=tk.DISABLED)

            botao_adicionar.pack(side="bottom", pady=5, fill="x")
            self.botoes_produtos.append(botao_adicionar)
            
            # Lógica para organizar os produtos em colunas.
            coluna += 1
            if coluna >= num_colunas:
                coluna = 0
                linha += 1
            
    # Lógica para adicionar um produto ao carrinho do jogador.
    def adicionar_ao_carrinho_jogador(self, nome_produto, falar_nome=True):
        if not self.jogo_ativo or not self.turno_do_jogador:
            return
        
        dados_produto = self.produtos_com_estoque["Todos"][nome_produto]
        preco_produto = dados_produto["preco"]
        
        # Verifica se há estoque.
        if dados_produto["estoque"] <= 0:
            messagebox.showwarning("Sem Estoque", f"O produto '{nome_produto}' está fora de estoque!")
            return

        # Verifica se o preço não excede o valor-alvo.
        if self.total_jogador + preco_produto <= self.valor_alvo:
            self.carrinho_jogador.append((nome_produto, preco_produto))
            self.total_jogador += preco_produto
            dados_produto["estoque"] -= 1 # Decrementa o estoque.
            
            # Atualiza a interface.
            self.display_carrinho_jogador.insert(tk.END, f"{nome_produto} - R$ {preco_produto:.2f}")
            self.label_total_jogador.config(text=f"💰 SEU TOTAL: R$ {self.total_jogador:.2f}")
            saldo_restante = self.valor_alvo - self.total_jogador
            self.label_saldo_restante.config(text=f"SALDO: R$ {saldo_restante:.2f}")

            if falar_nome:
                texto_para_falar = f"{nome_produto} adicionado"
                threading.Thread(target=self.falar_texto, args=(texto_para_falar,), daemon=True).start()
            
            self.canvas_carrinho_vazio.update_idletasks()
            self.redesenhar_carrinho_jogador()
            self.exibir_produtos() # Atualiza os produtos para mostrar o novo estoque.

            # Verifica se o jogador atingiu o valor exato.
            if abs(self.total_jogador - self.valor_alvo) < 0.01:
                messagebox.showinfo("Parabéns!", "🎉 Você atingiu o valor exato!")
                self.finalizar_compra()
            else:
                self._passar_turno_para_robo() # Passa o turno.
        else:
            messagebox.showwarning("Orçamento Excedido", f"Não é possível adicionar '{nome_produto}'.\nSeu saldo restante é de R$ {self.valor_alvo - self.total_jogador:.2f}.")

    # Lógica para remover um item do carrinho do jogador.
    def remover_do_carrinho(self, index_para_remover=None):
        if not self.jogo_ativo or not self.turno_do_jogador:
            return

        indice = -1
        # Se um índice foi passado (pelo comando de voz), usa ele.
        if index_para_remover is not None:
            indice = index_para_remover
        # Senão, pega o item selecionado na Listbox.
        else:
            selecao = self.display_carrinho_jogador.curselection()
            if selecao:
                indice = selecao[0]
        
        if indice != -1 and 0 <= indice < len(self.carrinho_jogador):
            item_removido = self.carrinho_jogador[indice]
            nome_produto = item_removido[0]
            
            # Atualiza os valores e a interface.
            self.total_jogador -= item_removido[1]
            self.carrinho_jogador.pop(indice)
            self.display_carrinho_jogador.delete(indice)
            self.produtos_com_estoque["Todos"][nome_produto]["estoque"] += 1 # Devolve o item ao estoque.
            
            self.label_total_jogador.config(text=f"💰 SEU TOTAL: R$ {self.total_jogador:.2f}")
            saldo_restante = self.valor_alvo - self.total_jogador
            self.label_saldo_restante.config(text=f"SALDO: R$ {saldo_restante:.2f}")
            
            self.canvas_carrinho_vazio.update_idletasks()
            self.redesenhar_carrinho_jogador()
            self.exibir_produtos() # Atualiza a exibição de produtos.

            texto_para_falar = f"{item_removido[0]} removido"
            threading.Thread(target=self.falar_texto, args=(texto_para_falar,), daemon=True).start()
            
    # Lógica do turno do robo (IA).
    def executar_turno_robo(self):
        # Encontra o melhor item para adicionar com base no algoritmo escolhido.
        melhor_item = self._encontrar_melhor_proximo_item()
        
        if melhor_item:
            nome_produto, preco_produto = melhor_item
            
            # Adiciona o item ao carrinho do robo.
            self.carrinho_robo.append((nome_produto, preco_produto))
            self.total_robo += preco_produto
            self.produtos_com_estoque["Todos"][nome_produto]["estoque"] -= 1 # Remove do estoque compartilhado.
            
            self.atualizar_display_robo() # Atualiza a interface do robo.
        else:
            # Se não encontrou nenhum item válido, o robo passa a vez.
            print("Robo passou a vez.")
        
        self.exibir_produtos() # Atualiza a exibição de produtos para refletir a mudança no estoque.
        
        self._passar_turno_para_jogador() # Devolve o turno para o jogador.
    
    # Função heurística para o algoritmo A*. Calcula a diferença absoluta até o valor-alvo.
    def heuristica(self, total_atual):
        return abs(self.valor_alvo - total_atual)

    # Implementação do algoritmo A*
    def busca_a_estrela(self):
        # 1. Cria uma lista de produtos disponíveis com base no estoque atual.
        produtos_disponiveis = []
        for nome, dados in self.produtos_com_estoque["Todos"].items():
            if dados["estoque"] > 0:
                produtos_disponiveis.append((nome, dados["preco"]))
        
        # 2. Inicializa a fronteira (fila de prioridade) e o conjunto de visitados.
        fronteira = []
        visitados = set()

        # 3. O estado inicial é o carrinho atual do robo.
        h_inicial = self.heuristica(self.total_robo)
        g_inicial = len(self.carrinho_robo)
        f_inicial = g_inicial + h_inicial

        # A fronteira armazena: (f_score, h_score, total_monetario, caminho_do_carrinho)
        heapq.heappush(fronteira, (f_inicial, h_inicial, self.total_robo, self.carrinho_robo.copy()))
        
        # Guarda a melhor solução encontrada até agora como fallback.
        melhor_solucao = (self.carrinho_robo.copy(), self.total_robo)
        melhor_pontuacao_h = h_inicial
        
        passos_limite = 2000 # Limite de segurança para evitar loops infinitos.
        passo = 0
        while fronteira and passo < passos_limite:
            passo += 1
            _, h_atual, total_atual, carrinho_atual = heapq.heappop(fronteira)
            
            # Cria um identificador único para o estado atual para o conjunto de visitados.
            estado_atual = (round(total_atual, 2), tuple(sorted(p[0] for p in carrinho_atual)))
            if estado_atual in visitados:
                continue
            visitados.add(estado_atual)

            # Se o estado atual é o mais próximo do alvo que já vimos, salvamos.
            if h_atual < melhor_pontuacao_h:
                melhor_solucao = (carrinho_atual.copy(), total_atual)
                melhor_pontuacao_h = h_atual

            # Se encontramos a solução exata, retornamos.
            if abs(total_atual - self.valor_alvo) < 0.01:
                return carrinho_atual, round(total_atual, 2)
            
            # 4. Expande para os próximos estados possíveis.
            itens_no_carrinho = {p[0] for p in carrinho_atual}
            for produto, preco in produtos_disponiveis:
                novo_total = total_atual + preco
                if novo_total <= self.valor_alvo and produto not in itens_no_carrinho:
                    novo_carrinho = carrinho_atual + [(produto, preco)]
                    
                    # Calcula os custos para o novo estado.
                    g_novo = len(novo_carrinho)
                    h_novo = self.heuristica(novo_total)
                    f_novo = g_novo + h_novo
                    
                    heapq.heappush(fronteira, (f_novo, h_novo, novo_total, novo_carrinho))
                    
        # Se o loop terminar, retorna a melhor solução parcial encontrada.
        return melhor_solucao[0], round(melhor_solucao[1], 2)

    # Estratégia do robo para escolher o próximo item.
    def _encontrar_melhor_proximo_item(self):
        algoritmo = self.variavel_algoritmo.get()
        
        # --- Lógica da Busca Gulosa ---
        if algoritmo == "Gulosa":
            produtos_disponiveis = []
            for nome, dados in self.produtos_com_estoque["Todos"].items():
                if dados["estoque"] > 0 and self.total_robo + dados["preco"] <= self.valor_alvo:
                    produtos_disponiveis.append((nome, dados["preco"]))
            
            if not produtos_disponiveis:
                return None 
            # Retorna o item mais caro que cabe no orçamento.
            return sorted(produtos_disponiveis, key=lambda x: x[1], reverse=True)[0]
        
        # --- Lógica do Algoritmo A* ---
        else: # A*
            # 1. Roda a busca A* para encontrar o carrinho final ideal.
            carrinho_ideal, _ = self.busca_a_estrela()
            
            if not carrinho_ideal:
                return None

            # 2. Descobre qual o próximo item do caminho ideal que o robo deve pegar.
            itens_atuais_robo = {item[0] for item in self.carrinho_robo}
            
            for item_do_caminho_ideal in carrinho_ideal:
                if item_do_caminho_ideal[0] not in itens_atuais_robo:
                    # Verifica se o item ainda está em estoque (pode ter sido pego pelo jogador).
                    dados_produto = self.produtos_com_estoque["Todos"].get(item_do_caminho_ideal[0])
                    if dados_produto and dados_produto["estoque"] > 0:
                        return item_do_caminho_ideal # Retorna o próximo melhor passo (produto, preco).
            
            return None # Não há um próximo passo válido.
            
    # Atualiza a interface do robo (carrinho, total, saldo).
    def atualizar_display_robo(self):
        self.display_carrinho_robo.delete(0, tk.END)
        for produto, preco in self.carrinho_robo:
            self.display_carrinho_robo.insert(tk.END, f"{produto} - R$ {preco:.2f}")
            
        self.label_total_robo.config(text=f"💰 TOTAL ROBO: R$ {self.total_robo:.2f}")
        saldo_restante_robo = self.valor_alvo - self.total_robo
        self.label_saldo_restante_robo.config(text=f"SALDO: R$ {saldo_restante_robo:.2f}")

    # Lógica para finalizar a rodada e determinar o vencedor.
    def finalizar_compra(self):
        if not self.jogo_ativo: return
        self.jogo_ativo = False
        
        # Calcula a diferença de cada jogador para o valor-alvo.
        diff_jogador = abs(self.valor_alvo - self.total_jogador)
        diff_robo = abs(self.valor_alvo - self.total_robo)
        
        # Determina o vencedor.
        vencedor = "EMPATE"
        if diff_jogador < diff_robo:
            vencedor = "JOGADOR"
        elif diff_robo < diff_jogador:
            vencedor = "ROBO"
        else: # Em caso de empate na diferença, vence quem comprou menos itens.
            if len(self.carrinho_jogador) < len(self.carrinho_robo):
                vencedor = "JOGADOR"
            elif len(self.carrinho_robo) < len(self.carrinho_jogador):
                vencedor = "ROBO"
        
        # Monta a mensagem de resultado.
        msg_resultado = f"🎯 VALOR-ALVO: R$ {self.valor_alvo:.2f}\n\n"
        msg_resultado += f"👤 JOGADOR: R$ {self.total_jogador:.2f} ({len(self.carrinho_jogador)} itens)\n"
        msg_resultado += f"🤖 ROBO: R$ {self.total_robo:.2f} ({len(self.carrinho_robo)} itens)\n\n"
        
        if vencedor == "JOGADOR":
            msg_resultado += "🎉 VOCÊ VENCEU! Parabéns!"
        elif vencedor == "ROBO":
            msg_resultado += "🤖 O ROBO VENCEU! Tente novamente!"
        else:
            msg_resultado += "⚖️ EMPATE! Ambos foram igualmente bons!"
        
        messagebox.showinfo("Resultado Final", msg_resultado)
        
        # Se o jogador comprou algo, mostra a nota fiscal.
        if self.carrinho_jogador:
            self.mostrar_nota_fiscal()

    # Cria uma nova janela (Toplevel) para mostrar a nota fiscal da compra do jogador.
    def mostrar_nota_fiscal(self):
        nota_window = tk.Toplevel(self.master)
        nota_window.title("Nota da Sua Compra")
        nota_window.geometry("450x600")
        nota_window.configure(bg="#f5f5f5")
        nota_window.resizable(False, False)

        # Centraliza a janela da nota fiscal em relação à janela principal.
        self.master.update_idletasks()
        master_x = self.master.winfo_x()
        master_y = self.master.winfo_y()
        master_width = self.master.winfo_width()
        master_height = self.master.winfo_height()
        nota_width = 450
        nota_height = 600
        x = master_x + (master_width // 2) - (nota_width // 2)
        y = master_y + (master_height // 2) - (nota_height // 2)
        nota_window.geometry(f'{nota_width}x{nota_height}+{x}+{y}')

        frame_nota = tk.Frame(nota_window, bg="white", bd=2, relief="groove")
        frame_nota.pack(padx=20, pady=20, fill="both", expand=True)

        # Usa uma fonte monoespaçada para alinhar o texto da nota.
        receipt_font = font.Font(family="Courier", size=11)

        header_text = "MAIS POR MENOS SUPERMERCADO\n"
        header_text += "-" * 45 + "\n"
        header_text += "      CUPOM FISCAL      \n"
        header_text += "-" * 45
        
        label_header = tk.Label(frame_nota, text=header_text, font=receipt_font, bg="white", justify="left")
        label_header.pack(pady=(10, 5))

        # Usa um widget Text para exibir a lista de itens formatada.
        text_itens = tk.Text(frame_nota, font=receipt_font, bg="white", bd=0, highlightthickness=0, height=15, width=45)
        text_itens.pack(padx=15, fill="x")
        
        text_itens.insert(tk.END, f'{"ITEM":<3} {"DESCRIÇÃO":<25} {"VALOR (R$)":>12}\n')
        text_itens.insert(tk.END, "-" * 45 + "\n")
        
        for i, (produto, preco) in enumerate(self.carrinho_jogador, 1):
            nome_produto_curto = (produto[:22] + '..') if len(produto) > 24 else produto
            linha = f"{i:03d} {nome_produto_curto:<25} {preco:>12.2f}\n"
            text_itens.insert(tk.END, linha)

        text_itens.insert(tk.END, "\n" + "=" * 45 + "\n")
        total_line = f'{"TOTAL R$":<30} {self.total_jogador:>15.2f}\n'
        text_itens.insert(tk.END, total_line)
        text_itens.configure(state="disabled") # Torna o texto não editável.

        botao_fechar = tk.Button(frame_nota, text="Fechar",
                                 font=("Arial", 12, "bold"),
                                 bg="#e74c3c", fg="white",
                                 command=nota_window.destroy,
                                 relief="flat", padx=20, pady=8)
        botao_fechar.pack(pady=20)
        
        # Configura a janela da nota como modal (bloqueia a interação com a janela principal).
        nota_window.transient(self.master)
        nota_window.grab_set()
        self.master.wait_window(nota_window)

    # Inicia uma nova rodada do jogo.
    def iniciar_nova_rodada(self):
        self.inicializar_jogo()


# Ponto de entrada do programa.
if __name__ == "__main__":
    root = tk.Tk()  # Cria a janela principal do Tkinter.
    app = JogoSupermercado(root) # Cria uma instância da nossa classe de jogo.
    root.mainloop() # Inicia o loop principal da interface gráfica, que aguarda por eventos.