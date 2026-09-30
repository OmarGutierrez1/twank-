# -*- coding:utf-8 -*-

'''

made by omar gutierrez cisneros
omar.gutierrez.cisneros@outlook.com
proyecto: twank
planta tratadora de aguas grises automatizada

'''

from tkinter import *
from tkinter import ttk
import pygame
import sys
import os
import RPi.GPIO as gpio
import time
import statistics
# Import SPI library (for hardware SPI) and MCP3008 library.
import Adafruit_GPIO.SPI as SPI
import Adafruit_MCP3008
#this line is for use the A02YYUW
sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
#this libraris the only th in that change is each the constructor, so it can be optimized
from DFRobot_RaspberryPi_A02YYUW import DFRobot_A02_Distance as Board2
from DFRobot_RaspberryPi_A02YYUW import DFRobot_A02_Distance_2 as Board3
from DFRobot_RaspberryPi_A02YYUW import DFRobot_A02_Distance_3 as Board
#archivo de alarma
alarma = '/home/omar_comando/Desktop/omarguti/twank_music/alarma.mp3'
#cada objeto pertenece a un ultrasonico
board = Board()
board2 = Board2()
board3 = Board3()


gpio.cleanup()
 #Minimum ranging threshold: 0mm
dis_min = 0 
#Highest ranging threshold: 4500mm  
dis_max = 4500 
board.set_dis_range(dis_min, dis_max) # each object refer to one ultrasonic
board2.set_dis_range(dis_min, dis_max)
board3.set_dis_range(dis_min, dis_max)
# Software SPI configuration:

MOSI = 10
MISO = 9
CLK  = 11
CS   = 8
mcp = Adafruit_MCP3008.MCP3008(clk=CLK, cs=CS, miso=MISO, mosi=MOSI)

bomba=18
bomba2=23
bomba3=20
electro=21
flow=17
paro=2

count = 0
flow_water=0 
gpio.setmode(gpio.BCM)# bcm is for chose gpio number and not pcb pins

gpio.setup(bomba, gpio.OUT)# i set all gpio outs
gpio.setup(bomba2, gpio.OUT)
gpio.setup(bomba3, gpio.OUT)
gpio.setup(electro, gpio.OUT)

gpio.output(bomba,gpio.LOW)#nota: en alto o bajo dependera del tipo de relevador que se ponga
gpio.output(bomba2,gpio.LOW)#nota: en alto o bajo dependera del tipo de relevador que se ponga
gpio.output(bomba3,gpio.LOW)
gpio.output(electro,gpio.LOW)

def paro_emergencia(channel):
    print('entramos')
    frame_paro=Frame()
    frame_paro.config(bg='red',borderwidth=4,relief='raised')
    frame_paro.pack(side= TOP) #Frame de tanque 2
    mensaje_paro=Label(frame_paro,bg="red",fg="white", text="PARO DE EMERGENCIA ACTIVADO",font=("Helvetica",40))
    mensaje_paro2=Label(frame_paro,bg="red",fg="white", text="si desea continuar con la operacion normal de twank: \n 1)vaciar contenedores de agua, a mas de la mitad \n 2) presionar de nuevo el paro de emergencia y espere 5 segundos",font=("Helvetica",20))
    mensaje_paro3=Label(frame_paro,bg="black",fg="white", text="si este mensaje no desaparece despues de 5 segundos,comuniquece al servicio tecnico de twank: 3314556123",font=("Helvetica",15))
    mensaje_paro.pack()
    mensaje_paro2.pack()
    mensaje_paro3.pack()
    while not gpio.input(paro):
        print('boton')
        gpio.output(bomba,gpio.LOW)#nota: en alto o bajo dependera del tipo de relevador que se ponga
        gpio.output(bomba2,gpio.LOW)#nota: en alto o bajo dependera del tipo de relevador que se ponga
        gpio.output(bomba3,gpio.LOW)
        gpio.output(electro,gpio.LOW)
        pygame.mixer.init()
        pygame.mixer.music.load(alarma)
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            continue
    frame_paro.pack_forget()
    mensaje_paro.pack_forget()
    mensaje_paro2.pack_forget()
    mensaje_paro3.pack_forget()

def countPulse(channel):
    global count, flow_water
    count = count+1
    flow_water=(count * 60 * 2.25 / 1000)

