import os
import pathlib
from ctypes import c_uint16
from enum import Enum
from typing import Tuple, Union

import pygame as pg

from pynes.core.devices import Bus, Cpu6502, Ppu2C02, Ram, Cartridge, Apu
from pynes.core.devices.cpu.utils import FLAGS


class Colors(Enum):
    BLACK = (0x20, 0x20, 0x20)
    WHITE = (0xb6, 0xb6, 0xb6)
    RED   = (0xff, 0x08, 0x83)
    GREEN = (0x83, 0xff, 0x08)
    BLUE  = (0x08, 0x83, 0xff)


class DemoCpu6502Render:
    DEFAULT_WIDTH:  int = 640
    DEFAULT_HEIGHT: int = 480
    DEFAULT_FPS:    int = 60

    def __init__(self):
        self.width = DemoCpu6502Render.DEFAULT_WIDTH
        self.height = DemoCpu6502Render.DEFAULT_HEIGHT
        self.fps = DemoCpu6502Render.DEFAULT_FPS

        self.bus = self.get_prepared_bus()
        self.bus.get_cpu6502().reset()
        self.bus.get_cpu6502().pc.value = Cartridge.min_address

    def setup(self, width: int = DEFAULT_WIDTH, height: int = DEFAULT_HEIGHT, fps: int = DEFAULT_FPS) -> None:
        self.width = width
        self.height = height
        self.fps = fps

    def load_rom(self, rom: Union[str, bytes, os.PathLike], start: int = Cartridge.min_address) -> None:
        self.bus.get_cartridge().load_rom(rom, start)

    def run(self) -> None:
        # init
        pg.init()
        pg.font.init()
        clock = pg.time.Clock()
        screen = pg.display.set_mode((self.width, self.height))
        pg.display.set_caption("DemoCpu6502Render")
        font = pg.font.Font(pathlib.Path(__file__).parent / '..' / 'resources' / 'fonts' / 'joystix_monospace.ttf', 10)

        # main
        while self.event_iter():
            # some control stuff
            clock.tick(self.fps)

            # drawing
            screen.fill(Colors.BLACK.value)
            self.render_memory(screen, font)
            self.render_disassembled_code(screen, font)
            self.render_status(screen, font)
            self.render_pc(screen, font)
            self.render_a(screen, font)
            self.render_x(screen, font)
            self.render_y(screen, font)
            self.render_sp(screen, font)
            self.render_info(screen, font)

            # upd screen
            pg.display.flip()

        pg.font.quit()
        pg.quit()

    def event_iter(self) -> bool:
        running = True
        for event in pg.event.get():
            if event.type == pg.QUIT:
                running = False
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_SPACE:
                    self.bus.get_cpu6502().clock()
                    while not self.bus.get_cpu6502().complete():
                        self.bus.get_cpu6502().clock()
                elif event.key == pg.K_r:
                    self.bus.get_cpu6502().reset()
                    self.bus.get_cpu6502().pc.value = Cartridge.min_address
                elif event.key == pg.K_i:
                    self.bus.get_cpu6502().irq()
                elif event.key == pg.K_n:
                    self.bus.get_cpu6502().nmi()
                elif event.key == pg.K_q:
                    running = False
        return running

    def render_memory(self, screen: pg.display, font: pg.font.Font) -> None:

        def render_memory_page(_page_num: int, _pos: Tuple[int, int]) -> None:
            _lo = _page_num * 0x100
            _hi = (_page_num + 1) * 0x100
            _step = 0x10
            for _i, _addr_row in enumerate(range(_lo, _hi, _step)):
                line = '$' + hex(_addr_row)[2:].zfill(4) + ': '
                if self.bus.get_cpu6502().pc.value in range(_addr_row, _addr_row + _step):
                    color = Colors.BLUE.value
                else:
                    color = Colors.WHITE.value
                addr_label = font.render(line, False, color)
                screen.blit(addr_label, (_pos[0], _pos[1] + _i * 15))

                for _j, _addr in enumerate(range(_addr_row, _addr_row + _step)):
                    cell = self.bus.get_cpu6502().read(c_uint16(_addr))
                    cell_text = hex(cell.value)[2:].zfill(2) + ' '
                    # TODO: now only first uint16 is highlighting with no args -- fix it (when refactor addr modes)
                    color = Colors.BLUE.value if _addr == self.bus.get_cpu6502().pc.value else Colors.WHITE.value
                    cell_label = font.render(cell_text, False, color)
                    _x = _pos[0] + 50 + 25 * (_j + 1)
                    _y = _pos[1] + _i * 15
                    screen.blit(cell_label, (_x, _y))

        add_page_num = (self.bus.get_cpu6502().pc.value & 0xff00) >> 8
        for i, page_num in enumerate([0, add_page_num]):
            render_memory_page(page_num, (10, 10 + i * 260))

    def render_disassembled_code(self, screen: pg.display, font: pg.font.Font) -> None:
        pc = self.bus.get_cpu6502().pc.value
        lo = max(pc - 30, 0x0000)
        hi = min(pc + 30, 0xffff)
        instructions = self.bus.get_cpu6502().disassemble(lo, hi)
        curr_ins_index = list(instructions).index(pc)
        view_rng_lo = max(curr_ins_index - 10, 0x0000)
        view_rng_hi = min(curr_ins_index + 10, 0xffff)
        viewing_ins = list(instructions.items())[view_rng_lo:view_rng_hi]
        for i, (addr, line) in enumerate(viewing_ins):
            color = Colors.BLUE.value if addr == pc else Colors.WHITE.value
            ins_label = font.render(line, False, color)
            screen.blit(ins_label, (self.width - 280, 110 + 15 * i))

    def render_status(self, screen: pg.display, font: pg.font.Font) -> None:
        # preparing
        status_label = font.render("status: ", False, Colors.WHITE.value)
        flag_labels = list()
        for fname in reversed(FLAGS):
            if fname == 'u':
                fname = '-'
                color = Colors.GREEN
            else:
                flag = self.bus.get_cpu6502().get_flag(fname)
                color = Colors.GREEN if flag else Colors.RED
            flag_labels.append(font.render(fname, False, color.value))
        # positioning
        screen.blit(status_label, (self.width - 280, 10))
        for i, l in enumerate(flag_labels):
            screen.blit(l, (self.width - 215 + 15 * i, 10))

    def render_pc(self, screen: pg.display, font: pg.font.Font) -> None:
        pc_text = '$' + hex(self.bus.get_cpu6502().pc.value)[2:].zfill(4)
        pc_label = font.render(f"pc:     {pc_text}", False, Colors.WHITE.value)
        screen.blit(pc_label, (self.width - 280, 25))

    def render_a(self, screen: pg.display, font: pg.font.Font) -> None:
        a_val = self.bus.get_cpu6502().a.value
        a_text = '$' + hex(a_val)[2:].zfill(2) + '  [' + str(a_val) + ']'
        a_label = font.render(f"a:      {a_text}", False, Colors.WHITE.value)
        screen.blit(a_label, (self.width - 280, 40))

    def render_x(self, screen: pg.display, font: pg.font.Font) -> None:
        x_val = self.bus.get_cpu6502().x.value
        x_text = '$' + hex(x_val)[2:].zfill(2) + '  [' + str(x_val) + ']'
        x_label = font.render(f"x:      {x_text}", False, Colors.WHITE.value)
        screen.blit(x_label, (self.width - 280, 55))

    def render_y(self, screen: pg.display, font: pg.font.Font) -> None:
        y_val = self.bus.get_cpu6502().y.value
        y_text = '$' + hex(y_val)[2:].zfill(2) + '  [' + str(y_val) + ']'
        y_label = font.render(f"y:      {y_text}", False, Colors.WHITE.value)
        screen.blit(y_label, (self.width - 280, 70))

    def render_sp(self, screen: pg.display, font: pg.font.Font) -> None:
        sp_text = '$' + hex(self.bus.get_cpu6502().sp.value)[2:].zfill(2)
        sp_label = font.render(f"sp:     {sp_text}", False, Colors.WHITE.value)
        screen.blit(sp_label, (self.width - 280, 85))

    def render_info(self, screen: pg.display, font: pg.font.Font) -> None:
        info_label = font.render("SPACE = Step Instruction    R = RESET    "
                                 "I = IRQ    N = NMI", False, Colors.WHITE.value)
        q_label = font.render("Q = Quit", False, Colors.RED.value)
        screen.blit(info_label, (10, 550))
        screen.blit(q_label, (self.width - 75, 550))

    @staticmethod
    def get_prepared_bus() -> Bus:
        bus = Bus()
        Cpu6502().connect_to_bus(bus)
        Ppu2C02().connect_to_bus(bus)
        Ram().connect_to_bus(bus)
        Cartridge().connect_to_bus(bus)
        Apu().connect_to_bus(bus)
        bus.get_cartridge().connect_to_bus(bus.get_ppu2C02().internal_bus)
        return bus
