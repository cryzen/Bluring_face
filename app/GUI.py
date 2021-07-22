from app.bluring_image import BlurImage
from app.bluring_video import BlurVideo
from app.bluring_videostream import BlurVideoStream

import os
import time

import tkinter as tk, threading
from tkinter import ttk
from tkinter import filedialog as fd
from tkinter import messagebox

import imageio
from PIL import Image, ImageTk
from imutils.video import VideoStream
import imutils
import cv2

class App(ttk.Frame):
    def __init__(self, root):
        self.root = root
        
        super().__init__(self.root)

        self.face_detector = "face_detector"

        self.y = 0

        self.switch = True
        
        self.output = ""

        self.count_of_picture = 0

        self.configure_gui()

        self.interface()

    def configure_gui(self):

        self.root.title("Анонимизация лиц")

        width = self.root.winfo_screenwidth()
        height = self.root.winfo_screenheight()

        width = (width // 2) - 300
        height = (width // 2) - 250

        self.root.geometry("600x735+{}+{}".format(width, height))
        self.root.resizable(False, False)

    def interface(self):

        # Main window widgets
        self.textlabel = ttk.Label(text="Выберете режим: ")

        self.combo_var = tk.StringVar()
        self.comboExample = ttk.Combobox(textvariable=self.combo_var,
                                         values=[
                                                  "Блюр лица",
                                                  "Блюр видео",
                                                  "Блюр видеопотока"
                                                                    ])
        self.comboExample.bind("<<ComboboxSelected>>", self.get_choice_method)

        # Widgets for selecting files and directories
        self.label_open = ttk.Label(text="Открыть файл/ы: ")
        self.label_save = ttk.Label(text="Сохранить в: ")

        self.entry_open = ttk.Entry(state="disabled", width=39)
        self.entry_directory = ttk.Entry(state="disabled", width=39)

        self.btn_open = ttk.Button(text="...", command=self.open_filedialog)
        self.btn_save = ttk.Button(text="...", 
                                   state="disabled",
                                   command=self.choice_directory)

        # Widgets for choosing the blur method and the number of pixels
        self.choice_method = ttk.Label(text="Выберите метод блюра:")

        self.r_var = tk.IntVar()

        self.radio_simple = ttk.Radiobutton(text="simple",
                                            variable=self.r_var,
                                            value=0,
                                            command=lambda: self.scale.place_forget())
        self.radio_pixelated = ttk.Radiobutton(text="pixelated",
                                               variable=self.r_var,
                                               value=1,
                                               command=lambda: self.scale.place(x=10, y=self.y))
        
        self.scale = ttk.Scale(orient=tk.HORIZONTAL,
                               length=150,
                               from_=5,
                               to=20)
        self.scale.bind("<B1-Motion>", self.get_value)
        self.value = 5

        # Button widget
        self.processing_bnt = ttk.Button(text="Обработать и показать",
                                         state="disabled",
                                         command=self.processing)

        # Widget for displaying processed images
        self.canvas = tk.Canvas(bg="white", 
                                 width=500, 
                                 height=500)

        # Button widget for changing images
        self.btn_change = ttk.Button(text="Следующая фотография",
                                     state="disabled", 
                                     command=self.change_image)

        # Video display widget
        self.videoplayer = ttk.Label()

        # Video stream
        self.start_btn = ttk.Button(text="Начать", command=self.start_videostream)

        self.stop_btn = ttk.Button(text="Остановить", command=self.stop_videostream)

        self.draw_main_widgets()

    def draw_main_widgets(self):
        text = '''Как использовать программу:
        1. Выбрать режим из выпадающего списка.
        2. Выбрать файл/ы.
        3. Выбрать папку куда Вы хотите сохранить, обработанный/е файл/ы или видео.
        4. Нажать на кнопку "Обработать и показать"
        '''
        messagebox.showinfo(title="Справка",
                            message=text)
        
        self.textlabel.place(x=10, y=10)

        self.comboExample.place(x=115, y=10)
    
    def draw_common_widgets(self):
        
        self.label_open.place(x=10, y=40)
        self.label_save.place(x=10, y=70)

        self.entry_open.place(x=115, y=40)
        self.entry_directory.place(x=115, y=70)

        self.btn_open.place(x=365, y=37)
        self.btn_save.place(x=365, y=67)

        self.choice_method.place(x=10, y=100)

        self.y = 160

        self.radio_simple.place(x=10, y=130)
        self.radio_pixelated.place(x=70, y=130)
        
        self.processing_bnt.place(x=455, y=113)

    def draw_videostream_widget(self):
        
        self.choice_method.place(x=10, y=40)

        self.y = 100

        self.radio_simple.place(x=10, y=70)
        self.radio_pixelated.place(x=70, y=70)

        self.videoplayer.place(x=50, y=185)

        self.start_btn.place(x=455, y=43)

        self.stop_btn.place(x=455, y=83)

    def cleaning_image_widgets(self):
        
        self.scale.place_forget()
        
        self.canvas.place_forget()

        self.btn_change.place_forget()
        self.btn_change.config(state="disabled")

        self.canvas.delete("all")

        self.entry_open.config(state="normal")
        self.entry_open.delete(0, "end")
        self.entry_open.config(state="disabled")

        self.entry_directory.config(state="normal")
        self.entry_directory.delete(0, "end")
        self.entry_directory.config(state="disabled")

    def cleaning_video_widgets(self):

        self.videoplayer.place_forget()

        self.scale.place_forget()

        self.entry_open.config(state="normal")
        self.entry_open.delete(0, "end")
        self.entry_open.config(state="disabled")

        self.entry_directory.config(state="normal")
        self.entry_directory.delete(0, "end")
        self.entry_directory.config(state="disabled")

    def cleaning_videostream_widgets(self):

        self.start_btn.place_forget()

        self.stop_btn.place_forget()

    def cleaning_common_widgets(self):

        self.label_open.place_forget()
        self.label_save.place_forget()

        self.entry_open.place_forget()
        self.entry_directory.place_forget()

        self.btn_open.place_forget()
        self.btn_save.place_forget()

        self.choice_method.place_forget()

        self.y = 100

        self.radio_simple.place_forget()
        self.radio_pixelated.place_forget()
        self.scale.place_forget()
        
        self.processing_bnt.place_forget()
    
    def get_value(self, event):

        self.value = int(self.scale.get())

    def get_choice_method(self, event):

        if self.combo_var.get() == "Блюр лица":
            
            self.cleaning_videostream_widgets()
            
            self.cleaning_video_widgets()

            self.draw_common_widgets()

            self.r_var.set(0)
            
            self.canvas.place(x=50, y=185)

            self.btn_change.place(x=445, y=700)

            self.btn_save.config(state="disabled")
            self.processing_bnt.config(state="disabled")

        elif self.combo_var.get() == "Блюр видео":
            
            self.cleaning_videostream_widgets()

            self.cleaning_image_widgets()
            
            self.draw_common_widgets()

            self.r_var.set(0)

            self.videoplayer.place(x=50, y=185)

            self.btn_save.config(state="disabled")
            self.processing_bnt.config(state="disabled")

        else:
            
            self.cleaning_image_widgets()

            self.cleaning_video_widgets()

            self.cleaning_common_widgets()

            self.r_var.set(0)

            self.draw_videostream_widget()
            
    def open_filedialog(self):
        
        if self.combo_var.get() == "Блюр лица":
            try:

                self.images = fd.askopenfilenames(title="Выберите файл или файлы",
                                                  filetypes=[('Image Files', ['.jpeg', '.jpg',
                                                                              '.png', '.gif', '.bmp'])])
                self.entry_open.config(state="normal")
                self.entry_open.insert(0, self.images[0])
                self.entry_open.config(state="disabled")

                self.draw_image()
            except IndexError:
               
                self.entry_open.config(state="disabled")

        elif self.combo_var.get() == "Блюр видео":
            try:
                self.videofile = fd.askopenfilename(title="Выберите файл", filetypes=(("MP4 files", "*.mp4"),
                                                                ("WMV files", "*.wmv"), ("AVI files", "*.avi")))
                self.entry_open.config(state="normal")
                self.entry_open.insert(0, self.videofile)
                self.entry_open.config(state="disabled")
                
                self.video_name = os.path.basename(self.videofile)
            except Exception:

                self.entry_open.config(state="disabled")
            
        if self.entry_open.get():
            self.btn_save.config(state="normal")

    def choice_directory(self):

        self.directory = fd.askdirectory(title="Выберите папку для сохранения.")

        try:

            self.entry_directory.config(state="normal")
            self.entry_directory.insert(0, self.directory)
            self.entry_directory.config(state="disabled")

            self.output = os.path.join(self.directory, self.video_name)
        except Exception:

            pass

        if self.entry_open.get() and self.entry_directory.get():
            self.processing_bnt.config(state="normal")
    
    def get_choice(self):

        self.method = ""

        if self.r_var.get() == 0:
            self.method = "simple"
        else:
            self.method = "pixelated"

    def change_image(self):
        
        if self.switch:
            self.draw_image()
        else:
            self.draw_output_image()

    def check_canvas(self):
        
        if self.canvas.find_all() and len(self.images) == 1:
            self.btn_change.config(state="disabled")
        else:
            self.btn_change.config(state="normal")

    def draw_image(self):

        try:
            if self.count_of_picture == 0:
                image = Image.open(self.images[self.count_of_picture])
            else:
                image = Image.open(self.images[self.count_of_picture])

            resized_image = image.resize((500, 500))
            self.photo = ImageTk.PhotoImage(resized_image)
            self.image_or = self.canvas.create_image(0, 0,
                                                     image=self.photo,
                                                     anchor="nw")
            self.count_of_picture += 1
            self.check_canvas()
        except IndexError:
            self.count_of_picture = 0
    
    def draw_output_image(self):

        try:
            if self.count_of_picture == 0:
                path_to_image = os.path.join(self.directory, 
                                             os.listdir(self.directory)[self.count_of_picture])
            else:
                path_to_image = os.path.join(self.directory, 
                                             os.listdir(self.directory)[self.count_of_picture])

            image = Image.open(path_to_image)
            resized_image = image.resize((500, 500))
            self.output_photo = ImageTk.PhotoImage(resized_image)
            self.prcd_image = self.canvas.create_image(0, 0,
                                                       image=self.output_photo,
                                                       anchor="nw")
            self.count_of_picture += 1
        except IndexError:
            self.count_of_picture = 0

    def processing(self):
        
        self.get_choice()

        if self.combo_var.get() == "Блюр лица":
            
            self.switch = False

            for image in self.images:
                if self.r_var.get() == 1:
                    BlurImage(image, self.face_detector, self.directory, 
                              self.method, self.value)
                else:
                    BlurImage(image, self.face_detector, self.directory, 
                              self.method)
            
            self.count_of_picture = 0
            self.draw_output_image()
        elif self.combo_var.get() == "Блюр видео":

            if self.r_var.get() == 1:
                BlurVideo(self.videofile, self.face_detector, self.output,
                          self.method, self.value)
            else:
                BlurVideo(self.videofile, self.face_detector, self.output,
                          self.method)
            
            self.video = imageio.get_reader(self.output)

            thread = threading.Thread(target=self.play_video, args=(self.videoplayer,))
            thread.daemon = 1
            thread.start()

    def play_video(self, label):
            
        for image in self.video.iter_data():

            frame = Image.fromarray(image)
            resized_frame = frame.resize((500, 500))

            result_frame = ImageTk.PhotoImage(resized_frame)

            self.videoplayer.config(image=result_frame)
            self.videoplayer.image = result_frame
            
        self.videoplayer.config(image="")

    def start_videostream(self):

        self.vs = VideoStream(src=0).start()
        time.sleep(2)

        self.show_frame()

    def show_frame(self):

        self.frame = self.vs.read()
        self.frame = imutils.resize(self.frame, width=400)

        self.get_choice()

        if self.r_var.get() == 1:
            BlurVideoStream(self.frame, self.face_detector, self.method, 
                            self.value)
        else:
            BlurVideoStream(self.frame, self.face_detector, self.method)

        cv2color = cv2.cvtColor(self.frame, cv2.COLOR_BGR2RGB)

        img = Image.fromarray(cv2color)
        imgtk = ImageTk.PhotoImage(image=img)

        self.videoplayer.config(image=imgtk)
        self.videoplayer.image = imgtk
        self.videoplayer.after(10, self.show_frame)

    def stop_videostream(self):
        
        self.vs.stop()

        self.videoplayer.config(image="")


