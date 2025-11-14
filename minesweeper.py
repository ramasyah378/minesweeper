import pygame
import sys
import time
import random

# Set judul jendela
pygame.display.set_caption('Minesweeper')

# Class Minesweeper 
class Minesweeper():

    def __init__(self, height=10, width=10, mines=8):
        # Tetapkan lebar, tinggi, dan jumlah ranjau awal
        self.height = height
        self.width = width
        self.mines = set()

        #  Inisialisasi papan kosong tanpa ranjau
        self.board = []
        for i in range(self.height):
            row = []
            for j in range(self.width):
                row.append(False)
            self.board.append(row)

        # Tambahkan ranjau secara acak
        while len(self.mines) != mines:
            i = random.randrange(height)
            j = random.randrange(width)
            if not self.board[i][j]:
                self.mines.add((i, j))
                self.board[i][j] = True

        # Pada awalnya, pemain belum menemukan ranjau
        self.mines_found = set()

    def print(self):
        """Mencetak representasi teks dari lokasi ranjau"""
        for i in range(self.height):
            print("--" * self.width + "-")
            for j in range(self.width):
                if self.board[i][j]:
                    print("|X", end="")
                else:
                    print("| ", end="")
            print("|")
        print("--" * self.width + "-")

    def is_mine(self, cell):
        i, j = cell
        return self.board[i][j]

    def nearby_mines(self, cell):
        """
        Mengembalikan jumlah ranjau yang berada
        dalam satu baris dan kolom dari sel yang diberikan,
        tidak termasuk sel itu sendiri.
        """
        # Menghitung jumlah ranjau terdekat
        count = 0
        # Mengulang semua sel dalam satu baris dan kolom
        for i in range(cell[0] - 1, cell[0] + 2):
            for j in range(cell[1] - 1, cell[1] + 2):
                # Abaikan sel itu sendiri
                if (i, j) == cell:
                    continue
                # Perbarui hitungan jika sel berada dalam batas dan merupakan ranjau
                if 0 <= i < self.height and 0 <= j < self.width:
                    if self.board[i][j]:
                        count += 1
        return count

    def won(self):
        """Memeriksa apakah semua ranjau telah ditandai"""
        return self.mines_found == self.mines

class Sentence():
    """
     Pernyataan logis tentang permainan Minesweeper
    Sebuah kalimat terdiri dari satu set sel papan,
    dan hitungan jumlah sel tersebut yang merupakan ranjau.
    """
    def __init__(self, cells, count):
        self.cells = set(cells)
        self.count = count

    def __eq__(self, other):
        return self.cells == other.cells and self.count == other.count

    def __str__(self):
        return f"{self.cells} = {self.count}"

    def known_mines(self):
        """Mengembalikan himpunan semua sel di self.cells yang diketahui sebagai ranjau."""
        if self.count == len(self.cells):
            return self.cells
        return None

    def known_safes(self):
        """Mengembalikan himpunan semua sel di self.cells yang diketahui aman."""
        if not self.count:
            return self.cells
        return None

    def mark_mine(self, cell):
        """
        Memperbarui representasi pengetahuan internal mengingat fakta bahwa
        sebuah sel diketahui sebagai ranjau.
        """
        if cell in self.cells:
            self.cells.remove(cell)
            self.count -= 1

    def mark_safe(self, cell):
        """
        Memperbarui representasi pengetahuan internal mengingat fakta bahwa
        sebuah sel diketahui aman
        """
        if cell in self.cells:
            self.cells.remove(cell)

