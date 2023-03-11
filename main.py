import WIFI_CONFIG
from network_manager import NetworkManager
import time
import uasyncio
import ujson
from Url_encode import url_encode
from urllib import urequest
from picographics import PicoGraphics, DISPLAY_INKY_PACK
from pimoroni import Button
import gc
import micropython


button_a = Button(12)
button_b = Button(13)
button_c = Button(14)

WHITE_PEN = 15
BLACK_PEN = 0

graphics = PicoGraphics(DISPLAY_INKY_PACK)
print("init",graphics)
graphics.set_font("bitmap8")

WIDTH, HEIGHT = graphics.get_bounds()
RANDOM_WORD_ENDPOINT = "https://www.vocabulary.com/randomword.json"
WORD_DEFINITION_ENDPOINT = "https://vocabulary.vercel.app/word/{word}"

def show_error(exception):
    
    print("error",graphics)
    
    graphics.set_update_speed(1)
    graphics.set_pen(WHITE_PEN)
    graphics.clear()
    graphics.set_pen(BLACK_PEN)
    graphics.text("Error", 10, 10, wordwrap=WIDTH - 20, scale=3)
    graphics.text("Exception: {e}".format(e=exception), 10, 40, wordwrap=WIDTH - 20, scale=2)
    graphics.update()


def status_handler(mode, status, ip):
    graphics.set_update_speed(2)
    graphics.set_pen(WHITE_PEN)
    graphics.clear()
    graphics.set_pen(BLACK_PEN)
    graphics.text("Network: {}".format(WIFI_CONFIG.SSID), 10, 10, scale=2)
    status_text = "Connecting..."
    if status is not None:
        if status:
            status_text = "Connection successful!"
        else:
            status_text = "Connection failed!"

    graphics.text(status_text, 10, 30, scale=2)
    graphics.text("IP: {}".format(ip), 10, 60, scale=2)
    graphics.update()
    
    
network_manager = NetworkManager(WIFI_CONFIG.COUNTRY, status_handler=status_handler)

def clearram():
    gc.collect()
    gc.mem_free()
    

def requestJSON(url):

    print("Requesting URL: {}".format(url))
    try:
        res = urequest.urlopen(url)
        json = ujson.load(res)
        res.close()
        return json
    except Exception as e:
        raise e
    
def draw_loading_bar(percent):
    bar_width = round((WIDTH / 100) * percent)
    graphics.set_update_speed(3)
    graphics.set_pen(WHITE_PEN)
    graphics.clear()
    graphics.set_pen(BLACK_PEN)
    graphics.rectangle(5, 5,bar_width, 10)
    graphics.text("LOADING...", 40, 50, scale=5)
    graphics.update()
   

def update():
    
    print("before update")
    micropython.mem_info()
    
    draw_loading_bar(25)
    
    print("is connected", network_manager.isconnected())
    if not network_manager.isconnected():
        uasyncio.get_event_loop().run_until_complete(network_manager.client(WIFI_CONFIG.SSID, WIFI_CONFIG.PSK))
        
    draw_loading_bar(60)
    
    randomWordJSON = requestJSON(RANDOM_WORD_ENDPOINT)
    print("randomWordJSON", randomWordJSON)
    randomWord = randomWordJSON["result"]["word"]
    
    draw_loading_bar(90)

    wordDefJSON = requestJSON(WORD_DEFINITION_ENDPOINT.format(word=url_encode().encode(randomWord)))
    defintion = wordDefJSON["data"]
                             
    graphics.set_update_speed(1)
    graphics.set_pen(WHITE_PEN)
    graphics.clear()
    graphics.set_pen(BLACK_PEN)
    graphics.text(randomWord, 10, 10, scale=5)
    graphics.text(defintion, 10, 60, wordwrap=WIDTH - 20, scale=1)

    graphics.update()
    
    print("after update")
    micropython.mem_info()
    
    del randomWordJSON
    del randomWord
    
    del wordDefJSON
    del defintion

    clearram()
    
    print("after gc")
    micropython.mem_info()
    


# Run continuously.
# Be friendly to the API you're using!
while True:
    try:
        update()
    except Exception as e:
        show_error(e)

    while not button_a.is_pressed:
        time.sleep(0.1)