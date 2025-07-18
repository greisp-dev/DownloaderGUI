import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from tkinter import filedialog, messagebox
from ttkbootstrap.scrolled import ScrolledText
import subprocess
import os
import threading
import queue
import re
import webbrowser
import urllib.request
import zipfile

# --- Classe principal da aplicação ---
class DownloaderApp:
    def __init__(self, master):
        self.master = master
        master.title("Universal Media Downloader")
        master.geometry("800x780")

        app_data_dir = os.path.join(os.getenv('LOCALAPPDATA'), 'UniversalMediaDownloader')
        self.bin_dir = os.path.join(app_data_dir, 'bin')
        os.makedirs(self.bin_dir, exist_ok=True)
        self.yt_dlp_path = os.path.join(self.bin_dir, 'yt-dlp.exe')
        self.gallery_dl_path = os.path.join(self.bin_dir, 'gallery-dl.exe')

        self.video_quality_options = { "Melhor Possível": "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best", "4K (2160p)": "bestvideo[height<=2160][ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best", "2K (1440p)": "bestvideo[height<=1440][ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best", "1080p 60fps": "bestvideo[height<=1080][fps>30][ext=mp4]+bestaudio[ext=m4a]/best[height<=1080][ext=mp4]/best", "1080p": "bestvideo[height<=1080][fps<=30][ext=mp4]+bestaudio[ext=m4a]/best[height<=1080][ext=mp4]/best", "720p 60fps": "bestvideo[height<=720][fps>30][ext=mp4]+bestaudio[ext=m4a]/best[height<=720][ext=mp4]/best", "720p": "bestvideo[height<=720][fps<=30][ext=mp4]+bestaudio[ext=m4a]/best[height<=720][ext=mp4]/best", "480p": "bestvideo[height<=480][ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best" }
        self.audio_quality_options = { "Máxima (VBR ~256k)": "0", "Alta (VBR ~192k)": "2", "Padrão (VBR ~128k)": "5", "Baixa (VBR ~65k)": "9" }

        self.output_dir_var = tk.StringVar(value=os.path.join(os.path.expanduser("~"), "Videos", "Media Downloads"))
        self.format_var = tk.StringVar(value="mp4")
        self.quality_var = tk.StringVar(value="Melhor Possível")
        self.downloader_var = tk.StringVar(value="yt-dlp")
        self.ignore_ssl_var = tk.BooleanVar(value=False)
        self.log_queue = queue.Queue()
        self.status_queue = queue.Queue()
        self.progress_regex = re.compile(r"\[download\]\s+([0-9.]+)%")

        self._create_widgets()
        self.format_var.trace_add("write", self._on_format_change)
        
        self.master.after(100, self.process_log_queue)
        self.master.after(100, self.process_status_queue)

        self.initialization_thread = threading.Thread(target=self._initialize_dependencies, daemon=True)
        self.initialization_thread.start()

    def _create_widgets(self):
        notebook = ttk.Notebook(self.master)
        notebook.pack(fill=BOTH, expand=True, padx=10, pady=5)
        downloader_tab_frame = ttk.Frame(notebook)
        notebook.add(downloader_tab_frame, text="Downloader")
        self._populate_downloader_tab(downloader_tab_frame)
        faq_tab_frame = ttk.Frame(notebook, padding=15)
        notebook.add(faq_tab_frame, text="FAQ (Ajuda)")
        self._populate_faq_tab(faq_tab_frame)
        self.status_bar = ttk.Label(self.master, text="Iniciando...", bootstyle="inverse-info", padding=5)
        self.status_bar.pack(side=BOTTOM, fill=X)
        self.set_ui_state(True) 

    def _populate_downloader_tab(self, parent):
        paned_window = ttk.PanedWindow(parent, orient=VERTICAL)
        paned_window.pack(fill=BOTH, expand=True)
        main_frame = ttk.Frame(paned_window, padding=10)
        paned_window.add(main_frame, weight=1)
        log_frame_container = ttk.Frame(paned_window, padding=(10, 0, 10, 10))
        paned_window.add(log_frame_container, weight=1)
        self._create_header(main_frame)
        self._create_downloader_selector(main_frame)
        self._create_url_input(main_frame)
        self._create_config_options(main_frame)
        self._create_action_buttons(main_frame)
        self._create_log_area(log_frame_container)
    
    def _populate_faq_tab(self, parent):
        faq_text_area = ScrolledText(parent, wrap=WORD, padding=10, autohide=True, height=20, width=80, state="normal", font=("Segoe UI", 10))
        faq_text_area.pack(fill=BOTH, expand=True)
        faq_content = {
            "O que este programa faz?": "Este é um downloader universal que gerencia e utiliza as ferramentas `yt-dlp` e `gallery-dl` para baixar mídias da internet.",
            "Por que alguns vídeos do YouTube não baixam?": "Vídeos com restrição de idade ou que exigem login não são suportados para garantir a simplicidade do programa.",
            "Onde meus arquivos são salvos?": "Por padrão, na pasta 'Media Downloads' dentro de 'Vídeos'. Você pode mudar o local clicando em 'Procurar...'.",
            "O que a barra de status 'Iniciando...' faz?": "Ao iniciar, o programa verifica se as ferramentas `yt-dlp` e `gallery-dl` estão instaladas e atualizadas, baixando-as se necessário. Isso garante que o programa esteja sempre pronto para uso."
        }
        for question, answer in faq_content.items():
            faq_text_area.insert(END, f"{question}\n", ("h2", "bold"))
            faq_text_area.insert(END, f"{answer}\n\n", "normal")
        faq_text_area.tag_config("h2", font=("Segoe UI", 12, "bold"), spacing1=5, spacing3=5)
        faq_text_area.tag_config("normal", font=("Segoe UI", 10))
        
        # A LINHA ABAIXO FOI REMOVIDA PARA CORRIGIR O ERRO
        # faq_text_area.config(state="disabled")

    def _create_header(self, parent):
        header_frame = ttk.Frame(parent)
        header_frame.pack(fill=X, pady=(0, 10))
        ttk.Label(header_frame, text="Universal Media Downloader", font=("Segoe UI", 16, "bold")).pack(side=LEFT)
        self.theme_button = ttk.Button(header_frame, text="🌙", command=self.toggle_theme, bootstyle="light")
        self.theme_button.pack(side=RIGHT)

    def _create_downloader_selector(self, parent):
        selector_frame = ttk.Labelframe(parent, text="1. Escolha o Tipo de Download", padding=10)
        selector_frame.pack(fill=X, pady=5)
        self.yt_dlp_rb = ttk.Radiobutton(selector_frame, text="Youtube (Vídeo/Áudio) (yt-dlp)", variable=self.downloader_var, value="yt-dlp", command=self.update_ui_for_downloader)
        self.yt_dlp_rb.pack(side=LEFT, padx=10)
        self.gallery_dl_rb = ttk.Radiobutton(selector_frame, text="Outros sites (gallery-dl)", variable=self.downloader_var, value="gallery-dl", command=self.update_ui_for_downloader)
        self.gallery_dl_rb.pack(side=LEFT, padx=10)

    def _create_url_input(self, parent):
        url_frame = ttk.Labelframe(parent, text="2. Insira as URLs (uma por linha)", padding=10)
        url_frame.pack(fill=BOTH, expand=True, pady=5)
        self.url_text = tk.Text(url_frame, height=5, width=70, relief=FLAT, undo=True)
        self.url_text.pack(fill=BOTH, expand=True)

    def _create_config_options(self, parent):
        config_frame = ttk.Labelframe(parent, text="3. Configurações", padding=10)
        config_frame.pack(fill=X, pady=5)
        config_frame.columnconfigure(1, weight=1)
        ttk.Label(config_frame, text="Salvar em:").grid(row=0, column=0, sticky=W, padx=5, pady=5)
        self.output_dir_entry = ttk.Entry(config_frame, textvariable=self.output_dir_var, state="readonly")
        self.output_dir_entry.grid(row=0, column=1, sticky=EW, padx=5, pady=5)
        self.browse_button = ttk.Button(config_frame, text="Procurar...", command=self.browse_output_dir)
        self.browse_button.grid(row=0, column=2, padx=5, pady=5)
        self.format_label = ttk.Label(config_frame, text="Formato:")
        self.format_label.grid(row=1, column=0, sticky=W, padx=5, pady=5)
        self.format_combo = ttk.Combobox(config_frame, values=["mp4", "mp3"], textvariable=self.format_var, state="readonly", width=10)
        self.format_combo.grid(row=1, column=1, sticky=W, padx=5, pady=5)
        self.quality_label = ttk.Label(config_frame, text="Qualidade:")
        self.quality_label.grid(row=2, column=0, sticky=W, padx=5, pady=5)
        self.quality_combo = ttk.Combobox(config_frame, values=list(self.video_quality_options.keys()), textvariable=self.quality_var, width=20, state="readonly")
        self.quality_combo.grid(row=2, column=1, sticky=W, padx=5, pady=5)
        sep = ttk.Separator(config_frame, orient=HORIZONTAL)
        sep.grid(row=4, column=0, columnspan=3, pady=10, sticky=EW)
        warning_label = ttk.Label(config_frame, text="⚠️ Aviso: Vídeos com restrição de idade ou que exigem login não são suportados.", bootstyle="warning", font=("Segoe UI", 9))
        warning_label.grid(row=5, column=0, columnspan=3, sticky=W, padx=5)
        self.ssl_check = ttk.Checkbutton(config_frame, text="Ignorar erros de certificado SSL (uso com cautela)", variable=self.ignore_ssl_var)
        self.ssl_check.grid(row=6, column=0, columnspan=3, sticky=W, padx=5, pady=(10, 5))

    def _create_action_buttons(self, parent):
        action_frame = ttk.Frame(parent)
        action_frame.pack(fill=X, pady=(10, 0))
        self.download_button = ttk.Button(action_frame, text="Iniciar Download", command=self.start_download, bootstyle="success-outline")
        self.download_button.pack(pady=5)
        self.progress_bar = ttk.Progressbar(action_frame, mode="determinate")
        self.progress_bar.pack(fill=X, pady=5)

    def _create_log_area(self, parent):
        log_label = ttk.Labelframe(parent, text="Status / Log", padding=10)
        log_label.pack(fill=BOTH, expand=True)
        self.log_text = tk.Text(log_label, state='disabled', wrap=WORD, relief=FLAT, height=10)
        self.log_text.pack(fill=BOTH, expand=True)

    def _update_status(self, message):
        self.status_queue.put(message)

    def process_status_queue(self):
        while not self.status_queue.empty():
            message = self.status_queue.get_nowait()
            self.status_bar.config(text=message)
        self.master.after(100, self.process_status_queue)

    def _initialize_dependencies(self):
        try:
            self._update_status("Verificando dependências...")
            self._setup_yt_dlp()
            self._setup_gallery_dl()
            self._update_status("Pronto.")
            self.set_ui_state(False)
        except Exception as e:
            self._update_status(f"Erro na inicialização: {e}")
            messagebox.showerror("Erro Crítico", f"Não foi possível inicializar as dependências.\n\n{e}")

    def _setup_yt_dlp(self):
        self._check_and_update_tool('yt-dlp', self.yt_dlp_path, 'https://github.com/yt-dlp/yt-dlp/releases/latest/download/yt-dlp.exe')

    def _setup_gallery_dl(self):
        self._check_and_update_tool('gallery-dl', self.gallery_dl_path, 'https://github.com/gdl-org/builds/releases/latest/download/gallery-dl_windows.exe')

    def _check_and_update_tool(self, name, path, url):
        if not os.path.exists(path):
            self._update_status(f"Baixando {name}...")
            try:
                urllib.request.urlretrieve(url, path)
                self.log_message('log', f"✅ {name} baixado com sucesso.")
            except Exception as e:
                self.log_message('log', f"❌ Falha ao baixar {name}: {e}")
                raise e
        else:
            self._update_status(f"Verificando atualizações para {name}...")
            try:
                proc = subprocess.run([path, "-U"], capture_output=True, text=True, check=False, creationflags=subprocess.CREATE_NO_WINDOW)
                self.log_message('log', f"Atualização de {name}:\n{proc.stdout}")
            except Exception as e:
                 self.log_message('log', f"⚠️ Erro ao verificar atualização para {name}: {e}")

    def set_ui_state(self, is_disabled):
        state = 'disabled' if is_disabled else 'normal'
        if not hasattr(self, 'interactive_widgets'):
            self.interactive_widgets = [self.theme_button, self.yt_dlp_rb, self.gallery_dl_rb, self.url_text, self.browse_button, self.format_combo, self.quality_combo, self.ssl_check, self.download_button]
        for widget in self.interactive_widgets:
            try: widget.config(state=state)
            except tk.TclError: pass
        if not is_disabled: self.update_ui_for_downloader()

    def update_ui_for_downloader(self):
        if not hasattr(self, 'format_combo'): return 
        is_yt_dlp = self.downloader_var.get() == "yt-dlp"
        yt_dlp_state = "readonly" if is_yt_dlp else "disabled"
        self.format_combo.config(state=yt_dlp_state)
        self.quality_combo.config(state=yt_dlp_state)
        self.quality_label.config(state="normal" if is_yt_dlp else "disabled")
        self.format_label.config(state="normal" if is_yt_dlp else "disabled")
        if is_yt_dlp: self._on_format_change()

    def download_media(self):
        downloader_name = self.downloader_var.get()
        downloader_path = self.yt_dlp_path if downloader_name == 'yt-dlp' else self.gallery_dl_path
        urls = [url.strip() for url in self.url_text.get("1.0", tk.END).splitlines() if url.strip()]
        output_dir = self.output_dir_var.get()
        if not urls: messagebox.showerror("Erro", "Insira pelo menos uma URL.", parent=self.master); self.set_ui_state(False); return
        os.makedirs(output_dir, exist_ok=True)
        self.log_message('log', f"--- Usando {downloader_name} para {len(urls)} link(s) ---")
        self.log_message('clear_progress', None)
        cmd_base = [downloader_path]
        if downloader_name == "yt-dlp":
            cmd_base.append('--no-warnings')
            fmt = self.format_var.get()
            cmd_base.extend(["-P", output_dir])
            if fmt == "mp4":
                selected_quality_label = self.quality_var.get()
                format_string = self.video_quality_options.get(selected_quality_label, self.video_quality_options["Melhor Possível"])
                cmd_base.extend(["-f", format_string, "--merge-output-format", "mp4"])
            elif fmt == "mp3":
                selected_quality_label = self.quality_var.get()
                audio_quality_code = self.audio_quality_options.get(selected_quality_label, "0")
                cmd_base.extend(["-f", "bestaudio/best", "-x", "--audio-format", "mp3", "--audio-quality", audio_quality_code, "--embed-thumbnail", "--add-metadata"])
        elif downloader_name == "gallery-dl": cmd_base.extend(["--directory", output_dir])
        if self.ignore_ssl_var.get(): self.log_message('log', "⚠️ Ignorando verificação de certificado SSL."); cmd_base.append("--no-check-certificate")
        cmd = cmd_base + urls
        try:
            self.log_message('log', f"Executando: {' '.join(cmd)}")
            process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0)
            for line_bytes in iter(process.stdout.readline, b''):
                line = line_bytes.decode('utf-8', errors='replace')
                if downloader_name == "yt-dlp":
                    progress_match = self.progress_regex.match(line)
                    if progress_match: self.log_message('progress', float(progress_match.group(1)))
                    else: self.log_message('log', line.strip())
                else: self.log_message('log', line.strip())
            process.wait(); stderr_output = process.stderr.read().decode('utf-8', errors='replace')
            if process.returncode == 0:
                self.log_message('log', "\n✅ Download(s) concluído(s) com sucesso!"); self.log_message('progress', 100); messagebox.showinfo("Concluído", "Todos os downloads foram finalizados.", parent=self.master)
            else:
                self.log_message('log', f"\n❌ Erro no processo. Log de erro:\n{stderr_output}")
                if "CERTIFICATE_VERIFY_FAILED" in stderr_output: messagebox.showerror("Erro de Certificado SSL", "A conexão falhou por um erro de certificado.", parent=self.master)
                else: messagebox.showerror("Erro no Download", "Ocorreu um erro. Verifique o log para detalhes.", parent=self.master)
        except FileNotFoundError: msg = f"Erro: O executável '{downloader_path}' não foi encontrado."; self.log_message('log', msg); messagebox.showerror("Arquivo não encontrado", msg, parent=self.master)
        except Exception as e: self.log_message('log', f"Erro inesperado: {e}"); messagebox.showerror("Erro Inesperado", str(e), parent=self.master)
        finally: self.set_ui_state(False)

    def start_download(self):
        if not self.initialization_thread.is_alive():
            if not self.url_text.get("1.0", tk.END).strip(): messagebox.showwarning("Aviso", "A caixa de URLs está vazia.", parent=self.master); return
            self.set_ui_state(True); threading.Thread(target=self.download_media, daemon=True).start()
        else:
            messagebox.showinfo("Aguarde", "O programa ainda está inicializando as dependências. Por favor, aguarde a mensagem 'Pronto.' na barra de status.", parent=self.master)
            
    def _on_format_change(self, *args):
        if hasattr(self, 'quality_label'):
            selected_format = self.format_var.get()
            if selected_format == "mp3":
                self.quality_label.config(text="Qualidade do Áudio:")
                self.quality_combo.config(values=list(self.audio_quality_options.keys()))
                self.quality_var.set("Máxima (VBR ~256k)")
            else:
                self.quality_label.config(text="Qualidade do Vídeo:")
                self.quality_combo.config(values=list(self.video_quality_options.keys()))
                self.quality_var.set("Melhor Possível")
        
    def toggle_theme(self):
        current_theme = self.master.style.theme_use()
        if current_theme == "litera": self.master.style.theme_use("superhero"); self.theme_button.config(text="☀️", bootstyle="dark")
        else: self.master.style.theme_use("litera"); self.theme_button.config(text="🌙", bootstyle="light")
        
    def browse_output_dir(self):
        directory = filedialog.askdirectory(initialdir=self.output_dir_var.get())
        if directory: self.output_dir_var.set(directory)
        
    def log_message(self, msg_type, data):
        self.log_queue.put((msg_type, data))
        
    def process_log_queue(self):
        while not self.log_queue.empty():
            try:
                msg_type, data = self.log_queue.get_nowait()
                if msg_type == 'log':
                    self.log_text.config(state='normal')
                    self.log_text.insert(tk.END, data + "\n")
                    self.log_text.see(tk.END)
                    self.log_text.config(state='disabled')
                elif msg_type == 'progress': self.progress_bar['value'] = data
                elif msg_type == 'clear_progress': self.progress_bar['value'] = 0
            except queue.Empty: pass
        self.master.after(100, self.process_log_queue)

if __name__ == "__main__":
    root = ttk.Window(themename="litera")
    app = DownloaderApp(root)
    root.mainloop()