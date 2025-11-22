import pygame, math
from typing import List
from theme import (draw_vertical_gradient, SURFACE, SURFACE_LIGHT, TEXT_MAIN, TEXT_DIM,
                   DANGER, SUCCESS, WARN, CLOCK_POINTER, lerp, ease_out_cubic, TEXT_ACCENT,
                   ACCENT)
from utils import shadowed_panel, blit_text, load_font
from ui import Button, InputField, TableGrid
from page_algos import generate_steps, StepRecord
from banker import BankersAlgorithm


class BaseScreen:
    def __init__(self, app):
        self.app = app
        self.transition = 0.0

    def enter(self):
        self.transition = 0.0

    def update(self, dt):
        self.transition = min(1.0, self.transition + dt * 2)

    def draw(self, surf):
        pass

    def handle_event(self, ev):
        pass


class LoginScreen(BaseScreen):
    def __init__(self, app):
        super().__init__(app)
        self.title_font = load_font(48, app.font_path)
        self.input_font = load_font(24, app.font_path)
        self.tip_font = load_font(18, app.font_path)
        self.user_field = InputField((app.w / 2 - 180, app.h / 2 - 80, 360, 56), self.input_font, "用户名")
        self.pass_field = InputField((app.w / 2 - 180, app.h / 2, 360, 56), self.input_font, "密码")
        self.pass_field.max_len = 32
        self.login_btn = Button((app.w / 2 - 120, app.h / 2 + 90, 240, 56), "登录", self.input_font, self.try_login)

    def try_login(self):
        username = self.user_field.get_value()
        password = self.pass_field.get_value()
        if username == "admin" and password == "123456":
            self.app.launch_cpp_visualization()
            self.app.set_screen("menu")
        else:
            self.app.toast("用户名或密码错误", danger=True)

    def handle_event(self, ev):
        self.user_field.handle_event(ev)
        self.pass_field.handle_event(ev)
        self.login_btn.handle_event(ev)

    def draw(self, surf):
        draw_vertical_gradient(surf, (30, 34, 42), (15, 17, 21))
        shadowed_panel(surf, (self.app.w / 2 - 220, self.app.h / 2 - 180, 440, 380), SURFACE)
        title_surf = self.title_font.render("操作系统算法可视化", True, TEXT_MAIN)
        surf.blit(title_surf, (self.app.w / 2 - title_surf.get_width() / 2, self.app.h / 2 - 160))
        self.user_field.draw(surf)
        self.pass_field.draw(surf)
        self.login_btn.draw(surf)
        tip = self.tip_font.render("账号：admin  密码：123456", True, TEXT_DIM)
        surf.blit(tip, (self.app.w / 2 - tip.get_width() / 2, self.app.h / 2 + 155))


class MenuScreen(BaseScreen):
    def __init__(self, app):
        super().__init__(app)
        self.font_big = load_font(42, app.font_path)
        self.font_btn = load_font(26, app.font_path)
        self.btn_page = Button((app.w / 2 - 200, app.h / 2 - 60, 400, 70), "页面置换算法", self.font_btn,
                               lambda: app.set_screen("page"))
        self.btn_banker = Button((app.w / 2 - 200, app.h / 2 + 30, 400, 70), "银行家算法", self.font_btn,
                                 lambda: app.set_screen("banker"))
        self.btn_thread = Button((app.w / 2 - 200, app.h / 2 + 120, 400, 70), "多线程演示 (C++)", self.font_btn,
                                 lambda: app.launch_cpp_visualization(), color=(100, 110, 125))
        self.info_font = load_font(18, app.font_path)

    def handle_event(self, ev):
        self.btn_page.handle_event(ev)
        self.btn_banker.handle_event(ev)
        self.btn_thread.handle_event(ev)
        if ev.type == pygame.KEYDOWN and ev.key == pygame.K_ESCAPE:
            self.app.set_screen("login")

    def draw(self, surf):
        draw_vertical_gradient(surf, (26, 28, 35), (10, 12, 15))
        shadowed_panel(surf, (self.app.w / 2 - 260, self.app.h / 2 - 170, 520, 360), SURFACE)
        title = self.font_big.render("选择算法", True, TEXT_MAIN)
        surf.blit(title, (self.app.w / 2 - title.get_width() / 2, self.app.h / 2 - 150))
        self.btn_page.draw(surf)
        self.btn_banker.draw(surf)
        self.btn_thread.draw(surf)
        txt = self.info_font.render("ESC 返回登录", True, TEXT_DIM)
        surf.blit(txt, (self.app.w / 2 - txt.get_width() / 2, self.app.h / 2 + 210))


