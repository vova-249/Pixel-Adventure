import pygame
import sys
import random
import os
import json
import math
import base64
import io
from pathlib import Path

# Импортируем закодированную музыку из файла music_data.py
import music_data

# Декодируем текстовые строки обратно в чистые байты
MENU_MUSIC_BYTES = base64.b64decode(music_data.MENU_MUSIC_RAW)
GAME_MUSIC_BYTES = base64.b64decode(music_data.GAME_MUSIC_RAW)

# 1. Предварительная настройка звукового микшера
pygame.mixer.pre_init(frequency=44100, size=-16, channels=2, buffer=512)

# 2. Полная инициализация всех модулей Pygame
pygame.init()

# 3. Принудительный старт модуля шрифтов для защиты от багов в циклах
pygame.font.init()

# Константы виртуального разрешения и цветовой палитры мегаполиса
VIRT_W, VIRT_H, FPS = 800, 450, 60
COLOR_BG_MENU = (174, 219, 240)
COLOR_BG_GAME = (25, 25, 35)
COLOR_DARK = (45, 45, 50)
COLOR_PLAYER = (25, 25, 25)
COLOR_HAZARD_DARK = (55, 30, 60)
COLOR_HAZARD_LIGHT = (180, 80, 100)
COLOR_TEXT = (240, 240, 240)

# На Android всегда используем полноэкранный режим
is_fullscreen, music_on = True, True
music_menu_loaded = True
music_game_loaded = True
current_music = None

# Инициализация мобильного экрана на весь дисплей
screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
pygame.display.set_caption("Pixel Adventure Metal Slopes Mobile")
clock = pygame.time.Clock()

# Функция для запуска музыки НАПРЯМУЮ из оперативной памяти
def play_music_from_memory(music_bytes, loops=-1):
    music_stream = io.BytesIO(music_bytes)
    pygame.mixer.music.load(music_stream)
    pygame.mixer.music.play(loops)

print("[INFO] Музыка и шрифты успешно инициализированы!")

# Функция переключения музыки из оперативной памяти
def switch_music(track_name):
    global current_music
    if not music_on:
        current_music = track_name
        return
    if current_music == track_name:
        return
    try:
        pygame.mixer.music.stop()
        if track_name == "menu":
            play_music_from_memory(MENU_MUSIC_BYTES, -1)
            pygame.mixer.music.set_volume(0.5)
        elif track_name == "game":
            play_music_from_memory(GAME_MUSIC_BYTES, -1)
            pygame.mixer.music.set_volume(0.5)
        current_music = track_name
    except Exception as e:
        print(f"[ERROR] Ошибка переключения музыки: {e}")

def get_screen_scale():
    w, h = screen.get_size()
    scale = min(w / VIRT_W, h / VIRT_H)
    return scale, (w - VIRT_W * scale) / 2, (h - VIRT_H * scale) / 2

