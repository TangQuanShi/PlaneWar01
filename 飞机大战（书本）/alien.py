import pygame
from pygame.sprite import Sprite
class Alien(Sprite):
    '''表示单个外星人'''
    def __init__(self,ai_game):
        super().__init__()
        self.screen = ai_game.screen
        self.settings = ai_game.settings
        self.image = pygame.image.load("images/enemy1.png")
        self.rect = self.image.get_rect()
        #每个外星人最初都在屏幕左上角附近
        self.rect.x = self.rect.width
        self.rect.y = self.rect.height
    def update(self):
        '''向右或向左 移动外星人'''
        self.x += (self.settings.alien_speed * self.settings.fleet_direction)
        self.rect.x = self.x
    def check_edges(self):
        '''如果外星人位于屏幕边缘，就返回True'''
        screen_rect = self.screen.get_rect()
        if self.rect.right >= screen_rect.right or self.rect.left <= screen_rect.left:
            return True