gpio.setup(paro, gpio.IN, pull_up_down=gpio.PUD_UP)
gpio.setup(flow, gpio.IN, pull_up_down=gpio.PUD_DOWN)
gpio.add_event_detect(flow,gpio.RISING,callback=countPulse,bouncetime=300)
gpio.add_event_detect(paro,gpio.FALLING,callback=paro_emergencia,bouncetime=100)


class App: #objeto para el tanque de agua gris
    def __init__(self, master):
        self.master=master
        
        frame=Frame(master)
        frame.config(bg='#3057E9',borderwidth=4,relief='raised')
        frame.pack() #Frame de tanque 1 agua gris
        frame.place(x=25,y=80)

        frame2=Frame(master)# frame de indicadores electrovalvula, sensor ultrasonico y flujo
        frame2.pack() 
        frame2.config(bg='#3057E9',borderwidth=4,relief='raised',width=400,height=400)
        frame2.place(x=80,y=300)
        self.canvas=Canvas(frame2,width=320,height=100,bg='#203B55',relief='sunken',borderwidth=4)
        #labels referidos al frame uno de tanque grise
        label=Label(frame, text="tanque 1", font=("Helvetica",26),bg='#3057E9',foreground='white')
        label1=Label(frame, text="agua gris", font=("Helvetica",16),bg='#3057E9',foreground='white')
        label2=Label(frame, text="litros:", font=("Helvetica",16),bg='#3057E9',foreground='white')
        label.grid(row=0)
        label1.grid(row=1)
        label2.grid(row=2)
        # x0,y0,x1,y1 el espacio entre x debe ser 65 para que sean iguales los circulos
        self.canvas.create_oval(235,30,300,85, width=1, fill='#330a04')#SENSOR DE FLUJO
        self.canvas.create_oval(125,30,190,85, width=1, fill='#330a04')#ULTRASONICO
        self.canvas.create_oval(15,30,80,85, width=1, fill='#330a04')#ELECTROVALVULA
        #texto de separacion para cada indicador
        self.canvas.create_text(50,15,text="Electrovalvula",font=("Helvetica",10), fill='white')
        self.canvas.create_text(155,15,text="Ultrasonico",font=("Helvetica",10), fill='white')
        self.canvas.create_text(270,15,text="sensor de flujo",font=("Helvetica",10), fill='white')
        #labels a los indicadores
        label_frame_2=Label(frame2, text="Indicadores", font=("Helvetica",26),bg='#3057E9',foreground='white')
        label1_frame_2=Label(frame2, text="estatus", font=("Helvetica",16),bg='#3057E9',foreground='white')
        label_frame_2.grid(row=0)
        label1_frame_2.grid(row=1)
        self.canvas.grid(row=2)

        #lectura de ultrasonico agua gris
        self.reading_label=Label(frame,text="12.34",font=("Helvetica",70),bg='#A0EEC1',relief='solid')
        self.reading_label.grid(row=3)
        self.update_reading()

    def print_distance(self,dis):
        if board.last_operate_status == board.STA_OK:
            print("Distance1 %d mm" %dis)
        elif board.last_operate_status == board.STA_ERR_CHECKSUM:
            print("ERROR")
        elif board.last_operate_status == board.STA_ERR_SERIAL:
            print("Serial open failed!")
        elif board.last_operate_status == board.STA_ERR_CHECK_OUT_LIMIT:
            print("Above the upper limit: %d" %dis)
        elif board.last_operate_status == board.STA_ERR_CHECK_LOW_LIMIT:
            print("Below the lower limit: %d" %dis)
        elif board.last_operate_status == board.STA_ERR_DATA:
            print("No data! en el 1")   
        
    def update_reading(self):
        distance = board.getDistance()
        self.print_distance(distance)
        global count, flow_water
        mm=160-distance
        litros=12.5*mm
        litros=litros*0.001
        reading_str="{:.2f}".format(litros)
        self.reading_label.configure(text=reading_str)
       
        
        if litros >= 1.2:
            self.canvas.create_oval(15,30,80,85, width=1, fill='#1f7f15')#ELECTROVALVULA
            count=0
            gpio.output(electro,gpio.HIGH)
            time.sleep(10)
            print ("The flow is: %.3f Liter/min" % (flow_water))
            distance = board.getDistance()
            self.print_distance(distance)
            mm=160-distance
            litros=12.5*mm
            litros=litros*0.001
            reading_str="{:.2f}".format(litros)
            self.reading_label.configure(text=reading_str)
            
            if flow_water>=0.200:
                distance = board.getDistance()
                self.print_distance(distance)
                mm=160-distance
                litros=12.5*mm
                litros=litros*0.001
                reading_str="{:.2f}".format(litros)
                self.reading_label.configure(text=reading_str)
                self.canvas.create_oval(235,30,300,85, width=1, fill='#1f7f15')#SENSOR DE FLUJO
            else:
                print("valor de flow: ",flow_water)
                self.reading_label.configure(text=reading_str,bg="#b57c00")
                self.canvas.create_oval(235,30,300,85, width=1, fill='red')#SENSOR DE FLUJO
                pygame.mixer.init()
                pygame.mixer.music.load(alarma)
                pygame.mixer.music.play()
                while pygame.mixer.music.get_busy():
                    continue
            if litros >=1.2:
                self.reading_label.configure(text=reading_str,bg="#b57c00")
                self.canvas.create_oval(125,30,190,85, width=1, fill='red')#ULTRASONICO
                pygame.mixer.init()
                pygame.mixer.music.load(alarma)
                pygame.mixer.music.play()
                while pygame.mixer.music.get_busy():
                    continue  
            else:
                self.canvas.create_oval(125,30,190,85, width=1, fill='#1f7f15')#ULTRASONICO
                self.canvas.create_oval(15,30,80,85, width=1, fill='#1f7f15')#ELECTROVALVULA    

        if litros <=0.55:
            self.canvas.create_oval(235,30,300,85, width=1, fill='#330a04')#SENSOR DE FLUJO
            self.canvas.create_oval(15,30,80,85, width=1, fill='#330a04')#ELECTROVALVULA
            self.canvas.create_oval(125,30,190,85, width=1, fill='#330a04')#ULTRASONICO
            gpio.output(electro,gpio.LOW)

            count = 0
            self.reading_label.configure(text=reading_str,bg="#A0EEC1",relief='solid')
        if litros > 1.7:
            self.reading_label.configure(text=reading_str,bg="red")
            time.sleep(5)
            pygame.mixer.init()
            pygame.mixer.music.load(alarma)
            pygame.mixer.music.play()
            while pygame.mixer.music.get_busy():
                continue  

        self.master.after(500,self.update_reading)

