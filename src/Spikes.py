import pygame

class Spikes():
    def __init__(self, x, y, w, h, image):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.image = image
        self.mask = pygame.mask.from_surface(self.image)
    
    def draw(self, win):
        win.blit(self.image, (self.x,self.y))

    def moveWithVelocity(self, x_vel, y_vel):
        self.x += x_vel
        self.y += y_vel

class SpikeArray():
    def __init__(self, y ,w, h, image, max_spikes, gap_index, gap_length=8):
        self.y = y
        self.w = w
        self.h = h
        self.image = image
        self.max_spikes = max_spikes
        self.gap_index = gap_index
        self.gap_length = gap_length
        self.array = []
        exclude = [i for i in range(self.gap_index, self.gap_index+self.gap_length)]
        for i in range(self.max_spikes):
            if i not in exclude:
                self.array.append(Spikes(i*self.w, self.y, self.w, self.h, self.image))
            else:
                self.array.append(None)

    def draw(self, win):
        for i in self.array:
            if i is not None:
                i.draw(win)
    
    def moveWithVelocity(self, x_vel, y_vel):
        self.y += y_vel
        for i in range(len(self.array)):
            if self.array[i] is not None:
                self.array[i].moveWithVelocity(x_vel, y_vel)

    def collision(self, object):
        for i in self.array:
            if i is not None:
                if i.collision(object):
                    return True