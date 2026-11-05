"""
Sudoku 9x9 Interaktif
=====================
Dibuat dengan Python bawaan: tkinter + random
Cocok untuk pemula yang ingin belajar struktur GUI dan algoritma backtracking.

Cara menjalankan:
    python sudoku.py
"""

import tkinter as tk
from tkinter import messagebox
import random
from typing import Optional


# ─────────────────────────────────────────────
#  KONSTANTA TAMPILAN
# ─────────────────────────────────────────────
WINDOW_TITLE  = "Sudoku 9×9"
CELL_SIZE     = 58          # lebar & tinggi setiap sel (piksel)
BOARD_OFFSET  = 20          # jarak tepi papan dari tepi canvas
FONT_GIVEN    = ("Helvetica", 22, "bold")   # angka yang sudah dikunci (soal)
FONT_USER     = ("Helvetica", 20)           # angka yang diisi pemain
FONT_BUTTON   = ("Helvetica", 12, "bold")

COLOR_BG      = "#f0f0f0"   # latar belakang jendela
COLOR_BOARD   = "#ffffff"   # latar sel kosong
COLOR_GIVEN   = "#1a1a2e"   # warna teks angka soal
COLOR_USER_OK = "#1565c0"   # biru – input valid
COLOR_USER_ERR= "#c62828"   # merah – input duplikat / salah
COLOR_SELECT  = "#bbdefb"   # sorot sel yang dipilih
COLOR_SUBGRID = "#3a3a3a"   # garis tebal batas 3×3
COLOR_CELL    = "#bdbdbd"   # garis tipis antar sel
COLOR_BTN_NEW = "#1976d2"
COLOR_BTN_RST = "#f57c00"
COLOR_BTN_SLV = "#388e3c"
COLOR_BTN_TXT = "#ffffff"


# ─────────────────────────────────────────────
#  LOGIKA SUDOKU
# ─────────────────────────────────────────────

