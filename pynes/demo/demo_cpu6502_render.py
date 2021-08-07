import pathlib
import pygame as pg
from enum import Enum

from pynes.core.bus import Bus
from pynes.core.cpu6502 import Cpu6502
from pynes.core.cpu6502_utils import FLAGS
from pynes.core.ram import Ram


class Colors(Enum):
    BLACK = (0x36, 0x36, 0x36)
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

    def setup(self, width: int = DEFAULT_WIDTH, height: int = DEFAULT_HEIGHT, fps: int = DEFAULT_FPS) -> None:
        self.width = width
        self.height = height
        self.fps = fps

    def run(self) -> None:
        # init
        pg.init()
        pg.font.init()
        clock = pg.time.Clock()
        screen = pg.display.set_mode((self.width, self.height))
        pg.display.set_caption("DemoCpu6502Render")
        font = pg.font.Font(pathlib.Path(__file__).parent / '..' / 'resources' / 'fonts' / 'visitor1.ttf', 15)

        # main
        running = True
        while running:
            # some control stuff
            clock.tick(self.fps)
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    running = False

            # background
            screen.fill(Colors.BLACK.value)
            # draw info
            self.render_status(screen, font)
            self.render_pc(screen, font)
            self.render_a(screen, font)
            self.render_x(screen, font)
            self.render_y(screen, font)
            self.render_sp(screen, font)

            # upd screen
            pg.display.flip()

        pg.font.quit()
        pg.quit()

    def render_ram(self, screen: pg.display, font: pg.font.Font) -> None:
        pass

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
        screen.blit(status_label, (self.width - 200, 10))
        for i, l in enumerate(flag_labels):
            screen.blit(l, (self.width - 135 + 15 * i, 10))

    def render_pc(self, screen: pg.display, font: pg.font.Font) -> None:
        pc_text = '$' + hex(self.bus.get_cpu6502().pc.value)[2:].zfill(4)
        pc_label = font.render(f"pc:     {pc_text}", False, Colors.WHITE.value)
        screen.blit(pc_label, (self.width - 200, 25))

    def render_a(self, screen: pg.display, font: pg.font.Font) -> None:
        a_text = '$' + hex(self.bus.get_cpu6502().a.value)[2:].zfill(2)
        a_label = font.render(f"a:      {a_text}", False, Colors.WHITE.value)
        screen.blit(a_label, (self.width - 200, 40))

    def render_x(self, screen: pg.display, font: pg.font.Font) -> None:
        x_text = '$' + hex(self.bus.get_cpu6502().x.value)[2:].zfill(2)
        x_label = font.render(f"x:      {x_text}", False, Colors.WHITE.value)
        screen.blit(x_label, (self.width - 200, 55))

    def render_y(self, screen: pg.display, font: pg.font.Font) -> None:
        y_text = '$' + hex(self.bus.get_cpu6502().y.value)[2:].zfill(2)
        y_label = font.render(f"y:      {y_text}", False, Colors.WHITE.value)
        screen.blit(y_label, (self.width - 200, 70))

    def render_sp(self, screen: pg.display, font: pg.font.Font) -> None:
        sp_text = '$' + hex(self.bus.get_cpu6502().sp.value)[2:].zfill(2)
        sp_label = font.render(f"sp:     {sp_text}", False, Colors.WHITE.value)
        screen.blit(sp_label, (self.width - 200, 85))

    @staticmethod
    def get_prepared_bus() -> Bus:
        bus = Bus()
        Cpu6502().connect_to_bus(bus)
        Ram().connect_to_bus(bus)
        return bus
