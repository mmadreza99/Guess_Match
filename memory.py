import pygame
from typing import List
import random
from network import Network


# Creating colors
BLUE = (0, 0, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
DARK_RED = (139, 0, 0)
GRAY = (211, 211, 211)

TILE_WIDTH = 100
TILE_FRONT_COL = BLACK

img1, img2, img3, img4, img5, img6, img7, img8 = '1.jpg', '2.jpg', '3.jpg', '4.jpg', '5.jpg', '6.jpg', '7.jpg', '8.jpg'
img_lst = [img1, img2, img3, img4, img5, img6, img7, img8]


class Player:
    width = height = 50

    def __init__(self, color=(255, 0, 0)):
        self.score = 0
        self.turn = True
        self.color = color


class Game:
    pygame.init()

    def __init__(self):
        self.net = Network()
        self.WINDOW_WIDTH = 800
        self.WINDOW_HEIGHT = 600
        self.player = Player()
        self.player2 = Player()
        self.BOARD_WIDTH = 4
        self.BOARD_HEIGHT = 4
        self.TILE_WIDTH = 100
        self.TILE_HEIGHT = 100
        self.UNCOVER_SPEED = 10
        self.LEFT_PANEL = 250
        self.GAP_SIZE = 20
        self.FPS = 30
        self.BORDER_GAP_X = (self.WINDOW_WIDTH - self.LEFT_PANEL - (self.BOARD_WIDTH * self.TILE_WIDTH) - (self.BOARD_WIDTH - 1) * self.GAP_SIZE) / 2
        self.BORDER_GAP_Y = (self.WINDOW_HEIGHT - (self.BOARD_HEIGHT * self.TILE_HEIGHT) - (self.BOARD_HEIGHT - 1) * self.GAP_SIZE) / 2
        self.BG_COLOR = WHITE
        self.TILE_FRONT_COL = BLACK
        self.PANEL_COL = BLACK
        self.font = pygame.font.SysFont("Verdana", 25)
        self.font_small = pygame.font.SysFont("Verdana", 20)
        self.screen = pygame.display.set_mode((self.WINDOW_WIDTH, self.WINDOW_HEIGHT))
        pygame.display.set_caption('Guess & Match')
        pygame.font.init()
        self.screen.fill(self.BG_COLOR)
        background = pygame.Surface(self.screen.get_size())
        background.fill(self.BG_COLOR)
        pygame.draw.rect(self.screen, BLACK, pygame.Rect(0, self.WINDOW_HEIGHT - 20, self.WINDOW_WIDTH, 25))
        self.draw_control_panel()

    def run(self):
        fps_clock = pygame.time.Clock()
        x_mouse_pos = 0
        y_mouse_pos = 0
        choice_one = None

        game_board, revealed_sects = self.new_game()

        mainloop = True
        playtime = 0

        while mainloop:
            self.draw_control_panel()
            milliseconds = fps_clock.tick(self.FPS)
            playtime += milliseconds / 1000.0
            mouse_clicked = False

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    mainloop = False
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    mainloop = False
                elif event.type == pygame.MOUSEMOTION:
                    x_mouse_pos, y_mouse_pos = event.pos
                elif event.type == pygame.MOUSEBUTTONUP:
                    x_mouse_pos, y_mouse_pos = event.pos
                    mouse_clicked = True
                    print("Mouse clicked at:", x_mouse_pos, y_mouse_pos)

            text = "Game FPS: {0:.2f}   Playtime: {1:.2f}".format(fps_clock.get_fps(), playtime)
            fps_text = self.font_small.render(text, True, WHITE)
            pygame.draw.rect(self.screen, BLACK, pygame.Rect(0, self.WINDOW_HEIGHT - 20, self.WINDOW_WIDTH, 25))
            self.screen.blit(fps_text, (10, self.WINDOW_HEIGHT - 20))

            # self.player2.score, self.player2.turn = self.parse_data(self.send_data())
            tile_pos = self.get_tile_at_pos(x_mouse_pos, y_mouse_pos)
            if (tile_pos[0] is None and tile_pos[1] is None) and mouse_clicked:
                new_game_rect = pygame.Rect(30, self.WINDOW_HEIGHT - 200, self.LEFT_PANEL - 50, 65)
                if new_game_rect.collidepoint(x_mouse_pos, y_mouse_pos):
                    print('touch new_game_rect')
                    self.game_won(game_board)
                    revealed_sects = self.initialize_exposed(False)
                    self.draw_board(game_board, revealed_sects, self.TILE_WIDTH, self.BG_COLOR)
                    pygame.time.wait(2000)

                    game_board, revealed_sects = self.new_game()
                    self.draw_board(game_board, revealed_sects)
                    choice_one = None
                    self.player.score = 0
                    self.player2.score = 0

            elif tile_pos[0] is not None and tile_pos[1] is not None:
                if not revealed_sects[tile_pos[0]][tile_pos[1]] and mouse_clicked:
                    self.reveal_card_slide(game_board, [tile_pos])
                    revealed_sects[tile_pos[0]][tile_pos[1]] = True
                    if choice_one is None and choice_one != tile_pos:
                        choice_one = tile_pos
                        self.draw_board(game_board, revealed_sects)
                    else:
                        first_tile = game_board[choice_one[0]][choice_one[1]]
                        second_tile = game_board[tile_pos[0]][tile_pos[1]]
                        print(f'first {first_tile} second {second_tile}')

                        if first_tile == second_tile:
                            if self.player.turn:
                                self.player.score += 1
                                self.turn_player()
                            elif self.player2.turn:
                                self.player2.score += 1
                                self.turn_player()

                        if first_tile != second_tile:
                            # Then images are not the same and therefore, cover them up
                            pygame.time.wait(800)
                            self.cover_card_slide(game_board, [choice_one, tile_pos])
                            revealed_sects[choice_one[0]][choice_one[1]] = False
                            revealed_sects[tile_pos[0]][tile_pos[1]] = False
                            self.turn_player()

                        elif self.game_complete(revealed_sects):
                            self.game_winner(self.player.score, self.player2.score)
                            self.game_won(game_board)
                            revealed_sects = self.initialize_exposed(False)
                            self.draw_board(game_board, revealed_sects, self.TILE_WIDTH, self.BG_COLOR)
                            pygame.time.wait(1000)

                            game_board, revealed_sects = self.new_game()
                            playtime = 0
                            self.player.score = 0
                            self.player2.score = 0

                        self.draw_board(game_board, revealed_sects)
                        choice_one = None

            pygame.display.flip()

    def send_data(self):
        """
        Send position to server
        :return: None
        """
        data = str(self.net.id) + ":" + str(self.player.score) + "," + str(self.player.turn)
        reply = self.net.send(data)
        return reply

    @staticmethod
    def parse_data(data):
        try:
            d = data.split(":")[1].split(",")
            return int(d[0]), d[1]
        except:
            return 0, False

    @staticmethod
    def update():
        pygame.display.update()

    def get_screen(self):
        return self.screen

    def turn_player(self):
        if self.player.turn:
            self.player.turn = False
            self.player2.turn = True
        elif self.player2.turn:
            self.player.turn = True
            self.player2.turn = False

    def game_winner(self, score1, score2):
        score = score1
        player = 'Player 1'
        if score1 < score2:
            score = score2
            player = 'Player 2'
        elif score1 == score2:
            pygame.draw.rect(self.screen, GRAY, pygame.Rect(50, 70, 210, 460))
            text = "This game is equal"
            equal_text = self.font.render(text, True, BLACK)
            self.screen.blit(equal_text, (55, 275))
            pygame.time.wait(3000)
            return True

        text = "{} Winner ({})".format(player, score)
        winner_text = self.font.render(text, True, BLACK)
        pygame.draw.rect(self.screen, GREEN, pygame.Rect(50, 70, 210, 460))
        self.screen.blit(winner_text, (55, 275))
        pygame.time.wait(3000)

    def expose_start_game_board(self, board):
        game_tiles = self.initialize_exposed(False)
        tiles = []
        for x in range(self.BOARD_WIDTH):
            for y in range(self.BOARD_HEIGHT):
                tiles.append((x, y))
        random.shuffle(tiles)
        self.draw_board(board, game_tiles)
        pygame.time.wait(2000)
        box_groups = []
        for i in range(0, len(tiles), 4):
            sect = tiles[i: i + 4]
            box_groups.append(sect)

        for boxes in box_groups:
            self.reveal_card_slide(board, boxes)
            self.cover_card_slide(board, boxes)

    def game_won(self, board):

        game_tiles = self.initialize_exposed(True)
        tiles = []
        for x in range(self.BOARD_WIDTH):
            for y in range(self.BOARD_HEIGHT):
                tiles.append((x, y))
        random.shuffle(tiles)

        self.draw_board(board, game_tiles, color=self.BG_COLOR)

        box_groups = []
        for i in range(0, len(tiles), 4):
            sect = tiles[i: i + 4]
            box_groups.append(sect)

        for boxes in box_groups:
            self.cover_card_slide(board, boxes, self.BG_COLOR)

    def board_reveal_animation(self, board):

        game_tiles = self.initialize_exposed(False)
        tiles = []
        for x in range(self.BOARD_WIDTH):
            for y in range(self.BOARD_HEIGHT):
                tiles.append((x, y))
        random.shuffle(tiles)

        self.draw_board(board, game_tiles, color=self.BG_COLOR)

        box_groups = []
        for i in range(0, len(tiles), 4):
            sect = tiles[i: i + 4]
            box_groups.append(sect)

        for boxes in box_groups:
            self.cover_card_slide(board, boxes, self.TILE_FRONT_COL, False)

    def reveal_card_slide(self, board, cards):

        for width in range(self.TILE_WIDTH, (-self.UNCOVER_SPEED), -self.UNCOVER_SPEED):
            self.draw_board_covers(board, cards, width)

    def cover_card_slide(self, board, cards, color=BLACK, image=True):

        for width in range(0, self.TILE_WIDTH + 1, self.UNCOVER_SPEED):
            self.draw_board_covers(board, cards, width, color, image)

    def create_random_board(self):
        """ Creates a random board of image tiles.
        """
        all_images = img_lst * 2
        random.shuffle(all_images)

        game_board: List[List[str]] = []  # Initializes an empty board
        for y in range(self.BOARD_HEIGHT):
            row = []
            for x in range(self.BOARD_WIDTH):
                row.append(all_images[0])
                del all_images[0]
            game_board.append(row)
        return game_board

    def initialize_exposed(self, val):

        exposed = []
        for y in range(self.BOARD_HEIGHT):
            exposed.append([val] * self.BOARD_WIDTH)
        return exposed

    def draw_board(self, board, exposed, width=TILE_WIDTH, color=BLACK):

        for dummy_row in range(self.BOARD_HEIGHT):
            for dummy_col in range(self.BOARD_WIDTH):
                card = (dummy_row, dummy_col)
                coord_pos = self.top_coord(card)
                if not exposed[dummy_row][dummy_col]:
                    pygame.draw.rect(self.screen, color, (coord_pos[0], coord_pos[1], width, self.TILE_HEIGHT))
                else:
                    self.draw_board_icons(board, dummy_row, dummy_col, coord_pos)
        pygame.display.update()

    def draw_board_icons(self, board, row, col, coord_pos):

        board_image = pygame.image.load(board[row][col]).convert()
        board_image = pygame.transform.scale(board_image, (self.TILE_WIDTH, self.TILE_HEIGHT))
        self.screen.blit(board_image, coord_pos)

    def draw_board_covers(self, board, cards, width=TILE_WIDTH, color=TILE_FRONT_COL, image=True):

        for card in cards:
            coord_pos = self.top_coord(card)
            if image:
                self.draw_board_icons(board, card[0], card[1], coord_pos)
            if width > 0:
                pygame.draw.rect(self.screen, color, (coord_pos[0], coord_pos[1], width, self.TILE_HEIGHT))
        pygame.display.update()
        fps_clock = pygame.time.Clock()
        fps_clock.tick(self.FPS)

    def top_coord(self, card):

        top_x = self.LEFT_PANEL + self.BORDER_GAP_X + card[0] * (self.TILE_WIDTH + self.GAP_SIZE)
        top_y = self.BORDER_GAP_Y + card[1] * (self.TILE_HEIGHT + self.GAP_SIZE)
        return top_x, top_y

    def get_tile_at_pos(self, pos_x, pos_y):

        for x in range(self.BOARD_WIDTH):
            for y in range(self.BOARD_HEIGHT):
                top_x, top_y = self.top_coord((x, y))
                card_rect = pygame.Rect(top_x, top_y, self.TILE_WIDTH, self.TILE_HEIGHT)
                if card_rect.collidepoint(pos_x, pos_y):
                    return x, y
        return None, None

    @staticmethod
    def game_complete(revealed_sect):

        for item in revealed_sect:
            if False in item:
                return False
        return True

    def draw_control_panel(self):
        text1 = "Player 1: score {}  ".format(self.player.score)
        text2 = "Player 2: score {}  ".format(self.player2.score)
        text_turn = "Turn {}  ".format('PLAYER 1' if self.player.turn else 'PLAYER 2')
        score_1_text = self.font_small.render(text1, True, BLACK)
        score_2_text = self.font_small.render(text2, True, BLACK)
        turn_text = self.font_small.render(text_turn, True, BLACK)
        pygame.draw.rect(self.screen, DARK_RED, pygame.Rect(50, 70, 210, 460))
        self.screen.blit(score_1_text, (55, 75))
        self.screen.blit(score_2_text, (55, 150))
        self.screen.blit(turn_text, (55, 250))

    def new_game(self):
        board = self.create_random_board()
        revealed_sects = self.initialize_exposed(False)
        self.draw_control_panel()
        pygame.time.wait(1000)
        self.board_reveal_animation(board)
        self.expose_start_game_board(board)
        return board, revealed_sects
