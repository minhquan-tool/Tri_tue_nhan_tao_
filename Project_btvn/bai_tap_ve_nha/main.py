import pygame
import sys
import time
import random
import math

import pygame.mouse
import pygame.draw
import pygame.display
import pygame.event

from modun.bfs import BFS
from modun.bfs_fast import BFS_FAST
from modun.dfs import DFS
from modun.dfs_optimal import DFS_OPTIMAL
from modun.ucs import UCS
from modun.ids import IDS
from modun.ids_early import IDS_EARLY
from modun.greedy_algorithm import GREEDYALGORITHM
from modun.a_star import A_STAR
from modun.ida_star import IDA_STAR
from modun.simple_hill_climbing import SIMPLE_HC
from modun.ignorant_hill_climbing import IGNORANT_HC
from modun.random_hill_climbing import RANDOM_HC

ALG_MAP = {
    "BFS": BFS(),
    "BFS Fast": BFS_FAST(),
    "DFS": DFS(),
    "DFS Optimal": DFS_OPTIMAL(),
    "UCS": UCS(),
    "IDS": IDS(),
    "IDS EARLY": IDS_EARLY(),
    "GREEDY ALGORITHM": GREEDYALGORITHM(),
    "A STAR": A_STAR(),
    "IDA STAR": IDA_STAR(),
    "SIMPLE_HC": SIMPLE_HC(), 
    "IGNORANT_HC": IGNORANT_HC(),
    "RANDOM_HC": RANDOM_HC(),
}

pygame.init()

HAS_FONT = True
try:
    import pygame.font
    pygame.font.init()
    FONT_XS  = pygame.font.SysFont("Consolas", 13)
    FONT_SM  = pygame.font.SysFont("Consolas", 15)
    FONT_MD  = pygame.font.SysFont("Consolas", 18, bold=True)
    FONT_LG  = pygame.font.SysFont("Consolas", 22, bold=True)
    FONT_XL  = pygame.font.SysFont("Consolas", 28, bold=True)
except Exception:
    HAS_FONT = False

class FallbackFont:
    def __init__(self, size): self.size = size
    def render(self, text, antialias, color):
        w = len(text) * (self.size // 2); h = self.size
        s = pygame.Surface((w, h), pygame.SRCALPHA)
        pygame.draw.rect(s, (*color, 40), (0,0,w,h), border_radius=3)
        return s
    def size(self, text): return (len(text)*8, self.size)

if not HAS_FONT:
    FONT_XS = FONT_SM = FONT_MD = FONT_LG = FONT_XL = FallbackFont(16)

C = {
    "bg":         (12,  14,  20),
    "panel":      (20,  23,  32),
    "panel2":     (26,  30,  42),
    "border":     (45,  50,  70),
    "border_hi":  (80,  90, 130),
    "text":       (220, 225, 240),
    "text_dim":   (100, 110, 140),
    "accent":     (80,  160, 255),
    "accent2":    (50,  220, 140),
    "accent3":    (255, 180,  60),
    "robot":      (80,  170, 255),
    "dirt":       (210, 160,  70),
    "obstacle":   (55,  58,  78),
    "obstacle_b": (75,  80, 108),
    "cleaned":    (40,  190, 110),
    "wall":       (35,  40,  55),
    "grid_bg":    (18,  20,  28),
    "red":        (220,  80,  80),
    "hover":      (35,  40,  58),
}

WIDTH, HEIGHT = 980, 680
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Project_BTVN")


def draw_rect_border(surf, color, border_color, rect, radius=6, bw=1):
    pygame.draw.rect(surf, color, rect, border_radius=radius)
    pygame.draw.rect(surf, border_color, rect, width=bw, border_radius=radius)

def draw_text_centered(surf, font, text, color, rect):
    t = font.render(text, True, color)
    x = rect.x + (rect.width  - t.get_width())  // 2
    y = rect.y + (rect.height - t.get_height()) // 2
    surf.blit(t, (x, y))

def draw_glow_circle(surf, color, pos, r, alpha=60):
    glow = pygame.Surface((r*4, r*4), pygame.SRCALPHA)
    for i in range(3):
        a = alpha // (i+1)
        rr = r + i*4
        pygame.draw.circle(glow, (*color, a), (r*2, r*2), rr)
    surf.blit(glow, (pos[0]-r*2, pos[1]-r*2), special_flags=pygame.BLEND_RGBA_ADD)

def lerp_color(a, b, t):
    return tuple(int(a[i] + (b[i]-a[i])*t) for i in range(3))


class Button:
    def __init__(self, rect, label, color, hover_color=None, font=None, text_color=None, radius=7):
        self.rect        = pygame.Rect(rect)
        self.label       = label
        self.color       = color
        self.hover_color = hover_color or lerp_color(color, (255,255,255), 0.15)
        self.font        = font or FONT_MD
        self.text_color  = text_color or C["text"]
        self.radius      = radius
        self._anim       = 0.0

    def draw(self, surf, mouse_pos):
        hovered = self.rect.collidepoint(mouse_pos)
        self._anim = min(1.0, self._anim + 0.15) if hovered else max(0.0, self._anim - 0.15)
        col = lerp_color(self.color, self.hover_color, self._anim)
        border = lerp_color(C["border"], C["border_hi"], self._anim)
        draw_rect_border(surf, col, border, self.rect, self.radius)
        draw_text_centered(surf, self.font, self.label, self.text_color, self.rect)

    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)