class MinesweeperAI():
    """Pemain permainan Minesweeper"""

    def __init__(self, height=10, width=10):
        # Set initial height and width
        self.height = height
        self.width = width

        # Keep track of which cells have been clicked on
        self.moves_made = set()

        # Keep track of cells known to be safe or mines
        self.mines = set()
        self.safes = set()

        # List of sentences about the game known to be true
        self.knowledge = []

    def mark_mine(self, cell):
        """
        Menandai sel sebagai ranjau, dan memperbarui semua pengetahuan
        untuk menandai sel itu sebagai ranjau juga.
        """
        self.mines.add(cell)
        for sentence in self.knowledge:
            sentence.mark_mine(cell)

    def mark_safe(self, cell):
        """
        Menandai sel sebagai aman, dan memperbarui semua pengetahuan
        untuk menandai sel tersebut sebagai aman juga.
        """
        self.safes.add(cell)
        for sentence in self.knowledge:
            sentence.mark_safe(cell)

    def add_knowledge(self, cell, count):
        """
        Dipanggil ketika papan Minesweeper memberi tahu kita, untuk sebuah sel aman tertentu,
        berapa banyak sel tetangga yang memiliki ranjau di dalamnya.

        Fungsi ini harus:
            1) menandai sel tersebut sebagai langkah yang telah dilakukan
            2) menandai sel tersebut sebagai aman
            3) menambahkan kalimat baru ke basis pengetahuan AI
               berdasarkan nilai sel dan hitungan
            4) menandai sel tambahan sebagai aman atau ranjau
               jika dapat disimpulkan berdasarkan basis pengetahuan AI
            5) menambahkan kalimat baru ke basis pengetahuan AI
               jika dapat disimpulkan dari pengetahuan yang ada
        """
        # 1) menandai sel tersebut sebagai langkah yang telah dilakukan
        self.moves_made.add(cell)

        # 2) menandai sel tersebut sebagai aman
        self.mark_safe(cell)

        # 3) menambahkan kalimat baru ke basis pengetahuan AI
        #    berdasarkan nilai sel dan hitungan
        cells = set()

        # Iterasi pada semua sel dalam satu baris dan kolom
        for i in range(cell[0] - 1, cell[0] + 2):
            for j in range(cell[1] - 1, cell[1] + 2):

                # Abaikan sel itu sendiri
                if (i, j) == cell:
                    continue

                # Tambahkan ke koleksi sel jika sel belum dijelajahi
                # dan bukan ranjau yang sudah diketahui
                if 0 <= i < self.height and 0 <= j < self.width:
                    if (i, j) not in self.moves_made and (i, j) not in self.mines:
                        cells.add((i, j))
                    # ketika mengecualikan sel ranjau yang diketahui, kurangi hitungan sebesar 1
                    elif (i, j) in self.mines:
                        count -= 1
        self.knowledge.append(Sentence(cells, count))

        # 4) menandai sel tambahan sebagai aman atau ranjau
        #    jika dapat disimpulkan berdasarkan basis pengetahuan AI
        for sentence in self.knowledge:
            safes = sentence.known_safes()
            if safes:
                for cell in safes.copy():
                    self.mark_safe(cell)
            mines = sentence.known_mines()
            if mines:
                for cell in mines.copy():
                    self.mark_mine(cell)

        # 5) menambahkan kalimat baru ke basis pengetahuan AI
        #    jika dapat disimpulkan dari pengetahuan yang ada
        for sentence1 in self.knowledge:
            for sentence2 in self.knowledge:
                if sentence1 is sentence2:
                    continue
                if sentence1 == sentence2:
                    self.knowledge.remove(sentence2)
                elif sentence1.cells.issubset(sentence2.cells):
                    new_knowledge = Sentence(
                        sentence2.cells - sentence1.cells,
                        sentence2.count - sentence1.count)
                    if new_knowledge not in self.knowledge:
                        self.knowledge.append(new_knowledge)

        """
        Mengembalikan sel aman untuk dipilih pada papan Minesweeper.
        Langkah tersebut harus diketahui aman, dan belum pernah dilakukan.

        Fungsi ini dapat menggunakan pengetahuan dalam self.mines, self.safes
        dan self.moves_made, tetapi tidak boleh mengubah nilai-nilai tersebut.
        """
        
    def make_safe_move(self):
        available_steps = self.safes - self.moves_made
        if available_steps:
            # Use Greedy Best First Search to find the best move
            best_move = None
            best_heuristic = float('inf')
            for move in available_steps:
                heuristic = self.greedy_best_first_search_heuristic(move)
                if heuristic < best_heuristic:
                    best_move = move
                    best_heuristic = heuristic
            return best_move
        return None
    
    def greedy_best_first_search_heuristic(self, move):
        # Hitung nilai heuristik untuk langkah tersebut
        # Menggunakan algoritma Greedy Best First Search
        # Fungsi heuristik: h(n) = estimasi jarak ke tujuan
        # Dalam kasus ini, tujuannya adalah untuk mengungkap semua sel yang aman
        # Perkiraan jarak adalah jumlah sel yang perlu diungkap
        # untuk mencapai tujuan dari pergerakan saat ini
        distance = 0
        for i in range(self.height):
            for j in range(self.width):
                if (i, j) not in self.moves_made and (i, j) not in self.mines:
                    distance += 1
        return distance

    def make_random_move(self):
        """
        Mengembalikan langkah untuk dilakukan pada papan Minesweeper.
        Harus memilih secara acak di antara sel yang:
            1) belum pernah dipilih, dan
            2) tidak diketahui sebagai ranjau
        """
        # jika tidak ada langkah yang bisa dilakukan
        if len(self.mines) + len(self.moves_made) == self.height * self.width:
            return None

        # loop hingga langkah yang sesuai ditemukan
        while True:
            i = random.randrange(self.height)
            j = random.randrange(self.width)
            if (i, j) not in self.moves_made and (i, j) not in self.mines:
                return (i, j)

