import sys
import webbrowser
import customtkinter as ctk
from tkinter import filedialog, messagebox, PhotoImage
from PIL import Image
import threading
import os
import subprocess
import platform
from typing import Optional, List, Dict, Any

from services.connection_service import ConnectionService
from services.download_service import DownloadService
from services.conversion_service import ConversionService
from services.history_service import HistoryService
from services.tooltip_service import ToolTipService
from constants.app_constants import AppConstants

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class ConverterApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.constants = AppConstants()
        self.file_path: Optional[str] = None

        self.connection_service = ConnectionService()
        self.download_service = DownloadService()
        self.conversion_service = ConversionService()
        self.history_service = HistoryService()

        self._setup_main_window()
        self._initialize_ui()
        self._start_services()

    def _setup_main_window(self) -> None:
        self.title(self.constants.WINDOW_TITLE)
        self.geometry(self.constants.WINDOW_SIZE)
        self.resizable(False, False)

    def _initialize_ui(self) -> None:
        self._create_sidebar()
        self._create_main_frame()
        self._load_github_icon()

    def _start_services(self) -> None:
        self._start_connection_monitor()
        self.show_download_frame()

    def _create_sidebar(self) -> None:
        self.sidebar_frame = ctk.CTkFrame(self, width=self.constants.SIDEBAR_WIDTH, corner_radius=0)
        self.sidebar_frame.pack(side="left", fill="y")

        ctk.CTkLabel(
            self.sidebar_frame,
            text="Menu",
            font=ctk.CTkFont(size=18, weight="bold")
        ).pack(pady=(20, 10))

        self.connection_label = ctk.CTkLabel(
            self.sidebar_frame,
            text="Status: Verificando...",
            font=ctk.CTkFont(size=12)
        )
        self.connection_label.pack(pady=(10, 0))

        self._create_navigation_buttons()

    def _create_navigation_buttons(self) -> None:
        buttons = [
            {"text": "Download", "command": self.show_download_frame},
            {"text": "Conversão", "command": self.show_convert_frame},
            {"text": "Sair", "command": self.destroy, "fg_color": "red"}
        ]

        for btn_config in buttons:
            btn = ctk.CTkButton(self.sidebar_frame, **btn_config)
            btn.pack(pady=10, fill="x", padx=10)

    def _create_main_frame(self) -> None:
        self.main_frame = ctk.CTkFrame(self, corner_radius=10)
        self.main_frame.pack(side="right", expand=True, fill="both", padx=10, pady=10)

    def _load_github_icon(self) -> None:
        try:
            if getattr(sys, 'frozen', False):
                icon_path = os.path.join(sys._MEIPASS, self.constants.ICON_PATH)
            else:
                icon_path = self.constants.ICON_PATH

            github_icon = ctk.CTkImage(
                dark_image=Image.open(icon_path),
                light_image=Image.open(icon_path),
                size=self.constants.ICON_SIZE
            )

            self.github_link = ctk.CTkLabel(
                self.sidebar_frame,
                text="",
                cursor="hand2",
                image=github_icon
            )
            self.github_link.pack(side="bottom", padx=(0, 110), pady=(0, 10))

            self.github_link.bind("<Button-1>", lambda e: self._open_browser(self.constants.GITHUB_URL))

            ToolTipService(self.github_link, "Visitar GitHub")

        except FileNotFoundError:
            print(f"Ícone não encontrado em: {self.constants.ICON_PATH}")

    def _start_connection_monitor(self) -> None:
        threading.Thread(target=self._monitor_connection, daemon=True).start()

    def _monitor_connection(self) -> None:
        while True:
            is_connected = self.connection_service.is_connected()
            status_text = "🟢 Online" if is_connected else "🔴 Offline"
            status_color = "green" if is_connected else "red"

            self.connection_label.configure(
                text=f"Status: {status_text}",
                text_color=status_color
            )

            threading.Event().wait(5)

    def _open_browser(self, url: str) -> None:
        webbrowser.open(url)

    def show_download_frame(self) -> None:
        self._clear_main_frame()
        frame = ctk.CTkFrame(self.main_frame)
        frame.pack(expand=True, fill="both", padx=20, pady=20)

        ctk.CTkLabel(
            frame,
            text="Baixar vídeo do YouTube",
            font=ctk.CTkFont(size=22, weight="bold")
        ).pack(pady=10)

        ctk.CTkLabel(frame, text="Insira a URL do vídeo:").pack(pady=5)
        self.url_entry = ctk.CTkEntry(frame, width=500, placeholder_text="Cole o link aqui...")
        self.url_entry.pack(pady=5)

        ctk.CTkButton(
            frame,
            text="Baixar",
            command=self._start_download_thread
        ).pack(pady=10)

        self._create_download_status_area(frame)

        self._create_download_history_section(frame)

    def _create_download_status_area(self, parent_frame: ctk.CTkFrame) -> None:
        self.file_label = ctk.CTkLabel(parent_frame, text="Nenhum arquivo baixado")
        self.file_label.pack(pady=5)

        self.progress_bar = ctk.CTkProgressBar(parent_frame, width=self.constants.PROGRESS_BAR_WIDTH)
        self.progress_bar.set(0)
        self.progress_bar.pack(pady=10)
        self.progress_bar.pack_forget()

        self.status_label = ctk.CTkLabel(parent_frame, text="")
        self.status_label.pack(pady=5)

    def _create_download_history_section(self, parent_frame: ctk.CTkFrame) -> None:
        ctk.CTkLabel(
            parent_frame,
            text="Arquivos Recentemente Baixados",
            font=ctk.CTkFont(size=18, weight="bold")
        ).pack(pady=(20, 10))

        self.history_container = ctk.CTkFrame(parent_frame)
        self.history_container.pack(pady=5, fill="both", expand=False)

        self._render_download_history()

    def _render_download_history(self) -> None:
        for widget in self.history_container.winfo_children():
            widget.destroy()

        history = self._get_filtered_history("download")

        if not history:
            ctk.CTkLabel(self.history_container, text="Nenhum download registrado.").pack()
            return

        self._create_history_scrollable_area(history)


    def _get_filtered_history(self, history_type: str) -> List[Dict[str, Any]]:
        return [
                   item for item in self.history_service.get_history()
                   if item["type"] == history_type
               ][-self.constants.HISTORY_DISPLAY_LIMIT:]

    def _create_history_scrollable_area(self, history: List[Dict[str, Any]]) -> None:
        canvas = ctk.CTkCanvas(self.history_container, width=700, height=150)
        canvas.pack(pady=1, fill="both", expand=True)

        h_scroll = ctk.CTkScrollbar(self.history_container, orientation="horizontal", command=canvas.xview)
        h_scroll.pack(fill="x", side="bottom")
        v_scroll = ctk.CTkScrollbar(self.history_container, orientation="vertical", command=canvas.yview)
        v_scroll.pack(fill="y", side="right")

        canvas.configure(xscrollcommand=h_scroll.set, yscrollcommand=v_scroll.set)

        inner_frame = ctk.CTkFrame(canvas)
        canvas.create_window((0, 0), window=inner_frame, anchor="nw")

        for item in reversed(history[-4:]):
            self._create_history_item(inner_frame, item)

        inner_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

    def _create_history_item(self, parent_frame: ctk.CTkFrame, item: Dict[str, Any]) -> None:
        item_frame = ctk.CTkFrame(parent_frame)
        item_frame.pack(fill="x", padx=5, pady=5)

        ctk.CTkLabel(
            item_frame,
            text=f"{item['filename']} - {item['path']}",
            anchor="w"
        ).pack(side="left", padx=5)

        self._create_history_item_buttons(item_frame, item['path'])

    def _create_history_item_buttons(self, parent_frame: ctk.CTkFrame, path: str) -> None:
        ctk.CTkButton(
            parent_frame,
            text="Abrir Arquivo",
            width=80,
            command=lambda p=path: self._open_file(p)
        ).pack(side="right", padx=5)

        ctk.CTkButton(
            parent_frame,
            text="Abrir Pasta",
            width=80,
            command=lambda p=path: self._open_folder(p)
        ).pack(side="right", padx=5)

    def _open_file(self, path: str) -> None:
        try:
            if platform.system() == "Windows":
                os.startfile(path)
            elif platform.system() == "Darwin":
                subprocess.Popen(["open", path])
            else:
                subprocess.Popen(["xdg-open", path])
        except Exception as e:
            messagebox.showerror("Erro", f"Não foi possível abrir o arquivo.\n{str(e)}")

    def _open_folder(self, path: str) -> None:
        try:
            folder = os.path.dirname(path)
            if platform.system() == "Windows":
                os.startfile(folder)
            elif platform.system() == "Darwin":
                subprocess.Popen(["open", folder])
            else:
                subprocess.Popen(["xdg-open", folder])
        except Exception as e:
            messagebox.showerror("Erro", f"Não foi possível abrir a pasta.\n{str(e)}")

    def show_convert_frame(self) -> None:
        self._clear_main_frame()
        frame = ctk.CTkFrame(self.main_frame)
        frame.pack(expand=True, fill="both", padx=20, pady=20)

        ctk.CTkLabel(
            frame,
            text="Conversor de Arquivos de Mídia",
            font=ctk.CTkFont(size=22, weight="bold")
        ).pack(pady=10)

        ctk.CTkButton(
            frame,
            text="Selecionar Arquivo",
            command=self._select_file
        ).pack(pady=10)

        self.file_label = ctk.CTkLabel(frame, text="Nenhum arquivo selecionado")
        self.file_label.pack(pady=5)

        ctk.CTkLabel(frame, text="Selecione o formato de saída:").pack(pady=5)
        self.format_option = ctk.CTkOptionMenu(frame, values=["mp3", "wav", "mp4"])
        self.format_option.pack(pady=5)

        ctk.CTkButton(
            frame,
            text="Converter",
            command=self._start_convert_thread
        ).pack(pady=20)

        self._create_conversion_status_area(frame)

    def _create_conversion_status_area(self, parent_frame: ctk.CTkFrame) -> None:
        self.progress_bar = ctk.CTkProgressBar(
            parent_frame,
            width=self.constants.PROGRESS_BAR_WIDTH
        )
        self.progress_bar.set(0)
        self.progress_bar.pack(pady=10)
        self.progress_bar.pack_forget()

        self.status_label = ctk.CTkLabel(parent_frame, text="")
        self.status_label.pack(pady=5)

    def _clear_main_frame(self) -> None:
        for widget in self.main_frame.winfo_children():
            widget.destroy()

    def _start_download_thread(self) -> None:
        threading.Thread(target=self._download_video, daemon=True).start()

    def _start_convert_thread(self) -> None:
        threading.Thread(target=self._convert_file, daemon=True).start()

    def _download_video(self) -> None:
        url = self.url_entry.get().strip()

        if not url:
            messagebox.showerror("Erro", "Por favor, insira uma URL válida.")
            return

        output_path = filedialog.askdirectory(title="Selecione a pasta para salvar")
        if not output_path:
            self.status_label.configure(text="Download cancelado.")
            return

        self._update_download_status("Baixando vídeo...", show_progress=True)

        try:
            file_path, filename = self.download_service.download(url, output_path)
            self.file_path = file_path
            self._handle_download_success(filename, file_path)
        except Exception as e:
            self._handle_download_error(e)
        finally:
            self._reset_progress_bar()

    def _update_download_status(self, message: str, show_progress: bool = False) -> None:
        self.status_label.configure(text=message)
        if show_progress:
            self.progress_bar.pack()
            self.progress_bar.start()

    def _handle_download_success(self, filename: str, file_path: str) -> None:
        self.file_label.configure(text=f"Baixado: {filename}")
        self.status_label.configure(text="Download concluído com sucesso!")
        messagebox.showinfo("Sucesso", f"'{filename}' baixado com sucesso!")
        self.history_service.add_record("download", filename, file_path)
        self._render_download_history()

    def _handle_download_error(self, error: Exception) -> None:
        self.status_label.configure(text="Erro no download.")
        messagebox.showerror("Erro", str(error))

    def _reset_progress_bar(self) -> None:
        self.progress_bar.stop()
        self.progress_bar.pack_forget()

    def _select_file(self) -> None:
        file = filedialog.askopenfilename(
            title="Selecione um arquivo",
            filetypes=[("Arquivos de mídia", "*.mp4 *.mp3 *.wav *.avi *.mov *.mkv")]
        )
        if file:
            self.file_path = file
            filename = os.path.basename(file)
            self.file_label.configure(text=f"Selecionado: {filename}")

    def _convert_file(self) -> None:
        if not self.file_path:
            messagebox.showerror("Erro", "Selecione ou baixe um arquivo primeiro.")
            return

        output_format = self.format_option.get()
        output_path = filedialog.asksaveasfilename(
            defaultextension=f".{output_format}",
            filetypes=[(f"{output_format.upper()} files", f"*.{output_format}")],
            initialfile="arquivo_convertido"
        )

        if not output_path:
            return

        self._update_conversion_status("Convertendo...")

        try:
            self.conversion_service.convert(self.file_path, output_path, output_format)
            self._handle_conversion_success(output_path)
        except Exception as e:
            self._handle_conversion_error(e)
        finally:
            self._reset_progress_bar()

    def _update_conversion_status(self, message: str) -> None:
        self.status_label.configure(text=message)
        self.progress_bar.pack()
        self.progress_bar.start()

    def _handle_conversion_success(self, output_path: str) -> None:
        self.status_label.configure(text="Conversão concluída!")
        messagebox.showinfo("Sucesso", "Arquivo convertido com sucesso!")
        output_name = os.path.basename(output_path)
        self.history_service.add_record("conversion", output_name, output_path)

    def _handle_conversion_error(self, error: Exception) -> None:
        self.status_label.configure(text="Erro na conversão.")
        messagebox.showerror("Erro", str(error))


if __name__ == "__main__":
    app = ConverterApp()
    app.mainloop()