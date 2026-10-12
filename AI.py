import pygame
import math
import sys

# --- INITIALISIERUNG & KONFIGURATION ---
pygame.init()
WIDTH, HEIGHT = 900, 650

# Double-Buffering verhindert schwarze Bildelemente unter Python 3.13
SCREEN = pygame.display.set_mode((WIDTH, HEIGHT), pygame.DOUBLEBUF)
pygame.display.set_caption("Tower Defense Game")
CLOCK = pygame.time.Clock()
FPS = 60

# Farben
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (34, 139, 34)
GRAY = (100, 100, 100)
LIGHT_GRAY = (200, 200, 200)
RED = (220, 20, 60)
BLUE = (30, 144, 255)
YELLOW = (255, 215, 0)
PURPLE = (138, 43, 226)
DARK_RED = (139, 0, 0)

# Standard Pygame-Fonts (Kompatibel mit Python 3.13)
FONT = pygame.font.Font(None, 22)
BIG_FONT = pygame.font.Font(None, 48)

# Pfadpunkte für die Gegner
WAYPOINTS = [(0, 300), (200, 300), (200, 150), (450, 150), (450, 450), (700, 450), (700, 300)]
BASE_POS = WAYPOINTS[-1]

# --- KLASSEN ---

class Base:
    def __init__(self, pos):
        self.pos = pos
        self.lives = 3

    def draw(self, surface):
        pygame.draw.circle(surface, DARK_RED, self.pos, 25)
        text = FONT.render(f"Base ({self.lives} HP)", True, WHITE)
        surface.blit(text, (self.pos[0] - 35, self.pos[1] - 8))


class Enemy:
    def __init__(self, wave_num):
        self.x, self.y = WAYPOINTS[0]
        self.target_waypoint_idx = 1
        self.max_health = 80 + (wave_num * 35)
        self.health = self.max_health
        self.speed = 1.2 + (wave_num * 0.05)
        self.reward = 15 + wave_num * 3
        self.radius = 12

    def move(self, base):
        if self.target_waypoint_idx < len(WAYPOINTS):
            target_x, target_y = WAYPOINTS[self.target_waypoint_idx]
            dx, dy = target_x - self.x, target_y - self.y
            dist = math.hypot(dx, dy)

            if dist < self.speed:
                self.x, self.y = target_x, target_y
                self.target_waypoint_idx += 1
            else:
                self.x += (dx / dist) * self.speed
                self.y += (dy / dist) * self.speed
        else:
            base.lives -= 1
            return True
        return False

    def draw(self, surface):
        pygame.draw.circle(surface, RED, (int(self.x), int(self.y)), self.radius)
        health_ratio = max(0, self.health / self.max_health)
        bar_w = 24
        bar_h = 4
        pygame.draw.rect(surface, BLACK, (self.x - bar_w/2, self.y - 18, bar_w, bar_h))
        pygame.draw.rect(surface, GREEN, (self.x - bar_w/2, self.y - 18, bar_w * health_ratio, bar_h))


class Tower:
    TYPES = {
        "Standard": {"cost": 100, "range": 120, "damage": 25, "cooldown": 30, "color": BLUE},
        "Sniper":   {"cost": 175, "range": 220, "damage": 70, "cooldown": 75, "color": PURPLE},
        "Rapid":    {"cost": 150, "range": 90,  "damage": 12, "cooldown": 10, "color": YELLOW},
        "Splash":   {"cost": 200, "range": 110, "damage": 35, "cooldown": 50, "color": DARK_RED}
    }

    def __init__(self, x, y, tower_type):
        self.x = x
        self.y = y
        self.type = tower_type
        stats = self.TYPES[tower_type]
        self.color = stats["color"]
        self.cost = stats["cost"]
        
        self.level = 1
        self.range = stats["range"]
        self.damage = stats["damage"]
        self.cooldown_max = stats["cooldown"]
        self.cooldown = 0
        self.upgrade_cost = int(self.cost * 0.8)

    def upgrade(self):
        self.level += 1
        self.damage = int(self.damage * 1.4)
        self.range += 15
        if self.cooldown_max > 5:
            self.cooldown_max = max(5, int(self.cooldown_max * 0.85))
        self.upgrade_cost = int(self.upgrade_cost * 1.5)

    def update(self, enemies, projectiles):
        if self.cooldown > 0:
            self.cooldown -= 1
            return

        target = None
        for enemy in enemies:
            dist = math.hypot(enemy.x - self.x, enemy.y - self.y)
            if dist <= self.range:
                target = enemy
                break

        if target:
            is_splash = (self.type == "Splash")
            projectiles.append(Projectile(self.x, self.y, target, self.damage, is_splash))
            self.cooldown = self.cooldown_max

    def draw(self, surface, selected=False):
        pygame.draw.circle(surface, self.color, (self.x, self.y), 16)
        lvl_text = FONT.render(f"L{self.level}", True, WHITE)
        surface.blit(lvl_text, (self.x - 6, self.y - 6))

        if selected:
            pygame.draw.circle(surface, WHITE, (self.x, self.y), self.range, 1)


