import tkinter as tk
import random
from PIL import ImageGrab

GRID_SIZE = 4
CELL_PADDING = 5
BG_COLOR = '#e3f2fd'
EMPTY_CELL_COLOR = '#f8f9fa'
FONT_FAMILY = 'Arial'
FONT_WEIGHT = 'bold'

COLOR_MAP = {
    0: (EMPTY_CELL_COLOR, "#6c757d"),
    2: ("#d1f7ff", "#005792"),
    4: ("#b1f5ff", "#005792"),
    8: ("#73efff", "#ffffff"),
    16: ("#40e0ff", "#ffffff"),
    32: ("#00c8ff", "#ffffff"),
    64:("#f7dce9", "#ffffff"),
    128:("#f2bcd6", "#ffffff"),
    256: ("#f2bcd6", "#f9f6f2"),
    512: ("#ec96c2", "#f9f6f2"),
    1024:("#dc80dc", "#f9f6f2"),
    2048:("#ff90b1", "#f9f6f2"),}
DEFAULT_COLOR = ("#3c3a32", "#f9f6f2")


class Game2048:
    def __init__(self, root):
        self.root = root
        self.root.title("Game2048")
        self.root.geometry("400x450")
        self.root.resizable(False, False)

        self.grid = [[0] * GRID_SIZE for _ in range(GRID_SIZE)]
        self.score = 0

        self.is_recording = False
        self.frames = []
        self.recording_interval = 500

        self.setup_ui()
        self.start_new_game()
        self.root.bind("<Key>", self.handle_key_press)
        self.root.focus_set()

    def setup_ui(self):
        self.control_frame = tk.Frame(self.root, bg=BG_COLOR, padx=10, pady=10)
        self.control_frame.pack(fill=tk.X)

        self.score_label = tk.Label(self.control_frame, text="Score: 0",
                                    font=(FONT_FAMILY, 16, FONT_WEIGHT), bg=BG_COLOR, fg="#0277bd")
        self.score_label.pack(side=tk.LEFT)

        btn_frame = tk.Frame(self.control_frame, bg=BG_COLOR)
        btn_frame.pack(side=tk.RIGHT)

        self.restart_button = tk.Button(btn_frame, text="New Game", command=self.start_new_game,
                                        font=(FONT_FAMILY, 12), bg="#42a5f5", fg="white", relief=tk.FLAT)
        self.restart_button.pack(side=tk.LEFT, padx=5)


        self.record_button = tk.Button(btn_frame, text="Start Rec", command=self.toggle_recording,
                                       font=(FONT_FAMILY, 12), bg="#e74c3c", fg="white", relief=tk.FLAT)
        self.record_button.pack(side=tk.LEFT, padx=5)

        self.grid_frame = tk.Frame(self.root, bg=BG_COLOR, padx=CELL_PADDING, pady=CELL_PADDING)
        self.grid_frame.pack(padx=10, pady=10)

        self.cells = []
        for r in range(GRID_SIZE):
            row_cells = []
            for c in range(GRID_SIZE):
                cell = tk.Label(self.grid_frame, text="",
                                font=(FONT_FAMILY, 24, FONT_WEIGHT), width=4, height=2,
                                bg=EMPTY_CELL_COLOR, fg="#776e65")
                cell.grid(row=r, column=c, padx=CELL_PADDING, pady=CELL_PADDING)
                row_cells.append(cell)
            self.cells.append(row_cells)

    def toggle_recording(self):
        if not self.is_recording:
            self.start_recording()
        else:
            self.stop_recording()

    def start_recording(self):
        self.is_recording = True
        self.frames = []
        self.record_button.config(text="Stop Rec", bg="#2ecc71")
        self.capture_frame()

    def capture_frame(self):
        if not self.is_recording:
            return
        try:
            # 强制更新界面，确保布局完整
            self.root.update()

            # 获取窗口坐标和尺寸
            x = self.root.winfo_rootx()
            y = self.root.winfo_rooty()
            w = self.root.winfo_width()
            h = self.root.winfo_height()


            img = ImageGrab.grab(bbox=(x, y,
                                        x + w + 400, y + h + 500))


            self.frames.append(img)

        except Exception as e:
            print(f"截图失败: {e}")

        self.root.after(self.recording_interval, self.capture_frame)

    def stop_recording(self):
        self.is_recording = False
        self.record_button.config(text="Start Rec", bg="#e74c3c")
        if self.frames:
            self.save_gif()

    def save_gif(self):
        try:
            self.frames[0].save(
                "game2048.gif",
                save_all=True,
                append_images=self.frames[1:],
                duration=self.recording_interval,
                loop=0
            )
            print(f" GIF 保存成功！共 {len(self.frames)} 帧")
        except Exception as e:
            print(f" 保存失败: {e}")

    def start_new_game(self):
        if self.is_recording:
            self.stop_recording()
        self.grid = [[0] * GRID_SIZE for _ in range(GRID_SIZE)]
        self.score = 0
        self.add_new_tile()
        self.add_new_tile()
        self.update_view()

    def add_new_tile(self):
        empty = [(r, c) for r in range(GRID_SIZE) for c in range(GRID_SIZE) if self.grid[r][c] == 0]
        if empty:
            r, c = random.choice(empty)
            self.grid[r][c]  = 2 if random.random() < 0.9 else 4

    def update_view(self):
        self.score_label.config(text=f"Score: {self.score}")
        for r in range(GRID_SIZE):
            for c in range(GRID_SIZE):
                v = self.grid[r][c]
                bg, fg = COLOR_MAP.get(v, DEFAULT_COLOR)
                self.cells[r][c].config(text=str(v) if v != 0 else "", bg=bg, fg=fg)

    def handle_key_press(self, event):
        key = event.keysym
        moved = False
        if key in ["Up", "w"]:
            moved = self.move_up()
        elif key in ["Down", "s"]:
            moved = self.move_down()
        elif key in ["Left", "a"]:
            moved = self.move_left()
        elif key in ["Right", "d"]:
            moved = self.move_right()

        if moved:
            self.add_new_tile()
            self.update_view()
            if self.check_game_over():
                print("Game Over!")

    def move_left(self):
        return self._move_merge(lambda row: self._slide_and_merge(row))

    def move_right(self):
        return self._move_merge(lambda row: self._slide_and_merge(row[::-1])[::-1])

    def move_up(self):
        self.transpose()
        moved = self.move_left()
        self.transpose()
        return moved

    def move_down(self):
        self.transpose()
        moved = self.move_right()
        self.transpose()
        return moved

    def _move_merge(self, func):
        new_grid = []
        moved = False
        for row in self.grid:
            new_row = func(row)
            new_grid.append(new_row)
            if new_row != row:
                moved = True
        self.grid = new_grid
        return moved

    def _slide_and_merge(self, row):
        filt = [x for x in row if x != 0]
        merged = []
        skip = False
        for i in range(len(filt)):
            if skip:
                skip = False
                continue
            if i + 1 < len(filt) and filt[i] == filt[i+1]:
                val = filt[i] * 2
                merged.append(val)
                self.score += val
                skip = True
            else:
                merged.append(filt[i])
        while len(merged) < GRID_SIZE:
            merged.append(0)
        return merged

    def transpose(self):
        self.grid = [list(x) for x in zip(*self.grid)]

    def check_game_over(self):
        for r in range(GRID_SIZE):
            for c in range(GRID_SIZE):
                if self.grid[r][c] == 0:
                    return False
        for r in range(GRID_SIZE):
            for c in range(GRID_SIZE):
                if c < GRID_SIZE-1 and self.grid[r][c] == self.grid[r][c+1]:
                    return False
                if r < GRID_SIZE-1 and self.grid[r][c] == self.grid[r+1][c]:
                    return False
        return True

if __name__ == "__main__":
    root = tk.Tk()
    game = Game2048(root)
    root.mainloop()