class App2:#objeto para el analizador despues de filtro y meidicion en analizador
    def __init__(self,master,alto,medio,bajo):
        self.master=master
        self.alto=alto
        self.medio=medio
        self.bajo=bajo
        frame1=Frame(master)
        frame1.config(bg='#3057E9',borderwidth=4,relief='raised')
        frame1.pack() #Frame de tanque 2
        frame1.place(x=250,y=80)
        frame2=Frame(master)
        frame2.config(bg='#203B55',borderwidth=4,relief='sunken')
        frame2.pack() #Frame de tanque 3
        frame2.place(x=750,y=175)
        label=Label(frame1, text="tanque 2", font=("Helvetica",26),bg='#3057E9',foreground='white')
        label1=Label(frame1, text="analizador de agua", font=("Helvetica",16),bg='#3057E9',foreground='white')
        label2=Label(frame1, text="litros:", font=("Helvetica",16),bg='#3057E9',foreground='white')
        label.grid(row=0)
        label1.grid(row=1)
        label2.grid(row=2)
        self.label_3=Label(frame2, text="Calidad de agua",foreground='white', font=("Helvetica",22),bg='#203B55',relief='raised')
        self.label_emoji=Label(frame2,bg='#203B55',borderwidth=8,relief='sunken')
        self.sensores=Label(frame2,text="Turbidez: \n"+"TDS: ",foreground='white', font=("Helvetica",26),bg='#203B55',relief='raised')
        self.label_3.grid(row=0)
        self.sensores.grid(row=1)
        self.label_emoji.grid(row=2)
        self.reading_label=Label(frame1,text="12.34",font=("Helvetica",70),bg='#A0EEC1',relief='sunken')
        self.reading_label.grid(row=3)
        self.update_reading()
        self.check_filtered_water()
    def check_filtered_water(self):
        if mcp.read_adc(2) <= 50 or mcp.read_adc(1)>=1000:
            self.label_emoji.configure(image=self.bajo)
            self.sensores.configure(text=f"Turbidez: {mcp.read_adc(2)}\n"+f"TDS: {mcp.read_adc(1)}",foreground='white', font=("Helvetica",14),bg='#203B55',relief='raised')
            print('salio mal: ',mcp.read_adc(2))
            #gpio.output(bomba3,gpio.HIGH)
            #time.sleep(4)
            #gpio.output(bomba3,gpio.LOW)
            pygame.mixer.init()
            pygame.mixer.music.load(alarma)
            pygame.mixer.music.play()
            while pygame.mixer.music.get_busy():
                continue  
        if mcp.read_adc(2) >= 100:
            self.label_emoji.configure(image=self.medio)
            self.sensores.configure(text=f"Turbidez: {mcp.read_adc(2)}\n"+f"TDS: {mcp.read_adc(1)}",foreground='white', font=("Helvetica",14),bg='#203B55',relief='raised')
        if mcp.read_adc(2) >= 281:
            self.label_emoji.configure(image=self.alto)
            self.sensores.configure(text=f"Turbidez: {mcp.read_adc(2)}\n"+f"TDS: {mcp.read_adc(1)}",foreground='white', font=("Helvetica",14),bg='#203B55',relief='raised')

        self.master.after(1000,self.check_filtered_water)
        
    def print_distance(self,dis):
        if board2.last_operate_status == board2.STA_OK:
            print("Distance 2: %d mm" %dis)
        elif board2.last_operate_status == board2.STA_ERR_CHECKSUM:
            print("ERROR")
        elif board2.last_operate_status == board2.STA_ERR_SERIAL:
            print("Serial open failed!")
        elif board2.last_operate_status == board2.STA_ERR_CHECK_OUT_LIMIT:
            print("Above the upper limit: %d" %dis)
        elif board2.last_operate_status == board2.STA_ERR_CHECK_LOW_LIMIT:
            print("Below the lower limit: %d" %dis)
        elif board2.last_operate_status == board2.STA_ERR_DATA:
            print("No data! en el 2")    

    def update_reading(self):
        distance = board2.getDistance()
        self.print_distance(distance)

        mm=160-distance
        litros=12.5*mm
        litros=litros*0.001
        reading_str="{:.2f}".format(litros)
        self.reading_label.configure(text=reading_str)
        if litros >= 1.2:
            gpio.output(bomba,gpio.HIGH)
        if litros <=0.9:    
            gpio.output(bomba,gpio.LOW)
        # if litros > 1.7:
        #     self.reading_label.configure(text=reading_str,bg="red")
        #     time.sleep(5)
        #     pygame.mixer.init()
        #     pygame.mixer.music.load(alarma)
        #     pygame.mixer.music.play()
        #     while pygame.mixer.music.get_busy():
        #         continue  
        else:
            self.reading_label.configure(text=reading_str,bg="#A0EEC1",relief='solid')

        self.master.after(1000,self.update_reading)
