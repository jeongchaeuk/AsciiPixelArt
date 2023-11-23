import pygame as pg
import cv2


class ArtConvert:
    def __init__(self, path='img/car.jpg', font_size=12):
        pg.init()
        self.path = path
        self.cv2_image = None
        self.image = self.get_image()
        self.WIDTH, self.HEIGHT = self.image.shape[0], self.image.shape[1]
        self.RES = self.WIDTH, self.HEIGHT
        self.surface = pg.display.set_mode(self.RES, vsync=1)
        self.clock = pg.time.Clock()

        self.ASCII_CHARS = ' .",:;!~+-xmo*#W&8@'
        self.ASCII_COEFF = 255 // (len(self.ASCII_CHARS) - 1)
        self.font = pg.font.SysFont('d2coding', font_size, bold=True)
        self.CHAR_STEP = int(font_size * .6)
        self.RENDERED_ASCII_CHARS = [self.font.render(char, False, 'white')
                                     for char in self.ASCII_CHARS]
        for index, surf in enumerate(self.RENDERED_ASCII_CHARS):
            print(self.ASCII_CHARS[index], surf.get_size())

    def draw_converted_image(self):
        char_indices = self.image // self.ASCII_COEFF
        for x in range(0, self.WIDTH, self.CHAR_STEP):
            for y in range(0, self.HEIGHT, self.CHAR_STEP):
                char_index = char_indices[x, y]
                if char_index:
                    self.surface.blit(self.RENDERED_ASCII_CHARS[char_index],
                                      (x, y))


    def get_image(self):
        self.cv2_image = cv2.imread(self.path)  # numpy array
        transposed_image = cv2.transpose(self.cv2_image)
        gray_image = cv2.cvtColor(transposed_image, cv2.COLOR_BGR2GRAY)
        return gray_image

    def draw_cv2_image(self):
        resized_cv2_image = cv2.resize(self.cv2_image, None, fx=0.5, fy=0.5,
                                       interpolation=cv2.INTER_AREA)
        cv2.imshow('opencv', resized_cv2_image)

    def draw(self):
        self.draw_cv2_image()
        self.surface.fill('black')
        self.draw_converted_image()

    def run(self):
        while True:
            for e in pg.event.get():
                if e.type == pg.QUIT:
                    exit()

            self.draw()
            pg.display.set_caption(f'pygame fps={self.clock.get_fps():.2f}')
            pg.display.flip()
            self.clock.tick()


if __name__ == '__main__':
    app = ArtConvert()
    app.run()
