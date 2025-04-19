from kivy.config import Config
Config.set('graphics', 'width', '900')
Config.set('graphics', 'height', '600')
Config.set('graphics', 'resizable', False)
from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.label import Label
from kivy.core.window import Window
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
import pyautogui
import threading
import subprocess
import time
import keyboard
import os


#add things in myWidget
class MyWidget(Widget):
    def __init__(self, **kwargs):
        super(MyWidget, self).__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10, size_hint=(None, None), size=(900, 600), pos_hint={'center_x': 0.5, 'center_y': 0.5})
        self.add_widget(layout)

        self.label = Label(text="Ez Desktop", font_size=42, halign="center", valign="middle", text_size=(400, 400))
        layout.add_widget(self.label)
        self.label.bind(size=self.label.setter('text_size'))

        self.label = Label(text="", font_size=32, halign="center", valign="middle", text_size=(400, 400))
        layout.add_widget(self.label)

        self.button = Button(text="Take Screenshot", size_hint=(None, None), size=(200, 50))
        self.button.bind(on_press=self.start_screenshot_thread)
        layout.add_widget(self.button)

        self.button = Button(text="Shutdown", size_hint=(None, None), size=(200, 50))
        self.button.bind(on_press=self.shutdown)
        layout.add_widget(self.button)

        self.button = Button(text="Restart", size_hint=(None, None), size=(200, 50))
        self.button.bind(on_press=self.restart)
        layout.add_widget(self.button)

        self.button = Button(text="Show Alert", size_hint=(None, None), size=(200, 50))
        self.button.bind(on_press = self.show_alert)
        layout.add_widget(self.button)

        self.button = Button(text="Lock Screen", size_hint=(None, None), size=(200, 50))
        self.button.bind(on_press=self.lock_screen)
        layout.add_widget(self.button)

        self.button = Button(text="Shutdown Others", size_hint=(None, None), size=(200, 50))
        self.button.bind(on_press=self.shutdown_others)
        layout.add_widget(self.button)

        self.button = Button(text="Sleep", size_hint=(None, None), size=(200, 50))
        self.button.bind(on_press=self.computer_sleep)
        layout.add_widget(self.button)

        self.button = Button(text="show mouse coords(press q to stop)",font_size = 10, size_hint=(None, None), size=(200, 50))
        self.button.bind(on_press=self.show_mouse_coords)
        layout.add_widget(self.button)

    #updating labels here
    def update_label(self, text):
        self.label.text = text

#shutdown WORKs wow it shut down my pc
#functions
    def shutdown(self,instance):
        os.system("shutdown /s /t 1")
        self.update_label("Shutting down...")
        pyautogui.sleep(3)
        self.update_label("")
        

    #uses threading so that the app does not freeze
    def start_screenshot_thread(self, instance):
        file_path = pyautogui.prompt("Enter Where you want to save the screenshot:")
        if file_path is None:
            return

        file_name = pyautogui.prompt("Enter your file name:")
        if file_name is None:
            return

        threading.Thread(target=self.take_screenshot, args=(file_path, file_name), daemon=True).start()

    def take_screenshot(self, file_path, file_name):
        try:
            full_path = os.path.join(file_path, file_name + ".png")
            screenshot = pyautogui.screenshot()
            screenshot.save(full_path)
            self.update_label("Screenshot taken!")
            time.sleep(3)
            self.update_label("")
        except Exception as e:
            print("Error taking screenshot:", e)


    def restart(self,instance):
        os.system("shutdown /r /t 1")

    def computer_sleep(self, instance):
        os.system("rundll32.exe powrprof.dll,SetSuspendState 0,1,0")
        
    
    def file_chooser(self):
        file_path = pyautogui.prompt("Enter Where you want to save the screenshot:(be sure to include the full path(or will be saved to desktop))")
        file_path_name = pyautogui.prompt(text='Enter your file name:', title='Save Screenshot As', default='screenshot')
        if file_path is None:
            return os.path.join(os.path.expanduser("~"), "Desktop")
        
        elif file_path.strip() == "":
            pyautogui.alert("Cancelled")
            return None

            

        if file_path is not None:
            desktop_path = os.path.join(file_path, file_path_name+".png")
            screenshot = pyautogui.screenshot()
            screenshot.save(desktop_path)
            self.update_label("Screenshot taken!")
            pyautogui.sleep(3)
            self.update_label("")
            
    def show_mouse_coords(self, instance):
        threading.Thread(target=self._track_mouse, daemon=True).start()
    

    def _track_mouse(self):
        while True:
            mouse_x, mouse_y = pyautogui.position()
            print("X:", mouse_x, "Y:", mouse_y)
            self.update_coords(mouse_x, mouse_y)
            if keyboard.is_pressed("q"):
                break
            time.sleep(0.1)

    def update_coords(self,mouse_x,mouse_y):
        self.label.text = "X: " + str(mouse_x) + " Y: " + str(mouse_y)
        



    def show_alert(self,text):
        text = pyautogui.prompt("Enter the text for the alert:")
        if text is None:
            return
        os.system("msg * " + text)
        self.update_label("Showing alert..."+ text)
        pyautogui.sleep(3)
        self.update_label("")

    def lock_screen(self, instance):
        os.system("rundll32.exe user32.dll,LockWorkStation")
        self.update_label("Locking screen...")
        pyautogui.sleep(3)
        self.update_label("")


    def save_computer_names(self):
        COMPUTER_NAMES = "COMPUTER_NAMES.txt"
        with open(COMPUTER_NAMES, "w") as file:
            while True:
                computer_name = pyautogui.prompt("Enter the computer name or IP address of the target computer (leave blank to finish):")
                if computer_name is None or computer_name.strip() == "":
                    pyautogui.alert("Finished entering computer names.")
                    break
                file.write(computer_name + "\n")





    def shutdown_others(self, instance):
        computer_name = self.save_computer_names()
        if not computer_name:
            pyautogui.alert("No valid computer name provided. Operation canceled.")
            return

        process = subprocess.Popen(["shutdown", "/s", "/t", "10", "/m", f"\\\\{computer_name}"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        stdout, stderr = process.communicate()
        if process.returncode == 0:
            return pyautogui.alert("Shutdown command sent to " + computer_name)
        else:
            return pyautogui.alert("The entered computer name " + str(computer_name) + " is not valid or remote shutdown is not supported on the target computer. Check the name and then try again or contact your system administrator. Error: " + stderr)




#show here(displaying stuff)
class MyApp(App):
    def build(self):
        Window.set_title("Ez Desktop")
        return MyWidget()





if __name__ == "__main__":
    MyApp().run()
    pyautogui.alert("Are you sure you want to exit?")   