class App3:#tanque de agua disponible
    def __init__(self, master):
        self.master=master
        frame1=Frame(master)
        frame1.config(bg='#203B55',borderwidth=4,relief='raised')
        frame1.pack() #Frame de tanque 3
        frame1.place(x=475,y=175)
        label=Label(frame1, text="agua disponible",font=("Helvetica",26),bg='#203B55',foreground='white')
        label2=Label(frame1, text="litros:", font=("Helvetica",16),bg='#203B55',foreground='white')
        label.grid(row=0)
        label2.grid(row=1)
        self.reading_label=Label(frame1,text="12.34",font=("Helvetica",70),bg='#A0EEC1')
        self.reading_label.grid(row=3)
        self.update_reading()  
    def print_distance(self,dis):
        if board3.last_operate_status == board3.STA_OK:
            print("Distance 3: %d mm" %dis)
        elif board3.last_operate_status == board3.STA_ERR_CHECKSUM:
            print("ERROR en el 3")
        elif board3.last_operate_status == board3.STA_ERR_SERIAL:
            print("Serial open failed!")
        elif board3.last_operate_status == board3.STA_ERR_CHECK_OUT_LIMIT:
            print("Above the upper limit: %d" %dis)
        elif board3.last_operate_status == board3.STA_ERR_CHECK_LOW_LIMIT:
            print("Below the lower limit: %d" %dis)
        elif board3.last_operate_status == board3.STA_ERR_DATA:
            print("No data! en el 3")    

    def update_reading(self):
        distance = board3.getDistance()
        self.print_distance(distance)

        mm=160-distance
        litros=12.5*mm
        litros=litros*0.001
        reading_str="{:.2f}".format(litros)
        self.reading_label.configure(text=reading_str)
        if litros > 1.7:
            self.reading_label.configure(text=reading_str,bg="red")
            time.sleep(2)
            pygame.mixer.init()
            pygame.mixer.music.load(alarma)
            pygame.mixer.music.play()
            while pygame.mixer.music.get_busy():
                continue  
        else:
            self.reading_label.configure(text=reading_str,bg="#A0EEC1",relief='solid')
        self.master.after(1000,self.update_reading)

