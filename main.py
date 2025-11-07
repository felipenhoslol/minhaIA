import tkinter as tk
from tkinter import scrolledtext, messagebox
import threading
import queue
import sys
import time

# ==============================================================================
#  TEMAS DE CORES (Mantido como estava)
# ==============================================================================
dark_theme = {
    "bg": "black", "fg": "#FF0000", "widget_bg": "#1a1a1a", "widget_fg": "white",
    "button_bg": "#FF0000", "button_fg": "black", "button_active_bg": "#b30000",
    "entry_bg": "#333333", "entry_fg": "white", "user_color": "#FF4d4d", "bot_color": "#FFB3B3"
}
light_theme = {
    "bg": "#f0f0f0", "fg": "#FF0000", "widget_bg": "white", "widget_fg": "black",
    "button_bg": "#FF0000", "button_fg": "white", "button_active_bg": "#b30000",
    "entry_bg": "white", "entry_fg": "black", "user_color": "#d90000", "bot_color": "#000000"
}

# ==============================================================================
#  CLASSE PRINCIPAL DA APLICAÇÃO
# ==============================================================================
class ChatApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Chatbot IA - Projeto Final")
        self.geometry("500x700")
        
        container = tk.Frame(self)
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames = {}
        self.current_user = "Usuário" 

        for F in (LoginFrame, ChatFrame):
            frame = F(container, self)
            self.frames[F] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame(LoginFrame)

    def show_frame(self, cont):
        frame = self.frames[cont]
        frame.tkraise()
        
    def successful_login(self, username):
        self.current_user = username
        self.show_frame(ChatFrame)
        self.frames[ChatFrame].setup_chat(username)

