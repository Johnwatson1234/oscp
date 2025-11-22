# -*- coding: utf-8 -*-
import os
import pygame
import threading
from volcenginesdkarkruntime import Ark

# Ark 客户端
client = Ark(
    base_url="https://ark.cn-beijing.volces.com/api/v3",
    api_key="b422a41f-6be4-4872-863b-e97889c46a32"
)

pygame.init()
pygame.key.start_text_input()
pygame.key.set_repeat(500, 40)

WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("豆包 AI - 中文 IME 输入")

# 颜色
BG_COLOR = (9, 16, 25)
AI_BUBBLE = (51, 51, 51)
USER_BUBBLE = (0, 180, 120)
WHITE = (255, 255, 255)
LIGHT_GRAY = (180, 180, 180)

# 中文字体
def load_chinese_font(size):
    paths = [
        r"C:\Windows\Fonts\msyh.ttc",
        r"C:\Windows\Fonts\simhei.ttf",
        r"C:\Windows\Fonts\simsun.ttc",
    ]
    for p in paths:
        if os.path.exists(p):
            return pygame.font.Font(p, size)
    return pygame.font.SysFont("SimHei", size)

FONT = load_chinese_font(28)
SMALL_FONT = load_chinese_font(22)

# 头像
ai_avatar = pygame.transform.smoothscale(pygame.image.load("ai.png"), (52, 52))
user_avatar = pygame.transform.smoothscale(pygame.image.load("user.png"), (52, 52))

# 输入区
INPUT_HEIGHT = 70
input_box = pygame.Rect(15, HEIGHT - INPUT_HEIGHT + 15, WIDTH - 120, INPUT_HEIGHT - 25)
send_box = pygame.Rect(WIDTH - 90, HEIGHT - INPUT_HEIGHT + 15, 70, INPUT_HEIGHT - 25)

user_text = ""
composing_text = ""  # 临时拼音/组合显示
active_input = True

messages = [{"sender": "ai", "text": "你好，我是灰原哀，有什么想说的吗？"}]
streaming = False

def wrap_text(text, font, max_width):
    lines = []
    tmp = ""
    for ch in text:
        test = tmp + ch
        if font.size(test)[0] <= max_width:
            tmp = test
        else:
            lines.append(tmp)
            tmp = ch
    if tmp:
        lines.append(tmp)
    return lines

def call_ai(question):
    global streaming
    streaming = True
    ai_msg = {"sender": "ai", "text": ""}
    messages.append(ai_msg)

    def run():
        global streaming
        try:
            stream = client.chat.completions.create(
                model="doubao-pro-32k",
                messages=[{"role": "user", "content": [{"type": "text", "text": question}]}],
                stream=True,
            )
            for chunk in stream:
                if chunk.choices and chunk.choices[0].delta.content:
                    ai_msg["text"] += chunk.choices[0].delta.content
        except Exception as e:
            ai_msg["text"] += f"\n[错误] {e}"
        streaming = False

    threading.Thread(target=run, daemon=True).start()

def send_user_message():
    global user_text
    if user_text.strip() == "":
        return
    messages.append({"sender": "user", "text": user_text})
    call_ai(user_text)
    user_text = ""

def draw_chat(surface):
    y = HEIGHT - INPUT_HEIGHT - 20
    max_width = WIDTH - 160
    for msg in reversed(messages):
        lines = wrap_text(msg["text"], SMALL_FONT, max_width)
        h = SMALL_FONT.get_linesize() * len(lines) + 20
        if msg["sender"] == "ai":
            surface.blit(ai_avatar, (15, y - h - 60))
            box = pygame.Rect(80, y - h - 40, max_width, h)
            pygame.draw.rect(surface, AI_BUBBLE, box, border_radius=12)
            color = WHITE
            px = 90
        else:
            surface.blit(user_avatar, (WIDTH - 67, y - h - 60))
            box = pygame.Rect(WIDTH - 20 - SMALL_FONT.size(msg["text"])[0] - 50,
                              y - h - 40,
                              SMALL_FONT.size(msg["text"])[0] + 30, h)
            pygame.draw.rect(surface, USER_BUBBLE, box, border_radius=12)
            color = WHITE
            px = box.x + 10

        ty = box.y + 10
        for line in lines:
            surface.blit(SMALL_FONT.render(line, True, color), (px, ty))
            ty += SMALL_FONT.get_linesize()
        y = box.y - 20

running = True
while running:
    screen.fill(BG_COLOR)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # 中文输入
        if event.type == pygame.TEXTINPUT:
            user_text += event.text

        # 输入法编辑阶段（显示拼音）
        if event.type == pygame.TEXTEDITING:
            composing_text = event.text

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_BACKSPACE:
                user_text = user_text[:-1]
            elif event.key == pygame.K_RETURN:
                send_user_message()
                composing_text = ""

        if event.type == pygame.MOUSEBUTTONDOWN:
            if send_box.collidepoint(event.pos):
                send_user_message()

    # 顶部标题
    screen.blit(FONT.render("灰原哀 · 豆包 AI", True, WHITE), (15, 10))

    draw_chat(screen)

    # 输入区域
    pygame.draw.rect(screen, (30, 38, 49), (0, HEIGHT - INPUT_HEIGHT, WIDTH, INPUT_HEIGHT))
    pygame.draw.rect(screen, (50, 60, 72), input_box, border_radius=12)
    screen.blit(SMALL_FONT.render(user_text if user_text else "请输入内容…",
                                 True, WHITE if user_text else LIGHT_GRAY),
                                 (input_box.x + 10, input_box.y + 10))

    # 拼音组合显示层
    if composing_text:
        comp = SMALL_FONT.render(composing_text, True, LIGHT_GRAY)
        screen.blit(comp, (input_box.x + 10, input_box.y - 25))

    pygame.draw.rect(screen, (0, 160, 230), send_box, border_radius=12)
    screen.blit(SMALL_FONT.render("发送", True, WHITE),
                (send_box.x + 10, send_box.y + 5))

    pygame.display.flip()

pygame.quit()
