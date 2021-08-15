class Bus:

    def __init__(self):
        self.devices = {}

    def register_device(self, device) -> None:
        self.devices.update({type(device).__name__: device})

    def get_ram(self):
        return self.devices.get('AbstractMemoryDevice')

    def get_cpu6502(self):
        return self.devices.get('Cpu6502')

    def __repr__(self) -> str:
        return "Bus({i}) {d}".format(i=id(self),
                                     d=self.devices)