def bomba1():
    gpio.output(bomba2,gpio.HIGH)
    time.sleep(4)
    gpio.output(bomba2,gpio.LOW)

def auxiliar():
    gpio.output(bomba,gpio.HIGH)
    time.sleep(4)
    gpio.output(bomba,gpio.LOW)
    

def main():
    root=Tk()# root en nuestra ventana main, toda nuestra ventana principal, donde podemos colocar frames(ventanas distintas)
    root.title(" ")
    root.geometry("1024x600+0+0")#1024x600+0+0 VENTANA PRINCIPAL COLOR AZUL
    root.configure(bg='#2E86C1')
    #declaramos imagenes de presentacion logo y cucei etc
    logo_twank=PhotoImage(file = "/home/omar_comando/Desktop/omarguti/images/logo.png")
    logo=logo_twank.subsample(4,4)
    l_twank=Label(root,image=logo,bg='#2E86C1')
    l_twank.pack()
    l_twank.place(x=600,y=10)
    logo_cucei=PhotoImage(file = "/home/omar_comando/Desktop/omarguti/images/cucei.png")
    logo_c=logo_cucei.subsample(10,10)
    logo_cu=Label(root,image=logo_c,bg='#2E86C1')
    logo_cu.pack()
    logo_cu.place(x=950,y=470)
    App(root) # creamos el frame de todo tanque 1 usando poo y se coloca en root= ventana principal azul
    App3(root)
    #declaramos imagenes para los botonoes donde estos llaman una funcion
    photo_boton_agua = PhotoImage(file = "/home/omar_comando/Desktop/omarguti/images/open.png")
    photo_boton_auxiliar = PhotoImage(file = "/home/omar_comando/Desktop/omarguti/images/auxiliar.png")
    #declaramos imagenes el estatus del agua limpia o sucia
    photo_status_agua_alto= PhotoImage(file = "/home/omar_comando/Desktop/omarguti/images/alto.png")
    photo_status_agua_medio =PhotoImage(file = "/home/omar_comando/Desktop/omarguti/images/medio.png")
    photo_status_agua_bajo = PhotoImage(file = "/home/omar_comando/Desktop/omarguti/images/bajo.png")
    #cambio de tamano de las imagenes del estado de agua
    alto = photo_status_agua_alto.subsample(3, 3)
    medio = photo_status_agua_medio.subsample(3, 3)
    bajo = photo_status_agua_bajo.subsample(3, 3)
    App2(root,alto,medio,bajo)
    #cambio de tamano de imagen
    photo_boton_auxiliar=photo_boton_auxiliar.subsample(7,7)
    photo_boton_agua = photo_boton_agua.subsample(4, 4)
    #configuracion de los botones y sus funciones
    boton_agua=Button(root,image = photo_boton_agua, compound = TOP,command=bomba1,bg='#2E86C1', highlightthickness = 0,bd=0,activebackground='#2E86C1')
    boton_auxiliar=Button(root,image = photo_boton_auxiliar, compound = TOP,command=auxiliar,bg='#2E86C1', highlightthickness = 0,bd=0,activebackground='#2E86C1')
    
    boton_agua.pack()
    boton_auxiliar.pack()

    boton_agua.place(x=480,y=420)
    boton_auxiliar.place(x=820,y=430)
    root.mainloop()
    
    
if __name__=="__main__":
    main()
    gpio.cleanup()