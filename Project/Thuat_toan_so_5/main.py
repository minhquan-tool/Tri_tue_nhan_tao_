import json
import tkinter as tk
from tkinter import messagebox, scrolledtext
from tkinter import ttk  # Sử dụng các widget nâng cấp
from collections import defaultdict

import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.patches import Polygon as MplPolygon
from matplotlib.collections import PatchCollection

from shapely.geometry import Polygon
import importlib.util
import os

from backtracking import Backtracking
from forward_checking import Forward_Checking
from min_conflict import Min_Conflicts
from ac_3 import AC_3

AC_3_PATH = os.path.join(os.path.dirname(__file__), "ac_3.py")
spec = importlib.util.spec_from_file_location("ac_3_module", AC_3_PATH)
ac_3_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ac_3_module)
AC_3Solver = ac_3_module.AC_3

PROVINCE_FILE = r"C:\Users\ASUS\Downloads\Thuat_toan_so_5\DATA\provNew.geojson"
WARD_FILE = r"C:\Users\ASUS\Downloads\Thuat_toan_so_5\DATA\Wards.json"


def load_geojson(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    polygons = []
    for feature in data["features"]:
        geom = feature["geometry"]
        if geom["type"] == "Polygon":
            polygons.append(geom["coordinates"][0])
        elif geom["type"] == "MultiPolygon":
            for polygon in geom["coordinates"]:
                polygons.append(polygon[0])
    return polygons


def get_center_point(coords):
    lon_sum = sum(lon for lon, lat in coords)
    lat_sum = sum(lat for lon, lat in coords)
    return lon_sum / len(coords), lat_sum / len(coords)


def load_topojson(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        topo = json.load(f)

    arcs = topo["arcs"]
    geometries = topo["objects"]["collection"]["geometries"]

    def get_arc(index):
        if index >= 0:
            return arcs[index]
        return list(reversed(arcs[-index - 1]))

    def join_arcs(arc_indices):
        coords = []
        for index in arc_indices:
            arc = get_arc(index)
            if coords and coords[-1] == arc[0]:
                coords.extend(arc[1:])
            else:
                coords.extend(arc)
        if coords and coords[0] != coords[-1]:
            coords.append(coords[0])
        return coords

    ward_polygons = []
    ward_names = []
    label_points = []
    shapely_polygons = []

    for i, geom in enumerate(geometries):
        name = geom["properties"].get("Tên", f"Ward {i}")
        if geom["type"] == "Polygon":
            coords = join_arcs(geom["arcs"][0])
            ward_polygons.append(coords)
            ward_names.append(name)
            label_points.append(get_center_point(coords))
            shapely_polygons.append(Polygon(coords).buffer(0))
        elif geom["type"] == "MultiPolygon":
            for polygon in geom["arcs"]:
                coords = join_arcs(polygon[0])
                ward_polygons.append(coords)
                ward_names.append(name)
                label_points.append(get_center_point(coords))
                shapely_polygons.append(Polygon(coords).buffer(0))

    return ward_polygons, ward_names, label_points, shapely_polygons


def build_neighbors(shapely_polygons):
    neighbors = defaultdict(set)
    n = len(shapely_polygons)
    for i in range(n):
        for j in range(i + 1, n):
            inter = shapely_polygons[i].boundary.intersection(
                shapely_polygons[j].boundary
            )
            if not inter.is_empty and inter.length > 0.000001:
                neighbors[i].add(j)
                neighbors[j].add(i)
    return neighbors


class MapColoringApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Bản đồ Việt Nam - CSP Tô màu bản đồ")
        self.root.geometry("1400x850")
        self.root.configure(bg="#f5f6fa")  # Nền xám nhạt hiện đại

        # Khởi tạo cấu trúc giao diện ttk style
        self.style = ttk.Style()
        self.style.theme_use("clam")
        self.configure_styles()

        self.province_polygons = []
        self.ward_polygons = []
        self.ward_names = []
        self.label_points = []
        self.shapely_polygons = []
        self.neighbors = {}

        self.solver = None
        self.generator = None
        self.assignment = {}

        self.running = False
        self.press = None
        self.current_xlim = None
        self.current_ylim = None

        self.algorithm_var = tk.StringVar(value="fc")

        self.setup_ui()
        self.load_data()
        self.draw_map(first_time=True)

    def configure_styles(self):
        # Thiết kế font chữ và bảng màu phẳng (Flat UI style)
        self.style.configure(".", font=("Segoe UI", 10), background="#f5f6fa", foreground="#2f3640")
        self.style.configure("TLabelframe", background="#ffffff", relief="solid", borderwidth=1)
        self.style.configure("TLabelframe.Label", font=("Segoe UI", 10, "bold"), foreground="#4a5568", background="#ffffff")
        
        # Thiết kế nút bấm hiện đại
        self.style.configure("TButton", font=("Segoe UI", 9, "bold"), padding=6, background="#e2e8f0", borderwidth=0)
        self.style.map("TButton",
                       background=[("active", "#cbd5e1"), ("disabled", "#f1f5f9")],
                       foreground=[("disabled", "#94a3b8")])
        
        # Nút bấm Hành Động Nổi Bật (Primary Button)
        self.style.configure("Primary.TButton", background="#3b82f6", foreground="white")
        self.style.map("Primary.TButton", background=[("active", "#2563eb")])
        
        # Radio button
        self.style.configure("TRadiobutton", background="#ffffff", font=("Segoe UI", 10))

    def setup_ui(self):
        # 1. THANH ĐIỀU KHIỂN PHÍA TRÊN (TOP TOOLBAR)
        top_bar = tk.Frame(self.root, bg="#f1eded", height=60, bd=1, relief="groove")
        top_bar.pack(side=tk.TOP, fill=tk.X, padx=10, pady=10)
        top_bar.pack_propagate(False)

        # Bộ chọn thuật toán
        algo_frame = ttk.LabelFrame(top_bar, text=" Thuật toán CSP ")
        algo_frame.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=2)

        ttk.Radiobutton(
            algo_frame, text="Backtracking", variable=self.algorithm_var, value="bt"
        ).pack(side=tk.LEFT, padx=15, pady=2)

        ttk.Radiobutton(
            algo_frame, text="Backtracking + Forward_Checking", variable=self.algorithm_var, value="fc"
        ).pack(side=tk.LEFT, padx=15, pady=2)

        ttk.Radiobutton(
            algo_frame, text="Min-Conflicts", variable=self.algorithm_var, value="mc"
        ).pack(side=tk.LEFT, padx=15, pady=2)

        ttk.Radiobutton(
            algo_frame, text="AC-3 ", variable=self.algorithm_var, value="ac3"
        ).pack(side=tk.LEFT, padx=15, pady=2)

        # Bộ nút bấm chức năng (Control Controls)
        ctrl_frame = ttk.LabelFrame(top_bar, text=" Điều khiển ")
        ctrl_frame.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=2)

        self.btn_start = ttk.Button(ctrl_frame, text="▶ Khởi chạy", style="Primary.TButton", command=self.start)
        self.btn_start.pack(side=tk.LEFT, padx=6, pady=2)

        self.btn_next = ttk.Button(ctrl_frame, text="⏭ Bước tiếp", command=self.next_step)
        self.btn_next.pack(side=tk.LEFT, padx=6, pady=2)

        self.btn_auto = ttk.Button(ctrl_frame, text="🔄 Tự động chạy", command=self.auto_run)
        self.btn_auto.pack(side=tk.LEFT, padx=6, pady=2)

        self.btn_stop = ttk.Button(ctrl_frame, text="⏸ Tạm dừng", command=self.stop)
        self.btn_stop.pack(side=tk.LEFT, padx=6, pady=2)

        self.btn_reset = ttk.Button(ctrl_frame, text="🧹 Làm mới", command=self.reset)
        self.btn_reset.pack(side=tk.LEFT, padx=6, pady=2)

        # 2. KHU VỰC CHÍNH (MAIN WORKSPACE)
        workspace = tk.Frame(self.root, bg="#F0F0F6")
        workspace.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=10, pady=0)

        # Khu vực bên trái: Bản đồ trực quan hóa
        map_wrapper = ttk.LabelFrame(workspace, text=" Bản đồ trực quan ")
        map_wrapper.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5), pady=5)

        self.fig, self.ax = plt.subplots(figsize=(10, 8), dpi=100)
        self.fig.patch.set_facecolor("#181717") # Đồng bộ màu nền đồ thị với app
        self.fig.subplots_adjust(left=0, right=1, top=1, bottom=0)

        self.canvas = FigureCanvasTkAgg(self.fig, master=map_wrapper)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Kết nối sự kiện chuột
        self.canvas.mpl_connect("scroll_event", self.zoom)
        self.canvas.mpl_connect("button_press_event", self.pan_start)
        self.canvas.mpl_connect("button_release_event", self.pan_end)
        self.canvas.mpl_connect("motion_notify_event", self.pan_move)

        # Khu vực bên phải: Log lịch sử thuật toán
        log_wrapper = ttk.LabelFrame(workspace, text=" Tiến trình thực thi & Nhật ký ")
        log_wrapper.pack(side=tk.RIGHT, fill=tk.Y, padx=(5, 0), pady=5)

        self.log_box = scrolledtext.ScrolledText(
            log_wrapper,
            width=50,
            font=("Consolas", 10), # Đổi sang font Monospace chuyên viết log
            bg="#1e293b",          # Nền tối chuẩn Terminal
            fg="#f8fafc",          # Chữ trắng sáng dễ đọc
            insertbackground="white",
            relief="flat"
        )
        self.log_box.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)

        # 3. THANH TRẠNG THÁI DƯỚI CÙNG (STATUS BAR)
        self.status_var = tk.StringVar(value="Sẵn sàng tải dữ liệu...")
        status_bar = tk.Label(self.root, textvariable=self.status_var, anchor="w", bg="#1e293b", fg="#f8fafc", font=("Segoe UI", 9), padx=10, pady=3)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)

    def load_data(self):
        try:
            self.status_var.set("Đang tải cơ sở dữ liệu bản đồ GeoJSON/TopoJSON...")
            self.root.update_idletasks()

            self.province_polygons = load_geojson(PROVINCE_FILE)
            result = load_topojson(WARD_FILE)
            self.ward_polygons = result[0]
            self.ward_names = result[1]
            self.label_points = result[2]
            self.shapely_polygons = result[3]
            self.neighbors = build_neighbors(self.shapely_polygons)
            
            self.status_var.set(f"Tải thành công: Đã nạp {len(self.ward_polygons)} phường/xã.")
        except Exception as e:
            messagebox.showerror("Lỗi dữ liệu", f"Không thể đọc file bản đồ:\n{str(e)}")
            self.status_var.set("Lỗi tải dữ liệu.")

    def start(self):
        self.assignment = {}
        if self.algorithm_var.get() == "bt":
            self.solver = Backtracking(
                len(self.ward_polygons), self.ward_names, self.neighbors
            )
            algo_name = "Backtracking"
        elif self.algorithm_var.get() == "fc":
            self.solver = Forward_Checking(
                len(self.ward_polygons), self.ward_names, self.neighbors
            )
            algo_name = "Backtracking + Forward_Checking"
        elif self.algorithm_var.get() == "mc":
            self.solver = Min_Conflicts(
                len(self.ward_polygons), self.ward_names, self.neighbors
            )
            algo_name = "Min-Conflicts"
        else:
            self.solver = AC_3(
                len(self.ward_polygons), self.ward_names, self.neighbors
            )
            algo_name = "AC_3"

        self.generator = self.solver.solve_generator()
        self.running = False

        self.log_box.delete("1.0", tk.END)
        self.log("================= CSP KHỞI TẠO =================")
        self.log("• Biến: Các đơn vị hành chính xã/phường")
        self.log("• Miền giá trị: [Đỏ, Cam, Xanh dương, Vàng]")
        self.log("• Ràng buộc : Các vùng giáp ranh khác màu nhau")
        self.log("------------------------------------------------")
        self.log(f"▶ Thuật toán lựa chọn: {algo_name}")
        self.log("▶ Khởi tạo Assignment = {}")
        self.log("================================================")
        self.log("")

        self.status_var.set(f"Đang chạy: {algo_name}")
        self.draw_map()

    def next_step(self):
        if self.generator is None:
            self.start()

        try:
            step = next(self.generator)
        except StopIteration:
            self.log("\n[KẾT THÚC] Thuật toán đã duyệt toàn bộ không gian trạng thái.")
            self.status_var.set("Thuật toán đã dừng.")
            self.running = False
            return

        action = step[0]
        ward_index = step[1]
        color = step[2]
        self.assignment = step[3]

        removed_list = step[4] if len(step) > 4 else []

        if action == "choose":
            self.log(f"🔍 Chọn biến tiếp theo: 【{self.ward_names[ward_index]}】")
        elif action == "try":
            self.log(f"   ↳ Thử gán màu: {color}")
        elif action == "valid":
            self.log("   ✔ Kiểm tra ràng buộc: HỢP LỆ")
            self.log(f"     {self.assignment_to_text()}")
        elif action == "invalid":
            self.log("   ❌ Kiểm tra ràng buộc: THẤT BẠI (Xung đột màu với lân cận)")
        elif action == "mc_init":
            self.log("🔧 Khởi tạo Min-Conflicts: gán màu ngẫu nhiên ban đầu")
            self.log(self.assignment_to_text())
        elif action == "mc_check":
            conflict_pairs = step[4]
            if not conflict_pairs:
                self.log("   ✔ Kiểm tra xung đột: hiện không còn cặp xung đột.")
            else:
                self.log(f"   ⚠️ Kiểm tra xung đột: {len(conflict_pairs)} cặp")
        elif action == "mc_choose":
            self.log(f"   ↳ Chọn biến xung đột: 【{self.ward_names[ward_index]}】")
        elif action == "mc_try_all":
            color_results = step[4]
            self.log(f"   ↳ Tính toán màu tối ưu cho 【{self.ward_names[ward_index]}】: {color_results}")
        elif action == "mc_update":
            self.log(f"   ✔ Cập nhật màu mới: 【{self.ward_names[ward_index]}】 = {color}")
        elif action == "ac3_init":
            queue = step[4]
            self.log(f"🔧 Khởi tạo AC-3 với {len(queue)} cung (arcs).")
        elif action == "ac3_check":
            self.log(f"   ↳ AC-3 kiểm tra cung: ({ward_index}, {color})")
        elif action == "ac3_remove":
            removed = step[4]
            self.log(f"   ➖ AC-3 loại bỏ giá trị {removed} khỏi miền của biến {ward_index}.")
        elif action == "ac3_add":
            self.log(f"   ➕ AC-3 thêm lại cung kiểm tra cho biến {ward_index}.")
        elif action == "ac3_done":
            self.log("✅ AC-3 hoàn tất: dữ liệu nhất quán trước khi chạy Backtracking.")
        elif action == "fc":
            self.log("   ⚡ Thực hiện Forward Checking:")
            if not removed_list:
                self.log("     ↳ Không có màu nào bị loại bỏ ở các miền lân cận.")
            else:
                for neighbor, removed_color in removed_list:
                    self.log(f"     ↳ Loại màu [{removed_color}] khỏi miền giá trị của 【{self.ward_names[neighbor]}】")
        elif action == "domain_empty":
            self.log("   ⚠️ Phát hiện phường lân cận bị rỗng miền giá trị!")
            self.log("   ⏭ Tự động tỉa nhánh sớm (Pruning) tại đây.")
        elif action == "backtrack":
            self.log(f"↩️ [BACKTRACK] Hủy bỏ màu {color} của 【{self.ward_names[ward_index]}】")
        elif action == "done":
            self.log("\n🎉 [THÀNH CÔNG] Đã tìm ra lời giải tối ưu cho bản đồ!")
            self.status_var.set("Hoàn thành tô màu!")
            self.log(self.assignment_to_text())

        self.draw_map()

    def auto_run(self):
        self.running = True
        self.run_auto_step()

    def run_auto_step(self):
        if not self.running:
            return
        self.next_step()
        self.root.after(50, self.run_auto_step) # Tốc độ hoạt họa tối ưu hóa 50ms

    def stop(self):
        self.running = False
        self.status_var.set("Đã tạm dừng tiến trình.")

    def reset(self):
        self.assignment = {}
        self.solver = None
        self.generator = None
        self.running = False
        self.log_box.delete("1.0", tk.END)
        self.status_var.set("Đã xóa trạng thái. Sẵn sàng bắt đầu lại.")
        self.draw_map()

    def assignment_to_text(self):
        items = [f"{self.ward_names[idx]}={clr}" for idx, clr in self.assignment.items()]
        return "Current State = {" + ", ".join(items[:3]) + ("..." if len(items) > 3 else "") + "}"

    def draw_map(self, first_time=False):
        if not first_time:
            self.current_xlim = self.ax.get_xlim()
            self.current_ylim = self.ax.get_ylim()

        self.ax.clear()

        province_patches = [MplPolygon(coords, closed=True) for coords in self.province_polygons]
        ward_patches = []
        ward_colors = []

        for i, coords in enumerate(self.ward_polygons):
            ward_patches.append(MplPolygon(coords, closed=True))
            ward_colors.append(self.assignment.get(i, "#ffffff")) # Mặc định chưa gán là màu trắng nền

        province_collection = PatchCollection(
            province_patches, facecolor="#cbd5e1", edgecolor="#64748b", linewidth=1.5, alpha=0.5
        )
        ward_collection = PatchCollection(
            ward_patches, facecolor=ward_colors, edgecolor="#1e293b", linewidth=0.4, alpha=0.9
        )

        self.ax.add_collection(province_collection)
        self.ax.add_collection(ward_collection)

        # Hiển thị text nhãn của phường xã với font chữ mảnh sạch sẽ
        for name, point in zip(self.ward_names, self.label_points):
            lon, lat = point
            self.ax.text(lon, lat, name, fontsize=5, fontname="Segoe UI", ha="center", va="center", alpha=0.8)

        if first_time or self.current_xlim is None or self.current_ylim is None:
            center_lon, center_lat = 106.7009, 10.7769
            zoom_width, zoom_height = 0.10, 0.075
            self.ax.set_xlim(center_lon - zoom_width, center_lon + zoom_width)
            self.ax.set_ylim(center_lat - zoom_height, center_lat + zoom_height)
        else:
            self.ax.set_xlim(self.current_xlim)
            self.ax.set_ylim(self.current_ylim)

        self.ax.set_aspect("equal", adjustable="box")
        self.ax.axis("off")
        self.canvas.draw_idle()

    def log(self, text):
        self.log_box.insert(tk.END, text + "\n")
        self.log_box.see(tk.END)
        line_count = int(self.log_box.index("end-1c").split(".")[0])
        if line_count > 800:
            self.log_box.delete("1.0", "150.0")

    def zoom(self, event):
        if event.xdata is None or event.ydata is None:
            return
        scale = 1.2
        cur_xlim, cur_ylim = self.ax.get_xlim(), self.ax.get_ylim()
        x, y = event.xdata, event.ydata
        factor = 1 / scale if event.button == "up" else scale
        new_width = (cur_xlim[1] - cur_xlim[0]) * factor
        new_height = (cur_ylim[1] - cur_ylim[0]) * factor
        self.ax.set_xlim(x - new_width / 2, x + new_width / 2)
        self.ax.set_ylim(y - new_height / 2, y + new_height / 2)
        self.canvas.draw_idle()

    def pan_start(self, event):
        if event.button == 1:
            self.press = (event.xdata, event.ydata, self.ax.get_xlim(), self.ax.get_ylim())

    def pan_end(self, event):
        self.press = None

    def pan_move(self, event):
        if self.press is None or event.xdata is None or event.ydata is None:
            return
        x0, y0, xlim, ylim = self.press
        dx, dy = event.xdata - x0, event.ydata - y0
        self.ax.set_xlim(xlim[0] - dx, xlim[1] - dx)
        self.ax.set_ylim(ylim[0] - dy, ylim[1] - dy)
        self.canvas.draw_idle()


if __name__ == "__main__":
    root = tk.Tk()
    app = MapColoringApp(root)
    root.mainloop()