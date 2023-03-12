import  sys
from time import sleep
import  pygame

from settings import Settings
from ship import Ship
from bullet import Bullet
from alien import Alien
from  game_stats import GameStats
from  button import Button
from  scoreboard import Scoreboard

class AlienInvasion:
    '''管理游戏资源和行为的类'''

    def __init__(self):
        '''初始化游戏并创建优秀资源'''
        pygame.init()
        self.settings = Settings()
        self.screen = pygame.display.set_mode((self.settings.screen_width,self.settings.screen_height))
        #pygame.display.set_caption("Alien Invasion")
        self.stats = GameStats(self)
        self.sb = Scoreboard(self)
        self.ship = Ship(self)
        self.bullets =pygame.sprite.Group()
        self.aliens = pygame.sprite.Group()
        self._create_fleet()
        self.play_button = Button(self,"play")

    def run_game(self):
        '''开始游戏的主循环'''
        while True:
            # 监视键盘和鼠标
            self._check_events()
            if self.stats.game_active:
                self.ship.update()
                self.bullets.update()
                self._update_aliens()
            self._update_screen()
    def _check_events(self):
        '''响应按键和鼠标事件'''
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                self._check_keydown_events(event)
            elif event.type == pygame.KEYUP:
                self._check_keyup_events(event)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                self._check_play_button(mouse_pos)
    def _check_play_button(self,mouse_pos):
        """在玩家单击play按钮时开始新游戏"""
        button_clicked = self.play_button.rect.collidepoint(mouse_pos)
        if button_clicked and not self.stats.game_active:
            #重置游戏设置
            self.settings.initialize_dynamic_settings()
            #重置游戏统计信息
            self.stats.game_active = True
            self.sb.prep_score()
            self.sb.prep_level()
            self.sb.prep_ships()
            #情况余下的外星人
            self.aliens.empty()
            self.bullets.empty()
            #创建一群外星人和子弹
            self._create_fleet()
            self.ship.center_ship()
            pygame.mouse.set_visible(False)

    def _check_keydown_events(self,event):
        if event.key == pygame.K_RIGHT:
            self.ship.moving_right = True
        elif event.key == pygame.K_LEFT:
            self.ship.moving_left = True
        elif event.key == pygame.K_q:
            sys.exit()
        elif event.key == pygame.K_SPACE:
            self._fire_bullet()
    def _check_keyup_events(self,event):
        if event.key == pygame.K_RIGHT:
            self.ship.moving_right = False
        elif event.key == pygame.K_LEFT:
            self.ship.moving_left = False
    def _create_fleet(self):
        '''创建外星人群'''
        alien = Alien(self)
        alien_width,alien_height= alien.rect.size
        available_space_x = self.settings.screen_width - (2 * alien_width) #可容下屏幕宽
        number_aliens_x = available_space_x // (2 * alien_width) #可容下的敌机数
        #计算屏幕可容纳多少行外星人
        ship_height = self.ship.rect.height
        available_space_y = (self.settings.screen_height - (3*alien_height) - ship_height)
        numbers_rows = available_space_y // (2 * alien_height)
        for row_number in range(numbers_rows):
            for alien_number in range(number_aliens_x):
                self._create_alien(alien_number,row_number)
    def _create_alien(self,alien_number,row_number):
        alien = Alien(self)
        alien_width,alien_height= alien.rect.size  # 间距
        alien.x = alien_width + 2 * alien_width * alien_number
        alien.rect.x = alien.x
        alien.rect.y = alien.rect.height + 2*alien.rect.height * row_number
        self.aliens.add(alien)
    def _update_aliens(self):
        '''更新外星人群中所有外星人的位置'''
        self._check_fleet_edges()
        self.aliens.update()
        #检测外星人和飞机碰撞
        if pygame.sprite.spritecollideany(self.ship,self.aliens):
            self._ship_hit()
        #检查是否有外星人到达了屏幕低端
        self._check_aliens_bottom()
    def _update_screen(self):
        self.screen.fill(self.settings.bg_color)
        self.ship.blitme()
        self._update_bullets()
        self.aliens.draw(self.screen)
        self.sb.show_score()#显示得分
        #如果游戏处于非活动状态，就绘制Play按钮
        if not self.stats.game_active:
            self.play_button.draw_button()
        # 让最近绘制的屏幕可见
        pygame.display.flip()
    def _update_bullets(self):
        for bullet in self.bullets.sprites():
            bullet.draw_bullet()
        self._check_bullet_alien_collisions()
    def _check_bullet_alien_collisions(self):
        """响应子弹和外星人碰撞"""
        collisions = pygame.sprite.groupcollide(self.bullets, self.aliens, True, True)
        if collisions:
            for alien in collisions.values():
                self.stats.score += self.settings.alien_points
                self.sb.prep_score()
                self.sb.check_high_score()
        if not self.aliens:
        #删除所有子弹并创建一群外星人
            self.bullets.empty()
            self._create_fleet()
            self.settings.increase_speed()
            #提高等级
            self.stats.level += 1
            self.sb.prep_level()

    def _ship_hit(self):
        """响应飞船被外星人撞到"""
        if self.stats.ship_left > 0:
            #将ship_left减1
            self.stats.ship_left -= 1
            self.sb.prep_ships()
            #清空余下的外星人和子弹
            self.aliens.empty()
            self.bullets.empty()
            #创建一群新的外星人，并将飞船放到屏幕的中央
            self._create_fleet()
            self.ship.center_ship()
            #暂停
            sleep(0.5)
        else:
            self.stats.game_active = False
            pygame.mouse.set_visible(True)
    def _fire_bullet(self):
        '''创建一颗子弹并将其加入编组bullets中'''
        if len(self.bullets) < self.settings.bullets_allowed:
            new_bullet = Bullet(self)
            self.bullets.add(new_bullet)
    def _check_fleet_edges(self):
        """有外星人到达边界采取相应的措施"""
        for alien in self.aliens.sprites():
            if alien.check_edges():
                self._change_fleet_direction()
                break
    def _change_fleet_direction(self):
        """将整群的外星人下移，并改变它们的方向"""
        for alien in self.aliens.sprites():
            alien.rect.y += self.settings.fleet_drop_speed
        self.settings.fleet_direction *= -1
    def _check_aliens_bottom(self):
        """检查是否有外星人到达了屏幕低端"""
        screen_rect = self.screen.get_rect()
        for alien in self.aliens.sprites():
            if alien.rect.bottom >= screen_rect.bottom:
                #像飞船被撞到一样处理
                self._ship_hit()
                break


if __name__ == '__main__':
    #创建游戏实例并运行游戏
    ai = AlienInvasion()
    ai.run_game()
