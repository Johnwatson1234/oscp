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
    api_key="b422a41f-6be4-4872-863b-e97889c46a32"
)

pygame.init()
pygame.key.start_text_input()
pygame.key.set_repeat(500, 40)

WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("双头像聊天 - 豆包 AI")

# 颜色
BG_COLOR = (9, 16, 25)        # 整体背景（深色一点）
AI_BUBBLE = (51, 51, 51)      # 左侧灰色气泡
USER_BUBBLE = (0, 180, 120)   # 右侧绿色气泡
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
# 3. 加载左右两张头像
# =========================
# 左边：AI 头像
ai_avatar = pygame.image.load("ai.png").convert_alpha()
ai_avatar = pygame.transform.smoothscale(ai_avatar, (52, 52))
# 右边：用户头像
user_avatar = pygame.image.load("user.png").convert_alpha()
user_avatar = pygame.transform.smoothscale(user_avatar, (52, 52))

AVATAR_SIZE = 52
AVATAR_MARGIN_X = 15  # 头像离左右边的距离
AVATAR_MARGIN_Y = 10

# =========================
# 4. 输入区域布局（底部）
# =========================
INPUT_HEIGHT = 70
input_box = pygame.Rect(
    15,
    HEIGHT - INPUT_HEIGHT + 15,
    WIDTH - 120,
    INPUT_HEIGHT - 25,
)
send_box = pygame.Rect(
    WIDTH - 90,
    HEIGHT - INPUT_HEIGHT + 15,
    70,
    INPUT_HEIGHT - 25,
)

user_text = ""
active_input = True

# =========================
# 5. 聊天消息结构
# =========================
# 每条消息：{"sender": "ai"/"user", "text": "..."}
messages = [
    {"sender": "ai", "text": "嗨，我是豆包 AI，小哀在线值班，有什么想聊的吗？"},
]
streaming = False  # 是否正在等待 AI 回复


# 文本换行（用于算气泡大小）
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


# =========================
# 6. 调用豆包（流式），让左边头像说话
# =========================
def call_ai(question):
    global streaming
    streaming = True

    # 新增一条空的 AI 消息，用来接收流式内容
    ai_msg = {"sender": "ai", "text": ""}
    messages.append(ai_msg)

    def run_stream():
        global streaming
        try:
            stream = client.chat.completions.create(
                model="doubao-seed-1-6-251015",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": question},
                        ],
                    }
                ],
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


# =========================
# 7. 发送一条用户消息 + 触发 AI 回复
# =========================
def send_user_message():
    global user_text
    text = user_text.strip()
    if not text:
        return
    # 添加用户消息（右侧头像、绿色气泡）
    messages.append({"sender": "user", "text": text})
    user_text = ""
    # 让 AI 回一条
    call_ai(text)


