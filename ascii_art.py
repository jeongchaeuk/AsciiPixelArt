import pygame as pg
import numpy as np
from numba import njit
import pygame.gfxdraw
import cv2


@njit(fastmath=True)
def accelerate_conversion(image, width, height, color_coeff, step):
    array_of_values = []
    for x in range(0, width, step):
        for y in range(0, height, step):
            r, g, b = image[x, y] // color_coeff
            if r + g + b:
                array_of_values.append(((r, g, b), (x, y)))
    return array_of_values


class ArtConvert:
    def __init__(self, path='video/test.mp4', font_size=12, color_lvl=8,
                 pixel_size=1):
        """
        :param path:
        :param font_size:
        :param color_lvl: This will determin the number of colors in the palette.
        choose values for it equal to numbers to the power of 2: 4, 8, 16, 32.
        The number of colors will be defined as (COLOR_LVL**3). 3 are RGB channel.
        e.g. with COLOR_LVL=4, the number of colors will be 4**3=64 (6bit),
        8: 512 (9 bit), 16: 4096 (12bit)
        """
        pg.init()
        self.path = path
        self.capture = cv2.VideoCapture(self.path)
        self.is_video = True
        self.PIXEL_SIZE = pixel_size
        self.COLOR_LVL = color_lvl
        self.cv2_image = None
        self.image, self.gray_image = self.get_image()
        self.WIDTH, self.HEIGHT = self.image.shape[0], self.image.shape[1]
        self.RES = self.WIDTH, self.HEIGHT
        self.surface = pg.display.set_mode(self.RES, vsync=1)
        self.clock = pg.time.Clock()

        if not self.PIXEL_SIZE:
            # self.ASCII_CHARS = ' .",:;!~+-xmo*#W&8@'  # black_white ascii
            self.ASCII_CHARS = ' ixzao*#MW&8%B@$'  # for color ascii.
            self.ASCII_COEFF = 255 // (len(self.ASCII_CHARS) - 1)
            self.font = pg.font.SysFont('Courier', font_size, bold=True)
            self.CHAR_STEP = int(font_size * .6)
            self.RENDERED_ASCII_CHARS = [self.font.render(char, False, 'white')
                                         for char in self.ASCII_CHARS]

        self.PALETTE, self.COLOR_COEFF = self.create_palette()

    def draw_converted_image(self):
        if self.PIXEL_SIZE:
            if self.is_video:
                self.image, _ = self.get_image()

            array_of_values = accelerate_conversion(self.image,
                                                    self.WIDTH, self.HEIGHT,
                                                    self.COLOR_COEFF,
                                                    self.PIXEL_SIZE)
            for color_key, (x, y) in array_of_values:
                color = tuple(self.PALETTE[color_key])
                pg.gfxdraw.box(
                        self.surface,
                        (x, y, self.PIXEL_SIZE, self.PIXEL_SIZE),
                        color)

        # color_indices = self.image // self.COLOR_COEFF
            # for x in range(0, self.WIDTH, self.PIXEL_SIZE):
            #     for y in range(0, self.HEIGHT, self.PIXEL_SIZE):
            #         color_key = tuple(color_indices[x, y])
            #         if not sum(color_key):
            #             continue
            #         color = tuple(self.PALETTE[color_key])
            #         pg.gfxdraw.box(
            #                 self.surface,
            #                 (x, y, self.PIXEL_SIZE, self.PIXEL_SIZE),
            #                 color)
        else:
            if self.is_video:
                self.image, self.gray_image = self.get_image()

            char_indices = self.gray_image // self.ASCII_COEFF
            color_indices = self.image // self.COLOR_COEFF
            for x in range(0, self.WIDTH, self.CHAR_STEP):
                for y in range(0, self.HEIGHT, self.CHAR_STEP):
                    char_index = char_indices[x, y]
                    if char_index:
                        char = self.ASCII_CHARS[char_index]
                        color = tuple(color_indices[x, y])
                        self.surface.blit(self.PALETTE[char][color], (x, y))

    def create_palette(self):
        """
        An example of the palette structure for one character '#' with
        COLOR_LVL=8: (each character will be rendered in 512 colors
        since 8**3==512, 3 are RGB channels.)

        palette = {
            '#': {
                (0, 0, 0): <Surface(7x14x8 SW)>, ..., (7, 7, 7): <Surface(7x14x8 SW)>
            }
        }

        :return:
        """
        colors, color_coeff = np.linspace(0, 255, num=self.COLOR_LVL,
                                          retstep=True, dtype=int)
        color_palette = [np.array([r, g, b])
                         for r in colors for g in colors for b in colors]
        if not self.PIXEL_SIZE:
            palette = dict.fromkeys(self.ASCII_CHARS, None)
        else:
            palette = {}
        color_coeff = int(color_coeff)

        if not self.PIXEL_SIZE:
            for char in palette:
                char_palette = {}
                for color in color_palette:
                    color_key = tuple(color // color_coeff)
                    char_palette[color_key] = (
                        self.font.render(char, False, tuple(color)))
                palette[char] = char_palette
        else:
            for color in color_palette:
                color_key = tuple(color // color_coeff)
                palette[color_key] = color

        return palette, color_coeff

    def get_image(self):
        if self.is_video:
            ret, self.cv2_image = self.capture.read()
            if not ret:
                exit()
        else:
            self.cv2_image = cv2.imread(self.path)  # numpy array
        transposed_image = cv2.transpose(self.cv2_image)
        image = cv2.cvtColor(transposed_image, cv2.COLOR_BGR2RGB)

        if self.PIXEL_SIZE:
            gray_image = None
        else:
            gray_image = cv2.cvtColor(transposed_image, cv2.COLOR_BGR2GRAY)

        return image, gray_image

    def draw_cv2_image(self):
        resized_cv2_image = cv2.resize(self.cv2_image, None, fx=0.5, fy=0.5,
                                       interpolation=cv2.INTER_AREA)
        cv2.imshow('opencv', resized_cv2_image)

    def draw(self):
        self.draw_cv2_image()
        self.surface.fill('black')
        self.draw_converted_image()

    def save(self):
        pygame_image = pg.surfarray.array3d(self.surface)
        cv2_img = cv2.transpose(pygame_image)
        cv2_img = cv2.cvtColor(cv2_img, cv2.COLOR_RGB2BGR)
        cv2.imwrite('output/img/converted_image.jpg', cv2_img)

    def run(self):
        while True:
            self.process_events()
            self.draw()
            pg.display.set_caption(
                    f'pygame fps={self.clock.get_fps():.2f} '
                    f'pixel_size={self.PIXEL_SIZE}')
            pg.display.flip()
            self.clock.tick()

    def process_events(self):
        for event in pg.event.get():
            match event.type:
                case pg.QUIT:
                    exit()
                case pg.KEYDOWN:
                    match event.key:
                        case pg.K_s:
                            self.save()
                        case pg.K_UP:
                            self.PIXEL_SIZE += 1
                            if self.PIXEL_SIZE > 20:
                                self.PIXEL_SIZE = 20
                        case pg.K_DOWN:
                            self.PIXEL_SIZE -= 1
                            if self.PIXEL_SIZE < 1:
                                self.PIXEL_SIZE = 1
                        case pg.K_ESCAPE:
                            exit()


if __name__ == '__main__':
    app = ArtConvert()
    app.run()
