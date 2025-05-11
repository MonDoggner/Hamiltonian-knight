import os
import tkinter as tk
from time import sleep


class KnightTour:
    def __init__(self, root):
        """Инициализация класса, создание шахматной доски и интерфейса"""
        self.root = root
        self.root.title('Гамильтонов конь')  # Заголовок окна

        # Параметры доски
        self.board_size = 400  # Общий размер доски в пикселях
        self.square_size = self.board_size // 8  # Размер одной клетки
        self.margin = 30  # Отступ от краев окна

        # Создание холста для рисования
        self.canvas = tk.Canvas(root,
                                width=self.board_size + 2 * self.margin,
                                height=self.board_size + 2 * self.margin,
                                bg="white")
        self.canvas.pack()

        # Цвета клеток и состояние доски
        self.colors = ["#f0d9b5", "#b58863"]  # Цвета клеток (светлая/темная)
        self.visited_color = "#a0c0ff"  # Цвет для посещенных клеток
        self.board = [[0 for _ in range(8)] for _ in range(8)]  # Матрица доски (0 - пусто)
        self.cell_coords = []  # Координаты центров клеток для размещения коня
        self.create_board()  # Инициализация визуальной доски

        # Все возможные ходы коня (8 направлений)
        self.moves = [
            (1, 2), (2, 1),  # Вниз-вправо
            (-1, 2), (-2, 1),  # Вверх-вправо
            (-1, -2), (-2, -1),  # Вверх-влево
            (1, -2), (2, -1)  # Вниз-влево
        ]

        # Кеш для хранения состояний доски (мемоизация)
        self.cache = {}

        # Загрузка изображения коня
        try:
            self.piece_img = tk.PhotoImage(file=os.path.join(os.path.dirname(__file__), "Конь.png"))
            self.root.piece_img = self.piece_img  # Сохраняем ссылку, чтобы изображение не удалилось
        except:
            # Если изображение не найдено, создаем простой круг
            self.piece_img = None

        # Начальная позиция коня (строка, столбец)
        self.start_row, self.start_col = 1, 7  # Соответствует позиции (2,8)
        self.piece = None  # Ссылка на изображение коня на холсте
        self.place_knight(self.start_row, self.start_col)  # Размещаем коня

        # Флаги состояния и параметры анимации
        self.solution_found = False  # Найден ли полный путь
        self.stop_search = False  # Флаг для остановки поиска
        self.animation_speed = 0.05  # Базовая скорость анимации (секунды)

        # Настройка интерфейса
        self.setup_ui()
        self.setup_click_handler()

    def create_board(self):
        """Создает визуальное представление шахматной доски"""
        for row in range(8):
            row_coords = []
            for col in range(8):
                # Координаты углов текущей клетки
                x1 = col * self.square_size + self.margin
                y1 = row * self.square_size + self.margin
                x2 = x1 + self.square_size
                y2 = y1 + self.square_size

                # Чередование цветов клеток
                color = self.colors[(row + col) % 2]

                # Создание прямоугольника клетки
                self.canvas.create_rectangle(x1, y1, x2, y2,
                                             fill=color,
                                             outline="black",
                                             tags=f"cell_{row}_{col}")

                # Вычисление центра клетки (для размещения коня)
                center_x = x1 + self.square_size // 2
                center_y = y1 + self.square_size // 2
                row_coords.append((center_x, center_y))

            self.cell_coords.append(row_coords)  # Сохраняем координаты центров

        # Добавление номеров строк и столбцов
        font = ("Arial", 12, "bold")
        for row in range(8):
            # Номера строк слева
            x = self.margin // 2
            y = row * self.square_size + self.margin + self.square_size // 2
            self.canvas.create_text(x, y, text=str(1 + row), font=font)

        for col in range(8):
            # Номера столбцов сверху
            x = col * self.square_size + self.margin + self.square_size // 2
            y = self.margin // 2
            self.canvas.create_text(x, y, text=str(col + 1), font=font)

    def setup_ui(self):
        """Настройка пользовательского интерфейса (кнопки, слайдер)"""
        control_frame = tk.Frame(self.root)
        control_frame.pack(fill=tk.X, padx=5, pady=5)

        # Кнопка выбора позиции
        self.btn_select = tk.Button(control_frame,
                                    text="Выбрать позицию",
                                    command=self.enable_position_selection)
        self.btn_select.pack(side=tk.LEFT, padx=5)

        # Кнопка начала поиска
        self.btn_start = tk.Button(control_frame,
                                   text="Начать поиск",
                                   command=self.start_tour)
        self.btn_start.pack(side=tk.LEFT, padx=5)

        # Кнопка остановки
        self.btn_stop = tk.Button(control_frame,
                                  text="Остановить",
                                  command=self.stop_tour)
        self.btn_stop.pack(side=tk.LEFT, padx=5)

        # Кнопка сброса
        self.btn_reset = tk.Button(control_frame,
                                   text="Сбросить",
                                   command=self.reset_board)
        self.btn_reset.pack(side=tk.LEFT, padx=5)

        # Слайдер для управления скоростью анимации
        self.speed_label = tk.Label(control_frame, text="Скорость:")
        self.speed_label.pack(side=tk.LEFT, padx=5)

        self.speed_scale = tk.Scale(control_frame,
                                    from_=0,
                                    to=100,
                                    orient=tk.HORIZONTAL,
                                    command=self.set_animation_speed)
        self.speed_scale.set(50)  # Среднее значение по умолчанию
        self.speed_scale.pack(side=tk.LEFT, padx=5)

        # Метка статуса
        self.status_label = tk.Label(control_frame,
                                     text="Выберите стартовую позицию коня")
        self.status_label.pack(side=tk.LEFT, padx=10)

        # Флаг режима выбора позиции
        self.position_selection_mode = False

    def set_animation_speed(self, value):
        """Установка скорости анимации на основе значения слайдера"""
        # Преобразуем значение слайдера (0-100) в интервал задержки
        # 100 -> 0.005s (быстро), 0 -> 0.05s (медленно)
        self.animation_speed = (100 - int(value)) / 2000

    def setup_click_handler(self):
        """Настройка обработки кликов по доске"""
        self.canvas.bind("<Button-1>", self.on_canvas_click)

    def enable_position_selection(self):
        """Активация режима выбора стартовой позиции"""
        self.position_selection_mode = True
        self.status_label.config(text="Кликните на клетку для выбора стартовой позиции")

    def on_canvas_click(self, event):
        """Обработка клика по доске в режиме выбора позиции"""
        if not self.position_selection_mode:
            return  # Выходим, если не в режиме выбора

        # Определяем клетку по координатам клика
        col = (event.x - self.margin) // self.square_size
        row = (event.y - self.margin) // self.square_size

        # Проверяем, что координаты в пределах доски
        if 0 <= row < 8 and 0 <= col < 8:
            self.start_row, self.start_col = row, col  # Обновляем стартовую позицию
            self.place_knight(row, col)  # Перемещаем коня
            self.status_label.config(text=f"Стартовая позиция: ({col + 1}, {row + 1})")
            self.position_selection_mode = False  # Выходим из режима выбора

    def place_knight(self, row, col):
        """Размещение коня на указанной клетке"""
        if self.piece:
            self.canvas.delete(self.piece)  # Удаляем старое изображение

        # Если изображение коня загружено, используем его
        if self.piece_img:
            self.piece = self.canvas.create_image(
                self.cell_coords[row][col][0],
                self.cell_coords[row][col][1],
                image=self.piece_img
            )
        else:
            # Иначе рисуем простой круг
            x, y = self.cell_coords[row][col]
            self.piece = self.canvas.create_oval(x - 15, y - 15, x + 15, y + 15,
                                                 fill="black", outline="gold")

    def reset_board(self):
        """Полный сброс доски в начальное состояние"""
        self.stop_search = True  # Останавливаем текущий поиск
        self.board = [[0 for _ in range(8)] for _ in range(8)]  # Очищаем матрицу
        self.cache = {}  # Очищаем кеш

        # Восстанавливаем исходные цвета всех клеток
        for row in range(8):
            for col in range(8):
                self.canvas.itemconfig(f"cell_{row}_{col}",
                                       fill=self.colors[(row + col) % 2])

        # Возвращаем коня на стартовую позицию
        self.place_knight(self.start_row, self.start_col)
        self.status_label.config(text="Доска сброшена. Выберите стартовую позицию")
        self.root.update()  # Принудительное обновление интерфейса

    def stop_tour(self):
        """Остановка текущего поиска пути"""
        self.stop_search = True
        self.status_label.config(text="Поиск остановлен")

    def is_valid_move(self, x, y):
        """Проверяет, что:
        1. Координаты (x,y) находятся в пределах доски
        2. Клетка еще не посещалась"""
        if not (0 <= x < 8 and 0 <= y < 8):
            return False
        return self.board[x][y] == 0

    def get_board_hash(self):
        """Генерация уникального хеша текущего состояния доски для кеширования"""
        return hash(tuple(tuple(row) for row in self.board))

    def draw_move(self, x, y):
        """Визуализация хода коня"""
        # Закрашиваем клетку цветом посещения
        self.canvas.itemconfig(f"cell_{x}_{y}", fill=self.visited_color)

        # Перемещаем коня
        self.canvas.coords(self.piece,
                           self.cell_coords[x][y][0],
                           self.cell_coords[x][y][1])

        self.root.update()  # Обновляем интерфейс
        sleep(self.animation_speed)  # Задержка для анимации

    def hamiltonian_tour(self, x, y, move_number):
        """Рекурсивный поиск гамильтонова пути с кешированием"""
        if self.stop_search:
            return False  # Поиск был остановлен

        # Генерируем хеш текущего состояния доски
        board_hash = self.get_board_hash()

        # Проверяем кеш перед выполнением рекурсии
        if board_hash in self.cache:
            return self.cache[board_hash]

        # Помечаем текущую клетку как посещенную
        self.board[x][y] = move_number
        self.draw_move(x, y)  # Визуализируем ход

        # Если сделали 64 хода - решение найдено
        if move_number == 64:
            self.solution_found = True
            self.status_label.config(text="Гамильтонов путь найден!")
            self.cache[board_hash] = True  # Сохраняем в кеш
            return True

        # Применяем эвристику Варнсдорфа: сортируем ходы по доступности
        moves_with_score = []
        for dx, dy in self.moves:
            nx, ny = x + dx, y + dy
            if self.is_valid_move(nx, ny):
                # Считаем количество возможных ходов из новой позиции
                count = 0
                for ddx, ddy in self.moves:
                    nnx, nny = nx + ddx, ny + ddy
                    if self.is_valid_move(nnx, nny):
                        count += 1
                moves_with_score.append((count, dx, dy))

        # Сортируем ходы по возрастанию доступных вариантов
        moves_with_score.sort()

        # Пробуем все ходы в оптимальном порядке
        for count, dx, dy in moves_with_score:
            next_x, next_y = x + dx, y + dy
            if self.hamiltonian_tour(next_x, next_y, move_number + 1):
                self.cache[board_hash] = True  # Сохраняем успешный результат
                return True

        # Backtracking - если решение не найдено
        if not self.solution_found:
            self.board[x][y] = 0  # Освобождаем клетку

            # Восстанавливаем исходный цвет клетки
            color = self.colors[(x + y) % 2]
            self.canvas.itemconfig(f"cell_{x}_{y}", fill=color)

            self.root.update()
            sleep(self.animation_speed / 2)  # Уменьшенная задержка при откате

        # Сохраняем неудачный результат в кеш
        self.cache[board_hash] = False
        return False

    def start_tour(self):
        """Запуск процесса поиска гамильтонова пути"""
        self.solution_found = False
        self.stop_search = False
        self.board = [[0 for _ in range(8)] for _ in range(8)]  # Очищаем доску
        self.cache = {}  # Очищаем кеш

        self.status_label.config(text="Идет поиск пути...")
        self.root.update()  # Обновляем интерфейс

        # Запускаем рекурсивный поиск
        if not self.hamiltonian_tour(self.start_row, self.start_col, 1):
            self.status_label.config(text="Гамильтонов путь не найден")


# Создание и запуск приложения
if __name__ == "__main__":
    root = tk.Tk()
    app = KnightTour(root)
    root.mainloop()