class PageReplacementScreen(BaseScreen):
    def __init__(self, app):
        super().__init__(app)
        self.font_title = load_font(36, app.font_path)
        self.font = load_font(22, app.font_path)
        self.font_small = load_font(16, app.font_path)
        self.input_seq = InputField((40, 130, 420, 50), self.font, "序列: 7,0,1,2,0,3...")
        self.input_frames = InputField((40, 190, 180, 50), self.font, "帧数")
        self.input_frames.set_numeric(True)
        self.algo_options = ["FIFO", "LRU", "CLOCK"]
        self.algo_index = 0
        self.btn_algo = Button((240, 190, 220, 50),
                               f"算法: {self.algo_options[self.algo_index]}",
                               self.font,
                               self.switch_algo,
                               color=(100, 110, 125))
        self.btn_gen = Button((40, 250, 220, 50), "生成步骤", self.font, self.generate)
        self.btn_next = Button((270, 250, 90, 50), "下一步", self.font, self.next_step)
        self.btn_prev = Button((370, 250, 90, 50), "上一步", self.font, self.prev_step)
        self.btn_play = Button((470, 250, 90, 50), "播放", self.font, self.play)
        self.btn_stop = Button((570, 250, 90, 50), "停止", self.font, self.stop)
        self.btn_reset = Button((670, 250, 90, 50), "重置", self.font, self.reset)
        self.btn_back = Button((770, 250, 120, 50), "返回(ESC)", self.font,
                               lambda: self.app.set_screen("menu"))
        self.sequence = []
        self.steps: List[StepRecord] = []
        self.current_idx = -1
        self.playing = False
        self.play_timer = 0.0
        self.animations = {}
        self.clock_angle = 0.0

    def switch_algo(self):
        self.algo_index = (self.algo_index + 1) % len(self.algo_options)
        self.btn_algo.set_text(f"算法: {self.algo_options[self.algo_index]}")

    def parse_sequence(self, s: str):
        parts = [p.strip() for p in s.replace("，", ",").replace(" ", "").split(",") if p.strip()]
        return [int(x) for x in parts]

    def generate(self):
        try:
            seq = self.parse_sequence(self.input_seq.get_value())
            if not seq:
                raise ValueError("序列为空")
            frames = int(self.input_frames.get_value() or "0")
            if frames <= 0:
                raise ValueError("帧数必须>0")
            algo = self.algo_options[self.algo_index]
            self.steps = generate_steps(algo, seq, frames)
            self.sequence = seq
            self.current_idx = -1
            self.playing = False
            self.animations.clear()
            self.app.toast(f"生成 {len(self.steps)} 步")
        except Exception as e:
            self.app.toast(str(e), danger=True)

    def next_step(self):
        if not self.steps:
            return
        if self.current_idx < len(self.steps) - 1:
            self.current_idx += 1
            self.prepare_animation()

    def prev_step(self):
        if self.current_idx > 0:
            self.current_idx -= 1
            self.prepare_animation()

    def play(self):
        if self.steps and self.current_idx < len(self.steps) - 1:
            self.playing = True

    def stop(self):
        self.playing = False

    def reset(self):
        self.current_idx = -1
        self.animations.clear()
        self.playing = False

    def prepare_animation(self):
        self.animations.clear()
        if self.current_idx < 0:
            return
        step = self.steps[self.current_idx]
        for i, _ in enumerate(step.frames):
            self.animations[i] = 0.0

    def update(self, dt):
        super().update(dt)
        if self.playing:
            self.play_timer += dt
            if self.play_timer > 0.8:
                self.play_timer = 0
                self.next_step()
            if self.current_idx >= len(self.steps) - 1:
                self.playing = False
        for k in list(self.animations.keys()):
            self.animations[k] = min(1.0, self.animations[k] + dt * 2)
        self.clock_angle += dt * 2.5

    def handle_event(self, ev):
        self.input_seq.handle_event(ev)
        self.input_frames.handle_event(ev)
        self.btn_algo.handle_event(ev)
        self.btn_gen.handle_event(ev)
        self.btn_next.handle_event(ev)
        self.btn_prev.handle_event(ev)
        self.btn_play.handle_event(ev)
        self.btn_stop.handle_event(ev)
        self.btn_reset.handle_event(ev)
        self.btn_back.handle_event(ev)
        if ev.type == pygame.KEYDOWN and ev.key == pygame.K_ESCAPE:
            self.app.set_screen("menu")

    def draw_frames(self, surf):
        title_y = 410
        if not self.steps or self.current_idx < 0:
            blit_text(surf, "插入过程：生成步骤后可查看帧演化", (40, title_y), self.font_small, TEXT_DIM)
            return
        blit_text(surf, "插入过程", (40, title_y - 24), self.font_small, TEXT_DIM)
        frame_w = 92
        frame_h = 52
        gap_x = 14
        gap_y = 12
        start_x = 40
        start_y = title_y + 20
        timeline_width = max(frame_w + gap_x, self.app.w - start_x - 320)
        max_cols = max(1, int(timeline_width // (frame_w + gap_x)))
        history_end = self.current_idx + 1
        start_idx = max(0, history_end - max_cols)
        steps_segment = self.steps[start_idx:history_end]

        for col_offset, step in enumerate(steps_segment):
            col_idx = start_idx + col_offset
            x = start_x + col_offset * (frame_w + gap_x)
            label_color = TEXT_MAIN if col_idx == self.current_idx else TEXT_DIM
            page_label = self.font_small.render(str(step.page), True, label_color)
            surf.blit(page_label, (x + (frame_w - page_label.get_width()) / 2, start_y - 32))
            for row_idx, val in enumerate(step.frames):
                rect = pygame.Rect(x, start_y + row_idx * (frame_h + gap_y), frame_w, frame_h)
                prog = self.animations.get(row_idx, 1.0) if col_idx == self.current_idx else 1.0
                rect = rect.move(0, -(1 - prog) * 30)
                base_color = (64, 70, 84)
                fill = base_color
                if step.hit and val == step.page:
                    fill = tuple(int(lerp(fill[i], SUCCESS[i], 0.7)) for i in range(3))
                elif not step.hit and step.replaced_index == row_idx:
                    fill = tuple(int(lerp(fill[i], DANGER[i], 0.65)) for i in range(3))
                elif not step.hit and val == step.page:
                    fill = tuple(int(lerp(fill[i], WARN[i], 0.65)) for i in range(3))
                if col_idx != self.current_idx:
                    fill = tuple(int(fill[i] * 0.78) for i in range(3))
                pygame.draw.rect(surf, fill, rect, border_radius=12)
                border = ACCENT if col_idx == self.current_idx else (36, 40, 50)
                pygame.draw.rect(surf, border, rect, 2, border_radius=12)
                txt = str(val) if val is not None else ""
                img = self.font.render(txt, True, TEXT_MAIN)
                surf.blit(img, (rect.x + (rect.width - img.get_width()) / 2,
                                rect.y + (rect.height - img.get_height()) / 2))

        info_x = min(self.app.w - 260, start_x + max_cols * (frame_w + gap_x) + 30)
        self.draw_algo_state(surf, info_x, start_y)

    def draw_algo_state(self, surf, info_x, start_y):
        if not self.steps or self.current_idx < 0:
            return
        step = self.steps[self.current_idx]
        info_y = start_y - 36
        if "fifo_ptr" in step.algorithm_state:
            blit_text(surf, f"FIFO指针 -> {step.algorithm_state['fifo_ptr']}", (info_x, info_y), self.font_small, TEXT_DIM)
            info_y += 24
        if "clock_hand" in step.algorithm_state:
            use_bits = step.algorithm_state["use"]
            hand = step.algorithm_state["clock_hand"]
            cx = min(self.app.w - 120, info_x + 120)
            cy = start_y + 120
            radius = 95
            pygame.draw.circle(surf, (80, 88, 104), (cx, cy), radius, 3)
            n = len(use_bits)
            for idx, b in enumerate(use_bits):
                ang = math.pi * 2 * idx / n - math.pi / 2
                tx = cx + math.cos(ang) * (radius - 16)
                ty = cy + math.sin(ang) * (radius - 16)
                dot_color = SUCCESS if b == 1 else (120, 130, 140)
                pygame.draw.circle(surf, dot_color, (int(tx), int(ty)), 12)
                num_img = self.font_small.render(str(idx), True, TEXT_MAIN)
                surf.blit(num_img, (int(tx) - num_img.get_width() / 2, int(ty) - num_img.get_height() / 2))
            hand_ang = math.pi * 2 * hand / n - math.pi / 2
            hx = cx + math.cos(hand_ang) * (radius - 32)
            hy = cy + math.sin(hand_ang) * (radius - 32)
            pygame.draw.line(surf, CLOCK_POINTER, (cx, cy), (hx, hy), 4)
            blit_text(surf, f"CLOCK指针 -> {hand}", (info_x, cy + radius + 20), self.font_small, TEXT_DIM)

    def draw_status(self, surf):
        base_y = 320
        if not self.steps or self.current_idx < 0:
            blit_text(surf, "准备：输入序列与帧数 -> 生成步骤 -> 下一步", (40, base_y + 20), self.font_small, TEXT_DIM)
            return
        step = self.steps[self.current_idx]
        status = f"Step {step.index + 1}/{len(self.steps)} 访问页 {step.page} | {'命中' if step.hit else '缺页'}"
        blit_text(surf, status, (40, base_y + 24), self.font_small, TEXT_MAIN)
        viewed = self.steps[:self.current_idx + 1]
        faults = sum(1 for s in viewed if not s.hit)
        hits = len(viewed) - faults
        rate = hits / len(viewed) * 100 if viewed else 0
        stats = (f"累计：{len(viewed)}/{len(self.steps)} 步 | 命中率 {rate:.2f}%"
                 f" | 命中 {hits} | 缺页 {faults}")
        blit_text(surf, stats, (40, base_y), self.font_small, TEXT_DIM)
        next_page = self.steps[self.current_idx + 1].page if self.current_idx + 1 < len(self.steps) else None
        if next_page is not None:
            hint = (f"下一次访问：{next_page} | 剩余 {len(self.steps) - len(viewed)} 页 | "
                    f"算法：{self.algo_options[self.algo_index]}")
        else:
            hint = f"序列已结束 | 算法：{self.algo_options[self.algo_index]}"
        blit_text(surf, hint, (40, base_y - 22), self.font_small, TEXT_DIM)

    def draw(self, surf):
        draw_vertical_gradient(surf, (22, 24, 30), (8, 10, 12))
        shadowed_panel(surf, (20, 90, self.app.w - 40, self.app.h - 110), SURFACE_LIGHT)
        title_text = "页面置换算法模拟"
        title = self.font_title.render(title_text, True, TEXT_MAIN)
        surf.blit(title, (self.app.w / 2 - title.get_width() / 2, 40))
        self.input_seq.draw(surf)
        self.input_frames.draw(surf)
        self.btn_algo.draw(surf)
        for b in [self.btn_gen, self.btn_next, self.btn_prev, self.btn_play, self.btn_stop, self.btn_reset, self.btn_back]:
            b.draw(surf)
        self.draw_status(surf)
        if self.steps and self.current_idx >= 0:
            self.draw_frames(surf)


class BankerScreen(BaseScreen):
    def __init__(self, app):
        super().__init__(app)
        self.font_title = load_font(34, app.font_path)
        self.font = load_font(20, app.font_path)
        self.font_small = load_font(16, app.font_path)
        self.n = 5
        self.m = 3
        self.alloc = TableGrid(40, 220, self.n, self.m, font=self.font_small)
        self.max_tab = TableGrid(40 + self.m * 80 + 40, 220, self.n, self.m, font=self.font_small)
        self.available_field = InputField((40, 180, 320, 50), self.font, "Available: 3,3,2")
        self.pid_field = InputField((380, 180, 180, 50), self.font, "进程ID")
        self.pid_field.set_numeric(True)
        self.req_field = InputField((580, 180, 240, 50), self.font, "请求向量: 1,0,2")
        self.req_field.set_numeric(True)
        self.btn_resize = Button((40, 130, 240, 40), "设置规模(n,m)", self.font_small, self.resize)
        self.btn_compute = Button((340, 130, 180, 40), "计算安全性", self.font_small, self.compute)
        self.btn_request = Button((540, 130, 180, 40), "请求资源", self.font_small, self.request)
        self.btn_back = Button((740, 130, 180, 40), "返回(ESC)", self.font_small,
                               lambda: self.app.set_screen("menu"))
        self.algo = None
        self.safe_seq = []
        self.trace = []
        self.trace_anim = 0.0
        self.selected_trace = -1

    def resize(self):
        try:
            val = self.available_field.get_value()
            if "n=" in val and "m=" in val:
                parts = val.split(",")
                n = int(parts[0].split("=")[1])
                m = int(parts[1].split("=")[1])
                if n < 1 or m < 1 or n > 15 or m > 10:
                    raise ValueError("规模不合理")
                self.n = n
                self.m = m
                self.alloc = TableGrid(40, 220, self.n, self.m, font=self.font_small)
                self.max_tab = TableGrid(40 + self.m * 80 + 40, 220, self.n, self.m, font=self.font_small)
                self.app.toast("矩阵规模已改变，请填写数据")
            else:
                self.app.toast("格式示例: n=5,m=3", danger=True)
        except Exception as e:
            self.app.toast(str(e), danger=True)

    def parse_vector(self, txt: str, m: int):
        parts = [p.strip() for p in txt.replace("，", ",").split(",") if p.strip()]
        if len(parts) != m:
            raise ValueError(f"向量长度应为 {m}")
        return [int(x) for x in parts]

    def compute(self):
        try:
            alloc = self.alloc.get_matrix()
            maximum = self.max_tab.get_matrix()
            avail_raw = self.available_field.get_value()
            if " " in avail_raw:
                avail_raw = avail_raw.split()[-1]
            avail = self.parse_vector(avail_raw, self.m)
            self.algo = BankersAlgorithm(alloc, maximum, avail)
            safe, seq, trace = self.algo.is_safe_state()
            self.safe_seq = seq if safe else []
            self.trace = trace
            self.selected_trace = -1
            self.app.toast("安全" if safe else "不安全", danger=(not safe))
        except Exception as e:
            self.app.toast(str(e), danger=True)

    def request(self):
        if not self.algo:
            self.app.toast("先计算安全性", danger=True)
            return
        try:
            pid = int(self.pid_field.get_value() or "0")
            if pid < 0 or pid >= self.n:
                raise ValueError("PID越界")
            req = self.parse_vector(self.req_field.get_value(), self.m)
            ok, msg = self.algo.request(pid, req)
            safe, seq, trace = self.algo.is_safe_state()
            self.safe_seq = seq if safe else []
            self.trace = trace
            self.app.toast(msg, danger=not ok)
        except Exception as e:
            self.app.toast(str(e), danger=True)

    def update(self, dt):
        super().update(dt)
        self.trace_anim += dt * 0.7

    def handle_event(self, ev):
        self.alloc.handle_event(ev)
        self.max_tab.handle_event(ev)
        self.available_field.handle_event(ev)
        self.pid_field.handle_event(ev)
        self.req_field.handle_event(ev)
        self.btn_resize.handle_event(ev)
        self.btn_compute.handle_event(ev)
        self.btn_request.handle_event(ev)
        self.btn_back.handle_event(ev)
        if ev.type == pygame.KEYDOWN and ev.key == pygame.K_ESCAPE:
            self.app.set_screen("menu")

    def draw_trace(self, surf):
        base_x = 40 + self.m * 80 * 2 + 120
        y = 220
        blit_text(surf, "安全性检查轨迹:", (base_x, y - 30), self.font_small, TEXT_ACCENT)
        line_gap = 30
        for i, row in enumerate(self.trace):
            color = SUCCESS if i < len(self.safe_seq) else TEXT_DIM
            text = f"P{row['process']} Work:{row['work_before']} Need:{row['need']} Alloc:{row['allocation']}"
            blit_text(surf, text, (base_x, y + i * line_gap), self.font_small, color)

    def draw(self, surf):
        draw_vertical_gradient(surf, (22, 24, 30), (8, 10, 12))
        shadowed_panel(surf, (20, 90, self.app.w - 40, self.app.h - 110), SURFACE_LIGHT)
        title_text = "银行家算法模拟"
        title = self.font_title.render(title_text, True, TEXT_MAIN)
        surf.blit(title, (self.app.w / 2 - title.get_width() / 2, 40))
        self.available_field.draw(surf)
        self.pid_field.draw(surf)
        self.req_field.draw(surf)
        for b in [self.btn_resize, self.btn_compute, self.btn_request, self.btn_back]:
            b.draw(surf)
        blit_text(surf, f"矩阵规模: n={self.n} m={self.m}", (380, 70), self.font_small, TEXT_DIM)
        blit_text(surf, f"安全序列: {self.safe_seq if self.safe_seq else '无 / 未安全'}",
                  (380, 95), self.font_small,
                  TEXT_MAIN if self.safe_seq else DANGER)
        blit_text(surf, "Allocation", (40, 190), self.font_small, TEXT_DIM)
        blit_text(surf, "Max", (40 + self.m * 80 + 40, 190), self.font_small, TEXT_DIM)
        self.alloc.draw(surf)
        self.max_tab.draw(surf)
        self.draw_trace(surf)