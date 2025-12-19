import customtkinter as ctk
from tkinter import filedialog
import os
from modules import config

class SettingsWindow(ctk.CTkToplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.title("Configurações")
        self.geometry("500x550")
        self.attributes("-topmost", True) 
        
        self.listening_button = None 
        self.listening_key_name = None 

        self.label_title = ctk.CTkLabel(self, text="Configurações", font=("Arial", 20, "bold"))
        self.label_title.pack(pady=20)

        self.frame_path = ctk.CTkFrame(self)
        self.frame_path.pack(fill="x", padx=20, pady=10)
        
        ctk.CTkLabel(self.frame_path, text="Pasta de Downloads:").pack(anchor="w", padx=10, pady=5)
        
        self.entry_path = ctk.CTkEntry(self.frame_path, width=300)
        self.entry_path.insert(0, self.parent.config["download_path"])
        self.entry_path.pack(side="left", padx=10, pady=10)
        
        btn_browse = ctk.CTkButton(self.frame_path, text="Selecionar", width=80, command=self.browse_folder)
        btn_browse.pack(side="right", padx=10)

        self.frame_keys = ctk.CTkFrame(self)
        self.frame_keys.pack(fill="x", padx=20, pady=10)
        
        ctk.CTkLabel(self.frame_keys, text="Clique em 'Definir' e aperte a combinação:", font=("Arial", 14, "bold")).pack(pady=10)

        self.btn_binds = {}
        
        self.create_hotkey_row("Play/Pause:", "play_pause")
        self.create_hotkey_row("Próxima:", "next")
        self.create_hotkey_row("Anterior:", "prev")

        self.btn_save = ctk.CTkButton(self, text="Salvar e Fechar", fg_color="green", command=self.save_settings)
        self.btn_save.pack(pady=20)
        
        self.protocol("WM_DELETE_WINDOW", self.on_close)

    def create_hotkey_row(self, label_text, key_map_name):
        f = ctk.CTkFrame(self.frame_keys, fg_color="transparent")
        f.pack(fill="x", pady=5)
        
        ctk.CTkLabel(f, text=label_text, width=100, anchor="w").pack(side="left", padx=10)
        
        current_hotkey = self.parent.config["hotkeys"].get(key_map_name, "")
        
        btn = ctk.CTkButton(f, text=current_hotkey, fg_color="#333333", border_color="gray", border_width=1)
        btn.configure(command=lambda b=btn, k=key_map_name: self.prepare_listening(b, k))
        btn.pack(side="right", fill="x", expand=True, padx=10)
        
        self.btn_binds[key_map_name] = btn

    def browse_folder(self):
        self.attributes("-topmost", False)
        folder = filedialog.askdirectory(parent=self)
        self.attributes("-topmost", True)
        self.lift()
        
        if folder:
            self.entry_path.delete(0, "end")
            self.entry_path.insert(0, folder)

    def prepare_listening(self, btn_obj, key_name):
        self.listening_button = btn_obj
        self.listening_key_name = key_name
        
        btn_obj.configure(text="Aguardando...", fg_color="#900000")
        
        self.parent.input_manager.listen_for_hotkey(self.on_hotkey_detected)

    def on_hotkey_detected(self, result_str):
        self.after(0, lambda: self._apply_hotkey_ui(result_str))

    def _apply_hotkey_ui(self, result_str):
        if self.listening_button:
            self.listening_button.configure(text=result_str, fg_color="#333333")
            self.parent.config["hotkeys"][self.listening_key_name] = result_str
        
        self.listening_button = None

    def save_settings(self):
        new_path = self.entry_path.get()
        if os.path.isdir(new_path):
            self.parent.config["download_path"] = new_path
        
        config.save_config(self.parent.config)
        
        self.parent.update_shortcuts()
        self.destroy()

    def on_close(self):
        if self.parent.input_manager:
            self.parent.input_manager.stop_listening()
        self.destroy()