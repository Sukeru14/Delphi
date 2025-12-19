import keyboard
import mouse
import threading
import time

class InputManager:
    def __init__(self):
        self._listening = False
        self._listener_thread = None

    def listen_for_hotkey(self, result_callback):
        if self._listening:
            return
        self._listening = True

        def run():
            time.sleep(0.4)
            found_event = None

            def key_hook(e):
                nonlocal found_event
                if e.event_type == 'down':
                    modifiers = [
                        'ctrl', 'left ctrl', 'right ctrl',
                        'shift', 'left shift', 'right shift',
                        'alt', 'left alt', 'right alt', 'alt gr',
                        'windows', 'left windows', 'right windows', 'menu'
                    ]
                    if e.name in modifiers:
                        return
                    combo_parts = []
                    if keyboard.is_pressed('ctrl'):
                        combo_parts.append('ctrl')
                    if keyboard.is_pressed('alt'):
                        combo_parts.append('alt')
                    if keyboard.is_pressed('shift'):
                        combo_parts.append('shift')
                    if keyboard.is_pressed('windows'):
                        combo_parts.append('windows')
                    combo_parts.append(e.name)
                    found_event = '+'.join(combo_parts)

            def mouse_hook(e):
                nonlocal found_event
                if isinstance(e, mouse.ButtonEvent) and e.event_type == 'up':
                    if e.button == 'x': found_event = 'x'
                    elif e.button == 'x2': found_event = 'x2'
                    elif e.button == 'left': found_event = 'left'
                    elif e.button == 'right': found_event = 'right'
                    elif e.button == 'middle': found_event = 'middle'

            k_hook = keyboard.hook(key_hook)
            m_hook = mouse.hook(mouse_hook)

            while found_event is None and self._listening:
                time.sleep(0.05)

            keyboard.unhook(k_hook)
            mouse.unhook(m_hook)
            self._listening = False
            if found_event:
                try:
                    result_callback(found_event)
                except Exception:
                    pass

        self._listener_thread = threading.Thread(target=run, daemon=True)
        self._listener_thread.start()

    def stop_listening(self):
        self._listening = False

    def setup_global_shortcuts(self, hotkeys, action_map):
        try:
            keyboard.unhook_all()
            mouse.unhook_all()
        except Exception:
            pass

        def register_action(trigger_str, action_func):
            if not trigger_str or not action_func:
                return
            if trigger_str in ['left', 'right', 'middle', 'x', 'x2']:
                try:
                    mouse.on_button(lambda e=None: action_func(), buttons=(trigger_str,), types=('up',))
                except Exception:
                    pass
            else:
                try:
                    keyboard.add_hotkey(trigger_str, action_func)
                except Exception:
                    pass

        register_action(hotkeys.get('play_pause'), action_map.get('play_pause'))
        register_action(hotkeys.get('next'), action_map.get('next'))
        register_action(hotkeys.get('prev'), action_map.get('prev'))