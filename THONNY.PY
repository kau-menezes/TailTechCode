from machine import Pin, PWM
import time
import urequests
import ujson
import network
import _thread
import mfrc522
from machine import Pin,SPI
from utime import ticks_ms

# =================================================== SERVO MOTOR  ===================================================

MotorEntrada = PWM(Pin(32, Pin.OUT), freq=50, duty=102)
MotorSaida = PWM(Pin(33, Pin.OUT), freq=50, duty=102)

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
    

# =================================================== TAG  ===================================================
def inicio_rc():
    spi = SPI(2, baudrate=2500000, polarity=0, phase=0)
    spi.init()
    rdr = mfrc522.MFRC522(spi=spi, gpioRst=4, gpioCs=5)
    return rdr

def inicio_rc2():
    #spi = SPI(2, baudrate=2500000, polarity=0, phase=0)
    #spi.init()
    rdr = mfrc522.MFRC522(spi=None , gpioRst=26, gpioCs=27)
    return rdr

def autenticator_cat(PortaJson,rdr):
    global card_id
    (stat, tag_type) = rdr.request(rdr.REQIDL)
    if stat == rdr.OK:
        (stat,raw_uid) = rdr.anticoll()
        if stat == rdr.OK:
            card_id = "0x%02x%02x%02x%02x" % (raw_uid[0], raw_uid[1], raw_uid[2], raw_uid[3])
            print(card_id)
            for gato in PortaJson["Gatos"]:
                if card_id == gato:
                    return True
    return False
        
# =================================================== CREDENCIAIS WIFI  ===================================================

#nome = "Vivo-Internet-BF17"
#senha = "78814222"

# nome = "Wifi Amilton"
# senha =  "87654321"

nome = "Kauane's Galaxy S21 5G"
senha =  "03101409"




# =================================================== ENVIO E RESPOSTA DO FIREBASE  ===================================================

# endereço e configurações
FIREBASE_URL = "https://iiot-7276b-default-rtdb.firebaseio.com/iotgato"
SECRET_KEY = ""

#tentativa de var global
PortaJson = {}
dados_SQL = {}

def conectarWifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        print("Conectando no WiFi...")
        wlan.connect(nome, senha)
        while not wlan.isconnected():
            pass
    print("Wifi conectado... IP: {}".format(wlan.ifconfig()[0]))

def getFire():
    global PortaJson
    try:
        headers = {
            "Content-Type": "application/json",
            "Authorization": "Bearer " + SECRET_KEY
        }
        url = FIREBASE_URL + "/porta.json"  # Coloque o seu nome
        
        response = urequests.get(url,headers=headers)
        PortaJson = ujson.loads(response.text)
        response.close()
        time.sleep(1)
    except:
        pass

def sendFire():
    global dados_SQL
    if dados_SQL == {}:
        return
    try:
        headers = {
            "Content-Type": "application/json",
            "Authorization": "Bearer " + SECRET_KEY
        }
        url = FIREBASE_URL + "/gatoStatus.json"  # Coloque o seu nome

        response = urequests.put(url, data=ujson.dumps(dados_SQL), headers=headers)
        #'print("resposta: ", response.text)
        response.close()
    except:
        pass
    
def GetSendFire():
    while True:
        getFire()
        sendFire()
        time.sleep(2)
# =================================================== MAIN  ===================================================

# variável global
card_id = ""
    
# variávewl para verificação de envio para o SQL
id = 0

# conecta ao wifi

conectarWifi()
getFire()
# inicia a thread de pegar os dados do Firebase e Enviar para o Firebase
_thread.start_new_thread(GetSendFire,())
print("Pronto para receber gatos")
while True:
    
    # pega o horário do momento - retorna uma lista 
    now = time.localtime();
    
    # inicia o leitor da ENTRADA
    rdr = inicio_rc()
    
    #verifica o card_id da tag e retorna o acesso da tag
    entrada = autenticator_cat(PortaJson,rdr)
    
    # inicia o leitor da SAÍDA
    rdr = inicio_rc2()
    
    #verifica o card_id da tag e retorna o acesso da tag
    saida = autenticator_cat(PortaJson,rdr)
    
#     print(entrada)
#     print(saida)
    
    
    if entrada:
        hour = f"0{now[3]}" if now[3] <= 9 else f"{now[3]}"
        minutes = f"0{now[4]}" if now[4] <= 9 else f"{now[4]}"
        seconds = f"0{now[5]}" if now[5] <= 9 else f"{now[5]}"
        agora = f"{hour}:{minutes}:{seconds}.0000000"
        
        if agora >= PortaJson["InicioEntrada"] and agora <= PortaJson["FimEntrada"]:
            print("Pode entrar")
            AbrirEntrada()
            AbrirSaida()
            
            
            id+=1
            dados_SQL = { "ID" : id, "Tag" : card_id, "Entrada" : entrada, "IDPorta" : 1}
        
            time.sleep(8)
            FecharSaida()
            FecharEntrada()
            
            
    if saida:
        hour = f"0{now[3]}" if now[3] <= 9 else f"{now[3]}"
        minutes = f"0{now[4]}" if now[4] <= 9 else f"{now[4]}"
        seconds = f"0{now[5]}" if now[5] <= 9 else f"{now[5]}"
        agora = f"{hour}:{minutes}:{seconds}.0000000"
        
        if agora >= PortaJson["InicioSaida"] and agora <= PortaJson["FimSaida"]:
            print("Pode sair");
            AbrirSaida()
            AbrirEntrada()
            
            id+=1
            dados_SQL ={ "ID" : id, "Tag" : card_id, "Entrada" : not saida, "IDPorta" : 1}
            

            time.sleep(8)
            FecharSaida()
            FecharEntrada()

    time.sleep(0.1)

    



    