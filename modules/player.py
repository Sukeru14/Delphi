import vlc
import os
import random

class PlayerController:
    def __init__(self, download_path):
        self.download_path = download_path
        
        self.vlc_instance = vlc.Instance()
        self.player = self.vlc_instance.media_player_new()
        
        self.playlist_items = []
        self.queue = []
        self.queue_pos = -1
        
        self.is_shuffle = False
        self.current_filename = None

    def update_path(self, new_path):
        self.download_path = new_path

    def load_playlist(self, items):
        self.playlist_items = items
        self.generate_queue()

    def generate_queue(self):
        if not self.playlist_items:
            self.queue = []
            return

        indices = list(range(len(self.playlist_items)))
        
        if self.is_shuffle:
            current_real_index = -1
            if self.queue and self.queue_pos >= 0 and self.queue_pos < len(self.queue):
                current_real_index = self.queue[self.queue_pos]

            random.shuffle(indices)
            
            if current_real_index != -1:
                pass 
        else:
            indices.sort()

        self.queue = indices
        if not self.player.is_playing() and self.player.get_state() != vlc.State.Paused:
            self.queue_pos = -1

    def toggle_shuffle(self):
        self.is_shuffle = not self.is_shuffle
        
        if not self.queue or not self.playlist_items:
            self.generate_queue()
            return self.is_shuffle

        current_real_index = -1
        if self.queue_pos >= 0 and self.queue_pos < len(self.queue):
            current_real_index = self.queue[self.queue_pos]

        if self.is_shuffle:
            remaining_indices = list(range(len(self.playlist_items)))
            if current_real_index != -1:
                remaining_indices.remove(current_real_index)
            
            random.shuffle(remaining_indices)
            
            if current_real_index != -1:
                self.queue = [current_real_index] + remaining_indices
                self.queue_pos = 0
            else:
                self.queue = remaining_indices
                self.queue_pos = -1

        else:
            self.queue = list(range(len(self.playlist_items)))
            
            if current_real_index != -1:
                self.queue_pos = current_real_index
            else:
                self.queue_pos = 0

        return self.is_shuffle

    def play_index(self, index):
        self.is_shuffle = False
        self.queue = list(range(len(self.playlist_items)))
        self.queue_pos = index
        self._play_current()

    def _play_current(self):
        if not self.queue or self.queue_pos < 0 or self.queue_pos >= len(self.queue):
            return

        real_index = self.queue[self.queue_pos]
        self.current_filename = self.playlist_items[real_index]
        full_path = os.path.join(self.download_path, self.current_filename)

        if not os.path.exists(full_path):
            print(f"Arquivo não encontrado: {full_path}")
            return

        media = self.vlc_instance.media_new(full_path)
        self.player.set_media(media)
        self.player.play()

    def next(self):
        if not self.queue: return
        self.queue_pos += 1
        if self.queue_pos >= len(self.queue):
            self.queue_pos = 0
        self._play_current()

    def prev(self):
        if not self.queue: return
        self.queue_pos -= 1
        if self.queue_pos < 0:
            self.queue_pos = len(self.queue) - 1
        self._play_current()

    def toggle_play_pause(self):
        if not self.player.get_media():
            if self.queue:
                self.queue_pos = 0
                self._play_current()
            return "playing"

        if self.player.is_playing():
            self.player.pause()
            return "paused"
        else:
            self.player.play()
            return "playing"

    def stop(self):
        self.player.stop()
        self.current_filename = None
        self.queue_pos = -1 

    def seek(self, percentage_0_to_1):
        if self.player.get_media():
            length = self.player.get_length()
            if length > 0:
                target_ms = int(length * percentage_0_to_1)
                self.player.set_time(target_ms)

    def set_volume(self, value):
        self.player.audio_set_volume(int(value))

    def is_playing(self):
        return self.player.is_playing()

    def has_ended(self):
        return self.player.get_state() == vlc.State.Ended

    def get_time_info(self):
        if not self.player.get_media():
            return 0, 0
        return self.player.get_time(), self.player.get_length()