# =========================
# 8. 绘制聊天区域（上半部分）
# =========================
def draw_chat_area(surface):
    # 顶部留一点标题空间
    top_margin = 50
    bottom_limit = HEIGHT - INPUT_HEIGHT - 10  # 底部留给输入区域
    y = bottom_limit

    max_bubble_width = WIDTH - 160  # 两侧头像 + 边距 之后，气泡最大宽度

    # 从最后一条消息往上画
    for msg in reversed(messages):
        sender = msg["sender"]
        text = msg["text"]

        # 先把文本换行
        lines = wrap_text(text, SMALL_FONT, max_bubble_width)
        line_height = SMALL_FONT.get_linesize()
        bubble_height = line_height * len(lines) + 16  # 上下 padding 8 + 8

        # 头像和气泡的位置
        if sender == "ai":
            # 左边头像
            avatar_x = AVATAR_MARGIN_X
            avatar_y = y - bubble_height - AVATAR_MARGIN_Y - AVATAR_SIZE
            bubble_x = AVATAR_MARGIN_X + AVATAR_SIZE + 10
        else:  # user
            avatar_x = WIDTH - AVATAR_MARGIN_X - AVATAR_SIZE
            avatar_y = y - bubble_height - AVATAR_MARGIN_Y - AVATAR_SIZE
            # 气泡从右向左对齐
            # 先估一个文本宽度（取最长行）
            max_line_width = 0
            for ln in lines:
                w, _ = SMALL_FONT.size(ln)
                max_line_width = max(max_line_width, w)
            bubble_width = max_line_width + 20  # 左右 padding 10+10
            bubble_x = avatar_x - 10 - bubble_width
        bubble_y = avatar_y + (AVATAR_SIZE - bubble_height)

        # 如果超出顶部就不再画（简单的「只看最近」）
        if bubble_y < top_margin:
            break

        # 画头像
        if sender == "ai":
            surface.blit(ai_avatar, (avatar_x, avatar_y))
        else:
            surface.blit(user_avatar, (avatar_x, avatar_y))

        # 再算一遍气泡宽度（AI 的也一样）
        max_line_width = 0
        for ln in lines:
            w, _ = SMALL_FONT.size(ln)
            max_line_width = max(max_line_width, w)
        bubble_width = max_line_width + 20

        # 画气泡
        if sender == "ai":
            bubble_color = AI_BUBBLE
            text_color = WHITE
        else:
            bubble_color = USER_BUBBLE
            text_color = WHITE

        bubble_rect = pygame.Rect(bubble_x, bubble_y, bubble_width, bubble_height)
        pygame.draw.rect(surface, bubble_color, bubble_rect, border_radius=12)

        # 画文字
        text_y = bubble_y + 8
        for ln in lines:
            txt_surf = SMALL_FONT.render(ln, True, text_color)
            surface.blit(txt_surf, (bubble_x + 10, text_y))
            text_y += line_height

        # 更新下一条消息的 y 坐标（向上叠）
        y = bubble_y - 15  # 两条气泡之间留一点间距


# =========================
# 9. 主循环
# =========================
running = True
while running:
    screen.fill(BG_COLOR)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # 鼠标点击发送按钮
        if event.type == pygame.MOUSEBUTTONDOWN:
            if send_box.collidepoint(event.pos):
                send_user_message()

        # 文字输入（支持中文）
        if event.type == pygame.TEXTINPUT and active_input:
            user_text += event.text

        # 回车 / 退格
        if event.type == pygame.KEYDOWN and active_input:
            if event.key == pygame.K_BACKSPACE:
                user_text = user_text[:-1]
            elif event.key == pygame.K_RETURN:
                send_user_message()

    # 标题
    title = FONT.render("灰原哀 · 豆包 AI", True, WHITE)
    screen.blit(title, (20, 10))

    # 聊天区域
    draw_chat_area(screen)

    # 底部输入栏背景
    pygame.draw.rect(
        screen,
        (20, 28, 36),
        (0, HEIGHT - INPUT_HEIGHT, WIDTH, INPUT_HEIGHT),
    )

    # 输入框
    pygame.draw.rect(
        screen,
        (40, 50, 60),
        input_box,
        border_radius=12,
    )
    input_text_surface = SMALL_FONT.render(
        user_text if user_text else "请输入内容…", True,
        WHITE if user_text else LIGHT_GRAY,
    )
    screen.blit(input_text_surface, (input_box.x + 10, input_box.y + 10))

    # 发送按钮
    pygame.draw.rect(screen, (0, 160, 230), send_box, border_radius=12)
    send_text = SMALL_FONT.render("发送", True, WHITE)
    screen.blit(
        send_text,
        (
            send_box.x + (send_box.width - send_text.get_width()) / 2,
            send_box.y + (send_box.height - send_text.get_height()) / 2,
        ),
    )

    # 状态提示
    status_msg = "AI 思考中…" if streaming else ""
    if status_msg:
        status_surf = SMALL_FONT.render(status_msg, True, LIGHT_GRAY)
        screen.blit(status_surf, (15, HEIGHT - INPUT_HEIGHT - 25))

    pygame.display.flip()

pygame.quit()