def is_valid_placement(board, row, col, num):
    """
    Periksa apakah angka `num` boleh ditempatkan di (row, col).
    Aturan Sudoku: tidak boleh duplikat dalam baris, kolom, dan kotak 3×3.
    Mengembalikan True jika valid, False jika tidak.
    """
    # Cek baris
    if num in board[row]:
        return False
    # Cek kolom
    if num in [board[r][col] for r in range(9)]:
        return False
    # Cek kotak 3×3
    box_r, box_c = (row // 3) * 3, (col // 3) * 3
    for r in range(box_r, box_r + 3):
        for c in range(box_c, box_c + 3):
            if board[r][c] == num:
                return False
    return True


def solve_board(board):
    """
    Selesaikan papan Sudoku menggunakan algoritma backtracking rekursif.
    Memodifikasi `board` secara in-place.
    Mengembalikan True jika solusi ditemukan, False jika tidak ada solusi.
    """
    for row in range(9):
        for col in range(9):
            if board[row][col] == 0:          # temukan sel kosong
                nums = list(range(1, 10))
                random.shuffle(nums)          # acak urutan agar solusi bervariasi
                for num in nums:
                    if is_valid_placement(board, row, col, num):
                        board[row][col] = num
                        if solve_board(board): # rekursi
                            return True
                        board[row][col] = 0   # backtrack
                return False                  # tidak ada angka yang cocok
    return True                               # semua sel terisi


def generate_full_board():
    """
    Buat papan Sudoku yang terisi penuh dan valid.
    Mulai dari papan kosong lalu panggil solve_board dengan urutan angka acak.
    """
    board = [[0] * 9 for _ in range(9)]
    solve_board(board)
    return board


def generate_puzzle(clues=30):
    """
    Buat puzzle Sudoku dengan menghapus sejumlah angka dari papan penuh.
    Parameter `clues` menentukan jumlah angka yang TERSISA sebagai soal.
    Rentang yang disarankan: 25–35 (lebih sedikit = lebih sulit).
    Mengembalikan (puzzle, solution) di mana keduanya adalah list 9×9.
    """
    solution = generate_full_board()
    puzzle   = [row[:] for row in solution]   # salin papan penuh

    # Daftar semua posisi, lalu acak dan hapus hingga tersisa `clues` angka
    positions = [(r, c) for r in range(9) for c in range(9)]
    random.shuffle(positions)
    to_remove = 81 - clues

    for r, c in positions[:to_remove]:
        puzzle[r][c] = 0

    return puzzle, solution


# ─────────────────────────────────────────────
#  APLIKASI GUI
# ─────────────────────────────────────────────

class SudokuApp:
    """
    Kelas utama yang mengelola seluruh tampilan dan logika game Sudoku.
    Menggunakan tkinter Canvas untuk menggambar papan secara manual
    agar pengendalian visual (garis tebal, warna sel) lebih fleksibel.
    """

    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title(WINDOW_TITLE)
        self.root.configure(bg=COLOR_BG)
        self.root.resizable(False, False)

        # Status game
        self.puzzle:    list[list[int]] = []   # angka soal (0 = kosong)
        self.solution:  list[list[int]] = []   # solusi lengkap
        self.user_grid: list[list[int]] = []   # input pemain
        self.given:     list[list[bool]]= []   # True jika sel ini adalah soal
        self.selected:  Optional[tuple] = None # (row, col) sel yang dipilih

        self._build_ui()
        self.new_game()                        # langsung mulai game saat aplikasi dibuka

    # ── Bangun antarmuka ──────────────────────────────────────────────────

    def _build_ui(self):
        """Buat semua widget: canvas papan + tombol aksi."""
        board_px = CELL_SIZE * 9 + BOARD_OFFSET * 2   # total lebar/tinggi canvas

        # Canvas untuk papan Sudoku
        self.canvas = tk.Canvas(
            self.root,
            width=board_px, height=board_px,
            bg=COLOR_BOARD, highlightthickness=0
        )
        self.canvas.pack(padx=20, pady=(20, 10))
        self.canvas.bind("<Button-1>", self._on_click)    # klik sel
        self.root.bind("<Key>",        self._on_keypress) # tekan angka

        # Frame tombol aksi
        btn_frame = tk.Frame(self.root, bg=COLOR_BG)
        btn_frame.pack(pady=(0, 20))

        btn_specs = [
            ("🎮  Game Baru", COLOR_BTN_NEW, self.new_game),
            ("🔄  Reset",     COLOR_BTN_RST, self.reset_game),
            ("✅  Auto-Solve", COLOR_BTN_SLV, self.auto_solve),
        ]
        for label, color, cmd in btn_specs:
            tk.Button(
                btn_frame, text=label, command=cmd,
                font=FONT_BUTTON, bg=color, fg=COLOR_BTN_TXT,
                activebackground=color, activeforeground=COLOR_BTN_TXT,
                relief="flat", padx=18, pady=8, cursor="hand2", bd=0
            ).pack(side="left", padx=8)

    # ── Manajemen game ────────────────────────────────────────────────────

    def new_game(self):
        """Mulai game baru: generate puzzle baru lalu gambar ulang papan."""
        self.puzzle, self.solution = generate_puzzle(clues=random.randint(28, 33))
        self.user_grid = [[0] * 9 for _ in range(9)]
        self.given     = [[self.puzzle[r][c] != 0 for c in range(9)] for r in range(9)]
        self.selected  = None
        self._draw_board()

    def reset_game(self):
        """Hapus semua input pemain, kembalikan ke kondisi awal soal."""
        self.user_grid = [[0] * 9 for _ in range(9)]
        self.selected  = None
        self._draw_board()

    def auto_solve(self):
        """
        Isi papan secara otomatis dengan solusi yang sudah dihitung saat
        puzzle dibuat. Animasi singkat: isi sel kosong satu per satu.
        """
        for r in range(9):
            for c in range(9):
                if not self.given[r][c]:
                    self.user_grid[r][c] = self.solution[r][c]
        self.selected = None
        self._draw_board()
        messagebox.showinfo("Auto-Solve", "Puzzle diselesaikan secara otomatis! 🎉")

    # ── Penanganan input ──────────────────────────────────────────────────

    def _on_click(self, event: tk.Event):
        """
        Tangani klik mouse pada canvas.
        Hitung baris/kolom berdasarkan koordinat klik, lalu pilih sel itu.
        """
        x, y = event.x - BOARD_OFFSET, event.y - BOARD_OFFSET
        col  = x // CELL_SIZE
        row  = y // CELL_SIZE
        if 0 <= row < 9 and 0 <= col < 9:
            self.selected = (row, col)
            self._draw_board()

    def _on_keypress(self, event: tk.Event):
        """
        Tangani penekanan tombol keyboard.
        - Angka 1–9  : isi sel yang dipilih (jika bukan sel soal)
        - Backspace/Delete/0 : hapus isi sel
        """
        if self.selected is None:
            return
        row, col = self.selected

        if self.given[row][col]:          # sel soal tidak bisa diubah
            return

        key = event.keysym
        if key in ("BackSpace", "Delete", "0"):
            self.user_grid[row][col] = 0
        elif key.isdigit() and key != "0":
            self.user_grid[row][col] = int(key)

        self._draw_board()
        self._check_win()                 # cek apakah puzzle sudah selesai

    # ── Menggambar papan ──────────────────────────────────────────────────

    def _draw_board(self):
        """
        Hapus canvas lalu gambar ulang seluruh papan:
        latar sel, angka, dan garis grid.
        Dipanggil setiap kali ada perubahan state.
        """
        self.canvas.delete("all")
        self._draw_cells()
        self._draw_numbers()
        self._draw_grid_lines()

    def _draw_cells(self):
        """Gambar latar belakang setiap sel, sorot sel yang dipilih."""
        for r in range(9):
            for c in range(9):
                x1 = BOARD_OFFSET + c * CELL_SIZE
                y1 = BOARD_OFFSET + r * CELL_SIZE
                x2 = x1 + CELL_SIZE
                y2 = y1 + CELL_SIZE

                if self.selected == (r, c):
                    fill = COLOR_SELECT          # sorot biru muda
                else:
                    fill = COLOR_BOARD           # putih biasa

                self.canvas.create_rectangle(x1, y1, x2, y2, fill=fill, outline="")

    def _draw_numbers(self):
        """
        Gambar angka di setiap sel:
        - Angka soal  → hitam tebal
        - Input benar → biru
        - Input salah → merah (duplikat dalam baris/kolom/kotak)
        """
        for r in range(9):
            for c in range(9):
                cx = BOARD_OFFSET + c * CELL_SIZE + CELL_SIZE // 2
                cy = BOARD_OFFSET + r * CELL_SIZE + CELL_SIZE // 2

                if self.given[r][c]:
                    # Angka soal yang dikunci
                    num = self.puzzle[r][c]
                    self.canvas.create_text(
                        cx, cy, text=str(num),
                        font=FONT_GIVEN, fill=COLOR_GIVEN
                    )
                elif self.user_grid[r][c] != 0:
                    # Angka yang diisi pemain
                    num   = self.user_grid[r][c]
                    valid = self._is_user_input_valid(r, c, num)
                    color = COLOR_USER_OK if valid else COLOR_USER_ERR
                    self.canvas.create_text(
                        cx, cy, text=str(num),
                        font=FONT_USER, fill=color
                    )

    def _draw_grid_lines(self):
        """
        Gambar garis-garis grid.
        Garis tipis antar sel biasa; garis tebal antar sub-grid 3×3.
        """
        total = CELL_SIZE * 9
        for i in range(10):
            is_thick = (i % 3 == 0)
            width = 3 if is_thick else 1
            color = COLOR_SUBGRID if is_thick else COLOR_CELL

            # Garis horizontal
            x0 = BOARD_OFFSET
            y  = BOARD_OFFSET + i * CELL_SIZE
            self.canvas.create_line(x0, y, x0 + total, y, fill=color, width=width)

            # Garis vertikal
            x  = BOARD_OFFSET + i * CELL_SIZE
            y0 = BOARD_OFFSET
            self.canvas.create_line(x, y0, x, y0 + total, fill=color, width=width)

    # ── Validasi ──────────────────────────────────────────────────────────

    def _is_user_input_valid(self, row, col, num):
        """
        Periksa apakah angka yang dimasukkan pemain valid dalam konteks
        seluruh papan (gabungan angka soal dan input pemain lainnya).
        Mengembalikan True jika tidak ada konflik, False jika ada duplikat.
        """
        # Bangun tampilan papan saat ini
        board = self._current_board()
        # Sementara kosongkan sel ini agar tidak menghitung dirinya sendiri
        board[row][col] = 0
        return is_valid_placement(board, row, col, num)

    def _current_board(self):
        """
        Gabungkan angka soal (puzzle) dan input pemain (user_grid) menjadi
        satu papan 9×9 yang merepresentasikan kondisi game saat ini.
        """
        board = [[0] * 9 for _ in range(9)]
        for r in range(9):
            for c in range(9):
                if self.given[r][c]:
                    board[r][c] = self.puzzle[r][c]
                else:
                    board[r][c] = self.user_grid[r][c]
        return board

    def _check_win(self):
        """
        Cek apakah pemain telah mengisi semua sel dengan benar.
        Kondisi menang: setiap sel terisi DAN semua input valid.
        """
        for r in range(9):
            for c in range(9):
                if self.given[r][c]:
                    continue
                val = self.user_grid[r][c]
                if val == 0:                              # masih ada yang kosong
                    return
                if not self._is_user_input_valid(r, c, val):  # ada yang salah
                    return
        # Jika sampai di sini, semua sel valid dan terisi
        messagebox.showinfo(
            "Selamat! 🏆",
            "Hebat! Kamu berhasil menyelesaikan puzzle Sudoku!\nMain lagi?"
        )


# ─────────────────────────────────────────────
#  ENTRY POINT
# ─────────────────────────────────────────────

if __name__ == "__main__":
    root = tk.Tk()
    app  = SudokuApp(root)
    root.mainloop()
