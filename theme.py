import pygame
from pygame import Color

# 调色板
BG_GRADIENT_TOP = (28, 34, 52)
BG_GRADIENT_BOTTOM = (10, 13, 24)

ACCENT = (94, 155, 255)
ACCENT_HOVER = (122, 181, 255)
DANGER = (255, 102, 128)
WARN = (255, 204, 114)
SUCCESS = (104, 220, 168)
SURFACE = (44, 52, 70, 210)  # 半透明面板
SURFACE_LIGHT = (60, 68, 90, 215)
TEXT_MAIN = (248, 251, 255)
TEXT_DIM = (210, 216, 228)
TEXT_MUTED = (166, 174, 190)
TEXT_ACCENT = (255, 222, 160)

CLOCK_POINTER = (255, 255, 255)

SHADOW = (0, 0, 0, 120)

def draw_vertical_gradient(surface, top_color, bottom_color):
    w, h = surface.get_size()
    for y in range(h):
        ratio = y / h
        r = int(top_color[0] + (bottom_color[0] - top_color[0]) * ratio)
        g = int(top_color[1] + (bottom_color[1] - top_color[1]) * ratio)
        b = int(top_color[2] + (bottom_color[2] - top_color[2]) * ratio)
        pygame.draw.line(surface, (r, g, b), (0, y), (w, y))

def lerp(a, b, t):
    return a + (b - a) * t

def ease_out_cubic(t):
    return 1 - pow(1 - t, 3)

def with_alpha(color, a):
    return (color[0], color[1], color[2], a)