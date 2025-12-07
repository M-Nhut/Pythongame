import pygame

class SpriteSheet:
    def __init__(self, filename):
        self.sheet = pygame.image.load(filename).convert_alpha()

    def get_animation(self, x_start, y, frame_width, frame_height, frame_count, scale=None):
        frames = []
        for i in range(frame_count):
            frame = self.sheet.subsurface(pygame.Rect(
                x_start + i * frame_width, y, frame_width, frame_height
            ))
            if scale:
                frame = pygame.transform.scale(frame, scale)
            frames.append(frame)
        return frames