from abc import ABC


class AbstractDevice(ABC):

    def __init__(self):
        self.bus = None

    def connect_to_bus(self, bus) -> None:
        self.bus = bus
        self.bus.register_device(self)