# ==============================================================================
#  FRAME DA TELA DE LOGIN
# ==============================================================================
class LoginFrame(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        
        self.PREDEFINED_USER = "aluno"
        self.PREDEFINED_PASS = "12345"
        
        self.configure(bg=dark_theme["bg"])

        login_container = tk.Frame(self, bg=dark_theme["bg"])
        login_container.place(relx=0.5, rely=0.5, anchor="center")

        title = tk.Label(login_container, text="LOGIN CHATBOT", font=("Helvetica", 20, "bold"), 
                         fg=dark_theme["fg"], bg=dark_theme["bg"])
        title.pack(pady=20)

        user_label = tk.Label(login_container, text="Usuário:", font=("Helvetica", 12), 
                              fg=dark_theme["fg"], bg=dark_theme["bg"])
        user_label.pack(pady=(10, 5))
        self.user_entry = tk.Entry(login_container, font=("Helvetica", 12), 
                                   bg=dark_theme["entry_bg"], fg=dark_theme["entry_fg"], 
                                   insertbackground=dark_theme["fg"], relief="flat")
        self.user_entry.pack(pady=5, padx=20)

        pass_label = tk.Label(login_container, text="Senha:", font=("Helvetica", 12), 
                              fg=dark_theme["fg"], bg=dark_theme["bg"])
        pass_label.pack(pady=(10, 5))
        self.pass_entry = tk.Entry(login_container, show="*", font=("Helvetica", 12), 
                                   bg=dark_theme["entry_bg"], fg=dark_theme["entry_fg"], 
                                   insertbackground=dark_theme["fg"], relief="flat")
        self.pass_entry.pack(pady=5, padx=20)
        
        self.error_label = tk.Label(login_container, text="", font=("Helvetica", 10), 
                                    fg="orange", bg=dark_theme["bg"])
        self.error_label.pack(pady=10)

        login_button = tk.Button(login_container, text="Entrar", font=("Helvetica", 12, "bold"), 
                                 command=self.attempt_login, bg=dark_theme["button_bg"], 
                                 fg=dark_theme["button_fg"], activebackground=dark_theme["button_active_bg"],
                                 activeforeground=dark_theme["button_fg"], relief="flat", padx=20)
        login_button.pack(pady=20)
        
        self.pass_entry.bind("<Return>", self.attempt_login)
        self.user_entry.bind("<Return>", self.attempt_login)

    def attempt_login(self, event=None):
        username = self.user_entry.get()
        password = self.pass_entry.get()

        if username == self.PREDEFINED_USER and password == self.PREDEFINED_PASS:
            self.error_label.config(text="")
            self.controller.successful_login(username)
        else:
            self.error_label.config(text="Usuário ou senha inválidos.")


# ==============================================================================
#  FRAME DA TELA PRINCIPAL DO CHAT
# ==============================================================================
class ChatFrame(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.username = "Usuário"
        self.current_theme = "dark"
        self.theme_colors = dark_theme
        
        self.configure(bg=self.theme_colors["bg"])
        
        self.response_queue = queue.Queue()
        
        # Chamadas cruciais que estavam faltando
        self.setup_ui()
        self.apply_theme()

    def setup_chat(self, username):
        """Prepara o chat com o nome do usuário e uma mensagem de boas-vindas."""
        self.username = username
        self.add_message_to_chat(
            "ChatBot", "🤖",
            f"Olá {self.username}! Sou um assistente de TI. Pergunte-me sobre 'python', 'redes', 'hardware' ou 'software'.", "bot"
        )

    def setup_ui(self):
        """Cria todos os widgets da interface do chat (botões, caixas de texto, etc.)."""
        top_frame = tk.Frame(self, bg=self.theme_colors["bg"])
        top_frame.pack(side="top", fill="x", padx=10, pady=5)
        
        self.theme_button = tk.Button(top_frame, text="Alternar Tema", command=self.toggle_theme, relief="flat")
        self.theme_button.pack(side="left", padx=5)
        
        self.clear_button = tk.Button(top_frame, text="Limpar Chat", command=self.clear_chat, relief="flat")
        self.clear_button.pack(side="right", padx=5)
        
        chat_frame = tk.Frame(self, bg=self.theme_colors["widget_bg"], bd=1, relief="solid")
        chat_frame.pack(side="top", fill="both", expand=True, padx=10, pady=5)

        self.chat_display = scrolledtext.ScrolledText(chat_frame, wrap=tk.WORD, state="disabled", bd=0, relief="flat")
        self.chat_display.pack(fill="both", expand=True, padx=5, pady=5)
        
        self.chat_display.tag_config("user_name", font=("Helvetica", 10, "bold"), justify="right")
        self.chat_display.tag_config("user_msg", font=("Helvetica", 11), justify="right", spacing1=5, spacing3=15, rmargin=10)
        self.chat_display.tag_config("bot_name", font=("Helvetica", 10, "bold"), justify="left")
        self.chat_display.tag_config("bot_msg", font=("Helvetica", 11), justify="left", spacing1=5, spacing3=15, lmargin1=10, lmargin2=10)

        bottom_frame = tk.Frame(self, bg=self.theme_colors["bg"])
        bottom_frame.pack(side="bottom", fill="x", padx=10, pady=10)

        self.entry_field = tk.Entry(bottom_frame, font=("Helvetica", 12), relief="flat")
        self.entry_field.pack(side="left", fill="x", expand=True, ipady=8)
        
        self.send_button = tk.Button(bottom_frame, text="Enviar", font=("Helvetica", 10, "bold"), command=self.send_message, relief="flat")
        self.send_button.pack(side="right", padx=(5, 0), ipady=5, ipadx=10)

        self.entry_field.bind("<Return>", self.send_message)
        self.after(100, self.process_response_queue)

    def get_ai_response(self, user_message):
        """
        IA Simulada que responde a palavras-chave de TI.
        Custo zero, funciona offline e cumpre todos os requisitos da atividade.
        """
        msg_lower = user_message.lower()
        response_text = "Desculpe, não reconheci o comando. Como um assistente de TI, posso falar sobre: 'python', 'tkinter', 'redes', 'hardware' ou 'software'."

        ti_responses = {
            "python": "Python é uma linguagem de programação versátil e poderosa, ideal para backend, ciência de dados e automação. Você está usando-a agora mesmo com Tkinter!",
            "tkinter": "Tkinter é a biblioteca padrão do Python para criar interfaces gráficas (GUI). É ótima para criar aplicações desktop como esta, de forma rápida e eficiente.",
            "rede": "Redes de computadores são essenciais para a comunicação de dados. O modelo TCP/IP, com suas camadas, é a base de toda a internet que usamos hoje.",
            "hardware": "Hardware é a parte física de um computador. Isso inclui a CPU (o cérebro), a RAM (memória de curto prazo) e o SSD/HD (armazenamento de longo prazo).",
            "software": "Software são os programas e sistemas operacionais que rodam no hardware. Eles são as instruções que fazem a máquina funcionar e ser útil para nós.",
            "segurança": "Segurança da informação é crucial. Envolve proteger dados contra acesso não autorizado, usando técnicas como criptografia, firewalls e senhas fortes.",
            "olá": f"Olá, {self.username}! Pronto para falar sobre tecnologia? Mande sua pergunta sobre TI.",
            "tudo bem": "Tudo ótimo por aqui, rodando em bits e bytes! E com você?",
            "tchau": "Até a próxima! Se tiver mais dúvidas de TI, é só chamar.",
            "obrigado": "De nada! Fico feliz em ajudar."
        }
        
        for keyword, response in ti_responses.items():
            if keyword in msg_lower:
                response_text = response
                break

        time.sleep(1.5)
        self.response_queue.put(response_text)

    def apply_theme(self):
        colors = self.theme_colors
        self.configure(bg=colors["bg"])
        self.winfo_children()[0].configure(bg=colors["bg"])
        self.winfo_children()[1].configure(bg=colors["widget_bg"])
        self.winfo_children()[2].configure(bg=colors["bg"])
        self.theme_button.configure(bg=colors["button_bg"], fg=colors["button_fg"], activebackground=colors["button_active_bg"], activeforeground=colors["button_fg"])
        self.clear_button.configure(bg=colors["button_bg"], fg=colors["button_fg"], activebackground=colors["button_active_bg"], activeforeground=colors["button_fg"])
        self.send_button.configure(bg=colors["button_bg"], fg=colors["button_fg"], activebackground=colors["button_active_bg"], activeforeground=colors["button_fg"])
        self.chat_display.configure(bg=colors["widget_bg"], fg=colors["widget_fg"], insertbackground=colors["widget_fg"])
        self.chat_display.tag_config("user_name", foreground=colors["user_color"])
        self.chat_display.tag_config("user_msg", foreground=colors["widget_fg"])
        self.chat_display.tag_config("bot_name", foreground=colors["bot_color"])
        self.chat_display.tag_config("bot_msg", foreground=colors["widget_fg"])
        self.entry_field.configure(bg=colors["entry_bg"], fg=colors["entry_fg"], insertbackground=colors["entry_fg"])

    def toggle_theme(self):
        if self.current_theme == "dark":
            self.current_theme = "light"; self.theme_colors = light_theme; self.theme_button.config(text="Modo Escuro")
        else:
            self.current_theme = "dark"; self.theme_colors = dark_theme; self.theme_button.config(text="Modo Claro")
        self.apply_theme()

    def clear_chat(self):
        self.chat_display.config(state="normal")
        self.chat_display.delete("1.0", tk.END)
        self.chat_display.config(state="disabled")
        self.add_message_to_chat("ChatBot", "🤖", "O histórico foi limpo. Pode perguntar de novo!", "bot")

    def send_message(self, event=None):
        msg = self.entry_field.get()
        if not msg.strip(): return
        self.entry_field.delete(0, tk.END)
        self.add_message_to_chat(self.username, "🧑", msg, "user")
        self.add_message_to_chat("ChatBot", "🤖", "Digitando...", "bot_typing")
        threading.Thread(target=self.get_ai_response, args=(msg,), daemon=True).start()

    def process_response_queue(self):
        try:
            response = self.response_queue.get_nowait()
            self.chat_display.config(state="normal")
            content = self.chat_display.get("1.0", tk.END)
            last_bot_icon_pos = content.rfind("🤖")
            if last_bot_icon_pos != -1:
                line_number = content[:last_bot_icon_pos].count('\n') + 1
                self.chat_display.delete(f"{line_number}.0", tk.END)
            self.chat_display.config(state="disabled")
            self.add_message_to_chat("ChatBot", "🤖", response, "bot")
        except queue.Empty:
            pass
        self.after(100, self.process_response_queue)

    def add_message_to_chat(self, user, icon, message, tag_type):
        self.chat_display.config(state="normal")
        if self.chat_display.get("end-2c", "end-1c") != '\n': self.chat_display.insert(tk.END, "\n")
        if tag_type == "user":
            self.chat_display.insert(tk.END, f"{user} {icon}\n", "user_name")
            self.chat_display.insert(tk.END, f"{message}\n", "user_msg")
        elif tag_type in ("bot", "bot_typing"):
            self.chat_display.insert(tk.END, f"{icon} {user}\n", "bot_name")
            self.chat_display.insert(tk.END, f"{message}\n", "bot_msg")
        self.chat_display.see(tk.END)
        self.chat_display.config(state="disabled")

# ==============================================================================
#  INICIALIZAÇÃO DA APLICAÇÃO
# ==============================================================================
if __name__ == "__main__":
    app = ChatApp()
    app.mainloop()