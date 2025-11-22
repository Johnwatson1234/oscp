# import pygame, sys, os, time
# from screens import LoginScreen, MenuScreen, PageReplacementScreen, BankerScreen
# from utils import load_font
# from theme import TEXT_MAIN, DANGER, SUCCESS
# from utils import create_surface
# class App:
#     def __init__(self, width=1280, height=760):
#         pygame.init()
#         pygame.display.set_caption("操作系统算法可视化教学系统 (Pygame)")
#         self.w=width; self.h=height
#         self.screen=pygame.display.set_mode((self.w,self.h))
#         self.clock=pygame.time.Clock()
#         self.font_path = self._detect_font()
#         self.font_toast=load_font(20, self.font_path)

#         self.screens={
#             "login": LoginScreen(self),
#             "menu": MenuScreen(self),
#             "page": PageReplacementScreen(self),
#             "banker": BankerScreen(self)
#         }
#         self.current="login"
#         self.screens[self.current].enter()
#         self.toast_msg=""
#         self.toast_timer=0
#         self.toast_color = SUCCESS
#         self.running=True

#     def _detect_font(self):
#         # 允许使用 assets/Font.ttf
#         if os.path.exists("assets/Font.ttf"):
#             return "assets/Font.ttf"
#         return None

#     def set_screen(self, name):
#         if name in self.screens:
#             self.current=name
#             self.screens[name].enter()

#     def toast(self, msg, danger=False):
#         self.toast_msg=msg
#         self.toast_timer=2.5
#         self.toast_color = DANGER if danger else SUCCESS

#     def run(self):
#         while self.running:
#             dt = self.clock.tick(60)/1000.0
#             for ev in pygame.event.get():
#                 if ev.type==pygame.QUIT:
#                     self.running=False
#                 else:
#                     self.screens[self.current].handle_event(ev)
#             self.screens[self.current].update(dt)
#             self.draw()
#         pygame.quit()
#         sys.exit()

#     def draw(self):
#         self.screens[self.current].draw(self.screen)
#         if self.toast_timer > 0:
#             self.toast_timer -= self.clock.get_time() / 1000.0
#             alpha = min(1.0, self.toast_timer / 2.5 * 1.4)
#             surf = create_surface(self.w, 60, True)
#             base_color = self.toast_color[:3] if len(self.toast_color) >= 3 else (255, 255, 255)
#             toast_color = (*base_color, max(0, min(255, int(200 * alpha))))
#             pygame.draw.rect(surf, toast_color, (0, 0, self.w, 60))
#             txt = self.font_toast.render(self.toast_msg, True, (255, 255, 255))
#             self.screen.blit(surf, (0, self.h - 70))
#             self.screen.blit(txt, (40, self.h - 70 + (60 - txt.get_height()) / 2))
#         pygame.display.flip()
# if __name__=="__main__":
#     App().run()

import pygame, sys, os, subprocess
from screens import LoginScreen, MenuScreen, PageReplacementScreen, BankerScreen
from utils import load_font
from theme import TEXT_MAIN, DANGER, SUCCESS
from utils import create_surface

class App:
    def __init__(self, width=1280, height=760):
        pygame.init()
        pygame.display.set_caption("操作系统算法可视化教学系统 (Pygame)")
        self.w=width; self.h=height
        self.screen=pygame.display.set_mode((self.w,self.h))
        self.clock=pygame.time.Clock()
        self.font_path = self._detect_font()
        self.font_toast=load_font(20, self.font_path)

        self.screens={
            "login": LoginScreen(self),
            "menu": MenuScreen(self),
            "page": PageReplacementScreen(self),
            "banker": BankerScreen(self)
        }
        self.current="login"
        self.screens[self.current].enter()
        self.toast_msg=""
        self.toast_timer=0
        self.toast_color = SUCCESS
        self.running=True

    def _detect_font(self):
        if os.path.exists("assets/Font.ttf"):
            return "assets/Font.ttf"
        return None

    def set_screen(self, name):
        if name in self.screens:
            self.current=name
            self.screens[name].enter()

    def launch_cpp_visualization(self, thread_count=8):
        exe_path = os.path.abspath("Multithreading.exe")
        if not os.path.exists(exe_path):
            self.toast("未找到 Multithreading.exe", danger=True)
            return
        creation_flags = 0
        if sys.platform.startswith("win"):
            creation_flags = subprocess.CREATE_NEW_CONSOLE
        try:
            subprocess.Popen([exe_path, str(thread_count)], creationflags=creation_flags)
            self.toast("已启动 C++ 多线程演示窗口")
        except Exception as exc:
            self.toast(f"启动失败: {exc}", danger=True)

    def toast(self, msg, danger=False):
        self.toast_msg=msg
        self.toast_timer=2.5
        self.toast_color = DANGER if danger else SUCCESS

    def run(self):
        while self.running:
            dt = self.clock.tick(60)/1000.0
            for ev in pygame.event.get():
                if ev.type==pygame.QUIT:
                    self.running=False
                else:
                    self.screens[self.current].handle_event(ev)
            self.screens[self.current].update(dt)
            self.draw()
        pygame.quit()
        sys.exit()

    def draw(self):
        self.screens[self.current].draw(self.screen)
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

if __name__=="__main__":
    App().run()