# Antarmuka Pygame
HEIGHT = 10
WIDTH = 10
MINES = 8

# Warna
BLACK = (0, 0, 0)
GRAY = (180, 180, 180)
WHITE = (255, 255, 255)

NUM_COLOR = [(0, 0, 255), (0, 128, 0), (255, 0, 0), (0, 0, 128),
             (128, 0, 0), (0, 128, 128), (0, 0, 0), (128, 128, 128)]

# Buat Permainan
pygame.init()
size = width, height = 600, 400
screen = pygame.display.set_mode(size)

# Fonts
OPEN_SANS = "assets/fonts/OpenSans-Regular.ttf"
smallFont = pygame.font.Font(OPEN_SANS, 20)
mediumFont = pygame.font.Font(OPEN_SANS, 28)
largeFont = pygame.font.Font(OPEN_SANS, 40)

# Menghitung ukuran papan
BOARD_PADDING = 20
board_width = ((2 / 3) * width) - (BOARD_PADDING * 2)
board_height = height - (BOARD_PADDING * 2)
cell_size = int(min(board_width / WIDTH, board_height / HEIGHT))
board_origin = (BOARD_PADDING, BOARD_PADDING)

# Tambahkan gambar
flag = pygame.image.load("assets/images/flag.png")
flag = pygame.transform.scale(flag, (cell_size, cell_size))
mine = pygame.image.load("assets/images/mine.png")
mine = pygame.transform.scale(mine, (cell_size, cell_size))

# Membuat game dan agen AI
game = Minesweeper(height=HEIGHT, width=WIDTH, mines=MINES)
ai = MinesweeperAI(height=HEIGHT, width=WIDTH)

# Melacak sel yang terungkap, sel yang ditandai, dan jika ada ranjau yang terkena
revealed = set()
flags = set()
lost = False

# Tampilkan instruksi pada awalnya
instructions = True