HIGHSCORE_FILE = "high_scores.json"
def load_highscores():
    if os.path.exists(HIGHSCORE_FILE):
        try:
            with open(HIGHSCORE_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                return data.get("top10", [])
        except:
            return []
    return []

def save_highscore(score, has_won=False):
    scores = load_highscores()
    scores.append({"score": score, "won": has_won})
    scores = sorted(scores, key=lambda x: x["score"], reverse=True)[:10]
    try:
        with open(HIGHSCORE_FILE, "w", encoding="utf-8") as f:
            json.dump({"top10": scores}, f)
    except Exception as e:
        None

def save_game_checkpoint(score, lives, rx, ry, idx):
    with open("savegame.txt", "w", encoding="utf-8") as f:
        f.write(f"{score}\n{lives}\n{int(rx)}\n{int(ry)}\n{idx}\n")

def load_game_checkpoint():
    if os.path.exists("savegame.txt"):
        try:
            with open("savegame.txt", "r", encoding="utf-8") as f:
                lines = [line.strip() for line in f if line.strip()]
                if len(lines) >= 5:
                    return int(lines[0]), int(lines[1]), float(lines[2]), float(lines[3]), int(lines[4])
        except Exception as e:
            None
            return None
    return None
def draw_ui_btn(surface, rect, text, is_hovered, is_pressed):
    by = rect.y + (3 if is_pressed else 0)
    pygame.draw.rect(surface, (95, 95, 95) if is_hovered else (55, 55, 55), (rect.x, by, rect.width, rect.height - (3 if is_pressed else 0)))
    font = pygame.font.SysFont("Arial", 14, bold=True)
    txt_surf = font.render(text, True, COLOR_TEXT)
    surface.blit(txt_surf, (rect.centerx - txt_surf.get_width() // 2, by + 8))

def update_screen_mode():
    global screen
    screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)

def draw_hearts(surface, lives):
    for i in range(lives):
        x = VIRT_W - 35 - (i * 24)
        heart_surf = pygame.Surface((18, 16), pygame.SRCALPHA)
        pygame.draw.rect(heart_surf, (235, 35, 35), (2, 0, 5, 3))
        pygame.draw.rect(heart_surf, (235, 35, 35), (11, 0, 5, 3))
        pygame.draw.rect(heart_surf, (235, 35, 35), (0, 3, 18, 5))
        pygame.draw.rect(heart_surf, (235, 35, 35), (2, 8, 14, 3))
        pygame.draw.rect(heart_surf, (235, 35, 35), (5, 11, 8, 3))
        surface.blit(heart_surf, (x, 15))

def render_glitch_text(surface, text, center_x, center_y):
    font = pygame.font.SysFont("Courier New", 42, bold=True)
    for dx, dy in [(-3, -3), (3, 3), (-3, 3), (3, -3), (0, 0)]:
        b_surf = font.render(text, True, (40, 10, 60))
        surface.blit(b_surf, (center_x - b_surf.get_width() // 2 + dx, center_y - b_surf.get_height() // 2 + dy))
    pink_surf = font.render(text, True, (255, 0, 128))
    blue_surf = font.render(text, True, (0, 128, 255))
    white_surf = font.render(text, True, (255, 255, 255))
    surface.blit(pink_surf, (center_x - pink_surf.get_width() // 2 + random.randint(-4, 4), center_y - pink_surf.get_height() // 2 + random.randint(-2, 2)))
    surface.blit(blue_surf, (center_x - blue_surf.get_width() // 2 - random.randint(-4, 4), center_y - blue_surf.get_height() // 2 - random.randint(-2, 2)))
    surface.blit(white_surf, (center_x - white_surf.get_width() // 2, center_y - white_surf.get_height() // 2))

# Отрисовка наэкранного мобильного джойстика
def draw_mobile_controls(surface, left_hovered, right_hovered):
    pygame.draw.rect(surface, (100, 100, 100, 120) if left_hovered else (50, 50, 50, 80), (20, 350, 70, 70), border_radius=10)
    pygame.draw.polygon(surface, (240, 240, 240), [(35, 385), (60, 365), (60, 405)])
    pygame.draw.rect(surface, (100, 100, 100, 120) if right_hovered else (50, 50, 50, 80), (110, 350, 70, 70), border_radius=10)
    pygame.draw.polygon(surface, (240, 240, 240), [(155, 385), (130, 365), (130, 405)])
class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.rect = pygame.Rect(x, y, 24, 48)
        self.change_x = self.change_y = 0
        self.speed, self.jump_power, self.gravity = 5, -12.0, 0.55
        self.is_grounded = False
        self.walk_frame = 0
        self.last_anim_update = pygame.time.get_ticks()
        self.image = pygame.Surface((24, 48), pygame.SRCALPHA)

    def draw_player_sprite(self):
        self.image.fill((0, 0, 0, 0))
        pygame.draw.rect(self.image, COLOR_PLAYER, (6, 4, 12, 12))
        pygame.draw.rect(self.image, (255, 255, 255), (14, 8, 3, 3))
        pygame.draw.rect(self.image, (180, 40, 40), (4, 1, 14, 4))
        pygame.draw.rect(self.image, (180, 40, 40), (12, 4, 10, 2))
        pygame.draw.rect(self.image, COLOR_PLAYER, (3, 16, 18, 18))

        if not self.is_grounded:
            pygame.draw.rect(self.image, COLOR_PLAYER, (4, 34, 6, 10))
            pygame.draw.rect(self.image, COLOR_PLAYER, (14, 34, 6, 10))
            pygame.draw.rect(self.image, COLOR_PLAYER, (1, 18, 3, 12))
            pygame.draw.rect(self.image, COLOR_PLAYER, (20, 18, 3, 12))
        elif self.change_x == 0:
            pygame.draw.rect(self.image, COLOR_PLAYER, (4, 34, 6, 14))
            pygame.draw.rect(self.image, COLOR_PLAYER, (14, 34, 6, 14))
            pygame.draw.rect(self.image, COLOR_PLAYER, (1, 18, 3, 14))
            pygame.draw.rect(self.image, COLOR_PLAYER, (20, 18, 3, 14))
        else:
            leg_frames = [
                ((4, 34, 6, 14), (14, 34, 6, 14)), ((5, 34, 6, 13), (13, 34, 6, 14)),
                ((6, 34, 6, 11), (12, 34, 6, 14)), ((14, 34, 6, 14), (4, 34, 6, 14)),
                ((13, 34, 6, 13), (5, 34, 6, 14)), ((12, 34, 6, 11), (6, 34, 6, 14))
            ]
            hand_frames = [
                ((1, 16, 3, 14), (20, 20, 3, 12)), ((1, 17, 3, 13), (20, 19, 3, 13)),
                ((1, 19, 3, 11), (20, 17, 3, 15)), ((1, 20, 3, 12), (20, 16, 3, 14)),
                ((1, 19, 3, 13), (20, 17, 3, 13)), ((1, 17, 3, 15), (20, 19, 3, 11))
            ]
            left_leg, right_leg = leg_frames[self.walk_frame]
            left_hand, right_hand = hand_frames[self.walk_frame]
            pygame.draw.rect(self.image, COLOR_PLAYER, left_leg)
            pygame.draw.rect(self.image, COLOR_PLAYER, right_leg)
            pygame.draw.rect(self.image, COLOR_PLAYER, left_hand)
            pygame.draw.rect(self.image, COLOR_PLAYER, right_hand)

    def update(self, platforms):
        self.change_y = min(15, self.change_y + self.gravity)
        self.rect.x += self.change_x
        for b in pygame.sprite.spritecollide(self, platforms, False):
            if b.visible and b.collidable and not getattr(b, 'is_slope', False):
                if self.change_x > 0: self.rect.right = b.rect.left
                elif self.change_x < 0: self.rect.left = b.rect.right
        self.is_grounded = False
        self.rect.y += self.change_y
        for b in pygame.sprite.spritecollide(self, platforms, False):
            if b.visible and b.collidable:
                if getattr(b, 'is_slope', False):
                    rel_x = self.rect.centerx - b.rect.x
                    if 0 <= rel_x <= b.rect.width:
                        slope_y = b.get_slope_y(rel_x)
                        if self.change_y >= 0 and self.rect.bottom >= slope_y - 8:
                            self.rect.bottom = slope_y
                            self.change_y = 0
                            self.is_grounded = True
                else:
                    if self.change_y > 0:
                        self.rect.bottom = b.rect.top
                        self.change_y = 0
                        self.is_grounded = True
                        if hasattr(b, 'stepped_on'): b.stepped_on()
                    elif self.change_y < 0:
                        self.rect.top = b.rect.bottom
                        self.change_y = 0
        if self.change_x != 0 and self.is_grounded:
            now = pygame.time.get_ticks()
            if now - self.last_anim_update >= 166:
                self.last_anim_update = now
                self.walk_frame = (self.walk_frame + 1) % 6
        self.draw_player_sprite()

    def jump(self):
        if self.is_grounded:
            self.change_y = self.jump_power
class Platform(pygame.sprite.Sprite):
    def __init__(self, x, y, width, is_disappearing=False, is_slope=False):
        super().__init__()
        self.is_disappearing = is_disappearing
        self.is_slope = is_slope
        self.width = width
        self.visible = self.collidable = True
        self.timer = self.anim_frame = self.last_frame_time = 0
        self.height = VIRT_H - y
        self.image = pygame.Surface((width, self.height), pygame.SRCALPHA)
        self.rect = pygame.Rect(x, y, width, self.height)
        self.generate_pixel_details(width)

    def generate_pixel_details(self, width):
        self.image.fill((0, 0, 0, 0))
        if self.is_slope:
            W, H = width, self.height
            half = W // 2
            for y in range(H):
                shade = 22 + int((y / max(1, H)) * 10)
                pygame.draw.line(self.image, (shade, shade + 4, shade + 14), (0, y), (W, y))
            for vx in range(0, W, 22):
                pygame.draw.line(self.image, (60, 68, 84), (vx, H), (vx, 0), 1)
            step = 40
            for sx in range(-step, W + step, step):
                pygame.draw.line(self.image, (95, 105, 128), (sx, H), (sx + step * 2, 0), 2)
                pygame.draw.line(self.image, (140, 150, 175), (sx, H), (sx + step * 2, 0), 1)
                pygame.draw.line(self.image, (75, 82, 100), (sx + step * 2, H), (sx, 0), 2)
            pygame.draw.polygon(self.image, (0, 180, 150), [(0, H), (half, 0), (W, H)], 14)
            pygame.draw.polygon(self.image, (0, 220, 180), [(0, H), (half, 0), (W, H)], 6)
            pygame.draw.polygon(self.image, (0, 255, 200), [(0, H), (half, 0), (W, H)], 3)
            pygame.draw.polygon(self.image, (220, 255, 245), [(0, H), (half, 0), (W, H)], 1)
            for i in range(10, W, 22):
                t = i / max(1, half) if i < half else 1.0 - (i - half) / max(1, half)
                bx, by = i, int(H * (1 - t))
                if 0 <= by < H - 2:
                    pygame.draw.circle(self.image, (180, 190, 200), (bx, by + 3), 2)
                    pygame.draw.circle(self.image, (90, 95, 110), (bx, by + 3), 2, 1)
                    pygame.draw.circle(self.image, (240, 240, 255), (bx - 1, by + 2), 1)
            pulse = int(abs(math.sin(pygame.time.get_ticks() * 0.005)) * 120)
            pygame.draw.rect(self.image, (255, 60, 60), (half - 12, 0, 24, 8))
            pygame.draw.rect(self.image, (255, 140 + pulse // 2, 100), (half - 8, 1, 16, 4))
            pygame.draw.circle(self.image, (255, 200, 200), (half, 4), 3)
            pygame.draw.circle(self.image, (255, 80, 80), (half, 2), 8)
            for cx in range(0, W, 14):
                color = (255, 215, 60) if (cx // 14) % 2 == 0 else (30, 30, 35)
                pygame.draw.rect(self.image, color, (cx, H - 8, 7, 6))
        elif not self.is_disappearing:
            pygame.draw.rect(self.image, COLOR_DARK, (0, 0, width, self.height))
            pygame.draw.rect(self.image, (85, 85, 90), (0, 0, width, 4))
            for wx in range(16, width - 16, 32):
                for wy in range(20, self.height - 20, 40):
                    w_color = (255, 230, 130) if random.random() > 0.4 else (30, 30, 35)
                    pygame.draw.rect(self.image, w_color, (wx, wy, 12, 18))
                    pygame.draw.rect(self.image, (20, 20, 23), (wx, wy, 12, 18), 1)
            for px in range(0, width, 4):
                for py in range(0, self.height, 8):
                    if random.random() > 0.85: pygame.draw.rect(self.image, (35, 35, 40), (px, py, 3, 1))
        else:
            self.height = 24
            self.image = pygame.Surface((width, self.height), pygame.SRCALPHA)
            self.redraw_sky_block()

    def get_slope_y(self, rel_x):
        w = self.rect.width
        if rel_x < w // 2: return self.rect.bottom - int((rel_x / (w // 2)) * self.rect.height)
        else: return self.rect.y + int(((rel_x - (w // 2)) / (w // 2)) * self.rect.height)

    def redraw_sky_block(self):
        self.image.fill((0, 0, 0, 0))
        if self.anim_frame < 14:
            crack_w = max(2, self.rect.width - (self.anim_frame * (self.rect.width // 14)))
            if crack_w > 0:
                pygame.draw.rect(self.image, (120 - self.anim_frame*5, 70, 75), (0, 0, crack_w, 20))
                pygame.draw.rect(self.image, (240, 240, 245), (0, 0, crack_w, 20), 2)

    def stepped_on(self):
        if self.is_disappearing and self.timer == 0: self.timer = pygame.time.get_ticks(); self.last_frame_time = self.timer

    def update_disappear(self):
        if self.is_disappearing and self.timer > 0 and self.anim_frame < 14:
            now = pygame.time.get_ticks()
            if now - self.last_frame_time >= 71:
                self.last_frame_time = now; self.anim_frame += 1
                if self.anim_frame >= 4: self.collidable = False
                self.redraw_sky_block()
                if self.anim_frame >= 14: self.visible = False
class Checkpoint(pygame.sprite.Sprite):
    def __init__(self, platform_obj, rel_x):
        super().__init__()
        self.platform = platform_obj
        self.rel_x = rel_x
        self.rect = pygame.Rect(self.platform.rect.x + self.rel_x, self.platform.rect.top - 64, 32, 64)
        self.activated = False
        self.animation_frame = self.time_counter = 0
        self.image = pygame.Surface((32, 64), pygame.SRCALPHA)

    def update_position(self):
        self.rect.x = self.platform.rect.x + self.rel_x
        self.rect.y = self.platform.rect.top - 64

    def animate_flag(self, is_final=False):
        self.time_counter = (self.time_counter + 1) % 15
        if self.time_counter == 0: self.animation_frame = (self.animation_frame + 1) % 4
        self.image.fill((0, 0, 0, 0))
        pygame.draw.rect(self.image, (215, 175, 30) if is_final else (45, 45, 50), (4, 14, 3, 50))
        color = (255, 215, 0) if is_final and self.activated else ((235, 40, 40) if self.activated else (100, 100, 105))
        pts = [[(7, 14), (28, 19), (28, 30), (7, 25)], [(7, 14), (30, 17), (30, 28), (7, 25)], [(7, 14), (28, 21), (28, 32), (7, 25)], [(7, 14), (26, 18), (26, 29), (7, 25)]]
        pygame.draw.polygon(self.image, color, pts[self.animation_frame])

    def activate(self): self.activated = True

class FlowerHazard(pygame.sprite.Sprite):
    def __init__(self, x, y, sz="medium"):
        super().__init__()
        self.sz = sz
        config = {
            "small": {"w": 24, "h": 32, "stem": (40, 25, 45), "petal": (170, 60, 190), "core": (255, 220, 60), "spikes": False},
            "medium": {"w": 32, "h": 44, "stem": (55, 30, 60), "petal": (220, 50, 70), "core": (255, 240, 130), "spikes": False},
            "large": {"w": 44, "h": 58, "stem": (30, 15, 30), "petal": (140, 20, 30), "core": (255, 90, 40), "spikes": True},
            "neon": {"w": 34, "h": 46, "stem": (20, 60, 80), "petal": (0, 240, 220), "core": (255, 255, 255), "spikes": False},
        }
        cfg = config.get(sz, config["medium"])
        w, h = cfg["w"], cfg["h"]
        self.image = pygame.Surface((w, h), pygame.SRCALPHA)
        cx = w // 2
        stem_top = int(h * 0.45)
        pygame.draw.line(self.image, cfg["stem"], (cx, stem_top), (cx, h - 1), 3 if sz != "large" else 5)
        pygame.draw.ellipse(self.image, cfg["stem"], (cx - w // 3, stem_top + 4, w // 3, h // 6))
        pygame.draw.ellipse(self.image, cfg["stem"], (cx + 1, stem_top + h // 5, w // 3, h // 6))
        petal_r = w // 3
        for ang in range(0, 360, 60):
            rad = math.radians(ang)
            px = cx + int(math.cos(rad) * petal_r * 0.7)
            py = stem_top + int(math.sin(rad) * petal_r * 0.7)
            pygame.draw.circle(self.image, cfg["petal"], (px, py), max(4, petal_r // 2))
        pygame.draw.circle(self.image, cfg["core"], (cx, stem_top), max(3, petal_r // 2))
        pygame.draw.circle(self.image, (255, 255, 255), (cx - 1, stem_top - 1), max(1, petal_r // 5))
        if cfg["spikes"]:
            for ang in range(0, 360, 45):
                rad = math.radians(ang)
                sx1 = cx + int(math.cos(rad) * petal_r * 0.9)
                sy1 = stem_top + int(math.sin(rad) * petal_r * 0.9)
                sx2 = cx + int(math.cos(rad) * petal_r * 1.4)
                sy2 = stem_top + int(math.sin(rad) * petal_r * 1.4)
                pygame.draw.line(self.image, (90, 10, 20), (sx1, sy1), (sx2, sy2), 2)
        if sz == "neon":
            glow = pygame.Surface((w + 10, h + 10), pygame.SRCALPHA)
            pygame.draw.circle(glow, (0, 240, 220, 60), (cx, stem_top), petal_r + 6)
            self.image.blit(glow, (-5, -5), special_flags=pygame.BLEND_RGBA_ADD)
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.bottom = x - w // 2, y

class Bird(pygame.sprite.Sprite):
    def __init__(self, px, py):
        super().__init__()
        self.w, self.h = 36, 36; self.anim_frame = 0; self.last_anim_update = pygame.time.get_ticks()
        self.rect = pygame.Rect(px + 500, py - random.randint(20, 80), self.w, self.h)
        self.speed = random.uniform(-4.0, -2.0)
        self.image = pygame.Surface((self.w, self.h), pygame.SRCALPHA)

    def update(self):
        self.rect.x += self.speed
        if pygame.time.get_ticks() - self.last_anim_update >= 80:
            self.last_anim_update = pygame.time.get_ticks(); self.anim_frame = (self.anim_frame + 1) % 4
        self.image.fill((0, 0, 0, 0))
        wy = int(math.sin((self.anim_frame / 4.0) * math.pi * 2) * 9)
        pygame.draw.rect(self.image, (245, 245, 245), (10, 10, 15, 15))
        pygame.draw.rect(self.image, (245, 160, 40), (2, 13, 8, 4))
        pygame.draw.rect(self.image, (170, 175, 180), (15, 15 + wy, 15, 10))
class BackgroundLandscape:
    def __init__(self):
        self.surf_mountains = pygame.Surface((2400, 200), pygame.SRCALPHA)
        self.surf_bridge = pygame.Surface((2400, 260), pygame.SRCALPHA)
        self.surf_sky_city = pygame.Surface((2400, 280), pygame.SRCALPHA)
        pygame.draw.polygon(self.surf_mountains, (130, 155, 175), [(0, 200), (300, 40), (600, 200)])
        pygame.draw.polygon(self.surf_mountains, (115, 140, 160), [(400, 200), (800, 20), (1200, 200)])
        pygame.draw.polygon(self.surf_mountains, (130, 155, 175), [(1000, 200), (1400, 50), (1800, 200)])
        pygame.draw.polygon(self.surf_mountains, (115, 140, 160), [(1600, 200), (2000, 30), (2400, 200)])
        for bx in range(100, 2400, 480):
            pygame.draw.rect(self.surf_bridge, (90, 95, 105), (bx, 20, 16, 240))
            pygame.draw.rect(self.surf_bridge, (65, 70, 75), (bx - 40, 200, 96, 12))
            for i in range(1, 10):
                pygame.draw.line(self.surf_bridge, (140, 145, 155), (bx + 8, 20 + i * 16), (bx - i * 18, 200), 1)
                pygame.draw.line(self.surf_bridge, (140, 145, 155), (bx + 8, 20 + i * 16), (bx + 16 + i * 18, 200), 1)

    def draw(self, surf, scroll, state):
        cloud_shift = int(pygame.time.get_ticks() * 0.005) % 2400
        for cx in range(50, 2400, 400):
            pygame.draw.ellipse(surf, (255, 255, 255, 180), ((cx - cloud_shift) % 2400, 30, 90, 24))
            pygame.draw.ellipse(surf, (255, 255, 255, 180), ((cx - cloud_shift + 30) % 2400, 20, 70, 26))
        if state in ['menu', 'settings', 'highscores']:
            scroll_mountains = int(scroll * 0.12) % 2400; scroll_bridge = int(scroll * 0.28) % 2400
            surf.blit(self.surf_mountains, (-scroll_mountains, 60)); surf.blit(self.surf_mountains, (-scroll_mountains + 2400, 60))
            river_y = 260; pygame.draw.rect(surf, (70, 120, 170), (0, river_y, VIRT_W, VIRT_H - river_y))
            wave_shift = int(pygame.time.get_ticks() * 0.04) % 32
            for wx in range(-32, VIRT_W + 32, 32): pygame.draw.line(surf, (100, 150, 200), (wx + wave_shift, river_y + 8), (wx + wave_shift + 14, river_y + 8), 2)
            surf.blit(self.surf_bridge, (-scroll_bridge, 40)); surf.blit(self.surf_bridge, (-scroll_bridge + 2400, 40))
        else:
            scroll_sky_city = int(scroll * 0.45) % 2400; self.surf_sky_city.fill((0, 0, 0, 0))
            m_frame = (pygame.time.get_ticks() // 71) % 14; angle = (m_frame / 14.0) * math.pi * 2
            pygame.draw.rect(self.surf_sky_city, (35, 38, 48), (320, 30, 16, 230))
            pygame.draw.rect(self.surf_sky_city, (180, 40, 40), (314, 30, 28, 5))
            pygame.draw.circle(self.surf_sky_city, (255, 255, 180), (328, 20), 4)
            for direction in [-1, 1]:
                lx = 328 + math.cos(angle + (math.pi if direction == 1 else 0)) * 130; ly = 20 + math.sin(angle + (math.pi if direction == 1 else 0)) * 25
                pygame.draw.polygon(self.surf_sky_city, (255, 255, 190), [(328, 20), (int(lx) - 12, int(ly)), (int(lx) + 12, int(ly))])
            for i in range(16):
                bx = i * 150; pygame.draw.rect(self.surf_sky_city, (40, 42, 50), (bx, 60, 80, 220))
                rot = (pygame.time.get_ticks() // 50) % 4; pygame.draw.line(self.surf_sky_city, (20, 20, 25), (bx + 40, 56), (bx + 40 + (4 if rot % 2 == 0 else -4), 54), 2)
                if i % 3 == 0:
                    pygame.draw.rect(self.surf_sky_city, (25, 25, 30), (bx + 15, 45, 6, 15))
                    smoke_y = 35 + int(math.sin(pygame.time.get_ticks() * 0.01) * 3); pygame.draw.circle(self.surf_sky_city, (180, 185, 190), (bx + 18, smoke_y), 4)
                if i % 4 == 0:
                    n_col = (80, 220, 80) if (pygame.time.get_ticks() // 200) % 3 == 0 else (220, 80, 220)
                    pygame.draw.polygon(self.surf_sky_city, n_col, [(bx + 65, 90), (bx + 75, 95), (bx + 65, 100)])
                if i < 15: pygame.draw.line(self.surf_sky_city, (20, 20, 25), (bx + 80, 80), (bx + 150, 90), 1)
                for ox in range(bx + 12, bx + 70, 24):
                    for oy in range(80, 240, 35):
                        w_color = (255, 230, 130) if (math.sin(pygame.time.get_ticks() * 0.001 + ox + oy) > 0.1) else (30, 30, 35)
                        pygame.draw.rect(self.surf_sky_city, w_color, (ox, oy, 10, 14))
            pygame.draw.rect(self.surf_sky_city, (32, 50, 38), (0, 273, 2400, 12)); pygame.draw.rect(self.surf_sky_city, (50, 75, 55), (0, 273, 2400, 2))
            surf.blit(self.surf_sky_city, (-scroll_sky_city, 40)); surf.blit(self.surf_sky_city, (-scroll_sky_city + 2400, 40))

def make_checkpoint(platform, desired_rel_x):
    safe_x = max(20, min(platform.rect.width - 40, desired_rel_x))
    return Checkpoint(platform, safe_x)

def layout_menu_buttons(has_save):
    menu_btn_w, menu_btn_h, menu_btn_gap = 200, 32, 12
    buttons = []
    if has_save: buttons.append(b_menu_resume)
    buttons += [b_menu_new, b_menu_set, b_menu_rec, b_menu_exit]
    start_y = 120
    for i, b in enumerate(buttons):
        b.x = VIRT_W // 2 - menu_btn_w // 2
        b.y = start_y + i * (menu_btn_h + menu_btn_gap)
        b.width = menu_btn_w
        b.height = menu_btn_h
def main_loop():
    global is_fullscreen, music_on, screen
    global b_menu_resume, b_menu_new, b_menu_set, b_menu_rec, b_menu_exit

    virt_screen = pygame.Surface((VIRT_W, VIRT_H))
    player = Player(150, 200)
    all_sprites, platforms, hazards, checkpoints, birds = [pygame.sprite.Group() for _ in range(5)]
    bg_landscape = BackgroundLandscape()

    level_map = [
        Platform(-200, 380, 1000), Platform(900, 380, 550), Platform(1550, 360, 500), Platform(2150, 340, 650),
        Platform(2950, 340, 750), Platform(3850, 320, 600), Platform(4550, 350, 700), Platform(5350, 350, 750),
        Platform(6200, 320, 1100), Platform(7450, 320, 150), Platform(7750, 270, 150), Platform(8050, 230, 160),
        Platform(8350, 270, 150), Platform(8650, 310, 160), Platform(8950, 340, 1200), Platform(10300, 320, 1100),
        Platform(11600, 330, 1200), Platform(13000, 310, 1100), Platform(14300, 330, 200, is_slope=True),
        Platform(14500, 340, 1200), Platform(15900, 320, 150, is_disappearing=True), Platform(16200, 280, 200),
        Platform(16550, 340, 200, is_slope=True), Platform(16750, 340, 1200),
        Platform(18150, 300, 150, is_disappearing=True), Platform(18400, 260, 150, is_disappearing=True),
        Platform(18700, 340, 1300), Platform(20200, 330, 1100), Platform(21500, 310, 200), Platform(21850, 270, 200),
        Platform(22200, 340, 2000)
    ]
    for p in level_map: platforms.add(p); all_sprites.add(p)

    flowers_x = [
        (450, "small"), (1650, "medium"), (2250, "large"), (6350, "medium"),
        (9100, "neon"), (11800, "large"), (13200, "small"), (15000, "neon"),
        (17200, "medium"), (19000, "large")
    ]
    for fx, sz in flowers_x:
        for p in platforms:
            if p.rect.x <= fx <= p.rect.right and not p.is_disappearing and not p.is_slope:
                fl = FlowerHazard(fx, p.rect.top, sz)
                hazards.add(fl); all_sprites.add(fl); break

    checkpoints_instances = [
        make_checkpoint(level_map[4], 400), make_checkpoint(level_map[8], 500),
        make_checkpoint(level_map[15], 400), make_checkpoint(level_map[21], 400),
        make_checkpoint(level_map[-1], 800)
    ]
    for cp in checkpoints_instances: checkpoints.add(cp); all_sprites.add(cp)

    camera_scroll, lives, score = 0, 3, 0
    respawn_x, respawn_y, current_state, fade_alpha = 150, 200, 'menu', 0
    last_bird_spawn, last_activated_checkpoint_idx = pygame.time.get_ticks(), -1
    scout_scroll, max_scout_limit = 0, 0
    win_timer = 0
    confetti_particles = []

    scout_dragging = False
    scout_drag_start_mx = 0
    scout_drag_start_scroll = 0

    pause_rect = pygame.Rect(15, 15, 32, 32)
    b_menu_resume = pygame.Rect(VIRT_W // 2 - 100, 0, 200, 32)
    b_menu_new = pygame.Rect(VIRT_W // 2 - 100, 0, 200, 32)
    b_menu_set = pygame.Rect(VIRT_W // 2 - 100, 0, 200, 32)
    b_menu_rec = pygame.Rect(VIRT_W // 2 - 100, 0, 200, 32)
    b_menu_exit = pygame.Rect(VIRT_W // 2 - 100, 0, 200, 32)

    b_p_res = pygame.Rect(VIRT_W // 2 - 100, 120, 200, 32)
    b_p_scout = pygame.Rect(VIRT_W // 2 - 100, 165, 200, 32)
    b_p_set = pygame.Rect(VIRT_W // 2 - 100, 210, 200, 32)
    b_p_men = pygame.Rect(VIRT_W // 2 - 100, 255, 200, 32)

    b_set_fs = pygame.Rect(VIRT_W // 2 - 120, 160, 240, 38)
    b_set_mu = pygame.Rect(VIRT_W // 2 - 120, 215, 240, 38)
    b_set_back = pygame.Rect(VIRT_W // 2 - 100, 290, 200, 38)
    b_death_rst = pygame.Rect(VIRT_W // 2 - 90, 240, 180, 45)
    b_rec_back = pygame.Rect(VIRT_W // 2 - 100, 360, 200, 35)

    btn_left_rect = pygame.Rect(20, 350, 70, 70)
    btn_right_rect = pygame.Rect(110, 350, 70, 70)
    running = True
    while running:
        scale, off_x, off_y = get_screen_scale()
        mx, my = pygame.mouse.get_pos()
        m_pos = ((mx - off_x) / scale, (my - off_y) / scale)
        m_press = pygame.mouse.get_pressed()

        click_event = False
        screen_tapped_for_jump = False

        for event in pygame.event.get():
            if event.type == pygame.QUIT: running = False
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                click_event = True
                if current_state == 'game':
                    if not pause_rect.collidepoint(m_pos) and not btn_left_rect.collidepoint(
                            m_pos) and not btn_right_rect.collidepoint(m_pos):
                        screen_tapped_for_jump = True

        keys = pygame.key.get_pressed()
        if current_state in ('menu', 'settings', 'highscores'):
            switch_music("menu")
        else:
            switch_music("game")

        # Мобильные свайпы/перетаскивание карты пальцем в режиме разведки
        if current_state == 'scout':
            if m_press:
                if not scout_dragging:
                    scout_dragging = True
                    scout_drag_start_mx = m_pos[0]
                    scout_drag_start_scroll = scout_scroll
                else:
                    dx = m_pos[0] - scout_drag_start_mx
                    scout_scroll = max(camera_scroll, min(max_scout_limit, scout_drag_start_scroll - dx))
            else:
                scout_dragging = False
            if keys[pygame.K_ESCAPE] or keys[pygame.K_SPACE]: current_state = 'pause'; scout_dragging = False

        if current_state == 'game' and event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE: current_state = 'pause'
        # ИСПРАВЛЕНО: Разделение части 12. Логика победы и игровой физики
        if current_state == 'win_anim':
            player.change_x = 0
            if pygame.time.get_ticks() - win_timer >= 2000:
                current_state = 'highscores';
                fade_alpha = 255
            for p in platforms: p.update_disappear()
            birds.update();
            player.update(platforms)

            # Точный рассчет движения конфетти по числовым индексам списка
            for p_c in confetti_particles:
                p_c[1] += p_c[3]  # Смещаем Y на величину скорости
                if p_c[1] > VIRT_H:
                    p_c[1] = random.randint(-50, -10)
                    p_c[0] = random.randint(0, VIRT_W)

        elif current_state == 'game':
            touch_left = m_press and btn_left_rect.collidepoint(m_pos)
            touch_right = m_press and btn_right_rect.collidepoint(m_pos)

            if keys[pygame.K_LEFT] or keys[pygame.K_a] or touch_left:
                player.change_x = -player.speed
            elif keys[pygame.K_RIGHT] or keys[pygame.K_d] or touch_right:
                player.change_x = player.speed
            else:
                player.change_x = 0

            if keys[pygame.K_SPACE] or keys[pygame.K_UP] or keys[pygame.K_w] or screen_tapped_for_jump: player.jump()

            if player.rect.x >= 2000 and pygame.time.get_ticks() - last_bird_spawn >= 8000:
                last_bird_spawn = pygame.time.get_ticks()
                birds.add(Bird(player.rect.x, player.rect.y));
                all_sprites.add(birds.sprites()[-1])

            for p in platforms: p.update_disappear()
            birds.update();
            player.update(platforms)

            for cp in checkpoints: cp.update_position(); cp.animate_flag(is_final=(cp == checkpoints.sprites()[-1]))
            for idx, cp in enumerate(checkpoints):
                if player.rect.colliderect(cp.rect) and not cp.activated:
                    cp.activate();
                    last_activated_checkpoint_idx = idx
                    if idx == len(checkpoints) - 1:
                        score += 100;
                        save_highscore(score, has_won=True);
                        current_state = 'win_anim';
                        win_timer = pygame.time.get_ticks()
                        confetti_particles = [[random.randint(0, VIRT_W), random.randint(-200, 0),
                                               random.choice([(255, 215, 0), (245, 160, 40), (180, 80, 100)]),
                                               random.randint(2, 5)] for _ in range(60)]
                    else:
                        respawn_x, respawn_y = cp.rect.x, cp.rect.y + 10;
                        score += 10;
                        save_game_checkpoint(score, lives, respawn_x, respawn_y, idx)

            if player.rect.x - camera_scroll > 320:
                camera_scroll += (player.rect.x - camera_scroll - 320) * 0.1
            elif player.rect.x - camera_scroll < 160:
                camera_scroll += (player.rect.x - camera_scroll - 160) * 0.1

            if click_event and pause_rect.collidepoint(m_pos): current_state = 'pause'; fade_alpha = 0

            if pygame.sprite.spritecollideany(player, birds) or any(
                    f.rect.colliderect(player.rect) for f in hazards for p in platforms if
                    p.rect.x <= f.rect.x <= p.rect.right and p.visible) or player.rect.y > VIRT_H + 50:
                lives -= 1
                if lives <= 0:
                    save_highscore(score, has_won=False)
                    if os.path.exists("savegame.txt"): os.remove("savegame.txt")
                    birds.empty();
                    current_state = 'menu'
                else:
                    current_state = 'death'; fade_alpha = 0

        elif current_state == 'death' and ((click_event and b_death_rst.collidepoint(m_pos)) or keys[pygame.K_r]):
            player.rect.x, player.rect.y = respawn_x, respawn_y;
            player.change_x = player.change_y = 0;
            camera_scroll = player.rect.x - 160
            for b in birds: b.kill()
            birds.empty()
            for p in platforms: p.visible = p.collidable = True; p.timer = p.anim_frame = 0; p.generate_pixel_details(
                p.width)
            current_state = 'game'
        # === ЧАСТЬ 12.2: ВЗАИМОДЕЙСТВИЕ С UI, РЕНДЕРИНГ МЕНЮ И МОБИЛЬНЫЙ ОВЕРЛЕЙ ===
        elif current_state == 'menu' and click_event:
            has_save = os.path.exists("savegame.txt")
            if has_save and b_menu_resume.collidepoint(m_pos):
                save_data = load_game_checkpoint()
                if save_data:
                    score, lives, respawn_x, respawn_y, chk_idx = save_data
                    player.rect.x, player.rect.y = respawn_x, respawn_y
                    camera_scroll = player.rect.x - 160
                    last_activated_checkpoint_idx = chk_idx
                    for idx, c in enumerate(checkpoints):
                        if idx <= chk_idx:
                            c.activated = True
                    birds.empty()
                    for p in platforms:
                        p.visible = p.collidable = True
                        p.timer = p.anim_frame = 0
                        p.generate_pixel_details(p.width)
                    current_state = 'game'
            elif b_menu_new.collidepoint(m_pos):
                birds.empty()
                current_state = 'game'
                lives, score = 3, 0
                player.rect.x, player.rect.y = 150, 200
                last_activated_checkpoint_idx = -1
                respawn_x, respawn_y = 150, 200
                camera_scroll = 0
                for c in checkpoints:
                    c.activated = False
                for p in platforms:
                    p.visible = p.collidable = True
                    p.timer = p.anim_frame = 0
                    p.generate_pixel_details(p.width)
            elif b_menu_set.collidepoint(m_pos):
                current_state = 'settings'
            elif b_menu_rec.collidepoint(m_pos):
                current_state = 'highscores'
            elif b_menu_exit.collidepoint(m_pos):
                running = False

        elif current_state == 'highscores' and click_event and b_rec_back.collidepoint(m_pos):
            current_state = 'menu'

        elif current_state == 'pause' and click_event:
            if b_p_res.collidepoint(m_pos):
                current_state = 'game'
            elif b_p_scout.collidepoint(m_pos):
                current_state = 'scout'
                scout_scroll = camera_scroll
                next_idx = min(len(checkpoints) - 1, last_activated_checkpoint_idx + 1)
                max_scout_limit = checkpoints.sprites()[next_idx].rect.x - 100
                scout_dragging = False
            elif b_p_set.collidepoint(m_pos):
                current_state = 'settings'
            elif b_p_men.collidepoint(m_pos):
                current_state = 'menu'
                fade_alpha = 255

        elif current_state == 'settings' and click_event:
            if b_set_mu.collidepoint(m_pos):
                music_on = not music_on
                if music_on:
                    pygame.mixer.music.unpause()
                    current_music = None
                else:
                    pygame.mixer.music.pause()
            elif b_set_back.collidepoint(m_pos):
                current_state = 'pause' if player.rect.x > 160 and lives > 0 else 'menu'

        active_scroll = scout_scroll if current_state == 'scout' else camera_scroll
        bg_color = COLOR_BG_MENU if current_state in ['menu', 'settings', 'highscores'] else COLOR_BG_GAME
        virt_screen.fill(bg_color)
        bg_landscape.draw(virt_screen, active_scroll, current_state)

        if current_state not in ['menu', 'settings', 'highscores']:
            for sprite in all_sprites:
                if getattr(sprite, 'visible', True):
                    virt_screen.blit(sprite.image, (sprite.rect.x - active_scroll, sprite.rect.y))
            virt_screen.blit(player.image, (player.rect.x - active_scroll, player.rect.y))

            # Отрисовка летящих конфетти при победе на экране (исправлены индексы)
            if current_state == 'win_anim':
                for p_c in confetti_particles:
                    pygame.draw.rect(virt_screen, p_c[2], (p_c[0], p_c[1], 4, 4))
            elif current_state != 'scout':
                draw_ui_btn(virt_screen, pause_rect, "||", pause_rect.collidepoint(m_pos),
                            m_press and pause_rect.collidepoint(m_pos))
                draw_hearts(virt_screen, lives)
                txt_score = pygame.font.SysFont("Arial", 16, bold=True).render(f"Счёт: {score}", True, (240, 240, 240))
                virt_screen.blit(txt_score, (VIRT_W // 2 - txt_score.get_width() // 2, 15))
                draw_mobile_controls(virt_screen, m_press and btn_left_rect.collidepoint(m_pos),
                                     m_press and btn_right_rect.collidepoint(m_pos))

        if current_state in ['menu', 'pause', 'settings', 'death', 'highscores', 'scout']:
            if current_state != 'scout':
                if current_state == 'death' and fade_alpha < 160:
                    fade_alpha += 4  # Реализация плавного затемнения при смерти
                overlay = pygame.Surface((VIRT_W, VIRT_H), pygame.SRCALPHA)
                overlay.fill((30, 30, 30, 180 if current_state == 'pause' else (
                    fade_alpha if current_state not in ['menu', 'settings', 'highscores'] else 140)))
                virt_screen.blit(overlay, (0, 0))
            if current_state == 'menu':
                has_save = os.path.exists("savegame.txt")
                layout_menu_buttons(has_save)
                render_glitch_text(virt_screen, "Pixel Adventure", VIRT_W // 2, 65)
                if has_save:
                    draw_ui_btn(virt_screen, b_menu_resume, "ПРОДОЛЖИТЬ ИГРУ", b_menu_resume.collidepoint(m_pos),
                                m_press and b_menu_resume.collidepoint(m_pos))
                draw_ui_btn(virt_screen, b_menu_new, "НОВАЯ ИГРА", b_menu_new.collidepoint(m_pos),
                            m_press and b_menu_new.collidepoint(m_pos))
                draw_ui_btn(virt_screen, b_menu_set, "НАСТРОЙКИ [⚙]", b_menu_set.collidepoint(m_pos),
                            m_press and b_menu_set.collidepoint(m_pos))
                draw_ui_btn(virt_screen, b_menu_rec, "РЕКОРДЫ", b_menu_rec.collidepoint(m_pos),
                            m_press and b_menu_rec.collidepoint(m_pos))
                draw_ui_btn(virt_screen, b_menu_exit, "ВЫХОД", b_menu_exit.collidepoint(m_pos),
                            m_press and b_menu_exit.collidepoint(m_pos))
            elif current_state == 'pause':
                render_glitch_text(virt_screen, "ПАУЗА", VIRT_W // 2, 65)
                draw_ui_btn(virt_screen, b_p_res, "ПРОДОЛЖИТЬ ИГРУ", b_p_res.collidepoint(m_pos),
                            m_press and b_p_res.collidepoint(m_pos))
                draw_ui_btn(virt_screen, b_p_scout, "РАЗВЕДКА КАРТЫ", b_p_scout.collidepoint(m_pos),
                            m_press and b_p_scout.collidepoint(m_pos))
                draw_ui_btn(virt_screen, b_p_set, "НАСТРОЙКИ [⚙]", b_p_set.collidepoint(m_pos),
                            m_press and b_p_set.collidepoint(m_pos))
                draw_ui_btn(virt_screen, b_p_men, "ВЫХОД В МЕНЮ", b_p_men.collidepoint(m_pos),
                            m_press and b_p_men.collidepoint(m_pos))
            elif current_state == 'settings':
                render_glitch_text(virt_screen, "НАСТРОЙКИ", VIRT_W // 2, 80)
                draw_ui_btn(virt_screen, b_set_fs, f"МОБИЛЬНЫЙ РЕЖИМ", b_set_fs.collidepoint(m_pos),
                            m_press and b_set_fs.collidepoint(m_pos))
                draw_ui_btn(virt_screen, b_set_mu, f"МУЗЫКА: {'ON' if music_on else 'OFF'}",
                            b_set_mu.collidepoint(m_pos), m_press and b_set_mu.collidepoint(m_pos))
                draw_ui_btn(virt_screen, b_set_back, "НАЗАД", b_set_back.collidepoint(m_pos),
                            m_press and b_set_back.collidepoint(m_pos))
            elif current_state == 'highscores':
                render_glitch_text(virt_screen, "TOP-10 РЕКОРДОВ", VIRT_W // 2, 60)
                scores = load_highscores()
                font_hs = pygame.font.SysFont("Courier New", 16, bold=True)
                for idx, s in enumerate(scores):
                    y_pos = 130 + idx * 22
                    txt_surf = font_hs.render(f"{idx + 1}. СЧЁТ: {s['score']} {'[ПОБЕДА]' if s['won'] else ''}", True,
                                              COLOR_TEXT)
                    virt_screen.blit(txt_surf, (VIRT_W // 2 - 120, y_pos))
                    # Рендеринг золотой медали (исправленные координаты привязки к тексту)
                    if s.get('won', False):
                        gold_x = VIRT_W // 2 - 120 + txt_surf.get_width() + 10
                        pygame.draw.rect(virt_screen, (255, 215, 0), (gold_x, y_pos, 10, 12))
                        pygame.draw.rect(virt_screen, (245, 160, 40), (gold_x + 2, y_pos + 12, 6, 2))
                draw_ui_btn(virt_screen, b_rec_back, "НАЗАД", b_rec_back.collidepoint(m_pos),
                            m_press and b_rec_back.collidepoint(m_pos))
            elif current_state == 'death':
                txt = pygame.font.SysFont("Arial", 36, bold=True).render("ВЫ ПОТЕРЯЛИ ЖИЗНЬ", True, COLOR_TEXT)
                virt_screen.blit(txt, (VIRT_W // 2 - txt.get_width() // 2, 140))
                draw_ui_btn(virt_screen, b_death_rst, "ВОЗРОДИТЬСЯ", b_death_rst.collidepoint(m_pos),
                            m_press and b_death_rst.collidepoint(m_pos))

        if current_state == 'scout':
            sc_font = pygame.font.SysFont("Courier New", 24, bold=True)
            sc_txt = sc_font.render("РЕЖИМ РАЗВЁРТКИ", True, (255, 215, 0))
            bg_rect = pygame.Rect(VIRT_W // 2 - sc_txt.get_width() // 2 - 14, 8, sc_txt.get_width() + 28, 36)
            bg_surf = pygame.Surface((bg_rect.width, bg_rect.height), pygame.SRCALPHA)
            bg_surf.fill((0, 0, 0, 160))
            virt_screen.blit(bg_surf, (bg_rect.x, bg_rect.y))
            pygame.draw.rect(virt_screen, (255, 215, 0), bg_rect, 2)
            virt_screen.blit(sc_txt, (VIRT_W // 2 - sc_txt.get_width() // 2, 14))
            hint_font = pygame.font.SysFont("Arial", 13)
            hint = hint_font.render("Листайте карту пальцем (свайп)", True, (220, 220, 220))
            virt_screen.blit(hint, (VIRT_W // 2 - hint.get_width() // 2, 48))

            # Кнопка мобильного выхода из режима разведки
            b_scout_exit_rect = pygame.Rect(VIRT_W // 2 - 80, VIRT_H - 50, 160, 36)
            draw_ui_btn(virt_screen, b_scout_exit_rect, "ВЫХОД ИЗ РАЗВЕДКИ", b_scout_exit_rect.collidepoint(m_pos), m_press and b_scout_exit_rect.collidepoint(m_pos))
            if click_event and b_scout_exit_rect.collidepoint(m_pos):
                current_state = 'pause'
                scout_dragging = False

        # Отрисовка виртуального экрана на физический дисплей смартфона (внутри цикла while)
        screen.fill((0, 0, 0))
        screen.blit(pygame.transform.scale(virt_screen, (int(VIRT_W * scale), int(VIRT_H * scale))), (off_x, off_y))
        pygame.display.flip()
        clock.tick(FPS)

    # Корректный выход из игры (находится строго ВНЕ цикла while running)
    pygame.quit()
    sys.exit()
if __name__ == "__main__":
    main_loop()
