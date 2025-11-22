# import os
# import pygame
# import threading
# from volcenginesdkarkruntime import Ark

# # =========================
# # 1. 初始化 Ark 客户端
# # =========================
# client = Ark(
#     base_url="https://ark.cn-beijing.volces.com/api/v3",
#     # 推荐：把密钥放到环境变量里，避免写死在代码中
#     api_key="b422a41f-6be4-4872-863b-e97889c46a32")


# # =========================
# # 2. Pygame 基本设置
# # =========================
# pygame.init()
# WIDTH, HEIGHT = 800, 600
# screen = pygame.display.set_mode((WIDTH, HEIGHT))
# pygame.display.set_caption("豆包AI 图文问答 - 灰原哀版")

# FONT = pygame.font.Font(None, 28)
# SMALL_FONT = pygame.font.Font(None, 24)

# WHITE = (255, 255, 255)
# BLACK = (0, 0, 0)
# GRAY = pygame.Color("gray")
# BLUE = (0, 180, 250)
# LIGHT_BLUE = pygame.Color("lightskyblue3")

# # =========================
# # 3. 加载灰原哀小人形象
# # =========================
# # 确保当前目录有 haibara.png
# ai_image = pygame.image.load("haibara.png").convert_alpha()
# # 缩放一下，避免太大
# ai_image = pygame.transform.smoothscale(ai_image, (150, 200))
# ai_rect = ai_image.get_rect()
# ai_rect.bottomleft = (50, HEIGHT - 30)   # 左下角

# # =========================
# # 4. 聊天框布局
# # =========================
# chat_open = False  # 是否打开对话框

# # 对话框整体区域
# chat_box = pygame.Rect(220, 60, 520, 480)

# # 输出区域（上半部分）
# output_area = pygame.Rect(
#     chat_box.x + 15,
#     chat_box.y + 15,
#     chat_box.width - 30,
#     chat_box.height - 110
# )

# # 输入框
# input_box = pygame.Rect(
#     chat_box.x + 15,
#     chat_box.bottom - 60,
#     chat_box.width - 120,
#     40
# )

# # 发送按钮
# button_box = pygame.Rect(
#     chat_box.right - 90,
#     chat_box.bottom - 60,
#     70,
#     40
# )

# active_input = False  # 当前输入框是否激活
# user_text = ""        # 用户输入的问题
# output_text = ""      # AI 的回答（会不断追加）
# streaming = False     # 是否正在流式回答

# # 如果你还想使用图片问答，可以在这里固定一张图片的 URL
# image_url = "https://ark-project.tos-cn-beijing.ivolces.com/images/view.jpeg"


# # =========================
# # 5. 文本自动换行函数
# # =========================
# def wrap_text(text, font, max_width):
#     """
#     根据 max_width 对 text 换行，返回行列表
#     """
#     lines = []
#     for raw_line in text.split("\n"):
#         words = raw_line.split(" ")
#         if not words:
#             lines.append("")
#             continue

#         current_line = words[0]
#         for word in words[1:]:
#             # 尝试把单词加到这一行
#             test_line = current_line + " " + word
#             width, _ = font.size(test_line)
#             if width <= max_width:
#                 current_line = test_line
#             else:
#                 lines.append(current_line)
#                 current_line = word
#         lines.append(current_line)
#     return lines


# # =========================
# # 6. 调用豆包（流式）
# # =========================
# def call_ai():
#     global output_text, streaming, user_text

#     if not user_text.strip():
#         return  # 空字符串就不发了

#     # 清空旧回答，标记为正在回答
#     output_text = ""
#     streaming = True

#     question = user_text  # 先保存一份，避免边输边修改
#     user_text = ""        # 清空输入框内容

#     def run_stream():
#         global output_text, streaming
#         try:
#             stream = client.chat.completions.create(
#                 model="doubao-seed-1-6-251015",
#                 messages=[
#                     {
#                         "role": "user",
#                         "content": [
#                             # 如需纯文本问答，可以只留 text 这一项
#                             {"type": "image_url", "image_url": {"url": image_url}},
#                             {"type": "text", "text": question},
#                         ],
#                     }
#                 ],
#                 reasoning_effort="medium",
#                 stream=True,
#             )

