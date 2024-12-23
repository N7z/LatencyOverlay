import time
from ping3 import ping
from colorama import Fore, Style
import tkinter as tk

# Configurações iniciais
target = "8.8.8.8"
loss_window = []
max_window_size = 15
refresh_delay = 500  # em milissegundos

# Cria janela de overlay
def create_overlay():
    root = tk.Tk()
    
    # Configurações da janela
    root.geometry(f"400x30+{root.winfo_screenwidth() - 445}+{root.winfo_screenheight() - 80}")
    root.overrideredirect(1)  # Remove bordas da janela
    root.attributes("-topmost", True)  # Janela sempre no topo
    root.configure(bg="black")  # Cor de fundo preta

    # Configuração do texto
    label = tk.Label(
        root,
        text="Latency: -- ms",
        fg="white",
        bg="black",
        font=("Helvetica", 16)
    )
    label.pack(expand=True)

    # Retorna a janela e lambda para atualizar o texto
    return root, lambda text, color: label.config(text=text, fg=color)

# Função para atualizar a interface e realizar o ping
def update_overlay():
    try:
        # Realiza o ping
        latency = ping(target, timeout=2)

        # Atualiza o "intervalo" de loss
        if latency is None:
            loss_window.append(1)  # Pacote perdido
        else:
            loss_window.append(0)  # Pacote recebido

        # Remove elementos antigos do loss
        if len(loss_window) > max_window_size:
            loss_window.pop(0)

        # Calcula o número de pacotes perdidos
        loss_count = sum(loss_window)

        # Determina a mensagem e a cor com base no resultado
        if latency is None:
            alert = "⚠️ "
            msg = f"{alert}Latency: ---- | Packets lost: {loss_count}/{max_window_size}"
            color = "red"
        else:
            latency_ms = round(latency * 1000, 2)
            alert = ""
            msg = f"{alert}Latency: {latency_ms} ms | Packets lost: {loss_count}/{max_window_size}"
            
            if latency_ms < 100:
                color = "green"
            elif latency_ms < 300:
                color = "yellow"
            else:
                color = "red"

        # Exibe a mensagem no terminal
        if latency is None:
            print(Fore.RED + f"\r{msg}      " + Style.RESET_ALL, end="", flush=True)
        else:
            print(Fore.GREEN + f"\r{msg}      " + Style.RESET_ALL, end="", flush=True)

        # Atualiza o texto na janela
        update_label(msg, color)

        # Agenda a próxima execução
        root.after(refresh_delay, update_overlay)
    except KeyboardInterrupt:
        # Trata a interrupção e fecha o Tkinter corretamente
        root.destroy()
        print(Fore.YELLOW + "\nExiting..." + Style.RESET_ALL)

# Criação da interface
root, update_label = create_overlay()

# Exibe uma mensagem inicial no terminal
print(Fore.CYAN + f"Pinging {target}. Press Ctrl+C to stop." + Style.RESET_ALL)

# Inicia o loop principal
try:
    root.after(0, update_overlay)
    root.mainloop()
except KeyboardInterrupt:
    root.destroy()
    print(Fore.YELLOW + "\nExiting..." + Style.RESET_ALL)
