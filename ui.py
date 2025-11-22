import pygame
from typing import Callable
from theme import ACCENT, ACCENT_HOVER, TEXT_MAIN, TEXT_DIM, TEXT_MUTED, TEXT_ACCENT
from utils import draw_round_rect

class Button:
    def __init__(self, rect, text, font, callback: Callable, color=ACCENT):
        self.rect = pygame.Rect(rect)
        self.text = text
        self.font = font
        self.callback = callback
        self.color = color
        self.hover = False
        self.disabled = False

    def set_text(self, text: str):
        self.text = text

    def draw(self, surf):
        c = self.color
        if self.disabled:
            c = (90, 95, 110)
        elif self.hover:
            c = ACCENT_HOVER if self.color == ACCENT else tuple(min(255, x + 25) for x in self.color)
        draw_round_rect(surf, self.rect, c, 14)
        img = self.font.render(self.text, True, TEXT_ACCENT if self.color != ACCENT else TEXT_MAIN)
        r = img.get_rect(center=self.rect.center)
        surf.blit(img, r)

    def handle_event(self, ev):
        if self.disabled:
            return
        if ev.type == pygame.MOUSEMOTION:
            self.hover = self.rect.collidepoint(ev.pos)
        elif ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
            if self.rect.collidepoint(ev.pos):
                if self.callback:
                    self.callback()


class InputField:
    def __init__(self, rect, font, placeholder=""):
        self.rect = pygame.Rect(rect)
        self.font = font
        self.text = ""
        self.placeholder = placeholder
        self.focus = False
        self.cursor_timer = 0
        self.type_numeric = False
        self.max_len = 64

    def set_numeric(self, numeric=True):
        self.type_numeric = numeric

    def draw(self, surf):
        base_color = (60, 66, 76)
        draw_round_rect(surf, self.rect, base_color, 10)
        show = self.text if self.text else self.placeholder
        color = TEXT_MAIN if self.text else TEXT_MUTED
        img = self.font.render(show, True, color)
        surf.blit(img, (self.rect.x + 12, self.rect.y + (self.rect.height - img.get_height()) / 2))
        if self.focus:
            self.cursor_timer += 1
            if self.cursor_timer % 40 < 20:
                x = self.rect.x + 12 + img.get_width() + 3
                y1 = self.rect.y + 10
                y2 = self.rect.y + self.rect.height - 10
                pygame.draw.line(surf, TEXT_MAIN, (x, y1), (x, y2), 2)

    def handle_event(self, ev):
        if ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
            self.focus = self.rect.collidepoint(ev.pos)
        if not self.focus:
            return
        if ev.type == pygame.KEYDOWN:
            if ev.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            elif ev.key == pygame.K_RETURN:
                self.focus = False
            else:
                ch = ev.unicode
                if ch:
                    if self.type_numeric and not (ch.isdigit() or ch in ", "):
                        return
                    if len(self.text) < self.max_len:
                        self.text += ch

    def get_value(self):
        return self.text.strip()


class TableGrid:
    def __init__(self, x, y, rows, cols, cell_w=70, cell_h=40, font=None):
        self.x = x
        self.y = y
        self.rows = rows
        self.cols = cols
        self.cell_w = cell_w
        self.cell_h = cell_h
        self.font = font
        self.data = [[0 for _ in range(cols)] for _ in range(rows)]
        self.sel = (0, 0)

    def set_data(self, mat):
        self.rows = len(mat)
        self.cols = len(mat[0]) if self.rows else 0
        self.data = [row[:] for row in mat]

    def draw(self, surf):
        for r in range(self.rows):
            for c in range(self.cols):
                rx = self.x + c * self.cell_w
                ry = self.y + r * self.cell_h
                rect = pygame.Rect(rx, ry, self.cell_w - 4, self.cell_h - 4)
                color = (54, 62, 72)
                if (r, c) == self.sel:
                    color = (76, 139, 255)
                draw_round_rect(surf, rect, color, 8)
                txt = str(self.data[r][c])
                img = self.font.render(txt, True, (240, 242, 246))
                surf.blit(img, (rect.x + (rect.width - img.get_width()) / 2,
                                rect.y + (rect.height - img.get_height()) / 2))

    def handle_event(self, ev):
        if ev.type == pygame.KEYDOWN:
            r, c = self.sel
            if ev.key == pygame.K_RIGHT:
                c = (c + 1) % self.cols
            elif ev.key == pygame.K_LEFT:
                c = (c - 1) % self.cols
            elif ev.key == pygame.K_DOWN:
                r = (r + 1) % self.rows
            elif ev.key == pygame.K_UP:
                r = (r - 1) % self.rows
            elif ev.key == pygame.K_BACKSPACE:
                cur = str(self.data[r][c])
                cur = cur[:-1] if cur else cur
                self.data[r][c] = int(cur) if cur.isdigit() else 0
            else:
                if ev.unicode.isdigit():
                    cur = str(self.data[r][c])
                    if len(cur) < 4:
                        cur += ev.unicode
                        self.data[r][c] = int(cur)
            self.sel = (r, c)

    def get_matrix(self):
        return [row[:] for row in self.data]