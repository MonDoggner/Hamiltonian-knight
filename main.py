
import os
import tkinter as tk
from time import sleep

class KnightTour:
    def __init__(self, root):
        self.root = root
        self.root.title('Гамильтонов конь')
        
        self.board_size = 400
        self.square_size = self.board_size // 8
        self.margin = 30
        
        self.canvas = tk.Canvas(root, 
                              width=self.board_size + 2 * self.margin, 
                              height=self.board_size + 2 * self.margin, 
                              bg="white")
        self.canvas.pack()
        
        self.colors = ["#f0d9b5", "#b58863"]
        self.board = [[0 for _ in range(8)] for _ in range(8)]
        self.cell_coords = []
        self.create_board()
        
        self.moves = [
            (1, 2), (2, 1), 
            (-1, 2), (-2, 1),
            (-1, -2), (-2, -1),
            (1, -2), (2, -1)
        ]
        
        self.piece_img = tk.PhotoImage(file=os.path.join("Конь.png"))
        self.root.piece_img = self.piece_img
        
        self.start_row, self.start_col = 1, 7  # Начальная позиция (2,8)
        self.piece = None
        self.place_knight(self.start_row, self.start_col)
        
        self.solution_found = False
        self.stop_search = False
        self.move_history = []  # Для хранения истории ходов
        
        self.setup_ui()
        self.setup_click_handler()
    
    def create_board(self):
        for row in range(8):
            row_coords = []
            for col in range(8):
                x1 = col * self.square_size + self.margin
                y1 = row * self.square_size + self.margin
                x2 = x1 + self.square_size
                y2 = y1 + self.square_size
                color = self.colors[(row + col) % 2]
                self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline="black", tags=f"cell_{row}_{col}")
                center_x = x1 + self.square_size // 2
                center_y = y1 + self.square_size // 2
                row_coords.append((center_x, center_y))
            self.cell_coords.append(row_coords)
        
        font = ("Arial", 12, "bold")
        for row in range(8):
            x = self.margin // 2
            y = row * self.square_size + self.margin + self.square_size // 2
            self.canvas.create_text(x, y, text=str(1 + row), font=font)
        
        for col in range(8):
            x = col * self.square_size + self.margin + self.square_size // 2
            y = self.margin // 2
            self.canvas.create_text(x, y, text=str(col + 1), font=font)
    
    def setup_ui(self):
        control_frame = tk.Frame(self.root)
        control_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.btn_select = tk.Button(control_frame, text="Выбрать позицию", command=self.enable_position_selection)
        self.btn_select.pack(side=tk.LEFT, padx=5)
        
        self.btn_start = tk.Button(control_frame, text="Начать поиск", command=self.start_tour)
        self.btn_start.pack(side=tk.LEFT, padx=5)
        
        self.btn_stop = tk.Button(control_frame, text="Остановить", command=self.stop_tour)
        self.btn_stop.pack(side=tk.LEFT, padx=5)
        
        self.btn_reset = tk.Button(control_frame, text="Сбросить", command=self.reset_board)
        self.btn_reset.pack(side=tk.LEFT, padx=5)
        
        self.status_label = tk.Label(control_frame, text="Выберите стартовую позицию коня")
        self.status_label.pack(side=tk.LEFT, padx=10)
        
        self.position_selection_mode = False
    
    def setup_click_handler(self):
        self.canvas.bind("<Button-1>", self.on_canvas_click)
    
    def enable_position_selection(self):
        self.position_selection_mode = True
        self.status_label.config(text="Кликните на клетку для выбора стартовой позиции")
    
    def on_canvas_click(self, event):
        if not self.position_selection_mode:
            return
            
        col = (event.x - self.margin) // self.square_size
        row = (event.y - self.margin) // self.square_size
        
        if 0 <= row < 8 and 0 <= col < 8:
            self.start_row, self.start_col = row, col
            self.place_knight(row, col)
            self.status_label.config(text=f"Стартовая позиция: ({col+1}, {row+1})")
            self.position_selection_mode = False
    
    def place_knight(self, row, col):
        if self.piece:
            self.canvas.delete(self.piece)
        
        self.piece = self.canvas.create_image(
            self.cell_coords[row][col][0],
            self.cell_coords[row][col][1],
            image=self.piece_img
        )
    
    def reset_board(self):
        self.stop_search = True
        self.board = [[0 for _ in range(8)] for _ in range(8)]
        self.move_history = []
        
        # Очищаем все номера ходов
        for row in range(8):
            for col in range(8):
                self.canvas.itemconfig(f"cell_{row}_{col}", fill=self.colors[(row + col) % 2])
                # Удаляем все текстовые метки
                for item in self.canvas.find_withtag(f"text_{row}_{col}"):
                    self.canvas.delete(item)
        
        self.place_knight(self.start_row, self.start_col)
        self.status_label.config(text="Доска сброшена. Выберите стартовую позицию")
        self.root.update()
    
    def stop_tour(self):
        self.stop_search = True
        self.status_label.config(text="Поиск остановлен")
    
    def is_valid_move(self, x, y):
        return 0 <= x < 8 and 0 <= y < 8 and self.board[x][y] == 0
    
    def draw_move(self, x, y, move_number):
        # Оставляем все предыдущие номера на доске
        self.canvas.itemconfig(f"cell_{x}_{y}", fill="white")
        
        # Создаем текст с номером хода
        text_id = self.canvas.create_text(
            self.cell_coords[x][y][0], 
            self.cell_coords[x][y][1], 
            text=str(move_number), 
            font=("Arial", 12, "bold"), 
            fill="red",
            tags=f"text_{x}_{y}"
        )
        
        # Перемещаем коня
        self.canvas.coords(self.piece, self.cell_coords[x][y][0], self.cell_coords[x][y][1])
        
        # Сохраняем ход в историю
        self.move_history.append((x, y, move_number, text_id))
        
        self.root.update()
        sleep(0.1)  # Замедление для визуализации
    
    def heuristic_order_moves(self, x, y):
        # Эвристика Варнсдорфа: сортируем ходы по доступности
        moves_with_count = []
        for dx, dy in self.moves:
            nx, ny = x + dx, y + dy
            if self.is_valid_move(nx, ny):
                count = 0
                for ddx, ddy in self.moves:
                    nnx, nny = nx + ddx, ny + ddy
                    if self.is_valid_move(nnx, nny):
                        count += 1
                moves_with_count.append((count, dx, dy))
        
        # Сортируем по возрастанию доступных ходов
        moves_with_count.sort()
        return [(dx, dy) for (count, dx, dy) in moves_with_count]
    
    def hamiltonian_tour(self, x, y, move_number):
        if self.stop_search:
            return False
            
        self.board[x][y] = move_number
        self.draw_move(x, y, move_number)
        
        if move_number == 64:
            self.solution_found = True
            self.status_label.config(text="Гамильтонов путь найден!")
            return True
        
        # Используем эвристику для выбора следующего хода
        for dx, dy in self.heuristic_order_moves(x, y):
            next_x, next_y = x + dx, y + dy
            if self.hamiltonian_tour(next_x, next_y, move_number + 1):
                return True
        
        # Backtracking - оставляем номер, но отмечаем клетку как свободную
        if not self.solution_found:
            self.board[x][y] = 0
            # Не удаляем текст при backtracking, только меняем цвет
            self.canvas.itemconfig(f"cell_{x}_{y}", fill="#a0a0a0")  # Серый для неудачных ходов
            self.root.update()
            sleep(0.05)
        
        return False
    
    def start_tour(self):
        self.solution_found = False
        self.stop_search = False
        self.board = [[0 for _ in range(8)] for _ in range(8)]
        self.move_history = []
        self.status_label.config(text="Идет поиск пути...")
        self.root.update()
        
        if not self.hamiltonian_tour(self.start_row, self.start_col, 1):
            self.status_label.config(text="Гамильтонов путь не найден")

root = tk.Tk()
app = KnightTour(root)
root.mainloop()