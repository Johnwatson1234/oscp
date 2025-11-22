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
    # 推荐：把密钥放到环境变量里，避免写死在代码中
    api_key="b422a41f-6be4-4872-863b-e97889c46a32")
# 使用你刚刚上传的图片（系统会把本地路径转成 URL）
IMAGE_PATH = "haibara.png"

pygame.init()
pygame.key.start_text_input()
pygame.key.set_repeat(500, 40)

WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("豆包AI 图文问答 - 灰原哀版")

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = pygame.Color("gray")
BLUE = (0, 180, 250)
LIGHT_BLUE = pygame.Color("lightskyblue3")


# ============  中文字体  ============
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


FONT = load_chinese_font(28)
SMALL_FONT = load_chinese_font(24)

# ============  灰原哀小人  ============
haibara_img = pygame.image.load("haibara.png").convert_alpha()
haibara_img = pygame.transform.smoothscale(haibara_img, (150, 200))
haibara_rect = haibara_img.get_rect()
haibara_rect.bottomleft = (50, HEIGHT - 30)

# ============  聊天框布局  ============
chat_open = False

chat_box = pygame.Rect(220, 60, 520, 480)
output_area = pygame.Rect(
    chat_box.x + 15,
    chat_box.y + 15,
    chat_box.width - 30,
    chat_box.height - 110,
)
input_box = pygame.Rect(
    chat_box.x + 15,
    chat_box.bottom - 60,
    chat_box.width - 120,
    40,
)
button_box = pygame.Rect(
    chat_box.right - 90,
    chat_box.bottom - 60,
    70,
    40,
)

active_input = False
user_text = ""
output_text = ""
streaming = False


# ============  文本换行  ============
def wrap_text(text, font, max_width):
    lines = []
    for para in text.split("\n"):
        if not para:
            lines.append("")
            continue
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


# ============  调用豆包（纯文本，流式）  ============
def call_ai():
    global user_text, output_text, streaming

    if not user_text.strip():
        return

    question = user_text
    user_text = ""
    output_text = ""
    streaming = True

    def run_stream():
        global output_text, streaming
        try:
            stream = client.chat.completions.create(
                model="doubao-seed-1-6-251015",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            # 这里只发文本，不再发 image_url
                            {"type": "text", "text": question},
                        ],
                    }
                ],
                reasoning_effort="medium",
                stream=True,
            )

            for chunk in stream:
                if chunk.choices and chunk.choices[0].delta.content:
                    output_text += chunk.choices[0].delta.content
        except Exception as e:
            output_text += f"\n[错误] Error code: 400 - {e}"
        finally:
            streaming = False

    threading.Thread(target=run_stream, daemon=True).start()


# ============  主循环  ============
running = True
while running:
    screen.fill(WHITE)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.MOUSEBUTTONDOWN:
            if haibara_rect.collidepoint(event.pos):
                chat_open = not chat_open
                if chat_open:
                    active_input = True
            if chat_open:
                if input_box.collidepoint(event.pos):
                    active_input = True
                elif button_box.collidepoint(event.pos):
                    call_ai()

        if chat_open:
            if event.type == pygame.TEXTINPUT and active_input:
                user_text += event.text

            if event.type == pygame.KEYDOWN and active_input:
                if event.key == pygame.K_BACKSPACE:
                    user_text = user_text[:-1]
                elif event.key == pygame.K_RETURN:
                    call_ai()

    # 灰原哀小人
    screen.blit(haibara_img, haibara_rect.topleft)
    tip = SMALL_FONT.render("点我聊天~", True, BLACK)
    screen.blit(tip, (haibara_rect.x + 15, haibara_rect.top - 25))

    # 聊天框
    if chat_open:
        pygame.draw.rect(screen, (245, 245, 245), chat_box, border_radius=12)
        pygame.draw.rect(screen, GRAY, chat_box, 2, border_radius=12)

        title = FONT.render("灰原哀 · 豆包 AI", True, BLACK)
        screen.blit(title, (chat_box.x + 15, chat_box.y - 30))

        pygame.draw.rect(screen, WHITE, output_area, border_radius=8)
        pygame.draw.rect(screen, GRAY, output_area, 1, border_radius=8)

        lines = wrap_text(output_text, SMALL_FONT, output_area.width - 10)
        y = output_area.y + 5
        line_h = SMALL_FONT.get_linesize()
        for ln in lines:
            if y + line_h > output_area.bottom - 5:
                break
            surf = SMALL_FONT.render(ln, True, BLACK)
            screen.blit(surf, (output_area.x + 5, y))
            y += line_h

        pygame.draw.rect(
            screen,
            LIGHT_BLUE if active_input else GRAY,
            input_box,
            2,
            border_radius=8,
        )
        inp_surf = SMALL_FONT.render(user_text, True, BLACK)
        screen.blit(inp_surf, (input_box.x + 8, input_box.y + 9))

        pygame.draw.rect(screen, BLUE, button_box, border_radius=8)
        btn_txt = SMALL_FONT.render("发送", True, WHITE)
        screen.blit(
            btn_txt,
            (
                button_box.x + (button_box.width - btn_txt.get_width()) / 2,
                button_box.y + (button_box.height - btn_txt.get_height()) / 2,
            ),
        )

        status = "思考中..." if streaming else "请输入内容后按回车或点击发送"
        status_surf = SMALL_FONT.render(status, True, GRAY)
        screen.blit(status_surf, (chat_box.x + 15, chat_box.bottom - 90))

    pygame.display.flip()

pygame.quit()