# ── AlgoButton: nút chọn thuật toán hiển thị thẳng trên màn hình ──
class AlgoButton:
    def __init__(self, rect, label):
        self.rect  = pygame.Rect(rect)
        self.label = label
        self._anim = 0.0

    def draw(self, surf, mouse_pos, is_active):
        hovered = self.rect.collidepoint(mouse_pos)
        self._anim = min(1.0, self._anim + 0.15) if hovered else max(0.0, self._anim - 0.15)

        if is_active:
            bg     = (30, 60, 110)
            border = C["accent"]
            tc     = C["accent"]
        elif hovered:
            bg     = lerp_color(C["panel2"], C["hover"], self._anim)
            border = C["border_hi"]
            tc     = C["text"]
        else:
            bg     = C["panel2"]
            border = C["border"]
            tc     = C["text_dim"]

        draw_rect_border(surf, bg, border, self.rect, radius=6)

        # thanh accent trái khi active
        if is_active:
            pygame.draw.rect(surf, C["accent"],
                             pygame.Rect(self.rect.x + 1, self.rect.y + 4, 3, self.rect.height - 8),
                             border_radius=2)

        t = FONT_XS.render(self.label, True, tc)
        x = self.rect.x + (self.rect.width  - t.get_width())  // 2
        y = self.rect.y + (self.rect.height - t.get_height()) // 2
        surf.blit(t, (x, y))

    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)


