# -*- coding: utf-8 -*-
import os
import pygame
import threading
from volcenginesdkarkruntime import Ark

# =========================
# 1. Ark 客户端
# =========================
client = Ark(
    base_url="https://ark.cn-beijing.volces.com/api/v3",
    api_key="b422a41f-6b" 
)

pygame.init()
pygame.key.start_text_input()
pygame.key.set_repeat(500, 40)

WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("双头像聊天 - 豆包 AI")

# 颜色
BG_COLOR = (9, 16, 25)
AI_BUBBLE = (51, 51, 51)
USER_BUBBLE = (0, 180, 120)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
LIGHT_GRAY = (180, 180, 180)

# =========================
# 2. 加载中文字体
# =========================
def load_chinese_font(size):
    candidates = [
        r"C:\Windows\Fonts\msyh.ttc",
        r"C:\Windows\Fonts\simhei.ttf",
        r"C:\Windows\Fonts\simsun.ttc",
    ]
    for path in candidates:
        if os.path.exists(path):
            return pygame.font.Font(path, size)
    return pygame.font.SysFont("SimHei", size)


FONT = load_chinese_font(26)
SMALL_FONT = load_chinese_font(22)

# =========================
# 3. 加载左右头像
# =========================
ai_avatar = pygame.image.load("ai.png").convert_alpha()
ai_avatar = pygame.transform.smoothscale(ai_avatar, (52, 52))

user_avatar = pygame.image.load("user.png").convert_alpha()
user_avatar = pygame.transform.smoothscale(user_avatar, (52, 52))

AVATAR_SIZE = 52
INPUT_HEIGHT = 70

input_box = pygame.Rect(15, HEIGHT - INPUT_HEIGHT + 15, WIDTH - 120, INPUT_HEIGHT - 25)
send_box = pygame.Rect(WIDTH - 90, HEIGHT - INPUT_HEIGHT + 15, 70, INPUT_HEIGHT - 25)

messages = [{"sender": "ai", "text": "嗨，我是豆包 AI，有什么想聊的吗？"}]
streaming = False

# 输入内容管理
_ime_text = ""               # 已确认内容
_ime_editing_text = ""       # 拼音阶段内容
_ime_text_pos = 0            # 光标位置
_ime_editing_pos = 0         # 拼音阶段光标

# 换行工具
def wrap_text(text, font, max_width):
    lines = []
    for para in text.split("\n"):
        tmp = ""
        for ch in para:
            test = tmp + ch
            w, _ = font.size(test)
            if w <= max_width:
                tmp = test
            else:
                lines.append(tmp)
                tmp = ch
        if tmp:
            lines.append(tmp)
    return lines


# =========================
# AI 流式回复
# =========================
def call_ai(question):
    global streaming
    streaming = True
    ai_msg = {"sender": "ai", "text": ""}
    messages.append(ai_msg)

    def run_stream():
        global streaming
        try:
            stream = client.chat.completions.create(
                model="doubao-seed-1-6-251015",
                messages=[{"role": "user", "content": [{"type": "text", "text": question}]}],
                reasoning_effort="medium",
                stream=True,
            )
            for chunk in stream:
                if chunk.choices and chunk.choices[0].delta.content:
                    ai_msg["text"] += chunk.choices[0].delta.content
        except Exception as e:
            ai_msg["text"] += f"\n[错误] {e}"
        finally:
            streaming = False

    threading.Thread(target=run_stream, daemon=True).start()


def send_user_message():
    global _ime_text
    text = _ime_text.strip()
    if not text:
        return
    messages.append({"sender": "user", "text": text})
    _ime_text = ""
    call_ai(text)


# =========================
# 聊天区域绘制
# =========================
def draw_chat_area(surface):
    top_margin = 50
    bottom_limit = HEIGHT - INPUT_HEIGHT - 10
    y = bottom_limit
    max_bubble_width = WIDTH - 160

    for msg in reversed(messages):
        sender = msg["sender"]
        text = msg["text"]
        lines = wrap_text(text, SMALL_FONT, max_bubble_width)
        line_height = SMALL_FONT.get_linesize()
        bubble_height = line_height * len(lines) + 16

        if sender == "ai":
            avatar_x = 15
            bubble_x = 15 + 52 + 10
        else:
            avatar_x = WIDTH - 15 - 52

        # 计算泡大小
        max_line_width = max([SMALL_FONT.size(ln)[0] for ln in lines])
        bubble_width = max_line_width + 20

        if sender == "ai":
            bubble_y = y - bubble_height - 10
        else:
            bubble_y = y - bubble_height - 10
            bubble_x = avatar_x - 10 - bubble_width

        if bubble_y < top_margin:
            break

        if sender == "ai":
            surface.blit(ai_avatar, (avatar_x, bubble_y))
        else:
            surface.blit(user_avatar, (avatar_x, bubble_y))

        pygame.draw.rect(surface, AI_BUBBLE if sender == "ai" else USER_BUBBLE,
                         (bubble_x, bubble_y, bubble_width, bubble_height), border_radius=12)

        ty = bubble_y + 8
        for ln in lines:
            surface.blit(SMALL_FONT.render(ln, True, WHITE), (bubble_x + 10, ty))
            ty += line_height

        y = bubble_y - 15


# =========================
# 主循环
# =========================
running = True
while running:
    screen.fill(BG_COLOR)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.TEXTINPUT:
            _ime_text += event.text

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_BACKSPACE:
                _ime_text = _ime_text[:-1]
            elif event.key == pygame.K_RETURN:
                send_user_message()

        if event.type == pygame.MOUSEBUTTONDOWN:
            if send_box.collidepoint(event.pos):
                send_user_message()

    # 绘制顶部标题
    screen.blit(FONT.render("灰原哀 · 豆包 AI", True, WHITE), (20, 10))

    draw_chat_area(screen)

    # 输入栏
    pygame.draw.rect(screen, (20, 28, 36), (0, HEIGHT - INPUT_HEIGHT, WIDTH, INPUT_HEIGHT))
    pygame.draw.rect(screen, (40, 50, 60), input_box, border_radius=12)

    # 显示输入内容（> 开头 + 输入文字）
    display_text = "> " + _ime_text
    surf = SMALL_FONT.render(display_text if display_text.strip() else "请输入内容…",
                             True, WHITE if _ime_text else LIGHT_GRAY)
    screen.blit(surf, (input_box.x + 10, input_box.y + 15))

    pygame.draw.rect(screen, (0, 160, 230), send_box, border_radius=12)
    screen.blit(SMALL_FONT.render("发送", True, WHITE),
                (send_box.x + 15, send_box.y + 8))

    if streaming:
        screen.blit(SMALL_FONT.render("AI 思考中…", True, LIGHT_GRAY), (15, HEIGHT - INPUT_HEIGHT - 25))

    pygame.display.flip()

pygame.quit()