while True:
# Periksa apakah permainan berhenti
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()

    screen.fill(BLACK)
 

    # Papan gambar
    cells = []
    for i in range(HEIGHT):
        row = []
        for j in range(WIDTH):

            # Menggambar persegi panjang untuk sel
            rect = pygame.Rect(
                board_origin[0] + j * cell_size,
                board_origin[1] + i * cell_size,
                cell_size, cell_size
            )
            if (i, j) in revealed:
                pygame.draw.rect(screen, WHITE, rect)
            else:
                pygame.draw.rect(screen, GRAY, rect)
            pygame.draw.rect(screen, WHITE, rect, 3)

            # Tambahkan ranjau, bendera, atau nomor jika diperlukan
            if game.is_mine((i, j)) and lost:
                screen.blit(mine, rect)
            elif (i, j) in flags:
                screen.blit(flag, rect)
            elif (i, j) in revealed:
                nearby = game.nearby_mines((i, j))
                if nearby:
                    neighbors = smallFont.render(
                        str(nearby),
                        True, NUM_COLOR[nearby - 1]
                    )
                    neighborsTextRect = neighbors.get_rect()
                    neighborsTextRect.center = rect.center
                    screen.blit(neighbors, neighborsTextRect)

            row.append(rect)
        cells.append(row)

    # Tombol Pindah AI
    aiButton = pygame.Rect(
        (2 / 3) * width + BOARD_PADDING, (1 / 3) * height - 50,
        (width / 3) - BOARD_PADDING * 2, 50
    )
    buttonText = mediumFont.render("AI Move", True, BLACK)
    buttonRect = buttonText.get_rect()
    buttonRect.center = aiButton.center
    pygame.draw.rect(screen, WHITE, aiButton)
    screen.blit(buttonText, buttonRect)

    # Tombol reset
    resetButton = pygame.Rect(
        (2 / 3) * width + BOARD_PADDING, (1 / 3) * height + 20,
        (width / 3) - BOARD_PADDING * 2, 50
    )
    buttonText = mediumFont.render("Reset", True, BLACK)
    buttonRect = buttonText.get_rect()
    buttonRect.center = resetButton.center
    pygame.draw.rect(screen, WHITE, resetButton)
    screen.blit(buttonText, buttonRect)

    # Menampilkan teks
    text = "You Lose" if lost else "You Win" if game.mines == flags else ""
    text = mediumFont.render(text, True, WHITE)
    textRect = text.get_rect()
    textRect.center = ((5 / 6) * width, (2 / 3) * height)
    screen.blit(text, textRect)

    move = None

    left, _, right = pygame.mouse.get_pressed()

    # Periksa klik kanan untuk beralih penandaan
    if right == 1 and not lost:
        mouse = pygame.mouse.get_pos()
        for i in range(HEIGHT):
            for j in range(WIDTH):
                if cells[i][j].collidepoint(mouse) and (i, j) not in revealed:
                    if (i, j) in flags:
                        flags.remove((i, j))
                    else:
                        flags.add((i, j))
                    time.sleep(0.2)

    elif left == 1:
        mouse = pygame.mouse.get_pos()

        # Jika tombol AI diklik, lakukan gerakan AI
        if aiButton.collidepoint(mouse) and not lost:
            move = ai.make_safe_move()
            if move is None:
                move = ai.make_random_move()
                if move is None:
                    flags = ai.mines.copy()
                    print("No moves left to make.")
                else:
                    print("No known safe moves, AI making random move.")
            else:
                print("AI making safe move.")
            time.sleep(0.2)

       # Atur ulang status permainan
        elif resetButton.collidepoint(mouse):
            game = Minesweeper(height=HEIGHT, width=WIDTH, mines=MINES)
            ai = MinesweeperAI(height=HEIGHT, width=WIDTH)
            revealed = set()
            flags = set()
            lost = False
            continue

        # Gerakan buatan pengguna
        elif not lost:
            for i in range(HEIGHT):
                for j in range(WIDTH):
                    if (cells[i][j].collidepoint(mouse)
                            and (i, j) not in flags
                            and (i, j) not in revealed):
                        move = (i, j)

    # Bergerak dan perbarui pengetahuan AI
    def make_move(move):
        if game.is_mine(move):
            return True
        else:
            nearby = game.nearby_mines(move)
            revealed.add(move)
            ai.add_knowledge(move, nearby)
            if not nearby:
                # Ulangi semua sel dalam satu baris dan kolom
                for i in range(move[0] - 1, move[0] + 2):
                    for j in range(move[1] - 1, move[1] + 2):

                        # Abaikan sel itu sendiri
                        if (i, j) == move:
                            continue

                        # Tambahkan ke koleksi sel jika sel belum dieksplorasi
                        # dan belum menjadi milikku sudah tidak ada
                        if 0 <= i < HEIGHT and 0 <= j < WIDTH and (i, j) not in revealed:
                            make_move((i, j))
    if move:
        if make_move(move):
            lost = True

    pygame.display.flip()
   




   

    

   