class Visualizer:
    def __init__(self):
        self.grid_m = 5
        self.grid_n = 5
        self.active_input = None
        self.input_text   = ""

        self.grid_data = [[0]*5 for _ in range(5)]

        self.algorithms   = list(ALG_MAP.keys())
        self.current_algo = self.algorithms[0]

        self.PANEL_LEFT = 30
        self.PANEL_TOP  = 260
        self.GRID_X     = 30
        self.GRID_Y     = 290
        self.GRID_MAX   = 300
        self.RIGHT_X    = 390
        self.RIGHT_W    = WIDTH - self.RIGHT_X - 20

        # ── Xây dựng lưới nút thuật toán ──────────────────────────────
        ALGO_START_X = self.PANEL_LEFT
        ALGO_START_Y = 108          
        ALGO_BTN_W   = 115
        ALGO_BTN_H   = 28
        ALGO_GAP_X   = 6
        ALGO_GAP_Y   = 6
        ALGO_COLS    = 3      

        self.algo_buttons = []
        for i, name in enumerate(self.algorithms):
            col = i % ALGO_COLS
            row = i // ALGO_COLS
            rx  = ALGO_START_X + col * (ALGO_BTN_W + ALGO_GAP_X)
            ry  = ALGO_START_Y + row * (ALGO_BTN_H + ALGO_GAP_Y)
            self.algo_buttons.append(AlgoButton((rx, ry, ALGO_BTN_W, ALGO_BTN_H), name))
        

        self.btn_rand  = Button((660, 28, 130, 38), "RANDOM", (130, 100, 40), radius=7)
        self.btn_run   = Button((805, 28, 150, 38), "RUN", (30, 140, 80), radius=7,
                                text_color=(200, 255, 220))
        self.btn_reset = Button((805, 28, 150, 38), "STOP", (140, 40, 40), radius=7,
                                text_color=(255, 200, 200))

        self.logs               = []
        self.final_result       = None
        self.running_simulation = False
        self.sim_index          = 0
        self.current_sim_state  = None
        self._tick              = 0
        self._status_msg        = ""
        self._status_color      = C["text_dim"]

        self.randomize_dirt()
        self.reset_env()

    def reset_env(self):
        self.logs               = ["[ Click ô lưới để vẽ VẬT CẢN ]"]
        self.final_result       = None
        self.running_simulation = False
        self.sim_index          = 0
        self._status_msg        = "Chờ lệnh..."
        self._status_color      = C["text_dim"]
        tg = tuple(tuple(r) for r in self.grid_data)
        self.current_sim_state  = (0, 0, tg)

    def apply_new_dimensions(self, m, n):
        pass

    def randomize_dirt(self):
        for r in range(self.grid_m):
            for c in range(self.grid_n):
                if r == 0 and c == 0:
                    self.grid_data[r][c] = 0
                elif self.grid_data[r][c] != 2:
                    self.grid_data[r][c] = 1 if random.random() < 0.4 else 0
        self.reset_env()

    def run_algorithm(self):
        self.running_simulation = False
        self.sim_index          = 0
        tg                      = tuple(tuple(r) for r in self.grid_data)
        start_state             = (0, 0, tg)
        self.current_sim_state  = start_state
        self._status_msg        = f"Đang chạy {self.current_algo}..."
        self._status_color      = C["accent3"]

        algo_instance = ALG_MAP[self.current_algo]
        path, algo_logs = algo_instance.solve(start_state)

        self.final_result = path if path is not None else "Không tìm thấy đường đi!"
        self.logs         = algo_logs[-14:]

        if path and isinstance(path, list):
            self.running_simulation = True
            self._status_msg   = f"Mô phỏng đường chạy: {len(path)} bước"
            self._status_color = C["accent2"]
        else:
            self._status_msg   = "Không có đường đi!"
            self._status_color = C["red"]

    def update_simulation(self):
        if not (self.running_simulation and isinstance(self.final_result, list)):
            return
        if self.sim_index < len(self.final_result):
            action = self.final_result[self.sim_index]
            rx, ry, current_dirt = self.current_sim_state
            dl = [list(r) for r in current_dirt]
            if   action == "UP":    rx -= 1
            elif action == "DOWN":  rx += 1
            elif action == "LEFT":  ry -= 1
            elif action == "RIGHT": ry += 1
            elif action == "CLEAN":
                if 0 <= rx < self.grid_m and 0 <= ry < self.grid_n:
                    dl[rx][ry] = 0
            tg = tuple(tuple(r) for r in dl)
            self.current_sim_state = (rx, ry, tg)
            self.sim_index += 1
            pct = int(self.sim_index / len(self.final_result) * 100)
            self._status_msg   = f"Mô phỏng: {self.sim_index}/{len(self.final_result)} bước ({pct}%)"
            self._status_color = C["accent2"]
            time.sleep(0.35)
        else:
            self.running_simulation = False
            self._status_msg   = " Đã hoàn thành công việc rồi á ní!"
            self._status_color = C["accent2"]

    def handle_click(self, mx, my):
        # ── Kiểm tra click vào nút thuật toán ──
        for btn in self.algo_buttons:
            if btn.is_clicked((mx, my)) and not self.running_simulation:
                self.current_algo = btn.label
                self.reset_env()
                return

        self.active_input = None

        if self.btn_rand.is_clicked((mx, my)) and not self.running_simulation:
            self.randomize_dirt(); return
        if self.running_simulation:
            if self.btn_reset.is_clicked((mx, my)):
                self.reset_env(); return
        else:
            if self.btn_run.is_clicked((mx, my)):
                self.active_input = None
                self.run_algorithm(); return

        if not self.running_simulation:
            cs = self.GRID_MAX // max(self.grid_m, self.grid_n)
            gx = mx - self.GRID_X
            gy = my - self.GRID_Y
            if 0 <= gx < self.grid_n*cs and 0 <= gy < self.grid_m*cs:
                col = gx // cs; row = gy // cs
                if 0 <= row < self.grid_m and 0 <= col < self.grid_n:
                    if not (row == 0 and col == 0):
                        self.grid_data[row][col] = 2 if self.grid_data[row][col] != 2 else 0
                        self.reset_env()

    def handle_keydown(self, event):
        pass

    def draw(self, surf):
        self._tick += 1
        mouse = pygame.mouse.get_pos()

        surf.fill(C["bg"])

        pygame.draw.rect(surf, C["accent"], (0, 0, WIDTH, 3))

        bar_rect = pygame.Rect(0, 3, WIDTH, 78)
        pygame.draw.rect(surf, C["panel"], bar_rect)
        pygame.draw.rect(surf, C["border"], (0, 78, WIDTH, 1))

        t = FONT_XL.render("MAY_HUT_BUI_2.0", True, C["text"])
        surf.blit(t, (260, 22))

        grid_lbl = FONT_SM.render("MA TRẬN: 5×5", True, C["text_dim"])
        surf.blit(grid_lbl, (490, 38))

        # Buttons
        self.btn_rand.draw(surf, mouse)
        if self.running_simulation:
            self.btn_reset.draw(surf, mouse)
        else:
            self.btn_run.draw(surf, mouse)

        alg_label = FONT_SM.render("THUẬT TOÁN", True, C["text_dim"])
        surf.blit(alg_label, (self.PANEL_LEFT, 90))

        for btn in self.algo_buttons:
            btn.draw(surf, mouse, btn.label == self.current_algo)
      

        lp = pygame.Rect(self.GRID_X - 10, 260, self.GRID_MAX + 30, self.GRID_MAX + 60)
        draw_rect_border(surf, C["panel"], C["border"], lp, radius=10)

        lt = FONT_SM.render("LƯỚI MÔI TRƯỜNG", True, C["text_dim"])
        surf.blit(lt, (self.GRID_X, 263))

        cs = self.GRID_MAX // max(self.grid_m, self.grid_n)
        rx_sim, ry_sim, current_dirt = self.current_sim_state
        grid_w = self.grid_n * cs
        grid_h = self.grid_m * cs
        gox    = self.GRID_X
        goy    = self.GRID_Y

        pygame.draw.rect(surf, (8, 10, 16), (gox+4, goy+4, grid_w, grid_h), border_radius=6)
        pygame.draw.rect(surf, C["grid_bg"], (gox, goy, grid_w, grid_h), border_radius=6)

        for r in range(self.grid_m):
            for c in range(self.grid_n):
                cx = gox + c * cs
                cy = goy + r * cs
                cell = pygame.Rect(cx+1, cy+1, cs-2, cs-2)
                val  = current_dirt[r][c]

                if val == 2:
                    pygame.draw.rect(surf, C["obstacle"], cell, border_radius=4)
                    pygame.draw.rect(surf, C["obstacle_b"], cell, width=1, border_radius=4)
                    for i in range(0, cs*2, 10):
                        x1 = cx + max(0, i - cs); y1 = cy + min(cs, i)
                        x2 = cx + min(cs, i);     y2 = cy + max(0, i - cs)
                        if x1 != x2 or y1 != y2:
                            pygame.draw.line(surf, C["obstacle_b"], (x1, y1), (x2, y2), 1)
                else:
                    pygame.draw.rect(surf, C["wall"], cell, border_radius=4)
                    pygame.draw.rect(surf, C["border"], cell, width=1, border_radius=4)

                if val == 1:
                    center = (cx + cs//2, cy + cs//2)
                    rad    = cs // 5
                    draw_glow_circle(surf, C["dirt"], center, rad, alpha=80)
                    pygame.draw.circle(surf, C["dirt"], center, rad)
                    pygame.draw.circle(surf, (240, 200, 120), center, rad-2)

                if r == rx_sim and c == ry_sim:
                    rr = pygame.Rect(cx+5, cy+5, cs-10, cs-10)
                    pulse = abs(math.sin(self._tick * 0.05)) * 15
                    r_col = (max(0, C["robot"][0]-int(pulse)),
                             min(255, C["robot"][1]+int(pulse)),
                             C["robot"][2])
                    pygame.draw.rect(surf, r_col, rr, border_radius=6)
                    pygame.draw.rect(surf, (150, 210, 255), rr, width=2, border_radius=6)
                    ew = cs // 8
                    pygame.draw.circle(surf, (220,240,255),
                                       (cx + cs//3, cy + cs//3 + 2), ew)
                    pygame.draw.circle(surf, (220,240,255),
                                       (cx + 2*cs//3, cy + cs//3 + 2), ew)

        pygame.draw.rect(surf, C["border_hi"], (gox, goy, grid_w, grid_h), width=2, border_radius=6)

        legend_y = goy + grid_h + 12
        items = [
            (C["robot"],    "Robot"),
            (C["dirt"],     "Bụi bẩn"),
            (C["obstacle"], "Vật cản"),
        ]
        lx = gox
        for col_, lbl_ in items:
            pygame.draw.circle(surf, col_, (lx + 6, legend_y + 7), 5)
            lt2 = FONT_XS.render(lbl_, True, C["text_dim"])
            surf.blit(lt2, (lx + 15, legend_y))
            lx += lt2.get_width() + 30

        rp = pygame.Rect(self.RIGHT_X, 90, self.RIGHT_W, HEIGHT - 100)
        draw_rect_border(surf, C["panel"], C["border"], rp, radius=10)

        sb = pygame.Rect(self.RIGHT_X + 10, 100, self.RIGHT_W - 20, 30)
        draw_rect_border(surf, C["panel2"], C["border"], sb, radius=6)
        dot_col = C["accent2"] if self.running_simulation else C["text_dim"]
        pulse2  = abs(math.sin(self._tick * 0.08))
        dc2     = lerp_color(dot_col, (255,255,255), pulse2 * 0.3) if self.running_simulation else dot_col
        pygame.draw.circle(surf, dc2, (self.RIGHT_X + 24, 115), 5)
        st = FONT_XS.render(self._status_msg, True, self._status_color)
        surf.blit(st, (self.RIGHT_X + 35, 108))

        ab = pygame.Rect(self.RIGHT_X + self.RIGHT_W - 130, 100, 120, 30)
        draw_rect_border(surf, (20, 28, 48), C["accent"], ab, radius=6)
        at = FONT_XS.render(self.current_algo, True, C["accent"])
        surf.blit(at, (ab.x + (ab.width - at.get_width())//2, ab.y + 8))

        surf.blit(FONT_SM.render("LOG HOẠT ĐỘNG", True, C["text_dim"]),
                  (self.RIGHT_X + 10, 142))
        log_rect = pygame.Rect(self.RIGHT_X + 10, 162, self.RIGHT_W - 20, 310)
        draw_rect_border(surf, (10, 12, 18), C["border"], log_rect, radius=6)

        for idx, log in enumerate(self.logs):
            if idx >= 13: break
            row_r = pygame.Rect(log_rect.x + 1, log_rect.y + 1 + idx*23,
                                log_rect.width - 2, 22)
            if idx % 2 == 0:
                pygame.draw.rect(surf, (14, 16, 22), row_r)
            ln = FONT_XS.render(f"{idx+1:02d}", True, C["border_hi"])
            surf.blit(ln, (log_rect.x + 6, log_rect.y + 5 + idx*23))
            lt3 = FONT_XS.render(log[:62], True, (180, 190, 210))
            surf.blit(lt3, (log_rect.x + 30, log_rect.y + 5 + idx*23))

        surf.blit(FONT_SM.render("ĐƯỜNG ĐI TÌM ĐƯỢC", True, C["text_dim"]),
                  (self.RIGHT_X + 10, 484))

        res_rect = pygame.Rect(self.RIGHT_X + 10, 504, self.RIGHT_W - 20, 160)
        draw_rect_border(surf, (10, 12, 18), C["border"], res_rect, radius=6)

        if self.final_result is not None:
            if isinstance(self.final_result, list):
                sc = FONT_XS.render(f"  {len(self.final_result)} BƯỚC  ", True, C["bg"])
                scb = pygame.Rect(res_rect.x + 6, res_rect.y + 6,
                                  sc.get_width() + 4, sc.get_height() + 4)
                pygame.draw.rect(surf, C["accent2"], scb, border_radius=4)
                surf.blit(sc, (scb.x + 2, scb.y + 2))

                full  = " → ".join(self.final_result)
                words = full.split(" ")
                lines = []; cur = ""
                for w in words:
                    test = cur + w + " "
                    if FONT_SM.size(test)[0] < res_rect.width - 20:
                        cur = test
                    else:
                        lines.append(cur); cur = w + " "
                lines.append(cur)
                for li, line in enumerate(lines[:5]):
                    lc = C["accent2"] if li == 0 else C["text"]
                    lt4 = FONT_SM.render(line.strip(), True, lc)
                    surf.blit(lt4, (res_rect.x + 10, res_rect.y + 30 + li*24))
            else:
                et = FONT_MD.render(str(self.final_result), True, C["red"])
                surf.blit(et, (res_rect.x + 10, res_rect.y + 60))
        else:
            nt = FONT_SM.render("Chưa thực hiện...", True, C["text_dim"])
            surf.blit(nt, (res_rect.x + 10, res_rect.y + 65))

        if self.running_simulation and isinstance(self.final_result, list) and len(self.final_result) > 0:
            pct   = self.sim_index / len(self.final_result)
            pb    = pygame.Rect(self.RIGHT_X + 10, HEIGHT - 26, self.RIGHT_W - 20, 8)
            fill  = pygame.Rect(pb.x, pb.y, int(pb.width * pct), pb.height)
            pygame.draw.rect(surf, C["panel2"], pb, border_radius=4)
            pygame.draw.rect(surf, C["accent2"], fill, border_radius=4)
            pygame.draw.rect(surf, C["border"], pb, width=1, border_radius=4)

        pygame.draw.rect(surf, C["panel"], (0, HEIGHT-22, WIDTH, 22))
        pygame.draw.rect(surf, C["border"], (0, HEIGHT-23, WIDTH, 1))
        hint = "Chọn thuật toán  |  Click ô để vẽ/xóa vật cản  |  Nhấn RANDOM để tạo lưới mới"
        ht   = FONT_XS.render(hint, True, C["text_dim"])
        surf.blit(ht, (WIDTH//2 - ht.get_width()//2, HEIGHT - 18))


def main():
    clock      = pygame.time.Clock()
    visualizer = Visualizer()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = pygame.mouse.get_pos()
                visualizer.handle_click(mx, my)
            elif event.type == pygame.KEYDOWN:
                visualizer.handle_keydown(event)

        visualizer.update_simulation()
        visualizer.draw(screen)
        pygame.display.flip()
        clock.tick(60)

if __name__ == "__main__":
    main()