#             for chunk in stream:
#                 if chunk.choices and chunk.choices[0].delta.content:
#                     output_text += chunk.choices[0].delta.content
#         except Exception as e:
#             output_text += f"\n[错误] {e}"
#         finally:
#             streaming = False

#     threading.Thread(target=run_stream, daemon=True).start()


# # =========================
# # 7. 主循环
# # =========================
# running = True
# while running:
#     screen.fill(WHITE)

#     for event in pygame.event.get():
#         if event.type == pygame.QUIT:
#             running = False

#         # 鼠标点击事件
#         if event.type == pygame.MOUSEBUTTONDOWN:
#             # 点击灰原哀 → 打开/关闭聊天框
#             if ai_rect.collidepoint(event.pos):
#                 chat_open = not chat_open
#                 # 打开聊天框时，把输入框设为激活
#                 if chat_open:
#                     active_input = True
#             # 聊天框内部点击
#             if chat_open:
#                 if input_box.collidepoint(event.pos):
#                     active_input = True
#                 elif button_box.collidepoint(event.pos):
#                     call_ai()
#                 else:
#                     # 点对话框其它位置，不影响输入状态
#                     pass

#         # 键盘输入
#         if event.type == pygame.KEYDOWN and chat_open:
#             if active_input:
#                 if event.key == pygame.K_RETURN:
#                     # 回车发送
#                     call_ai()
#                 elif event.key == pygame.K_BACKSPACE:
#                     user_text = user_text[:-1]
#                 else:
#                     # 普通字符
#                     user_text += event.unicode

#     # =========================
#     # 绘制灰原哀小人
#     # =========================
#     screen.blit(ai_image, ai_rect.topleft)
#     tip = SMALL_FONT.render("点我聊天~", True, BLACK)
#     screen.blit(tip, (ai_rect.x + 15, ai_rect.top - 25))

#     # =========================
#     # 绘制聊天框
#     # =========================
#     if chat_open:
#         # 对话框背景
#         pygame.draw.rect(screen, (245, 245, 245), chat_box, border_radius=12)
#         pygame.draw.rect(screen, GRAY, chat_box, 2, border_radius=12)

#         # 标题
#         title = FONT.render("灰原哀 · 豆包 AI", True, BLACK)
#         screen.blit(title, (chat_box.x + 15, chat_box.y - 30))

#         # 输出区域背景
#         pygame.draw.rect(screen, WHITE, output_area, border_radius=8)
#         pygame.draw.rect(screen, GRAY, output_area, 1, border_radius=8)

#         # 把 output_text 按宽度换行后绘制
#         wrapped_lines = wrap_text(output_text, SMALL_FONT, output_area.width - 10)
#         y = output_area.y + 5
#         line_height = SMALL_FONT.get_linesize()
#         for line in wrapped_lines:
#             if y + line_height > output_area.bottom - 5:
#                 break  # 超出区域不再画
#             text_surface = SMALL_FONT.render(line, True, BLACK)
#             screen.blit(text_surface, (output_area.x + 5, y))
#             y += line_height

#         # 底部输入框 + 按钮
#         pygame.draw.rect(
#             screen,
#             LIGHT_BLUE if active_input else GRAY,
#             input_box,
#             2,
#             border_radius=8
#         )
#         input_surface = SMALL_FONT.render(user_text, True, BLACK)
#         screen.blit(input_surface, (input_box.x + 8, input_box.y + 9))

#         pygame.draw.rect(screen, BLUE, button_box, border_radius=8)
#         btn_text = SMALL_FONT.render("发送", True, WHITE)
#         screen.blit(
#             btn_text,
#             (button_box.x + (button_box.width - btn_text.get_width()) / 2,
#              button_box.y + (button_box.height - btn_text.get_height()) / 2)
#         )

#         # 状态提示
#         status_msg = "思考中..." if streaming else "请输入问题后按回车或点击发送"
#         status_surface = SMALL_FONT.render(status_msg, True, GRAY)
#         screen.blit(status_surface, (chat_box.x + 15, chat_box.bottom - 90))

#     pygame.display.flip()

# pygame.quit()


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

