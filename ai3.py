import os
import pygame
import threading
from volcenginesdkarkruntime import Ark

class AIChatScreen:
    def __init__(self, app):
        self.app = app
        self.client = Ark(
            base_url="https://ark.cn-beijing.volces.com/api/v3",
            api_key=os.getenv("DOUBAO_API_KEY", "b422a41f-6be4-4872-863b-e97889c46a32")
        )

        # 颜色
        self.BG_COLOR = (9, 16, 25)
        self.AI_BUBBLE = (51, 51, 51)
        self.USER_BUBBLE = (0, 180, 120)
        self.WHITE = (255, 255, 255)
        self.LIGHT_GRAY = (180, 180, 180)

        # 字体
        self.FONT = self.load_chinese_font(26)
        self.SMALL_FONT = self.load_chinese_font(22)

        # 头像
        self.ai_avatar = pygame.image.load("ai.png").convert_alpha()
        self.ai_avatar = pygame.transform.smoothscale(self.ai_avatar, (52, 52))
        self.user_avatar = pygame.image.load("user.png").convert_alpha()
        self.user_avatar = pygame.transform.smoothscale(self.user_avatar, (52, 52))
        self.AVATAR_SIZE = 52
        self.AVATAR_MARGIN_X = 15
        self.AVATAR_MARGIN_Y = 10

        # 输入区
        self.INPUT_HEIGHT = 70
        self.input_box = pygame.Rect(15, self.app.h - self.INPUT_HEIGHT + 15,
                                     self.app.w - 120, self.INPUT_HEIGHT - 25)
        self.send_box = pygame.Rect(self.app.w - 90, self.app.h - self.INPUT_HEIGHT + 15,
                                    70, self.INPUT_HEIGHT - 25)
        self.user_text = ""
        self.active_input = True

        # 消息
        self.messages = [{"sender": "ai", "text": "嗨，我是豆包 AI，小哀在线值班，有什么想聊的吗？"}]
        self.streaming = False

    # --------------------
    # 字体加载
    # --------------------
    def load_chinese_font(self, size):
        candidates = [
            r"C:\Windows\Fonts\msyh.ttc",
            r"C:\Windows\Fonts\simhei.ttf",
            r"C:\Windows\Fonts\simsun.ttc",
        ]
        for path in candidates:
            if os.path.exists(path):
                return pygame.font.Font(path, size)
        return pygame.font.SysFont("SimHei", size)

    # --------------------
    # 文本换行
    # --------------------
    def wrap_text(self, text, font, max_width):
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

    # --------------------
    # 调用 AI
    # --------------------
    def call_ai(self, question):
        self.streaming = True
        ai_msg = {"sender": "ai", "text": ""}
        self.messages.append(ai_msg)

        def run_stream():
            try:
                stream = self.client.chat.completions.create(
                    model="doubao-seed-1-6-251015",
                    messages=[{"role": "user", "content":[{"type": "text", "text": question}]}],
                    reasoning_effort="medium",
                    stream=True,
                )
                for chunk in stream:
                    if chunk.choices and chunk.choices[0].delta.content:
                        ai_msg["text"] += chunk.choices[0].delta.content
            except Exception as e:
                ai_msg["text"] += f"\n[错误] {e}"
            finally:
                self.streaming = False

        threading.Thread(target=run_stream, daemon=True).start()

    # --------------------
    # 发送消息
    # --------------------
    def send_user_message(self):
        text = self.user_text.strip()
        if not text:
            return
        self.messages.append({"sender": "user", "text": text})
        self.user_text = ""
        self.call_ai(text)

    # --------------------
    # 页面接口
    # --------------------
    def enter(self):
        pygame.key.start_text_input()
        pygame.key.set_repeat(500, 40)

    def handle_event(self, event):
        if event.type == pygame.TEXTINPUT and self.active_input:
            self.user_text += event.text
        elif event.type == pygame.KEYDOWN and self.active_input:
            if event.key == pygame.K_BACKSPACE:
                self.user_text = self.user_text[:-1]
            elif event.key == pygame.K_RETURN:
                self.send_user_message()
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if self.send_box.collidepoint(event.pos):
                self.send_user_message()

    def update(self, dt):
        pass  # 可加动画

    def draw(self, surface):
        surface.fill(self.BG_COLOR)
        # 标题
        title = self.FONT.render("灰原哀 · 豆包 AI", True, self.WHITE)
        surface.blit(title, (20, 10))

        # 聊天消息
        self.draw_chat_area(surface)

        # 输入区
        pygame.draw.rect(surface, (20,28,36), (0, self.app.h - self.INPUT_HEIGHT, self.app.w, self.INPUT_HEIGHT))
        pygame.draw.rect(surface, (40,50,60), self.input_box, border_radius=12)
        input_text_surface = self.SMALL_FONT.render(
            self.user_text if self.user_text else "请输入内容…", True,
            self.WHITE if self.user_text else self.LIGHT_GRAY
        )
        surface.blit(input_text_surface, (self.input_box.x + 10, self.input_box.y + 10))

        pygame.draw.rect(surface, (0,160,230), self.send_box, border_radius=12)
        send_text = self.SMALL_FONT.render("发送", True, self.WHITE)
        surface.blit(send_text, (
            self.send_box.x + (self.send_box.width - send_text.get_width()) / 2,
            self.send_box.y + (self.send_box.height - send_text.get_height()) / 2
        ))

        # AI 思考中
        if self.streaming:
            status_surf = self.SMALL_FONT.render("AI 思考中…", True, self.LIGHT_GRAY)
            surface.blit(status_surf, (15, self.app.h - self.INPUT_HEIGHT - 25))

    def draw_chat_area(self, surface):
        top_margin = 50
        bottom_limit = self.app.h - self.INPUT_HEIGHT - 10
        y = bottom_limit
        max_bubble_width = self.app.w - 160

        for msg in reversed(self.messages):
            sender = msg["sender"]
            text = msg["text"]
            lines = self.wrap_text(text, self.SMALL_FONT, max_bubble_width)
            line_height = self.SMALL_FONT.get_linesize()
            bubble_height = line_height * len(lines) + 16

            if sender == "ai":
                avatar_x = self.AVATAR_MARGIN_X
                avatar_y = y - bubble_height - self.AVATAR_MARGIN_Y - self.AVATAR_SIZE
                bubble_x = self.AVATAR_MARGIN_X + self.AVATAR_SIZE + 10
            else:
                avatar_x = self.app.w - self.AVATAR_MARGIN_X - self.AVATAR_SIZE
                avatar_y = y - bubble_height - self.AVATAR_MARGIN_Y - self.AVATAR_SIZE
                max_line_width = max([self.SMALL_FONT.size(ln)[0] for ln in lines] or [0])
                bubble_width = max_line_width + 20
                bubble_x = avatar_x - 10 - bubble_width
            bubble_y = avatar_y + (self.AVATAR_SIZE - bubble_height)
            if bubble_y < top_margin:
                break

            # 绘制头像
            surface.blit(self.ai_avatar if sender=="ai" else self.user_avatar, (avatar_x, avatar_y))
            max_line_width = max([self.SMALL_FONT.size(ln)[0] for ln in lines] or [0])
            bubble_width = max_line_width + 20
            bubble_color = self.AI_BUBBLE if sender=="ai" else self.USER_BUBBLE
            text_color = self.WHITE
            bubble_rect = pygame.Rect(bubble_x, bubble_y, bubble_width, bubble_height)
            pygame.draw.rect(surface, bubble_color, bubble_rect, border_radius=12)
            text_y = bubble_y + 8
            for ln in lines:
                txt_surf = self.SMALL_FONT.render(ln, True, text_color)
                surface.blit(txt_surf, (bubble_x + 10, text_y))
                text_y += line_height
            y = bubble_y - 15
