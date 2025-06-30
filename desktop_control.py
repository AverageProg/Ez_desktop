from kivy.config import Config
Config.set('graphics', 'width', '900')
Config.set('graphics', 'height', '700')
Config.set('graphics', 'resizable', False)
from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.label import Label
from kivy.core.window import Window
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
import geoip2.database
import pyautogui
import cv2
import numpy as np
import requests
import webbrowser
import threading
import subprocess
import time
import keyboard
import socket
import os
import shutil
import tempfile
import pyaudio
import wave
from tkinter import Tk
from tkinter import filedialog
#add things in myWidget


class MyWidget(Widget):
    def __init__(self, **kwargs):
        super(MyWidget, self).__init__(**kwargs)

        main_layout = BoxLayout(orientation='vertical', padding=10, spacing=10, size_hint=(None, None), size=(900, 600), pos_hint={'center_x': 0.5, 'center_y': 0.5})
        self.add_widget(main_layout)

        # Title at the top
        title = Label(text="Ez Desktop", font_size=42, size_hint=(1, None), height=80, halign="center", valign="middle")
        title.bind(size=title.setter('text_size'))
        main_layout.add_widget(title)

        # Label for displaying messages
        self.label = Label(text="", font_size=32, size_hint=(1, None), height=80, halign="center", valign="middle", text_size=(400, 400))
        self.label.bind(size=self.label.setter('text_size'))
        main_layout.add_widget(self.label)

        # Dynamic grid for buttons
        button_height = 60
        total_buttons = 11
        available_height = 700-400  # Adjust for title
        max_rows = available_height // button_height
        columns = (total_buttons + max_rows - 1) // max_rows

        grid = GridLayout(cols=columns, spacing=10, size_hint=(1, 1))
        main_layout.add_widget(grid)

        buttons = [
            ("Take Screenshot", self.start_screenshot_thread),
            ("Shutdown", self.shutdown),
            ("Restart", self.restart),
            ("Show Alert", self.show_alert),
            ("Lock Screen", self.lock_screen),
            ("Shutdown Others", self.shutdown_others),
            ("Sleep", self.computer_sleep),
            ("show mouse coords(press q to stop)", self.show_mouse_coords),
            ("Show IP Address", self.show_ip),
            ("Show on Map", self.show_on_map),
            ("Record Screen", self.record_screen_thread),
            ("Clear Temp Files", self.clear_temp_files),
            ("Toggle Webcam", self.toggle_webcam),
            ("Take Picture", self.take_picture),
        ]

        for text, func in buttons:
            btn = Button(text=text, size_hint=(None, None), size=(200, 50),font_size=12)
            btn.bind(on_press=func)
            grid.add_widget(btn)


        

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
        

    #uses threading so that the app does not freeze NEEDS FIXING TOO LAZY RN
    
    def start_screenshot_thread(self, instance):
        root = Tk()
        root.withdraw()

        self.output_file_name = filedialog.asksaveasfilename(
            defaultextension=".jpg",
            filetypes=[("JPEG files", "*.jpg"), ("All files", "*.*")],
            title="Save Picture As"
        )

        if self.output_file_name:
            threading.Thread(target=self.take_screenshot, daemon=True).start()
        else:
            self.update_label("Screenshot canceled.")

    def take_screenshot(self):
        try:
            full_path = self.output_file_name
            screenshot = pyautogui.screenshot()
            screenshot.save(full_path)
            self.update_label("Screenshot taken!")
            time.sleep(3)
            self.update_label("")
        except Exception as e:
            print("Error taking screenshot:", e)
            self.update_label("Error taking screenshot.")



    def restart(self,instance):
        os.system("shutdown /r /t 1")

    def computer_sleep(self, instance):
        os.system("rundll32.exe powrprof.dll,SetSuspendState 0,1,0")
        
    
            
    def show_mouse_coords(self, instance):
        threading.Thread(target=self._track_mouse, daemon=True).start()
    

    def _track_mouse(self):
        while True:
            mouse_x, mouse_y = pyautogui.position()
            print("X:", mouse_x, "Y:", mouse_y)
            self.update_coords(mouse_x, mouse_y)
            if keyboard.is_pressed("q"):
                self.update_label("")
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


    def show_ip(self,ip_address):
        self.ip_address = socket.gethostbyname(socket.gethostname())
        self.update_label("Your IP Address is: " + self.ip_address)
    

    def show_on_map(self,ip_address_show):
        ip_address_show = self.get_public_ip()
        reader = geoip2.database.Reader('GeoLite2-City.mmdb')
        response = reader.city(ip_address_show)
        lat = response.location.latitude
        lon = response.location.longitude
        webbrowser.open(f"https://www.google.com/maps/@{lat},{lon},15z")

    def get_public_ip(self):
        response = requests.get("https://api.ipify.org?format=json")
        return response.json()['ip']

    def record_screen(self, instance):
        try:
            self.output_file_name = pyautogui.prompt("enter name for recording") + ".mp4"
            
        except ValueError:
            return pyautogui.alert("Enter a valid name")

        
    
    def record_screen_thread(self, output_file_name, resolution,screen_width, screen_height):
        screen_width, screen_height = pyautogui.size()
        resolution = (screen_width, screen_height)
        fps = 30.0
        fourcc = cv2.VideoWriter_fourcc(*"mp4v")
        out = cv2.VideoWriter(output_file_name, fourcc, fps, resolution)

        recording = True
        if recording:
            pyautogui.alert("Recording started. Press 'q' to stop.")

        while recording:
            screen = pyautogui.screenshot()
            frame = np.array(screen)
            frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
            out.write(frame)

            if keyboard.is_pressed("q"):
                recording = False

        out.release()
        cv2.destroyAllWindows()




        threading.Thread(target=self.record_screen, daemon=True).start()

    def clear_temp_files(self,instance):
        temp_dir = tempfile.gettempdir()
        if not os.path.exists(temp_dir):
            os.makedirs(temp_dir)

        for filename in os.listdir(temp_dir):
            file_path = os.path.join(temp_dir, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception as e:
                print(f'Failed to delete {file_path}. Reason: {e}')

        self.update_label("Temporary files cleared.")
    
    def merge_audio_video(self,video_file="output.avi", audio_file="output_audio.wav", output_file="final_output.mp4"):
        subprocess.run([
            "ffmpeg",
            "-i", video_file,
            "-i", audio_file,
            "-c:v", "copy",
            "-c:a", "aac",
            "-strict", "experimental",
            output_file
        ], check=True)
        print(f"✅ Merged to {output_file}")


    def toggle_webcam(self, instance):
        cap = cv2.VideoCapture(0) 
        out = cv2.VideoWriter('output.avi', cv2.VideoWriter_fourcc(*'XVID'), 20.0, (640, 480))


        audio = pyaudio.PyAudio()
        audio_stream = audio.open(format=pyaudio.paInt16,
                                channels=1,
                                rate=44100,
                                input=True,
                                frames_per_buffer=1024)
        audio_frames = []

        self.update_label("Recording started. Press 'q' in video window to stop.")            

        def record_audio():
            while getattr(threading.current_thread(), "running", True):
                data = audio_stream.read(1024)
                audio_frames.append(data)
        audio_thread = threading.Thread(target=record_audio)
        audio_thread.running = True
        audio_thread.start()

        while True:
            ret, frame = cap.read()
            if ret:
                out.write(frame)
                cv2.imshow('Webcam', frame)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
            else:
                break
        
        cap.release()
        out.release()
        cv2.destroyAllWindows()

        # Stop audio thread
        audio_thread.running = False
        audio_thread.join()

        audio_stream.stop_stream()
        audio_stream.close()
        audio.terminate()

        # === Save audio to WAV file ===
        wf = wave.open("output_audio.wav", 'wb')
        wf.setnchannels(1)
        wf.setsampwidth(audio.get_sample_size(pyaudio.paInt16))
        wf.setframerate(44100)
        wf.writeframes(b''.join(audio_frames))
        wf.close()

        self.update_label("Webcam and audio recording stopped.")

        if keyboard.is_pressed("q"):
            self.update_label("Webcam recording stopped.")
            return
        cv2.destroyAllWindows()   
        self.save_video()
        if os.path.exists("output.avi"):
            os.remove("output.avi")

        if os.path.exists("output_audio.wav"):
            os.remove("output_audio.wav")
    

    def save_video(self):
        root = Tk()
        root.withdraw()

        output_file = filedialog.asksaveasfilename(
            defaultextension=".mp4",
            filetypes=[("MP4 files", "*.mp4"), ("All files", "*.*")],
            title="Save Merged Video As"
        )

        if output_file:
            self.merge_audio_video("output.avi", "output_audio.wav", output_file)
    
    def save_picture(self):
        root = Tk()
        root.withdraw()

        self.output_file_name = filedialog.asksaveasfilename(
            defaultextension=".jpg",
            filetypes=[("JPEG files", "*.jpg"), ("All files", "*.*")],
            title="Save Picture As"
        )

        if self.output_file_name:
            return self.output_file_name
        else:
            return None

    def take_picture(self, instance):
        cap = cv2.VideoCapture(0)
        ret = cap.isOpened()
        desired_width, desired_height = 1920, 1080
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, desired_width)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, desired_height)

        #apparently camera needs to "warm up" so we read a few frames before taking the picture
        for _ in range(5):
            cap.read()
        ret, frame = cap.read()

        actual_width = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
        actual_height = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
        print(f"Camera resolution set to: {actual_width}x{actual_height}")



        if not ret:
            return pyautogui.alert("Webcam not found or not accessible. Please check your webcam connection.")
                

        else:
            ret, frame = cap.read()
            if ret:
                cv2.imwrite(self.save_picture(), frame)
                self.update_label("Picture taken and saved to " + self.output_file_name)
            else:
                self.update_label("Failed to take picture.")
            cap.release()
            cv2.destroyAllWindows()
            
        


#show here(displaying stuff)
class MyApp(App):
    def build(self):
        Window.set_title("Ez Desktop")
        return MyWidget()

if __name__ == "__main__":
    MyApp().run()
    pyautogui.alert("Are you sure you want to exit?")   

    pyautogui.alert("Thanks for using Ez Desktop! If you have any feedback or suggestions, please let me know.")