# =========================
# 2. Pygame 初始化
# =========================
pygame.init()
pygame.key.start_text_input()       # 开启文本输入（支持中文）
pygame.key.set_repeat(500, 40)      # 按住退格键时连续删除

WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("豆包AI 图文问答 - 灰原哀版")

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = pygame.Color("gray")
BLUE = (0, 180, 250)
LIGHT_BLUE = pygame.Color("lightskyblue3")


# =========================
# 3. 加载中文字体
# =========================
def load_chinese_font(size):
    # Windows 下常见中文字体路径
    candidates = [
        r"C:\Windows\Fonts\msyh.ttc",      # 微软雅黑
        r"C:\Windows\Fonts\simhei.ttf",    # 黑体
        r"C:\Windows\Fonts\simsun.ttc",    # 宋体
    ]
    for path in candidates:
        if os.path.exists(path):
            return pygame.font.Font(path, size)

    # 兜底：尝试系统字体
    return pygame.font.SysFont("SimHei", size)


FONT = load_chinese_font(28)
SMALL_FONT = load_chinese_font(24)

# =========================
# 4. 灰原哀小人
# =========================
haibara_img = pygame.image.load("haibara.png").convert_alpha()
haibara_img = pygame.transform.smoothscale(haibara_img, (150, 200))
haibara_rect = haibara_img.get_rect()
haibara_rect.bottomleft = (50, HEIGHT - 30)

# =========================
# 5. 聊天框布局
# =========================
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
user_text = ""       # 输入框内容（支持中文）
output_text = ""     # AI 回答
streaming = False    # 是否在流式返回中


# =========================
# 6. 文本换行
# =========================
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
# 7. 调用豆包（流式）
# =========================
def call_ai():
    global user_text, output_text, streaming

    if not user_text.strip():
        return

    question = user_text
    user_text = ""       # 发送后清空输入框
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
                            {"type": "image_url", "image_url": {"url": IMAGE_PATH}},
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
            output_text += f"\n[错误] {e}"
        finally:
            streaming = False

    threading.Thread(target=run_stream, daemon=True).start()


# =========================
# 8. 主循环
# =========================
running = True
while running:
    screen.fill(WHITE)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # 鼠标事件
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

        # 处理中文输入：TEXTINPUT + BACKSPACE/RETURN
        if chat_open:
            if event.type == pygame.TEXTINPUT and active_input:
                # 这里会直接给出已经通过输入法上屏的字符（包括中文）
                user_text += event.text

            if event.type == pygame.KEYDOWN and active_input:
                if event.key == pygame.K_BACKSPACE:
                    user_text = user_text[:-1]
                elif event.key == pygame.K_RETURN:
                    call_ai()

    # ===== 绘制灰原哀 =====
    screen.blit(haibara_img, haibara_rect.topleft)
    tip = SMALL_FONT.render("点我聊天~", True, BLACK)
    screen.blit(tip, (haibara_rect.x + 15, haibara_rect.top - 25))

    # ===== 绘制聊天框 =====
    if chat_open:
        pygame.draw.rect(screen, (245, 245, 245), chat_box, border_radius=12)
        pygame.draw.rect(screen, GRAY, chat_box, 2, border_radius=12)

        title = FONT.render("灰原哀 · 豆包 AI", True, BLACK)
        screen.blit(title, (chat_box.x + 15, chat_box.y - 30))

        pygame.draw.rect(screen, WHITE, output_area, border_radius=8)
        pygame.draw.rect(screen, GRAY, output_area, 1, border_radius=8)

        # 输出内容自动换行
        lines = wrap_text(output_text, SMALL_FONT, output_area.width - 10)
        y = output_area.y + 5
        line_h = SMALL_FONT.get_linesize()
        for ln in lines:
            if y + line_h > output_area.bottom - 5:
                break
            surf = SMALL_FONT.render(ln, True, BLACK)
            screen.blit(surf, (output_area.x + 5, y))
            y += line_h

        # 输入框
        pygame.draw.rect(
            screen,
            LIGHT_BLUE if active_input else GRAY,
            input_box,
            2,
            border_radius=8,
        )
        inp_surf = SMALL_FONT.render(user_text, True, BLACK)
        screen.blit(inp_surf, (input_box.x + 8, input_box.y + 9))

        # 发送按钮
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

