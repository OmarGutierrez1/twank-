from tkinter import *
import RPi.GPIO as gpio
import time
import statistics
# Import SPI library (for hardware SPI) and MCP3008 library.
import Adafruit_GPIO.SPI as SPI
import Adafruit_MCP3008

gpio.cleanup()
# Software SPI configuration:
CLK  = 11
MISO = 9
MOSI = 10
CS   = 8
mcp = Adafruit_MCP3008.MCP3008(clk=CLK, cs=CS, miso=MISO, mosi=MOSI)

trigger_pin=24
echo_pin=23
trigger_pin2=14
echo_pin2=15
bomba=18
bomba2=4
boton=21

gpio.setmode(gpio.BCM)
gpio.setup(boton, gpio.IN, pull_up_down=gpio.PUD_UP)
gpio.setup(trigger_pin, gpio.OUT)
gpio.setup(echo_pin, gpio.IN)
gpio.setup(trigger_pin2, gpio.OUT)
gpio.setup(echo_pin2, gpio.IN)

gpio.setup(bomba, gpio.OUT)
gpio.setup(bomba2, gpio.OUT)
gpio.output(bomba,gpio.HIGH)#nota: en alto o bajo dependera del tipo de relevador que se ponga
gpio.output(bomba2,gpio.HIGH)#nota: en alto o bajo dependera del tipo de relevador que se ponga

def send_trigger():
    gpio.output(trigger_pin, True)
    time.sleep(0.0001)
    gpio.output(trigger_pin, False)
def send_trigger2():
    gpio.output(trigger_pin2, True)
    time.sleep(0.0001)
    gpio.output(trigger_pin2, False)
def wait_echo(value,timeout):
    count=timeout
    while gpio.input(echo_pin) != value and count > 0:
        count=count-1
def wait_echo2(value,timeout):
    count=timeout
    while gpio.input(echo_pin2) != value and count > 0:
        count=count-1
def get_distance():#obtiene la distancia del sensor uno
    muestras=[]# es una lista donde se despositan 9 mediciones cada 0.020 segundos
    for i in range(0,10):
            send_trigger()
            wait_echo(True, 10000)
            start=time.time()
            wait_echo(False, 10000)
            finish=time.time()
            pulse_len=finish-start
            distance_cm=pulse_len/0.000058
            muestras.append(distance_cm)
            time.sleep(.020)
    result=statistics.mean(muestras)#metodo que saca el promedio de las mediciones para darte una medicion mas exacta
    return result
def get_distance2():#obtiene la distancia del sensor uno
    muestras2=[]
    for i in range(0,10):
        send_trigger2()
        wait_echo2(True, 10000)
        start=time.time()
        wait_echo2(False, 10000)
        finish=time.time()
        pulse_len=finish-start
        distance_cm=pulse_len/0.000058
        muestras2.append(distance_cm)
        time.sleep(.030)
    result=statistics.mean(muestras2)
    return result
    
class App: #todo lo referido a la ventanda tanque 1
    def __init__(self, master):
        self.master=master
        frame=Frame(master)
        frame.pack(side=LEFT) #Frame de tanque 1
        label=Label(frame, text="tanque 1", font=("Helvetica",26))
        label1=Label(frame, text="agua decantada", font=("Helvetica",16))
        label2=Label(frame, text="litros:", font=("Helvetica",16))
        label.grid(row=0)
        label1.grid(row=1)
        label2.grid(row=2)
        self.reading_label=Label(frame,text="12.34",font=("Helvetica",80))
        self.reading_label.grid(row=3)
        self.update_reading()
        
    def update_reading(self):
        cm=16-get_distance()# tenemos que la resta es en base a que el tamano del recipiente es 16 cm que es igual a 2000ml
        
        litros=125*cm #2000ml entre 16 = a 125 ml por 1 cm , por eso se multiplica 125 * cm
        litros=litros*0.001
        
        if litros >= .75:# condicion para activar la bomba de tanque 1
            if mcp.read_adc(0) >= 580:
                gpio.output(bomba,gpio.LOW)
                time.sleep(0.5)
            else:
                print("water is no clean")
                print('water read: ',mcp.read_adc(0))
                print(" ")
        if litros <= .40:
            gpio.output(bomba,gpio.HIGH)
        reading_str="{:.2f}".format(litros)
        self.reading_label.configure(text=reading_str)
        self.master.after(1000,self.update_reading)

class App2:#todo lo referido a la ventana de tanque 2
    def __init__(self, master):
        self.master=master
        frame1=Frame(master)
        frame1.pack(side=RIGHT) #Frame de tanque 2
        label=Label(frame1, text="tanque 2", font=("Helvetica",26))
        label1=Label(frame1, text="almacen de agua", font=("Helvetica",16))
        label2=Label(frame1, text="litros:", font=("Helvetica",16))
        label.grid(row=0)
        label1.grid(row=1)
        label2.grid(row=2)
        self.reading_label=Label(frame1,text="12.34",font=("Helvetica",80))
        self.reading_label.grid(row=3)
        self.update_reading()
        
    def update_reading(self):
        cm=16-get_distance2()
        litros=125*cm
        litros=litros*0.001
        if gpio.input(boton):
            gpio.output(bomba2,gpio.HIGH)
        else:
            gpio.output(bomba2,gpio.LOW)
            time.sleep(10)
        reading_str="{:.2f}".format(litros)
        self.reading_label.configure(text=reading_str)
        self.master.after(1000,self.update_reading)
        
    
    
    
def main():
    
    root=Tk()# root en nuestra ventana main, toda nuestra ventana principal, donde podemos colocar frames(ventanas distintas)
    root.title("twank")
    root.geometry("500x500+0+0")#1024x600+0+0 VENTANA PRINCIPAL COLOR AZUL
    root.configure(bg='blue')
    ventana1=Frame()#nombre de nuestro proyecto
    ventana1.pack(side= TOP)
    ventana1.config(bg="gray",bd=20,width="200",height="35")
    etiqueta=Label(ventana1,bg="gray",fg="white", text="TWANK")
    etiqueta.pack()
    app=App(root) # creamos el frame de todo tanque 1 usando poo y se coloca en root= ventana principal azul
    app2=App2(root)
    root.mainloop()
    
    
if __name__=="__main__":
    main()