import customtkinter as ctk
import threading
import os
from PIL import Image

from modules import config, downloader, metadata, inputs
from modules.player import PlayerController
from ui.settings import SettingsWindow

ctk.set_appearance_mode("dark")

class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Delphi")
        self.geometry("950x900") 
        
        self.config = config.load_config()
        self.playlists = config.load_playlists()
        if not os.path.exists(self.config["download_path"]):
            try: os.makedirs(self.config["download_path"])
            except: pass

        self.input_manager = inputs.InputManager()
        self.player_ctrl = PlayerController(self.config["download_path"])

        self.current_view = "Todas as Músicas"
        self.loading_process = None
        self.hide_timer = None
        
        self.image_cache_small = {} 
        self.image_cache_large = {}
        self.default_image = ctk.CTkImage(Image.new("RGB", (200, 200), "#333333"), size=(200, 200))
        self.default_icon = ctk.CTkImage(Image.new("RGB", (30, 30), "#333333"), size=(30, 30))

        self.tabview = ctk.CTkTabview(self)
        self.tabview.pack(fill="both", expand=True, padx=20, pady=20)
        self.tabview.add("Download")
        self.tabview.add("Biblioteca")
        
        self.btn_settings = ctk.CTkButton(self, text="⚙️", width=40, height=40, command=self.open_settings)
        self.btn_settings.place(relx=0.95, rely=0.02, anchor="ne")

        self.setup_tab_download()
        self.setup_tab_biblioteca()
        
        self.monitor_playback()
        self.update_shortcuts()
        self.after(100, self.update_library_view)

    def update_shortcuts(self):
        action_map = {
            'play_pause': lambda: self.after(0, self.cmd_play_pause),
            'next': lambda: self.after(0, self.cmd_next),
            'prev': lambda: self.after(0, self.cmd_prev)
        }
        self.input_manager.setup_global_shortcuts(self.config['hotkeys'], action_map)

    def cmd_play_pause(self):
        state = self.player_ctrl.toggle_play_pause()
        self.update_play_button(state)

    def cmd_next(self):
        self.player_ctrl.next()
        self.update_ui_metadata()

    def cmd_prev(self):
        self.player_ctrl.prev()
        self.update_ui_metadata()
    
    def cmd_shuffle(self):
        is_active = self.player_ctrl.toggle_shuffle()
        self.btn_shuffle_toggle.configure(fg_color="green" if is_active else "gray")

    def cmd_click_track(self, index):
        self.player_ctrl.play_index(index)
        self.btn_shuffle_toggle.configure(fg_color="gray")
        self.update_play_button("playing")
        self.update_ui_metadata()

    def cmd_stop(self):
        self.player_ctrl.stop()
        self.player_label.configure(text="Parado")
        self.lbl_current_time.configure(text="00:00")
        self.slider_seek.set(0)
        self.update_play_button("paused")
        self.player_frame.pack_forget()
    
    def slider_event(self, value):
        self.player_ctrl.seek(value / 1000)

    def update_play_button(self, state):
        txt = "⏸" if state == "playing" else "▶"
        try: self.btn_play_pause.configure(text=txt)
        except: pass

    def update_ui_metadata(self):
        filename = self.player_ctrl.current_filename
        if filename:
            self.player_label.configure(text=filename)
            self.player_frame.pack(side="bottom", fill="x", padx=10, pady=10)
            
            img = self.get_display_image(filename, "large")
            self.player_cover.configure(image=img)

    def monitor_playback(self):
        if self.player_ctrl.has_ended():
            self.cmd_next()
        
        elif self.player_ctrl.is_playing():
            self.update_play_button("playing")
            
            curr, total = self.player_ctrl.get_time_info()
            if total > 0:
                self.lbl_current_time.configure(text=metadata.format_time(curr))
                self.lbl_total_time.configure(text=metadata.format_time(total))
                
                percent = curr / total
                self.slider_seek.set(percent * 1000) 
        else:
             self.update_play_button("paused")

        self.after(1000, self.monitor_playback)

    def get_display_image(self, filename, size_type="small"):
        size = (30, 30) if size_type == "small" else (200, 200)
        cache = self.image_cache_small if size_type == "small" else self.image_cache_large
        
        if filename in cache: return cache[filename]

        pil_img = metadata.get_file_image(filename, self.config["download_path"], size)
        if pil_img:
            ctk_img = ctk.CTkImage(light_image=pil_img, dark_image=pil_img, size=size)
            cache[filename] = ctk_img
            return ctk_img
        
        return self.default_icon if size_type == "small" else self.default_image

    def setup_tab_biblioteca(self):
        tab = self.tabview.tab("Biblioteca")
        
        self.playlist_ctrl_frame = ctk.CTkFrame(tab)
        self.playlist_ctrl_frame.pack(fill="x", padx=10, pady=5)
        
        self.option_playlists = ctk.CTkOptionMenu(
            self.playlist_ctrl_frame, 
            values=["Todas as Músicas"] + list(self.playlists.keys()),
            command=self.change_playlist_view
        )
        self.option_playlists.pack(side="left", padx=5)

        self.btn_play_ordered = ctk.CTkButton(self.playlist_ctrl_frame, text="▶ Seq", width=70, fg_color="#1f538d", command=self.play_ordered_mode)
        self.btn_play_ordered.pack(side="left", padx=5)
        self.btn_play_random_start = ctk.CTkButton(self.playlist_ctrl_frame, text="🔀 Rand", width=70, fg_color="#d68f15", hover_color="#b57912", command=self.play_random_mode)
        self.btn_play_random_start.pack(side="left", padx=5)

        ctk.CTkButton(self.playlist_ctrl_frame, text="+", width=40, command=self.create_playlist_dialog).pack(side="right", padx=5)
        self.btn_del_playlist = ctk.CTkButton(self.playlist_ctrl_frame, text="X", fg_color="red", width=40, command=self.delete_current_playlist)
        
        self.scroll_frame = ctk.CTkScrollableFrame(tab, label_text="Lista de Reprodução")
        self.scroll_frame.pack(fill="both", expand=True, pady=10)

        self.player_frame = ctk.CTkFrame(tab)
        self.player_cover = ctk.CTkLabel(self.player_frame, text="", image=self.default_image)
        self.player_cover.pack(pady=10)
        self.player_label = ctk.CTkLabel(self.player_frame, text="Nenhuma faixa", font=("Arial", 14, "bold"))
        self.player_label.pack(fill="x", pady=(0, 5))

        self.time_frame = ctk.CTkFrame(self.player_frame, fg_color="transparent")
        self.time_frame.pack(fill="x", padx=20, pady=5)
        self.lbl_current_time = ctk.CTkLabel(self.time_frame, text="00:00", width=50)
        self.lbl_current_time.pack(side="left")
        
        self.slider_seek = ctk.CTkSlider(self.time_frame, from_=0, to=1000, command=self.slider_event)
        self.slider_seek.set(0)
        self.slider_seek.pack(side="left", fill="x", expand=True, padx=10)
        
        self.lbl_total_time = ctk.CTkLabel(self.time_frame, text="00:00", width=50)
        self.lbl_total_time.pack(side="right")

        self.btns_frame = ctk.CTkFrame(self.player_frame, fg_color="transparent")
        self.btns_frame.pack(pady=10)
        
        self.btn_shuffle_toggle = ctk.CTkButton(self.btns_frame, text="🔀", width=40, fg_color="gray", command=self.cmd_shuffle)
        self.btn_shuffle_toggle.pack(side="left", padx=5)
        
        ctk.CTkButton(self.btns_frame, text="⏮", width=40, command=self.cmd_prev).pack(side="left", padx=5)
        ctk.CTkButton(self.btns_frame, text="⏹", width=40, command=self.cmd_stop).pack(side="left", padx=5)
        self.btn_play_pause = ctk.CTkButton(self.btns_frame, text="⏸", width=40, command=self.cmd_play_pause)
        self.btn_play_pause.pack(side="left", padx=5)
        ctk.CTkButton(self.btns_frame, text="⏭", width=40, command=self.cmd_next).pack(side="left", padx=5)

    def setup_tab_download(self):
        tab = self.tabview.tab("Download")
        self.label_titulo = ctk.CTkLabel(tab, text="Baixar Música", font=("Arial", 20, "bold"))
        self.label_titulo.pack(pady=20)
        self.entry_url = ctk.CTkEntry(tab, placeholder_text="Cole o link...", width=450)
        self.entry_url.pack(pady=10)
        self.btn_download = ctk.CTkButton(tab, text="Baixar Música", command=self.download_thread)
        self.btn_download.pack(pady=20)
        self.label_status = ctk.CTkLabel(tab, text="")
        self.progress_bar = ctk.CTkProgressBar(tab, width=400)
        self.label_percentage = ctk.CTkLabel(tab, text="0%")

    def my_hook(self, d):
        if d['status'] == 'downloading':
            try:
                total = d.get('total_bytes') or d.get('total_bytes_estimate')
                downloaded = d.get('downloaded_bytes', 0)
                if total:
                    percent = downloaded / total
                    percent_str = f"{percent * 100:.1f}%"
                    self.after(0, self.update_progress_ui, percent, percent_str, "Baixando...")
            except: pass
        elif d['status'] == 'finished':
            self.after(0, self.update_progress_ui, 1.0, "100%", "Convertendo áudio...")

    def download_thread(self):
        link = self.entry_url.get()
        if not link: return
        
        self.show_progress_widgets()
        self.btn_download.configure(state="disabled")
        
        threading.Thread(target=self._run_downloader, args=(link,)).start()

    def _run_downloader(self, link):
        try:
            downloader.baixar_musica(
                link, 
                self.config["download_path"], 
                self.my_hook
            )
            
            self.after(0, lambda: self.label_status.configure(text="Download Concluído!", text_color="green"))
            self.after(0, lambda: self.label_percentage.configure(text="Sucesso"))
            
            if self.current_view == "Todas as Músicas":
                self.after(100, self.update_library_view)
            
            self.after(0, lambda: self.schedule_hide())
            
        except Exception as e:
            self.after(0, lambda: self.label_status.configure(text=f"Erro: {str(e)[:50]}...", text_color="red"))
            self.after(0, lambda: self.schedule_hide())
        finally:
             self.after(0, lambda: self.btn_download.configure(state="normal"))

    def show_progress_widgets(self):
        if self.hide_timer:
            self.after_cancel(self.hide_timer)
            self.hide_timer = None
        self.label_status.pack(pady=(10, 0))
        self.progress_bar.pack(pady=5)
        self.label_percentage.pack(pady=0)
        self.progress_bar.set(0)
        self.label_percentage.configure(text="0%")
        self.label_status.configure(text="Iniciando...", text_color="white")

    def hide_progress_widgets(self):
        self.label_status.pack_forget()
        self.progress_bar.pack_forget()
        self.label_percentage.pack_forget()
        self.hide_timer = None

    def update_progress_ui(self, val, text_percent, text_status):
        self.progress_bar.set(val)
        self.label_percentage.configure(text=text_percent)
        self.label_status.configure(text=text_status)

    def schedule_hide(self):
        if self.hide_timer:
            self.after_cancel(self.hide_timer)
        self.hide_timer = self.after(5000, self.hide_progress_widgets)

    def open_settings(self):
        if hasattr(self, 'settings_window') and self.settings_window.winfo_exists():
            self.settings_window.lift()
        else:
            self.settings_window = SettingsWindow(self)

    def update_library_view(self):
        if hasattr(self, 'loading_process') and self.loading_process:
            self.after_cancel(self.loading_process)
            self.loading_process = None

        for widget in self.scroll_frame.winfo_children(): 
            widget.destroy()

        pasta_atual = self.config["download_path"]
        arquivos_fisicos = []
        if os.path.exists(pasta_atual):
            try: arquivos_fisicos = [f for f in os.listdir(pasta_atual) if f.lower().endswith(('.mp3', '.mka', '.wav', '.flac'))]
            except: pass

        if self.current_view == "Todas as Músicas":
            self.current_playlist_items = sorted(arquivos_fisicos)
        else:
            itens_salvos = self.playlists.get(self.current_view, [])
            self.current_playlist_items = [f for f in itens_salvos if f in arquivos_fisicos]

        self.player_ctrl.load_playlist(self.current_playlist_items)
        self.player_ctrl.update_path(self.config["download_path"])

        self._load_batch(start_index=0)

    def _load_batch(self, start_index):
        BATCH_SIZE = 12
        if not self.current_playlist_items: return
        end_index = min(start_index + BATCH_SIZE, len(self.current_playlist_items))

        for index in range(start_index, end_index):
            arquivo = self.current_playlist_items[index]
            item_frame = ctk.CTkFrame(self.scroll_frame)
            item_frame.pack(fill="x", pady=2, padx=2)

            thumb = self.get_display_image(arquivo, "small")
            ctk.CTkLabel(item_frame, text="", image=thumb, width=30).pack(side="left", padx=(5, 0))
            ctk.CTkLabel(item_frame, text=arquivo, anchor="w").pack(side="left", fill="x", expand=True, padx=8)
            
            ctk.CTkButton(item_frame, text="▶", width=30, 
                          command=lambda i=index: self.cmd_click_track(i)).pack(side="right", padx=2)

            if self.current_view == "Todas as Músicas":
                ctk.CTkButton(item_frame, text="+", width=30, fg_color="green", 
                              command=lambda f=arquivo: self.add_to_playlist_popup(f)).pack(side="right", padx=2)
            else:
                ctk.CTkButton(item_frame, text="x", width=30, fg_color="red", hover_color="darkred",
                              command=lambda f=arquivo: self.remove_from_playlist(f)).pack(side="right", padx=2)
                if index < len(self.current_playlist_items) - 1:
                    ctk.CTkButton(item_frame, text="⬇", width=30, fg_color="gray", 
                                  command=lambda i=index: self.move_song_down(i)).pack(side="right", padx=2)
                if index > 0:
                    ctk.CTkButton(item_frame, text="⬆", width=30, fg_color="gray", 
                                  command=lambda i=index: self.move_song_up(i)).pack(side="right", padx=2)

        if end_index < len(self.current_playlist_items):
            self.loading_process = self.after(10, lambda: self._load_batch(end_index))
        else:
            self.loading_process = None

    def create_playlist_dialog(self):
        dialog = ctk.CTkInputDialog(text="Nome da playlist:", title="Criar Playlist")
        name = dialog.get_input()
        if name:
            if name in self.playlists: return
            self.playlists[name] = []
            config.save_playlists(self.playlists)
            self.option_playlists.configure(values=["Todas as Músicas"] + list(self.playlists.keys()))
            self.option_playlists.set(name)
            self.change_playlist_view(name)

    def change_playlist_view(self, selection):
        self.current_view = selection
        if selection == "Todas as Músicas":
            self.btn_del_playlist.pack_forget()
        else:
            self.btn_del_playlist.pack(side="right", padx=5)
        self.update_library_view()

    def delete_current_playlist(self):
        if self.current_view == "Todas as Músicas": return
        del self.playlists[self.current_view]
        config.save_playlists(self.playlists)
        self.option_playlists.configure(values=["Todas as Músicas"] + list(self.playlists.keys()))
        self.option_playlists.set("Todas as Músicas")
        self.change_playlist_view("Todas as Músicas")

    def add_to_playlist_popup(self, filename):
        if not self.playlists: return
        top = ctk.CTkToplevel(self)
        top.title("Adicionar à Playlist")
        top.geometry("300x400")
        top.attributes("-topmost", True)
        ctk.CTkLabel(top, text=f"Adicionar:\n{filename}", wraplength=280).pack(pady=10)
        scroll = ctk.CTkScrollableFrame(top)
        scroll.pack(fill="both", expand=True, padx=10, pady=10)
        for pl_name in self.playlists.keys():
            ctk.CTkButton(scroll, text=pl_name, 
                command=lambda p=pl_name, f=filename, w=top: self._confirm_add(p, f, w)).pack(pady=2, fill="x")
            
    def _confirm_add(self, playlist_name, filename, window):
        if filename not in self.playlists[playlist_name]:
            self.playlists[playlist_name].append(filename)
            config.save_playlists(self.playlists)
        window.destroy()

    def remove_from_playlist(self, filename):
        if self.current_view != "Todas as Músicas":
            if filename in self.playlists[self.current_view]:
                self.playlists[self.current_view].remove(filename)
                config.save_playlists(self.playlists)
                self.update_library_view()

    def play_ordered_mode(self):
        self.player_ctrl.is_shuffle = False
        self.player_ctrl.generate_queue()
        self.player_ctrl.queue_pos = 0
        self.player_ctrl._play_current()
        self.update_ui_metadata()
        self.btn_shuffle_toggle.configure(fg_color="gray")

    def play_random_mode(self):
        self.player_ctrl.is_shuffle = True
        self.player_ctrl.generate_queue()
        self.player_ctrl.queue_pos = 0
        self.player_ctrl._play_current()
        self.update_ui_metadata()
        self.btn_shuffle_toggle.configure(fg_color="green")

if __name__ == "__main__":
    app = App()
    app.mainloop()