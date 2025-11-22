# 登录界面按esc键也有效
# app6.py
# -*- coding: utf-8 -*-
import pygame, sys, os, subprocess
from screens import LoginScreen, MenuScreen, PageReplacementScreen, BankerScreen
from ai3 import AIChatScreen
from utils import load_font, create_surface
from theme import TEXT_MAIN, DANGER, SUCCESS

class App:
    def __init__(self, width=1280, height=760):
        pygame.init()
        pygame.display.set_caption("操作系统算法可视化教学系统 (Pygame)")
        self.w = width
        self.h = height
        # 创建主屏幕
        self.screen = pygame.display.set_mode((self.w, self.h))
        self.clock = pygame.time.Clock()
        self.font_path = self._detect_font()
        self.font_toast = load_font(20, self.font_path)

        # 所有页面
        self.screens = {
            "login": LoginScreen(self),
            "menu": MenuScreen(self),
            "page": PageReplacementScreen(self),
            "banker": BankerScreen(self),
            "ai": AIChatScreen(self)
        }

        # 默认显示登录页
        self.current = "login"
        self.previous_screen = "menu"  # 进入AI前的页面
        self.screens[self.current].enter()

        # toast 提示
        self.toast_msg = ""
        self.toast_timer = 0
        self.toast_color = SUCCESS

        # AI 图标（右下角）
        self.ai_icon = pygame.image.load("ai_button.png").convert_alpha()
        self.ai_icon = pygame.transform.smoothscale(self.ai_icon, (65, 65))
        self.ai_rect = self.ai_icon.get_rect(bottomright=(self.w - 20, self.h - 20))

        self.running = True

    def _detect_font(self):
        if os.path.exists("assets/Font.ttf"):
            return "assets/Font.ttf"
        return None

    def set_screen(self, name):
        """切换页面"""
        if name in self.screens:
            if name == "ai":
                # 保存进入 AI 前的页面
                self.previous_screen = self.current
            self.current = name
            self.screens[name].enter()

    def toast(self, msg, danger=False):
        self.toast_msg = msg
        self.toast_timer = 2.5
        self.toast_color = DANGER if danger else SUCCESS

    def launch_cpp_visualization(self, thread_count=8):
        exe_path = os.path.abspath("multithreading.exe")
        exe_path = os.path.abspath("m4.exe")
        if not os.path.exists(exe_path):
            self.toast("未找到 multithreading.exe", danger=True)
            return
        creation_flags = 0
        if sys.platform.startswith("win"):
            creation_flags = subprocess.CREATE_NEW_CONSOLE
        try:
            subprocess.Popen([exe_path, str(thread_count)], creationflags=creation_flags)
            self.toast("已启动 C++ 多线程演示窗口")
        except Exception as exc:
            self.toast(f"启动失败: {exc}", danger=True)

    def run(self):
        while self.running:
            dt = self.clock.tick(60) / 1000.0
            for ev in pygame.event.get():
                if ev.type == pygame.QUIT:
                    self.running = False
                else:
                    self.screens[self.current].handle_event(ev)

                # 点击右下角 AI 图标，登录页和 AI 页不可用
                if ev.type == pygame.MOUSEBUTTONDOWN:
                    if self.current != "login" and self.current != "ai" and self.ai_rect.collidepoint(ev.pos):
                        self.set_screen("ai")

                # 按 ESC 键处理逻辑
                if ev.type == pygame.KEYDOWN:
                    if ev.key == pygame.K_ESCAPE:
                        if self.current == "ai":
                            # AI 页面返回上一个页面
                            self.set_screen(self.previous_screen)
                        elif self.current == "login":
                            # 登录页直接退出程序
                            self.running = False
                        # 其他页面可自定义逻辑（这里暂不处理）

            self.screens[self.current].update(dt)
            self.draw()

        pygame.quit()
        sys.exit()

    def draw(self):
        # 绘制当前页面
        self.screens[self.current].draw(self.screen)

        # 右下角 AI 图标：登录页和 AI 页不显示
        if self.current != "login" and self.current != "ai":
            self.screen.blit(self.ai_icon, self.ai_rect)

        # toast 提示
        if self.toast_timer > 0:
            self.toast_timer -= self.clock.get_time() / 1000.0
            alpha = min(1.0, self.toast_timer / 2.5 * 1.4)
            surf = create_surface(self.w, 60, True)
            base_color = self.toast_color[:3] if len(self.toast_color) >= 3 else (255, 255, 255)
            toast_color = (*base_color, max(0, min(255, int(200 * alpha))))
            pygame.draw.rect(surf, toast_color, (0, 0, self.w, 60))
            txt = self.font_toast.render(self.toast_msg, True, (255, 255, 255))
            self.screen.blit(surf, (0, self.h - 70))
            self.screen.blit(txt, (40, self.h - 70 + (60 - txt.get_height()) / 2))

        pygame.display.flip()


if __name__ == "__main__":
    App().run()
