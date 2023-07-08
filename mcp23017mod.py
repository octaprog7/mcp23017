# micropython
# MIT license
# Copyright (c) 2023 Roman Shevchik   goctaprog@gmail.com
import micropython

from sensor_pack import bus_service
from sensor_pack.base_sensor import Device, Iterator, check_value


class MCP23017(Device, Iterator):
    """MicroPython class for control 16-Bit I/O Expander with Serial Interface"""
    def __init__(self, adapter: bus_service.BusAdapter, address: int = 0x27):
        """eight_bit_mode - если Истина, то два порта (8-бит) ввода/вывода работают отдельно друг от друга.
        Иначе, два порта (8-бит) ввода/вывода объединяются в один (16 бит) порт ввода/вывода"""
        s0 = f"Invalid address value: 0x{address:x}!"
        check_value(address, range(0x20, 0x28), s0)
        super().__init__(adapter, address, big_byte_order=True)
        # после POR IOCON.BANK = 0 всегда!
        self._bank = self._get_addr_mode()  # то же самое, что и IOCON.BANK. После POR он в нуле!
        self._active_port = 0
        self._setup()

    def _get_addr_mode(self) -> bool:
        """Текущая адресация.
        Возвращает True, когда адресация портов раздельная (2 порта по 8 бит, IOCON.BANK = 1).
        Или False, когда адресация портов совместная (1 порт 16 бит, IOCON.BANK = 0)"""
        addrs = (0x0A, 0x0B), (0x05, 0x15)      # адреса IOCON
        lst = list()
        for ta in addrs:
            for a in ta:    # младший бит (бит 0) не доступен для записи в IOCON. Читается всегда, как 0!
                self._write_reg(a, self._read_reg(a)[0] | 0x03)     # пишу в биты 0 и 1 единицу
                lst.append(self._read_reg(a)[0] & 0x01)     # читаю два бита (0 и 1)
        #
        for i in (0, 2):
            if 0 == lst[i] == lst[i+1]:
                return i != 0       # если в младших битах нули, а я выше писал в них единицы, то это IOCON!
        return False

    # def _read(self, count: int):
    #    return self.adapter.read(self.address, count)

    @property
    def active_port(self) -> int:
        """возвращает текущий порт, над которым производятся операции чтения и записи!"""
        return self._active_port

    @active_port.setter
    def active_port(self, value: int):
        """устанавливает текущий порт, над которым производятся операции чтения и записи!
        # в режиме 8 бит active_port может принимать значения 0(port a) и 1(port b).
        # в режиме 16 бит active_port может принимать значение 0."""
        if self.hex_mode:
            self._active_port = 0
            return
        self._active_port = 1 if value else 0

    @property
    def hex_mode(self) -> bool:
        """Возвращает Истина, когда 16-ти битный режим включен. Один порт на 16 бит I/O!
        Иначе, два порта по 8 бит I/O"""
        return not self._bank

    @hex_mode.setter
    def hex_mode(self, value: bool):
        """Устанавливает режим 16 или 8 бит I/O"""
        # режим два порта(0, 1) по 8 bit
        # self._bank = True
        if value:   # режим один порт(0) 16 bit
            # self._bank = False
            self.active_port = 0

        self._setup_iocon(bank=not value, mirror=False, seqop=False)

    def _read_reg_by_index(self, index: int) -> int:
        """Чтение регистра по его индексу и текущему активному порту"""
        addr = self._get_reg_address(index)[self.active_port]    #
        bytes_count = 2 if self.hex_mode else 1  # кол-во байт
        res = self._read_reg(addr, bytes_count)  # bytes
        fmt = "H" if self.hex_mode else "B"  # формат (H - unsigned short/B - unsigned byte)
        # print(f"_read_reg: addr: 0x{addr:X}. index: {index}")
        return self.unpack(fmt, res)[0]

    def _write_reg_by_index(self, index: int, value: int):
        """Запись в регистр по его индексу и текущему активному порту"""
        addr = self._get_reg_address(index)[self.active_port]  #
        bytes_count = 2 if self.hex_mode else 1  # кол-во байт
        # print(f"_write_reg: addr: 0x{addr:X}. value: {value:X}")
        self._write_reg(addr, value, bytes_count)

    # PULL UP RESISTORS
    def get_pull_up(self) -> int:
        """возвращает содержимое регистра GPPU текущего активного порта"""
        return self._read_reg_by_index(6)   # 6 - GPPU

    def set_pull_up(self, value: int):
        self._write_reg_by_index(6, value)  # 6 - GPPU

    @property
    def pull_up(self) -> int:
        return self.get_pull_up()

    @pull_up.setter
    def pull_up(self, value):
        self.set_pull_up(value)

    def get_gpio(self) -> int:
        return self._read_reg_by_index(9)     # 9 - GPIO

    def set_gpio(self, value: int):
        self._write_reg_by_index(9, value)  # 9 - GPIO

    @property
    def gpio(self) -> int:
        return self.get_gpio()

    @gpio.setter
    def gpio(self, value):
        self.set_gpio(value)

    def get_output_latch(self) -> int:
        """Возвращает значение OLAT.
        Регистр OLAT обеспечивает доступ к вывода"""
        return self._read_reg_by_index(0x0A)     # 0x0A - OLAT

    def set_output_latch(self, value: int):
        """Записывает значение в OLAT"""
        self._write_reg_by_index(0x0A, value)  # 0x0A - OLAT

    @property
    def output_latch(self) -> int:
        return self.get_output_latch()

    @output_latch.setter
    def output_latch(self, value):
        self.set_output_latch(value)

    def get_io_dir(self) -> int:
        """Возвращает значение регистра IODIR.
        Управляет направлением ввода/вывода данных."""
        return self._read_reg_by_index(0)     # 0 - IODIR

    def set_io_dir(self, value: int):
        """Записывает значение в регистр IODIR.
        Управляет направлением ввода/вывода данных."""
        self._write_reg_by_index(0, value)  # 0 - IODIR

    @property
    def io_dir(self) -> int:
        """Управляет направлением ввода/вывода данных."""
        return self.get_io_dir()

    @io_dir.setter
    def io_dir(self, value):
        self.set_io_dir(value)

    def get_input_pol(self) -> int:
        """Возвращает значение регистра IPOL.
        Этот регистр позволяет пользователю настроить полярность соответствующих битов порта GPIO. Если бит установлен,
        соответствующий бит регистра GPIO будет отражать инвертированное значение на выводе."""
        return self._read_reg_by_index(1)     # 0 - IPOL

    def set_input_pol(self, value: int):
        """Записывает значение в регистр IPOL."""
        self._write_reg_by_index(1, value)  # 0 - IPOL

    @property
    def input_polarity(self) -> int:
        """Позволяет пользователю настроить полярность соответствующих битов порта GPIO."""
        return self.get_input_pol()

    @input_polarity.setter
    def input_polarity(self, value):
        self.set_input_pol(value)

    def get_int_en(self) -> int:
        """Возвращает значение регистра GPINTEN.
        Регистр GPINTEN управляет функцией прерывания при изменении для каждого вывода."""
        return self._read_reg_by_index(2)   # GPINTEN: INTERRUPT-ON-CHANGE

    def set_int_en(self, value: int):
        """Записывает значение в регистр GPINTEN.
        Регистр GPINTEN управляет функцией прерывания при изменении для каждого вывода."""
        self._write_reg_by_index(2, value)  # 0 - IPOL

    @property
    def int_en(self) -> int:
        """Управляет функцией прерывания при изменении для каждого вывода"""
        return self.get_int_en()

    @int_en.setter
    def int_en(self, value: int):
        self._write_reg_by_index(2, value)  # 0 - IPOL

    def get_int_ctrl(self) -> int:
        """Возвращаемое значение из регистра INTCON"""
        return self._read_reg_by_index(4)   # INTCON: INTERRUPT-ON-CHANGE CONTROL REGISTER

    def set_int_ctrl(self, value: int):
        """Записывает значение в регистр INTCON"""
        self._write_reg_by_index(4, value)  # 0 - INTCON

    @property
    def int_ctrl(self) -> int:
        """Управление прерываниями"""
        return self.get_int_ctrl()

    @int_ctrl.setter
    def int_ctrl(self, value: int):
        self.set_int_ctrl(value)

    def get_def_val(self) -> int:
        """Возвращает значение из регистра DEFVAL.
        Значение сравнения по умолчанию настраивается в регистре DEFVAL. Если включено (через GPINTEN и INTCON)
        сравнение с регистром DEFVAL, противоположное значение на соответствующем выводе вызовет прерывание."""
        return self._read_reg_by_index(3)

    def set_def_val(self, value: int):
        """Записывает значение в регистр DEFVAL."""
        self._write_reg_by_index(3, value)

    @property
    def def_val(self) -> int:
        """Значение по умолчанию для сравнения. Формирование прерывания!"""
        return self.get_def_val()

    @def_val.setter
    def def_val(self, value: int):
        self.set_def_val(value)

    def get_if(self) -> int:
        """Возвращает значение из регистра INTERRUPT FLAG REGISTER"""
        return self._read_reg_by_index(7)  # INTERRUPT FLAG REGISTER

    def get_int_cap(self) -> int:
        """Возвращает значение из регистра INTCAP.
        Регистр INTCAP содержит значение порта GPIO в момент возникновения прерывания."""
        return self._read_reg_by_index(8)

    @micropython.native
    def _get_reg_address(self, index: int) -> [tuple, int]:
        """
        Возвращает адреса пар(!) регистров по их индексу 0..10 в виде кортежа (адрес регистра А, адрес регистра Б)
        index,  REG
        0       IODIR
        1       IPOL
        2       GPINTEN
        3       DEFVAL
        4       INTCON
        5       IOCON
        6       GPPU
        7       INTF
        8       INTCAP
        9       GPIO
        10      OLAT

        :param index:
        :return:
        """
        s0 = f"Invalid index value: {index}!"
        check_value(index, range(11), s0)
        if self._bank:
            x = index
            return x, x + 0x10
        # 16 bit mode
        x = index << 1
        return x, x + 1

    def _setup_iocon(self, bank: bool, mirror: bool = False, seqop: bool = False, disslw: bool = False):
        """Setup IOCON register.
        Биты  HAEN, ODR, INTPOL обнуляю всегда!"""
        val = (bank << 7) | (mirror << 6) | (seqop << 5) | (disslw << 4)
        if not self._bank and bank:		# переход из 0 -> 1 (плоская адресация -> раздельная адресация)
            self._write_reg(0x0A, value=val)
            self._write_reg(0x0B, value=val)
        if not bank and self._bank:		# переход из 1 -> 0 (раздельная адресация -> плоская адресация)
            self._write_reg(0x05, value=val)
            self._write_reg(0x15, value=val)
        self._bank = bank

    def _setup_interrupt(self):
        # запрещаю все, связанное с прерываниями!
        # Регистр GPINTEN управляет функцией прерывания при изменении для каждого вывода. Если бит установлен,
        # соответствующий вывод активируется для прерывания по изменению. Регистры DEFVAL и INTCON также должны быть
        # сконфигурированы, если на каких-либо выводах разрешено прерывание по изменению.
        pass

    def _read_reg(self, reg_addr: int, bytes_count: int = 1) -> bytes:
        """Считывает значение из регистра по адресу регистра 0..0x10. Смотри _get_reg_address"""
        return self.adapter.read_register(self.address, reg_addr, bytes_count)

    def _write_reg(self, reg_addr: int, value: int, bytes_count: int = 1):
        """Записывает в регистр с адресом reg_addr значение value по шине."""
        bo = self._get_byteorder_as_str()[0]
        self.adapter.write_register(self.address, reg_addr, value, bytes_count, bo)   # !!!

    def _setup(self):
        """Настройка портов на ввод/вывод. По умолчанию выводы P0..P7 настраиваются как ВХОДЫ!
        Если бит установлен в ноль, то происходит "подтяжка" вывода порта P0..P7 к земле через внутренний транзистор!
        Если бит установлен в единицу, вывод порта P0..P7 будет подтянут к питанию через источник тока в 100 uA!

        Поэтому:
            * если вы подключаете к выводу порта P0..P7 кнопку, то записывайте в соотв. бит ЕДИНИЦУ и потом ЧИТАЙТЕ
              состояние, а кнопку подключайте между выводом порта и ЗЕМЛЕЙ(VSS)!!!
            * если вы подключаете к выводу порта P0..P7 нагрузку, то подавать напряжение на нее нужно ЗАПИСЬЮ в
              соответствующий бит НУЛЯ, а нагрузку подключайте между +Питание(VDD) и выводом порта P0..P7!!!"""
        self.hex_mode = False

    def __call__(self):
        """Чтение состояния линий портов Pх0..Pх7"""
        return self.gpio

    def __iter__(self):
        return self

    def __next__(self) -> int:
        """Можно использовать как итератор (чтение в цикле for)"""
        return self.gpio
