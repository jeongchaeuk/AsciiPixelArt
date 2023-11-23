import pygame as pg
import cv2


class ArtConvert:
    def __init__(self, path='img/car.jpg'):
        pg.init()
        self.path = path
        self.cv2_image = None
        self.image = self.get_image()
        self.WIDTH, self.HEIGHT = self.image.shape[0], self.image.shape[1]
        self.RES = self.WIDTH, self.HEIGHT
        self.surface = pg.display.set_mode(self.RES, vsync=1)
        self.clock = pg.time.Clock()

    def get_image(self):
        self.cv2_image = cv2.imread(self.path)  # numpy array
        transposed_image = cv2.transpose(self.cv2_image)
        rgb_image = cv2.cvtColor(transposed_image, cv2.COLOR_RGB2BGR)
        return rgb_image

    def draw_cv2_image(self):
        resized_cv2_image = cv2.resize(self.cv2_image, None, fx=0.5, fy=0.5,
                                       interpolation=cv2.INTER_AREA)
        cv2.imshow('opencv', resized_cv2_image)

    def draw(self):
        pg.surfarray.blit_array(self.surface, self.image)
        self.draw_cv2_image()

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
