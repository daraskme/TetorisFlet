import flet as ft
import random

GRID_SIZE = 30
GRID_WIDTH = 10
GRID_HEIGHT = 20
SHAPES = [
    [[1, 1, 1, 1]],  # I
    [[1, 1], [1, 1]],  # O
    [[1, 1, 1], [0, 1, 0]],  # T
    [[1, 1, 1], [1, 0, 0]],  # L
    [[1, 1, 1], [0, 0, 1]],  # J
    [[1, 1, 0], [0, 1, 1]],  # S
    [[0, 1, 1], [1, 1, 0]]   # Z
]
COLORS = [ft.colors.CYAN, ft.colors.YELLOW, ft.colors.PURPLE, ft.colors.ORANGE, ft.colors.BLUE, ft.colors.GREEN, ft.colors.RED]

class Tetris:
    def __init__(self, page: ft.Page):
        self.page = page
        self.grid = [[0 for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
        self.current_piece = None
        self.current_pos = [0, 0]
        self.game_over = False
        self.score = 0
        self.level = 1
        self.lines_cleared = 0
        self.bag = []
        self.next_pieces = []
        self.hold_piece = None
        self.can_hold = True
        
        self.game_area = ft.Stack(
            width=GRID_WIDTH * GRID_SIZE,
            height=GRID_HEIGHT * GRID_SIZE,
            controls=[
                ft.Container(
                    width=GRID_WIDTH * GRID_SIZE,
                    height=GRID_HEIGHT * GRID_SIZE,
                    border=ft.border.all(1, ft.colors.BLACK)
                )
            ]
        )
        self.next_area = ft.Column(width=150, height=400)
        self.hold_area = ft.Container(width=150, height=150, border=ft.border.all(1, ft.colors.BLACK))
        self.score_text = ft.Text(f"Score: {self.score}")
        self.level_text = ft.Text(f"Level: {self.level}")
        
        # 操作説明を追加
        self.controls_text = ft.Text(
            "Controls:\n"
            "← → : Move left/right\n"
            "↑ : Rotate\n"
            "↓ : Soft drop\n"
            "Space : Hard drop\n"
            "C : Hold",
            size=16,
        )
        
        game_column = ft.Column([
            ft.Row([self.hold_area, self.game_area, 
                    ft.Column([self.next_area, self.controls_text])]),  # ここに操作説明を追加
            self.score_text,
            self.level_text
        ])
        
        self.page.add(game_column)
        self.page.on_keyboard_event = self.on_keyboard
        
        self.new_piece()
        self.update_game_area()
        self.page.update()
        
    def new_piece(self):
        if not self.bag:
            self.bag = list(range(7))
            random.shuffle(self.bag)
        
        if len(self.next_pieces) < 3:
            self.next_pieces.append(SHAPES[self.bag.pop()])
        
        self.current_piece = self.next_pieces.pop(0)
        self.current_pos = [GRID_WIDTH // 2 - len(self.current_piece[0]) // 2, 0]
        self.can_hold = True
        
        if not self.is_valid_move(self.current_piece, self.current_pos):
            self.game_over = True
        
        self.update_next_area()
        
    def rotate_piece(self):
        rotated = list(zip(*self.current_piece[::-1]))
        if self.is_valid_move(rotated, self.current_pos):
            self.current_piece = rotated
        else:
            # SRSを実装する場合はここで壁蹴りなどの処理を行う
            pass
        
    def is_valid_move(self, piece, pos):
        for y, row in enumerate(piece):
            for x, cell in enumerate(row):
                if cell:
                    if (pos[0] + x < 0 or pos[0] + x >= GRID_WIDTH or
                        pos[1] + y >= GRID_HEIGHT or
                        (pos[1] + y >= 0 and self.grid[pos[1] + y][pos[0] + x])):
                        return False
        return True
        
    def merge_piece(self):
        for y, row in enumerate(self.current_piece):
            for x, cell in enumerate(row):
                if cell:
                    self.grid[self.current_pos[1] + y][self.current_pos[0] + x] = SHAPES.index(self.current_piece) + 1
        
    def clear_lines(self):
        lines_to_clear = [i for i, row in enumerate(self.grid) if all(row)]
        for line in lines_to_clear:
            del self.grid[line]
            self.grid.insert(0, [0 for _ in range(GRID_WIDTH)])
        return len(lines_to_clear)
        
    def update_game_area(self):
        self.game_area.controls = [self.game_area.controls[0]]  # Keep the border
        for y, row in enumerate(self.grid):
            for x, cell in enumerate(row):
                if cell:
                    self.game_area.controls.append(
                        ft.Container(
                            left=x * GRID_SIZE,
                            top=y * GRID_SIZE,
                            width=GRID_SIZE,
                            height=GRID_SIZE,
                            bgcolor=COLORS[cell - 1]
                        )
                    )
        
        if self.current_piece:
            ghost_pos = self.get_ghost_position()
            for y, row in enumerate(self.current_piece):
                for x, cell in enumerate(row):
                    if cell:
                        # Draw ghost piece
                        self.game_area.controls.append(
                            ft.Container(
                                left=(ghost_pos[0] + x) * GRID_SIZE,
                                top=(ghost_pos[1] + y) * GRID_SIZE,
                                width=GRID_SIZE,
                                height=GRID_SIZE,
                                bgcolor=ft.colors.WHITE24
                            )
                        )
                        # Draw current piece
                        self.game_area.controls.append(
                            ft.Container(
                                left=(self.current_pos[0] + x) * GRID_SIZE,
                                top=(self.current_pos[1] + y) * GRID_SIZE,
                                width=GRID_SIZE,
                                height=GRID_SIZE,
                                bgcolor=COLORS[SHAPES.index(self.current_piece)]
                            )
                        )
    
    def update_next_area(self):
        self.next_area.controls.clear()
        for i, piece in enumerate(self.next_pieces):
            piece_container = ft.Container(
                width=120,
                height=120,
                content=ft.Stack(
                    controls=[
                        ft.Container(
                            left=x * 30,
                            top=y * 30,
                            width=30,
                            height=30,
                            bgcolor=COLORS[SHAPES.index(piece)]
                        )
                        for y, row in enumerate(piece)
                        for x, cell in enumerate(row) if cell
                    ]
                )
            )
            self.next_area.controls.append(piece_container)
    
    def update_hold_area(self):
        self.hold_area.content = None
        if self.hold_piece:
            self.hold_area.content = ft.Stack(
                controls=[
                    ft.Container(
                        left=x * 30,
                        top=y * 30,
                        width=30,
                        height=30,
                        bgcolor=COLORS[SHAPES.index(self.hold_piece)]
                    )
                    for y, row in enumerate(self.hold_piece)
                    for x, cell in enumerate(row) if cell
                ]
            )
    
    def get_ghost_position(self):
        ghost_pos = self.current_pos.copy()
        while self.is_valid_move(self.current_piece, [ghost_pos[0], ghost_pos[1] + 1]):
            ghost_pos[1] += 1
        return ghost_pos
    
    def hold(self):
        if self.can_hold:
            if self.hold_piece:
                self.hold_piece, self.current_piece = self.current_piece, self.hold_piece
                self.current_pos = [GRID_WIDTH // 2 - len(self.current_piece[0]) // 2, 0]
            else:
                self.hold_piece = self.current_piece
                self.new_piece()
            self.can_hold = False
            self.update_hold_area()
        
    def on_keyboard(self, e: ft.KeyboardEvent):
        if self.game_over:
            return
        
        if e.key == "ArrowLeft":
            new_pos = [self.current_pos[0] - 1, self.current_pos[1]]
            if self.is_valid_move(self.current_piece, new_pos):
                self.current_pos = new_pos
        elif e.key == "ArrowRight":
            new_pos = [self.current_pos[0] + 1, self.current_pos[1]]
            if self.is_valid_move(self.current_piece, new_pos):
                self.current_pos = new_pos
        elif e.key == "ArrowDown":
            self.move_down()
        elif e.key == "ArrowUp":
            self.rotate_piece()
        elif e.key == " ":  # Space bar for hard drop
            while self.move_down():
                pass
        elif e.key == "C":  # 'C' key for hold
            self.hold()
        
        self.update_game_area()
        self.page.update()
        
    def move_down(self):
        new_pos = [self.current_pos[0], self.current_pos[1] + 1]
        if self.is_valid_move(self.current_piece, new_pos):
            self.current_pos = new_pos
            return True
        else:
            self.merge_piece()
            lines_cleared = self.clear_lines()
            self.lines_cleared += lines_cleared
            self.score += lines_cleared * 100 * self.level
            self.level = self.lines_cleared // 10 + 1
            self.score_text.value = f"Score: {self.score}"
            self.level_text.value = f"Level: {self.level}"
            self.new_piece()
            return False
        
    def run(self):
        import time
        while not self.game_over:
            self.move_down()
            self.update_game_area()
            self.page.update()
            time.sleep(max(0.1, 0.5 - (self.level - 1) * 0.05))
        
        game_over_text = ft.Text("Game Over!", size=30, color=ft.colors.RED)
        self.page.add(game_over_text)
        self.page.update()

def main(page: ft.Page):
    page.title = "Tetris"
    game = Tetris(page)
    page.update()
    game.run()

ft.app(target=main)