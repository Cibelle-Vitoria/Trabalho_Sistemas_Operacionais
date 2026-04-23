
import tkinter as tk
from tkinter import ttk, messagebox
import psutil
import platform
import time
from datetime import datetime

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure


def formatar_bytes(valor):
    unidades = ["B", "KB", "MB", "GB", "TB"]
    tamanho = float(valor)
    for unidade in unidades:
        if tamanho < 1024 or unidade == unidades[-1]:
            return f"{tamanho:.2f} {unidade}"
        tamanho /= 1024


class MonitorSistemaApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Monitor do Sistema - Projeto Simples")
        self.root.geometry("980x650")
        self.root.configure(bg="#f2f2f2")

        self.cpu_historico = [0] * 20
        self.mem_historico = [0] * 20

        self.criar_interface()
        self.atualizar_tudo()

    def criar_interface(self):
        titulo = tk.Label(
            self.root,
            text="Monitor do Sistema Operacional",
            font=("Arial", 18, "bold"),
            bg="#f2f2f2"
        )
        titulo.pack(pady=10)

        subtitulo = tk.Label(
            self.root,
            text="Sistema de Diagnóstico do Computador",
            font=("Arial", 10),
            bg="#f2f2f2"
        )
        subtitulo.pack()

        topo = tk.Frame(self.root, bg="#f2f2f2")
        topo.pack(fill="x", padx=10, pady=10)

        self.lbl_sistema = tk.Label(
            topo,
            text="Sistema: carregando...",
            font=("Arial", 10),
            bg="#f2f2f2",
            anchor="w"
        )
        self.lbl_sistema.pack(side="left")

        btn_frame = tk.Frame(topo, bg="#f2f2f2")
        btn_frame.pack(side="right")

        btn_atualizar = tk.Button(
            btn_frame,
            text="Atualizar agora",
            command=self.atualizar_tudo,
            width=15
        )
        btn_atualizar.pack(side="left", padx=5)

        btn_sair = tk.Button(
            btn_frame,
            text="Sair",
            command=self.root.quit,
            width=10
        )
        btn_sair.pack(side="left", padx=5)

        self.abas = ttk.Notebook(self.root)
        self.abas.pack(fill="both", expand=True, padx=10, pady=10)

        self.aba_visao = tk.Frame(self.abas, bg="white")
        self.aba_processos = tk.Frame(self.abas, bg="white")
        self.aba_pid = tk.Frame(self.abas, bg="white")
        self.aba_energia = tk.Frame(self.abas, bg="white")

        self.abas.add(self.aba_visao, text="Visão geral")
        self.abas.add(self.aba_processos, text="Processos")
        self.abas.add(self.aba_pid, text="Consultar PID")
        self.abas.add(self.aba_energia, text="Energia")

        self.criar_aba_visao()
        self.criar_aba_processos()
        self.criar_aba_pid()
        self.criar_aba_energia()

    def criar_aba_visao(self):
        info_frame = tk.Frame(self.aba_visao, bg="white")
        info_frame.pack(fill="x", padx=10, pady=10)

        self.lbl_cpu = tk.Label(info_frame, text="CPU", font=("Arial", 11), bg="white", justify="left")
        self.lbl_cpu.grid(row=0, column=0, sticky="w", padx=10, pady=10)

        self.lbl_mem = tk.Label(info_frame, text="Memória", font=("Arial", 11), bg="white", justify="left")
        self.lbl_mem.grid(row=0, column=1, sticky="w", padx=10, pady=10)

        self.lbl_disco = tk.Label(info_frame, text="Disco", font=("Arial", 11), bg="white", justify="left")
        self.lbl_disco.grid(row=1, column=0, sticky="w", padx=10, pady=10)

        self.lbl_boot = tk.Label(info_frame, text="Boot", font=("Arial", 11), bg="white", justify="left")
        self.lbl_boot.grid(row=1, column=1, sticky="w", padx=10, pady=10)

        grafico_frame = tk.Frame(self.aba_visao, bg="white")
        grafico_frame.pack(fill="both", expand=True, padx=10, pady=10)

        self.fig = Figure(figsize=(8, 4.2), dpi=100)
        self.ax_cpu = self.fig.add_subplot(211)
        self.ax_mem = self.fig.add_subplot(212)

        self.fig.tight_layout(pad=3.0)

        self.canvas = FigureCanvasTkAgg(self.fig, master=grafico_frame)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)

    def criar_aba_processos(self):
        topo = tk.Frame(self.aba_processos, bg="white")
        topo.pack(fill="x", padx=10, pady=10)

        tk.Label(
            topo,
            text="Lista de processos em execução",
            font=("Arial", 12, "bold"),
            bg="white"
        ).pack(anchor="w")

        tk.Label(
            topo,
            text="Mostrando PID, nome, uso de CPU e memória.",
            bg="white"
        ).pack(anchor="w")

        colunas = ("pid", "nome", "cpu", "memoria")
        self.tabela = ttk.Treeview(self.aba_processos, columns=colunas, show="headings", height=18)

        self.tabela.heading("pid", text="PID")
        self.tabela.heading("nome", text="Nome")
        self.tabela.heading("cpu", text="CPU %")
        self.tabela.heading("memoria", text="Memória")

        self.tabela.column("pid", width=90, anchor="center")
        self.tabela.column("nome", width=320)
        self.tabela.column("cpu", width=90, anchor="center")
        self.tabela.column("memoria", width=130, anchor="center")

        barra = ttk.Scrollbar(self.aba_processos, orient="vertical", command=self.tabela.yview)
        self.tabela.configure(yscroll=barra.set)

        self.tabela.pack(side="left", fill="both", expand=True, padx=(10, 0), pady=10)
        barra.pack(side="right", fill="y", pady=10, padx=(0, 10))

    def criar_aba_pid(self):
        frame = tk.Frame(self.aba_pid, bg="white")
        frame.pack(fill="both", expand=True, padx=20, pady=20)

        tk.Label(frame, text="Consultar processo por PID", font=("Arial", 12, "bold"), bg="white").pack(anchor="w")

        linha = tk.Frame(frame, bg="white")
        linha.pack(anchor="w", pady=10)

        tk.Label(linha, text="Digite o PID:", bg="white").pack(side="left")
        self.entry_pid = tk.Entry(linha, width=20)
        self.entry_pid.pack(side="left", padx=8)

        tk.Button(linha, text="Consultar", command=self.consultar_pid).pack(side="left")

        self.txt_pid = tk.Text(frame, height=22, width=90, font=("Consolas", 10))
        self.txt_pid.pack(fill="both", expand=True, pady=10)

    def criar_aba_energia(self):
        frame = tk.Frame(self.aba_energia, bg="white")
        frame.pack(fill="both", expand=True, padx=20, pady=20)

        tk.Label(frame, text="Informações de energia", font=("Arial", 12, "bold"), bg="white").pack(anchor="w")

        self.lbl_bateria = tk.Label(frame, text="Bateria: carregando...", bg="white", justify="left", font=("Arial", 11))
        self.lbl_bateria.pack(anchor="w", pady=10)

        self.lbl_rede = tk.Label(frame, text="Rede: carregando...", bg="white", justify="left", font=("Arial", 11))
        self.lbl_rede.pack(anchor="w", pady=10)

        self.lbl_usuarios = tk.Label(frame, text="Usuários: carregando...", bg="white", justify="left", font=("Arial", 11))
        self.lbl_usuarios.pack(anchor="w", pady=10)

    def atualizar_tudo(self):
        self.atualizar_info_sistema()
        self.atualizar_visao_geral()
        self.atualizar_tabela_processos()
        self.atualizar_energia()
        self.root.after(3000, self.atualizar_tudo)

    def atualizar_info_sistema(self):
        sistema = platform.system()
        versao = platform.release()
        maquina = platform.machine()
        self.lbl_sistema.config(text=f"Sistema: {sistema} {versao} | Arquitetura: {maquina}")

    def atualizar_visao_geral(self):
        uso_cpu = psutil.cpu_percent(interval=0.2)
        nucleos_logicos = psutil.cpu_count()
        nucleos_fisicos = psutil.cpu_count(logical=False)

        mem = psutil.virtual_memory()
        disco = psutil.disk_usage('/')

        boot = datetime.fromtimestamp(psutil.boot_time()).strftime("%d/%m/%Y %H:%M:%S")

        self.lbl_cpu.config(
            text=(
                "PROCESSADOR\n"
                f"Núcleos lógicos: {nucleos_logicos}\n"
                f"Núcleos físicos: {nucleos_fisicos}\n"
                f"Uso atual da CPU: {uso_cpu}%"
            )
        )

        self.lbl_mem.config(
            text=(
                "MEMÓRIA\n"
                f"Total: {formatar_bytes(mem.total)}\n"
                f"Em uso: {formatar_bytes(mem.used)}\n"
                f"Disponível: {formatar_bytes(mem.available)}\n"
                f"Percentual de uso: {mem.percent}%"
            )
        )

        self.lbl_disco.config(
            text=(
                "DISCO\n"
                f"Total: {formatar_bytes(disco.total)}\n"
                f"Usado: {formatar_bytes(disco.used)}\n"
                f"Livre: {formatar_bytes(disco.free)}\n"
                f"Uso: {disco.percent}%"
            )
        )

        self.lbl_boot.config(
            text=(
                "SISTEMA\n"
                f"Iniciado em: {boot}\n"
                f"Tempo desde a inicialização: {self.tempo_desde_boot()}"
            )
        )

        self.cpu_historico.pop(0)
        self.cpu_historico.append(uso_cpu)

        self.mem_historico.pop(0)
        self.mem_historico.append(mem.percent)

        self.desenhar_graficos()

    def desenhar_graficos(self):
        self.ax_cpu.clear()
        self.ax_mem.clear()

        self.ax_cpu.plot(self.cpu_historico)
        self.ax_cpu.set_title("Uso da CPU (%)")
        self.ax_cpu.set_ylim(0, 100)
        self.ax_cpu.set_ylabel("%")

        self.ax_mem.plot(self.mem_historico)
        self.ax_mem.set_title("Uso da Memória (%)")
        self.ax_mem.set_ylim(0, 100)
        self.ax_mem.set_ylabel("%")
        self.ax_mem.set_xlabel("Atualizações")

        self.fig.tight_layout(pad=3.0)
        self.canvas.draw()

    def atualizar_tabela_processos(self):
        for item in self.tabela.get_children():
            self.tabela.delete(item)

        processos = []
        for proc in psutil.process_iter(["pid", "name", "memory_info"]):
            try:
                pid = proc.info["pid"]
                nome = proc.info["name"] or "Sem nome"
                memoria = formatar_bytes(proc.info["memory_info"].rss) if proc.info["memory_info"] else "N/A"
                cpu = proc.cpu_percent(interval=None)
                processos.append((pid, nome, cpu, memoria))
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                continue

        processos.sort(key=lambda x: x[0])

        for pid, nome, cpu, memoria in processos[:120]:
            self.tabela.insert("", "end", values=(pid, nome, f"{cpu:.1f}", memoria))

    def consultar_pid(self):
        self.txt_pid.delete("1.0", tk.END)

        try:
            pid = int(self.entry_pid.get())
        except ValueError:
            messagebox.showerror("Erro", "Digite um PID válido.")
            return

        try:
            proc = psutil.Process(pid)

            nome = proc.name()
            status = proc.status()
            memoria = formatar_bytes(proc.memory_info().rss)
            cpu = proc.cpu_percent(interval=0.2)
            criado = datetime.fromtimestamp(proc.create_time()).strftime("%d/%m/%Y %H:%M:%S")
            tempo_execucao = self.tempo_execucao_processo(proc.create_time())

            texto = (
                f"Detalhes do processo PID {pid}\n"
                f"----------------------------------------\n"
                f"Nome: {nome}\n"
                f"Status: {status}\n"
                f"Uso de memória: {memoria}\n"
                f"Uso de CPU: {cpu:.2f}%\n"
                f"Iniciado em: {criado}\n"
                f"Tempo de execução: {tempo_execucao}\n"
            )

            self.txt_pid.insert(tk.END, texto)

        except psutil.NoSuchProcess:
            messagebox.showerror("Erro", "Esse PID não existe mais.")
        except psutil.AccessDenied:
            messagebox.showerror("Erro", "Acesso negado a esse processo.")
        except Exception as erro:
            messagebox.showerror("Erro", f"Não foi possível consultar o processo.\n{erro}")

    def atualizar_energia(self):
        bateria = psutil.sensors_battery()
        if bateria is None:
            texto_bateria = "Bateria: informação não disponível nesta máquina."
        else:
            ligado = "Sim" if bateria.power_plugged else "Não"
            texto_bateria = (
                f"Nível da bateria: {bateria.percent}%\n"
                f"Conectado à energia: {ligado}"
            )

        io_rede = psutil.net_io_counters()
        texto_rede = (
            f"Bytes enviados: {formatar_bytes(io_rede.bytes_sent)}\n"
            f"Bytes recebidos: {formatar_bytes(io_rede.bytes_recv)}"
        )

        usuarios = psutil.users()
        if usuarios:
            lista = ", ".join([u.name for u in usuarios])
            texto_usuarios = f"Usuários conectados: {lista}"
        else:
            texto_usuarios = "Usuários conectados: não foi possível identificar ou não há usuários listados."

        self.lbl_bateria.config(text=texto_bateria)
        self.lbl_rede.config(text=texto_rede)
        self.lbl_usuarios.config(text=texto_usuarios)

    def tempo_desde_boot(self):
        segundos = int(time.time() - psutil.boot_time())
        horas = segundos // 3600
        minutos = (segundos % 3600) // 60
        seg = segundos % 60
        return f"{horas}h {minutos}min {seg}s"

    def tempo_execucao_processo(self, create_time):
        segundos = int(time.time() - create_time)
        horas = segundos // 3600
        minutos = (segundos % 3600) // 60
        seg = segundos % 60
        return f"{horas}h {minutos}min {seg}s"


if __name__ == "__main__":
    root = tk.Tk()
    app = MonitorSistemaApp(root)
    root.mainloop()
