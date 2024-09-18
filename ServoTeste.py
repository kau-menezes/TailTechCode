from machine import Pin, PWM
import time

MotorEntrada = PWM(Pin(32, Pin.OUT), freq=50, duty=51)
MotorSaida = PWM(Pin(33, Pin.OUT), freq=50, duty=51)

def AbrirEntrada():
    global MotorEntrada
    MotorEntrada.duty(51)
def FecharEntrada():
    global MotorEntrada
    MotorEntrada.duty(102)
def AbrirSaida():
    global MotorSaida
    MotorSaida.duty(51)
def FecharSaida():
    global MotorSaida
    MotorSaida.duty(102)
    
while 1:
    AbrirEntrada()
    time.sleep(0.5)
    AbrirSaida()
    print("abri")
    time.sleep(0.5)
    FecharEntrada()
    time.sleep(0.5)
    FecharSaida()
    print("fechada")
    time.sleep(0.5)
    
    