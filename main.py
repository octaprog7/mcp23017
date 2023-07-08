# micropython
# mail: goctaprog@gmail.com
# MIT license
import time
# Please read MCP23017 datasheet!
from machine import I2C, Pin
import mcp23017mod
from sensor_pack.bus_service import I2cAdapter

# Если в обработчике прерывания возникнет ошибка, MicroPython не сможет создать сообщение о ней!
# Cоздаю специальный буфер для этой цели!
# micropython.alloc_emergency_exception_buf(100)
# interrupt counter, один байт
# irq_cnt = bytearray(1)


# def irq_handler(p: Pin):
#    """Пожалуйста прочитай это: http://docs.micropython.org/en/latest/reference/isr_rules.html#isr-rules"""
#    global irq_cnt
#    irq_cnt[0] += 1


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

    # функции irq_handler будет передаваться управление, когда один из выводов P0..P7, настроенных, как ВХОД,
    # изменит состояние! Вы можете подключить к выводу GPIO21 провод и подключать его к GND,
    # чтобы прерывание возникло!
    # Не забудьте подключить вывод INT PCF8574 к выводу GPIO21 платы Arduino Nano RP2040 Connect with RP2040 !!!

    # i2c = I2C(id=1, scl=Pin(27), sda=Pin(26), freq=400_000)  # on Arduino Nano RP2040 Connect tested
    i2c = I2C(id=1, scl=Pin(7), sda=Pin(6), freq=400_000)  # create I2C peripheral at frequency of 400kHz
    adapter = I2cAdapter(i2c)


if __name__ == '__main__':
    expander = mcp23017mod.MCP23017(adapter)
    print(f"expander._bank: {expander._bank}")
    """
    print(32*"_")
    for adr in range(0x16):
        expander._write_reg(adr, 0x00)
        v = expander._read_reg(adr)[0]
        print("0", hex(adr), hex(v))
        expander._write_reg(adr, 0xFF)
        v = expander._read_reg(adr)[0]
        print("1", hex(adr), hex(v))
        print(8*"_")
"""
    sys.exit(0)
    # b = expander._read(0x10)
    # print(b)
    print(16 * "_")
    # ba, bb = expander._read_reg(0), expander._read_reg(1)
    # print(ba[0], bb[0])
    # v = expander._read_reg(0, 2)
    # print(f"v={v}, {v[0]}, {v[1]}")
    # b = expander._read(0x10)
    # print(b)
    print(16 * "_")
    # for i in range(0x10):
    #    b = expander._read_reg(i)
    #    print(f"{i}; {b}")
    # expander.active_port = 0
    # print(f"hex mode: {expander.hex_mode}")
    # expander.io_dir = 0xFF	# 8 bit as input
    # expander.pull_up = 0xFF		# connect 8 pull up resistors
    # expander.input_polarity = 0xFF		# GPIO register bit reflects the same logic state of the input pin.
    # print(f"iodir: 0x{expander.io_dir:X}")
    # print(f"pull up: 0x{expander.pull_up:X}")
    # print(f"active_port: {expander.active_port}")
    # print(f"input polarity: 0x{expander.input_polarity:X}")
    
    for port in range(2):
        expander.active_port = port
        print(f"active_port: {expander.active_port}")
        expander.io_dir = 0xFF	# 8 bit as input
        expander.pull_up = 0xFF		# connect 8 pull up resistors
        expander.input_polarity = 0x00		# GPIO register bit reflects the same logic state of the input pin.
    
    while True:
        time.sleep_ms(500)
        print(f"0x{expander.gpio:X}")