class Projectile:
    def __init__(self, x, y, target, damage, is_splash=False):
        self.x = x
        self.y = y
        self.target = target
        self.damage = damage
        self.speed = 8
        self.is_splash = is_splash
        self.hit = False

    def move(self, enemies):
        if not self.target or self.target.health <= 0:
            self.hit = True
            return

        dx = self.target.x - self.x
        dy = self.target.y - self.y
        dist = math.hypot(dx, dy)

        if dist < self.speed:
            self.hit = True
            if self.is_splash:
                for enemy in enemies:
                    if math.hypot(enemy.x - self.target.x, enemy.y - self.target.y) <= 60:
                        enemy.health -= self.damage
            else:
                self.target.health -= self.damage
        else:
            self.x += (dx / dist) * self.speed
            self.y += (dy / dist) * self.speed

    def draw(self, surface):
        pygame.draw.circle(surface, BLACK, (int(self.x), int(self.y)), 4)


# --- GAME MANAGEMENT ---

class Game:
    def __init__(self):
        self.money = 350
        self.wave = 1
        self.max_waves = 20
        self.base = Base(BASE_POS)
        
        self.enemies = []
        self.towers = []
        self.projectiles = []

        self.selected_tower_type = "Standard"
        self.selected_placed_tower = None

        self.spawn_queue = 0
        self.spawn_cooldown = 0
        self.wave_in_progress = False

    def start_next_wave(self):
        if not self.wave_in_progress and self.wave <= self.max_waves:
            self.spawn_queue = 8 + (self.wave * 3)
            self.wave_in_progress = True

    def spawn_enemy(self):
        if self.spawn_queue > 0 and self.spawn_cooldown <= 0:
            self.enemies.append(Enemy(self.wave))
            self.spawn_queue -= 1
            self.spawn_cooldown = 40
        elif self.spawn_cooldown > 0:
            self.spawn_cooldown -= 1

    def update(self):
        if self.base.lives <= 0:
            return

        if self.wave_in_progress:
            self.spawn_enemy()
            if self.spawn_queue == 0 and len(self.enemies) == 0:
                self.wave_in_progress = False
                self.money += 100 + (self.wave * 20)
                self.wave += 1

        for enemy in self.enemies[:]:
            reached_base = enemy.move(self.base)
            if reached_base:
                self.enemies.remove(enemy)
            elif enemy.health <= 0:
                self.money += enemy.reward
                self.enemies.remove(enemy)

        for tower in self.towers:
            tower.update(self.enemies, self.projectiles)

        for proj in self.projectiles[:]:
            proj.move(self.enemies)
            if proj.hit:
                self.projectiles.remove(proj)

    def draw_ui(self, surface):
        ui_rect = pygame.Rect(750, 0, 150, HEIGHT)
        pygame.draw.rect(surface, LIGHT_GRAY, ui_rect)
        pygame.draw.line(surface, BLACK, (750, 0), (750, HEIGHT), 2)

        info_y = 10
        surface.blit(FONT.render(f"Geld: ${self.money}", True, BLACK), (760, info_y))
        surface.blit(FONT.render(f"Welle: {min(self.wave, self.max_waves)}/{self.max_waves}", True, BLACK), (760, info_y + 25))

        y_offset = 80
        surface.blit(FONT.render("Turm Bauen:", True, BLACK), (760, y_offset))
        y_offset += 20

        for t_name, data in Tower.TYPES.items():
            btn_rect = pygame.Rect(755, y_offset, 140, 35)
            is_selected = (self.selected_tower_type == t_name)
            color = data["color"] if not is_selected else GREEN
            
            pygame.draw.rect(surface, color, btn_rect)
            pygame.draw.rect(surface, BLACK, btn_rect, 2)

            txt_color = WHITE if color != YELLOW else BLACK
            txt = FONT.render(f"{t_name} (${data['cost']})", True, txt_color)
            surface.blit(txt, (760, y_offset + 8))

            y_offset += 42

        btn_wave = pygame.Rect(755, 300, 140, 40)
        btn_color = GRAY if self.wave_in_progress else GREEN
        pygame.draw.rect(surface, btn_color, btn_wave)
        pygame.draw.rect(surface, BLACK, btn_wave, 2)
        txt = FONT.render("Start Welle", True, WHITE)
        surface.blit(txt, (785, 312))

        if self.selected_placed_tower:
            t = self.selected_placed_tower
            y = 380
            pygame.draw.line(surface, BLACK, (750, y - 10), (900, y - 10), 2)
            surface.blit(FONT.render(f"{t.type} (Lvl {t.level})", True, BLACK), (760, y))
            surface.blit(FONT.render(f"Dmg:{t.damage} Rng:{t.range}", True, BLACK), (760, y + 20))
            
            upg_btn = pygame.Rect(755, y + 50, 140, 35)
            can_afford = self.money >= t.upgrade_cost
            pygame.draw.rect(surface, BLUE if can_afford else GRAY, upg_btn)
            pygame.draw.rect(surface, BLACK, upg_btn, 2)
            
            txt_upg = FONT.render(f"Upgrade (${t.upgrade_cost})", True, WHITE)
            surface.blit(txt_upg, (760, y + 58))

    def draw(self, surface):
        surface.fill(GREEN)

        pygame.draw.lines(surface, GRAY, False, WAYPOINTS, 40)

        self.base.draw(surface)

        for enemy in self.enemies:
            enemy.draw(surface)

        for tower in self.towers:
            tower.draw(surface, selected=(tower == self.selected_placed_tower))

        for proj in self.projectiles:
            proj.draw(surface)

        self.draw_ui(surface)

        if self.base.lives <= 0:
            txt = BIG_FONT.render("GAME OVER", True, RED)
            surface.blit(txt, (WIDTH // 2 - 120, HEIGHT // 2 - 20))
        elif self.wave > self.max_waves and len(self.enemies) == 0:
            txt = BIG_FONT.render("VICTORY!", True, BLUE)
            surface.blit(txt, (WIDTH // 2 - 100, HEIGHT // 2 - 20))

    def handle_click(self, pos):
        x, y = pos

        if x < 750:
            for tower in self.towers:
                if math.hypot(tower.x - x, tower.y - y) <= 20:
                    self.selected_placed_tower = tower
                    return

            self.selected_placed_tower = None
            cost = Tower.TYPES[self.selected_tower_type]["cost"]

            if self.money >= cost:
                on_path = False
                for i in range(len(WAYPOINTS) - 1):
                    p1 = WAYPOINTS[i]
                    if math.hypot(p1[0] - x, p1[1] - y) < 30:
                        on_path = True

                if not on_path:
                    self.towers.append(Tower(x, y, self.selected_tower_type))
                    self.money -= cost
        else:
            y_offset = 100
            for t_name in Tower.TYPES.keys():
                btn_rect = pygame.Rect(755, y_offset, 140, 35)
                if btn_rect.collidepoint(pos):
                    self.selected_tower_type = t_name
                    self.selected_placed_tower = None
                y_offset += 42

            btn_wave = pygame.Rect(755, 300, 140, 40)
            if btn_wave.collidepoint(pos):
                self.start_next_wave()

            if self.selected_placed_tower:
                upg_btn = pygame.Rect(755, 430, 140, 35)
                if upg_btn.collidepoint(pos):
                    t = self.selected_placed_tower
                    if self.money >= t.upgrade_cost:
                        self.money -= t.upgrade_cost
                        t.upgrade()


# --- MAIN LOOP ---

def main():
    game = Game()

    running = True
    while running:
        CLOCK.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    game.handle_click(event.pos)

        game.update()
        game.draw(SCREEN)

        pygame.display.flip()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()