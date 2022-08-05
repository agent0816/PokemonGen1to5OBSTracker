import os
import subprocess
import yaml
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.checkbox import CheckBox
from kivy.config import Config
from kivy.uix.label import Label
from kivy.uix.screenmanager import Screen
from kivy.uix.screenmanager import ScreenManager
from kivy.uix.screenmanager import FadeTransition

configsave = 'backend/config/'

bh = yaml.safe_load(open(f"{configsave}bh_config.yml"))
obs = yaml.safe_load(open(f"{configsave}obs_config.yml"))
sp = yaml.safe_load(open(f"{configsave}sprites.yml"))
pl = yaml.safe_load(open(f"{configsave}player.yml"))
cc = yaml.safe_load(open(f"{configsave}common_config.yml"))

class Screens(ScreenManager):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.transition = FadeTransition()

class MainMenu(Screen):
    def launchbh(self):
        subprocess.Popen([bh['path'], f'--lua={os.path.abspath("./backend/obsautomation.lua")}', f'--socket_ip={bh["host"]}', f'--socket_port={bh["port"]}'])

    def launchserver(self):
        pass

class SettingsMenu(Screen):   
    def changesettingscreen(self, settings):
        if len(self.children[0].children) > 1:
            self.children[0].remove_widget(self.children[0].children[0])

        widget = self.checkSettingScreen(settings)

        self.children[0].add_widget(widget)

    def checkSettingScreen(self, settings):
        widget = Screen()
        if settings == 'sprite':
            widget = SpriteSettings()
        elif settings == 'games':
            widget = SpritesGames()
        elif settings == 'bizhawk':
            widget = BizhawkSettings()
        elif settings == 'obs':
            widget = OBSSettings()
        elif settings == 'remote':
            widget = RemoteSettings()
        elif settings == 'player':
            widget = PlayerSettings()
        return widget


class SpriteSettings(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.ids.common_path.text = sp['common_path']
        self.ids.animated_check.state = 'down' if sp['animated'] else 'normal'
        for i in range(4):
            if i == ['route', 'lvl', 'team', 'dexnr'].index(sp['order']):
                self.ids.sortierung.children[i].state = 'down'

    def save_changes(self):
        sp['common_path'] = self.ids.common_path.text
        sp['animated'] = self.ids.animated_check.state == 'down'
        for i in range(4):
            if self.ids.sortierung.children[i].state == 'down':
                sp['order'] = ['route', 'lvl', 'team', 'dexnr'][i]

        with open(f"{configsave}sprites.yml", 'w') as file:
            yaml.dump(sp, file)

class SpritesGames(Screen):
    def __init__(self,**kwargs):
        super().__init__(**kwargs)
        self.ids.gen1_red.text = sp['red']
        self.ids.gen1_yellow.text = sp['yellow']
        self.ids.gen2_silver.text = sp['silver']
        self.ids.gen2_gold.text = sp['gold']
        self.ids.gen2_crystal.text = sp['crystal']
        self.ids.gen3_ruby.text = sp['ruby']
        self.ids.gen3_emerald.text = sp['emerald']
        self.ids.gen3_firered.text = sp['firered']
        self.ids.gen4_diamond.text = sp['diamond']
        self.ids.gen4_platinum.text = sp['platinum']
        self.ids.gen4_heartgold.text = sp['heartgold']
        self.ids.gen5_black.text = sp['black']

    def save_changes(self):
        sp['red'] = self.ids.gen1_red.text
        sp['yellow'] = self.ids.gen1_yellow.text
        sp['silver'] = self.ids.gen2_silver.text
        sp['gold'] = self.ids.gen2_gold.text
        sp['crystal'] = self.ids.gen2_crystal.text
        sp['ruby'] = self.ids.gen3_ruby.text
        sp['emerald'] = self.ids.gen3_emerald.text
        sp['firered'] = self.ids.gen3_firered.text
        sp['diamond'] = self.ids.gen4_diamond.text
        sp['platinum'] = self.ids.gen4_platinum.text
        sp['heartgold'] = self.ids.gen4_heartgold.text
        sp['black'] = self.ids.gen5_black.text

        with open(f"{configsave}sprites.yml", 'w') as file:
            yaml.dump(sp, file)

class BizhawkSettings(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.ids.bizhawk_exe.text = bh['path']
        self.ids.bizhawk_host.text = bh['host']
        self.ids.bizhawk_port.text = bh['port']

    def save_changes(self):
        bh['path'] = self.ids.bizhawk_exe.text
        bh['host'] = self.ids.bizhawk_host.text
        bh['port'] = self.ids.bizhawk_port.text
        
        with open(f"{configsave}bh_config.yml", 'w') as file:
            yaml.dump(bh, file)

class OBSSettings(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.ids.obs_password.text = obs['password']
        self.ids.obs_host.text = obs['host']
        self.ids.obs_port.text = obs['port']

    def save_changes(self):
        obs['password'] = self.ids.obs_password.text
        obs['host'] = self.ids.obs_host.text
        obs['port'] = self.ids.obs_port.text
        
        with open(f"{configsave}obs_config.yml", 'w') as file:
            yaml.dump(obs, file)

class RemoteSettings(Screen):
    pass

class PlayerSettings(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.addCheckBoxes()

    def addCheckBoxes(self):
        for i in range(1, pl['player_count'] + 1):
            idBox = f"box_spieler_{i}"
            self.children[0].add_widget(Label(text=f"Spieler {i}", id=f"label_spieler_{i}"))
            self.children[0].add_widget(BoxLayout(orientation="horizontal", id=idBox))
            idRemote = f"remote_player_{i}"
            idOBS = f"obs_player_{i}"
            checkRemote = CheckBox(active=pl[f"remote_{i}"], id=idRemote, pos_hint={"center_y": .5}, size_hint=[None, None], size=["20dp", "20dp"])
            checkRemoteLabel = Label(text="remote", pos_hint={"center_y": .5}, size_hint=[None, None], size=["40dp", "20dp"])
            checkOBS = CheckBox(active=pl[f"obs_{i}"], id = idOBS, pos_hint={"center_y": .5}, size_hint=[None, None], size=["20dp", "20dp"])
            checkOBSLabel = Label(text="OBS", pos_hint={"center_y": .5}, size_hint=[None, None], size=["40dp", "20dp"])
            self.idBox.add_widget(checkRemote)
            self.idBox.add_widget(checkRemoteLabel)
            self.idBox.add_widget(checkOBS)
            self.idBox.add_widget(checkOBSLabel)

class TrackerApp(App):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Config.set('graphics', 'resizable', 0)
        Config.set('graphics', 'width', "600")
        Config.set('graphics', 'height', "400")
        Config.set('input', 'mouse', 'mouse,multitouch_on_demand')
