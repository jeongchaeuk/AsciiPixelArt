import pygame as pg
import numpy as np
import cv2


class ArtConvert:
    def __init__(self, path='img/car.jpg', font_size=12, color_lvl=8):
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
        self.COLOR_LVL = color_lvl
        self.cv2_image = None
        self.image, self.gray_image = self.get_image()
        self.WIDTH, self.HEIGHT = self.image.shape[0], self.image.shape[1]
        self.RES = self.WIDTH, self.HEIGHT
        self.surface = pg.display.set_mode(self.RES, vsync=1)
        self.clock = pg.time.Clock()

        # self.ASCII_CHARS = ' .",:;!~+-xmo*#W&8@'
        self.ASCII_CHARS = ' ixzao*#MW&8%B@$'  # for color ascii.
        self.ASCII_COEFF = 255 // (len(self.ASCII_CHARS) - 1)
        self.font = pg.font.SysFont('Courier', font_size, bold=True)
        self.CHAR_STEP = int(font_size * .6)
        self.RENDERED_ASCII_CHARS = [self.font.render(char, False, 'white')
                                     for char in self.ASCII_CHARS]
        self.PALETTE, self.COLOR_COEFF = self.create_palette()

    def draw_converted_image(self):
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
        palette = dict.fromkeys(self.ASCII_CHARS, None)
        color_coeff = int(color_coeff)

        for char in palette:
            char_palette = {}
            for color in color_palette:
                color_key = tuple(color // color_coeff)
                char_palette[color_key] = (
                    self.font.render(char, False, tuple(color)))
            palette[char] = char_palette
        return palette, color_coeff

    def get_image(self):
        self.cv2_image = cv2.imread(self.path)  # numpy array
        transposed_image = cv2.transpose(self.cv2_image)
        image = cv2.cvtColor(transposed_image, cv2.COLOR_BGR2RGB)
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
            pg.display.set_caption(f'pygame fps={self.clock.get_fps():.2f}')
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
                        case pg.K_ESCAPE:
                            exit()


if __name__ == '__main__':
    app = ArtConvert()
    app.create_palette()
    app.run()
