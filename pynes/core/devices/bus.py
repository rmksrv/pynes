from ctypes import c_uint16

from pynes.core.devices import AbstractMemoryDevice
from pynes.core.exceptions import NoSuchDeviceException


class Bus:

    def __init__(self):
        self.devices = {}

    def register_device(self, device) -> None:
        self.devices.update({type(device).__name__: device})

    def get_ram(self):
        device_name = 'Ram'
        ram = self.devices.get(device_name)
        if not ram:
            raise NoSuchDeviceException(device_name)
        return ram

    def get_cartridge(self):
        device_name = 'Cartridge'
        cartridge = self.devices.get(device_name)
        if not cartridge:
            raise NoSuchDeviceException(device_name)
        return cartridge

    def get_cpu6502(self):
        device_name = 'Cpu6502'
        cpu = self.devices.get(device_name)
        if not cpu:
            raise NoSuchDeviceException(device_name)
        return cpu

    def address_owner(self, address: c_uint16) -> AbstractMemoryDevice:
        memory_devices = filter(lambda d: d.__class__ in AbstractMemoryDevice.__subclasses__(), self.devices.values())
        for device_instance in memory_devices:
            if device_instance.is_address_valid(address):
                return device_instance
        else:
            raise NoSuchDeviceException(f'with address {hex(address.value)}')

    def __repr__(self) -> str:
        return "Bus({i}) {d}".format(i=id(self),
                                     d=self.devices)
