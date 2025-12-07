class Animation:
    def __init__(self, frames, loop=True):
        self.frames = frames
        self.current = 0
        self.loop = loop
        self.done = False

    def update(self):
        if self.done: return
        self.current += 0.15
        if self.current >= len(self.frames):
            if self.loop:
                self.current = 0
            else:
                self.current = len(self.frames) - 1
                self.done = True

    def get_image(self):
        return self.frames[int(self.current)]