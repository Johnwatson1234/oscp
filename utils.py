import pygame, math, random, os
from typing import Tuple

_CJK_FONT_CANDIDATES = [
    "Microsoft YaHei UI",
    "Microsoft YaHei",
    "SimHei",
    "SimSun",
    "微软雅黑",
    "黑体",
    "宋体",
]

def load_font(size, path=None):
    """Return a font object that can render Chinese characters."""
    if path and os.path.exists(path):
        try:
            return pygame.font.Font(path, size)
        except Exception:
            pass
    for family in _CJK_FONT_CANDIDATES:
        try:
            font = pygame.font.SysFont(family, size)
            if font:
                font.render("测试", True, (255, 255, 255))
                return font
        except Exception:
            continue
    try:
        return pygame.font.SysFont("Segoe UI", size)
    except Exception:
        return pygame.font.SysFont("Arial", size)

def blit_text(surface, text, pos, font, color, align="topleft"):
    img = font.render(text, True, color)
    rect = img.get_rect()
    setattr(rect, align, pos)
    surface.blit(img, rect)
    return rect

def create_surface(w, h, alpha=True):
    flags = pygame.SRCALPHA if alpha else 0
    return pygame.Surface((w, h), flags)

def draw_round_rect(surface, rect, color, radius=12):
    x, y, w, h = rect
    pygame.draw.rect(surface, color, (x + radius, y, w - 2 * radius, h))
    pygame.draw.rect(surface, color, (x, y + radius, w, h - 2 * radius))
    pygame.draw.circle(surface, color, (x + radius, y + radius), radius)
    pygame.draw.circle(surface, color, (x + w - radius, y + radius), radius)
    pygame.draw.circle(surface, color, (x + radius, y + h - radius), radius)
    pygame.draw.circle(surface, color, (x + w - radius, y + h - radius), radius)

def shadowed_panel(surface, rect, panel_color, shadow_offset=(6, 6), radius=18):
    shadow = create_surface(rect[2] + shadow_offset[0] * 2, rect[3] + shadow_offset[1] * 2, True)
    draw_round_rect(shadow, (shadow_offset[0], shadow_offset[1], rect[2], rect[3]), (0, 0, 0, 120), radius)
    surface.blit(shadow, (rect[0] - shadow_offset[0], rect[1] - shadow_offset[1]))
    draw_round_rect(surface, rect, panel_color, radius)

class ParticleField:
    def __init__(self, w, h, count=60):
        self.particles = []
        for _ in range(count):
            self.particles.append([
                pygame.Vector2(random.randint(0, w), random.randint(0, h)),
                pygame.Vector2(random.uniform(-0.2, 0.2), random.uniform(-0.2, 0.2)),
                random.randint(1, 3)
            ])
        self.size = (w, h)

    def update(self):
        w, h = self.size
        for p in self.particles:
            p[0] += p[1]
            if p[0].x < 0: p[0].x = w
            if p[0].x > w: p[0].x = 0
            if p[0].y < 0: p[0].y = h
            if p[0].y > h: p[0].y = 0

    def draw(self, surf):
        for p in self.particles:
            pygame.draw.circle(surf, (255, 255, 255, 30), (int(p[0].x), int(p[0].y)), p[2])