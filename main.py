# MicroPython
# mail: goctaprog@gmail.com
# MIT license
import time
# Please read MCP23017 datasheet!
from machine import I2C, Pin
import mcp23017mod
from sensor_pack.bus_service import I2cAdapter

# Пожалуйста, прочитайте документацию на MCP23017!
# Please read the MCP23017 documentation!

if __name__ == '__main__':
    # пожалуйста установите выводы scl и sda в конструкторе для вашей платы, иначе ничего не заработает!
    # please set scl and sda pins for your board, otherwise nothing will work!
    # https://docs.micropython.org/en/latest/library/machine.I2C.html#machine-i2c
    # i2c = I2C(0, scl=Pin(13), sda=Pin(12), freq=400_000) # для примера
    # bus =  I2C(scl=Pin(4), sda=Pin(5), freq=100000)   # на esp8266    !
    # Внимание!!!
    # Замените id=1 на id=0, если пользуетесь первым портом I2C !!!
    # Warning!!!
    # Replace id=1 with id=0 if you are using the first I2C port !!!
    # i2c = I2C(0, scl=Pin(13), sda=Pin(12), freq=400_000) # для примера

    # i2c = I2C(id=1, scl=Pin(27), sda=Pin(26), freq=400_000)  # on Arduino Nano RP2040 Connect and Pico W tested!
    i2c = I2C(id=1, scl=Pin(7), sda=Pin(6), freq=400_000)  # create I2C peripheral at frequency of 400kHz
    adapter = I2cAdapter(i2c)       # адаптер для стандартного доступа к шине


if __name__ == '__main__':
    expander = mcp23017mod.MCP23017(adapter)
    print(f"hex mode: {expander.hex_mode}")
    print(16 * "_")
    
    # настройка всех выводов порта A на ввод
    expander.active_port = 0
    expander.io_dir = 0xFF      # 8 bit as input
    expander.pull_up = 0xFF		# connect 8 pull up resistors
    expander.input_polarity = 0		# GPIO register bit reflects the same logic state of the input pin.
    
    # вывод в консоль состояния порта expander.active_port. подключите к ним кнопки
    # между выводом порта и GND и смотрите, как меняется состояние битов! 
    cnt = 0
    print(f"active_port: {expander.active_port} input test!")
    for pin_state in expander:
        time.sleep_ms(500)
        print(f"pin binary state: b{pin_state:b}")
        cnt += 1
        if cnt > 50:
            break
    
    expander.active_port = 1
    expander.io_dir = 0x0      # 8 bit port A as output
    print(f"active_port: {expander.active_port} output test!")
    # к выводам порта В подключите светодиод (анодом к выводу порта),
    # последовательно с сопротивлением 150 Oм.
    # настройка всех выводов порта B на ВЫвод!
    for i in range(1000):
        expander.gpio = 0xFF    # led ON	светодиод(ы) светят
        time.sleep_ms(500)		# пауза в 500 мс
        expander.gpio = 0x00    # led OFF	светодиод(ы) не светят
        time.sleep_ms(500)		# пауза в 500 мс
        