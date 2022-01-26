import pygame
from typing import List
import random



pygame.init()

# Creating colors
BLUE = (0, 0, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
DARK_RED = (139, 0, 0)
GRAY = (211, 211, 211)

WINDOW_WIDTH = 800
WINDOW_HEIGHT = 800
BOARD_WIDTH = 4
BOARD_HEIGHT = 4
TILE_WIDTH = 100
TILE_HEIGHT = 100
UNCOVER_SPEED = 10
LEFT_PANEL = 250
GAP_SIZE = 20
FPS = 30
SCORE_1 = 0
SCORE_2 = 0

BORDER_GAP_X = (WINDOW_WIDTH - LEFT_PANEL - (BOARD_WIDTH * TILE_WIDTH) - (BOARD_WIDTH - 1) * GAP_SIZE) / 2
BORDER_GAP_Y = (WINDOW_HEIGHT - (BOARD_HEIGHT * TILE_HEIGHT) - (BOARD_HEIGHT - 1) * GAP_SIZE) / 2
BG_COLOR = WHITE
TILE_FRONT_COL = BLACK
PANEL_COL = BLACK
img1, img2, img3, img4, img5, img6, img7, img8 = '1.jpg', '2.jpg', '3.jpg', '4.jpg', '5.jpg', '6.jpg', '7.jpg', '8.jpg'
img_lst = [img1, img2, img3, img4, img5, img6, img7, img8]
turn_player1 = True
turn_player2 = False

font = pygame.font.SysFont("Verdana", 25)
font_small = pygame.font.SysFont("Verdana", 20)


def main():
    global screen, fps_clock, SCORE_1, SCORE_2 , turn_player1, turn_player2

    fps_clock = pygame.time.Clock()

    text = "game"
    pygame.display.set_caption(text)

    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    screen.fill(BG_COLOR)

    background = pygame.Surface(screen.get_size())
    background.fill(BG_COLOR)
    pygame.draw.rect(screen, BLACK, pygame.Rect(0, WINDOW_HEIGHT - 20, WINDOW_WIDTH, 25))
    draw_control_panel()

    x_mouse_pos = 0
    y_mouse_pos = 0
    choice_one = None

    game_board, revealed_sects = new_game()

    mainloop = True
    playtime = 0

    while mainloop:
        draw_control_panel()
        milliseconds = fps_clock.tick(FPS)
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
        fps_text = font_small.render(text, True, WHITE)
        pygame.draw.rect(screen, BLACK, pygame.Rect(0, WINDOW_HEIGHT - 20, WINDOW_WIDTH, 25))
        screen.blit(fps_text, (10, WINDOW_HEIGHT - 20))

        tile_pos = get_tile_at_pos(x_mouse_pos, y_mouse_pos)
        if (tile_pos[0] is None and tile_pos[1] is None) and mouse_clicked:
            new_game_rect = pygame.Rect(30, WINDOW_HEIGHT - 200, LEFT_PANEL - 50, 65)
            if new_game_rect.collidepoint(x_mouse_pos, y_mouse_pos):
                print('touch new_game_rect')
                game_won(game_board)
                revealed_sects = initialize_exposed(False)
                draw_board(game_board, revealed_sects, TILE_WIDTH, BG_COLOR)
                pygame.time.wait(2000)

                game_board, revealed_sects = new_game()
                draw_board(game_board, revealed_sects)
                choice_one = None
                SCORE_1 = 0
                SCORE_2 = 0
        elif tile_pos[0] is not None and tile_pos[1] is not None:
            if not revealed_sects[tile_pos[0]][tile_pos[1]] and mouse_clicked:
                reveal_card_slide(game_board, [tile_pos])
                revealed_sects[tile_pos[0]][tile_pos[1]] = True
                if choice_one is None and choice_one != tile_pos:
                    choice_one = tile_pos
                    draw_board(game_board, revealed_sects)
                else:
                    first_tile = game_board[choice_one[0]][choice_one[1]]
                    second_tile = game_board[tile_pos[0]][tile_pos[1]]
                    print(f'first {first_tile} second {second_tile}')

                    if first_tile == second_tile:
                        if turn_player1:
                            SCORE_1 += 1
                            turn_player()
                        elif turn_player2:
                            SCORE_2 += 1
                            turn_player()

                    if first_tile != second_tile:
                        # Then images are not the same and therefore, cover them up
                        pygame.time.wait(800)
                        cover_card_slide(game_board, [choice_one, tile_pos])
                        revealed_sects[choice_one[0]][choice_one[1]] = False
                        revealed_sects[tile_pos[0]][tile_pos[1]] = False
                        turn_player()

                    elif game_complete(revealed_sects):
                        game_winner(SCORE_1, SCORE_2)
                        game_won(game_board)
                        revealed_sects = initialize_exposed(False)
                        draw_board(game_board, revealed_sects, TILE_WIDTH, BG_COLOR)
                        pygame.time.wait(1000)

                        game_board, revealed_sects = new_game()
                        playtime = 0
                        SCORE_1 = 0
                        SCORE_2 = 0

                    draw_board(game_board, revealed_sects)
                    choice_one = None


        pygame.display.flip()


def turn_player():
    global turn_player1, turn_player2
    if turn_player1:
        turn_player1 = False
        turn_player2 = True
    elif turn_player2:
        turn_player1 = True
        turn_player2 = False


def blit_text(surface, text, pos, font, color=pygame.Color('black')):
    words = [word.split(' ') for word in text.splitlines()]  # 2D array where each row is a list of words.
    space = font.size(' ')[0]  # The width of a space.
    max_width, max_height = surface.get_size()
    x, y = pos
    for line in words:
        for word in line:
            word_surface = font.render(word, 0, color)
            word_width, word_height = word_surface.get_size()
            if x + word_width >= max_width:
                x = pos[0]  # Reset the x.
                y += word_height  # Start on new row.
            surface.blit(word_surface, (x, y))
            x += word_width + space
        x = pos[0]  # Reset the x.
        y += word_height  # Start on new row.


def game_winner(score1, score2):
    score = score1
    player = 'Player 1'
    if score1 < score2:
        score = score2
        player = 'Player 2'
    elif score1 == score2:
        pygame.draw.rect(screen, GRAY, pygame.Rect(50, 170, 210, 460))
        text = "This game is equal"
        blit_text(screen, text, (55, 275), font)
        pygame.time.wait(3000)
        return True

    text = "{} Winner ({})".format(player, score)
    winner_text = font.render(text, True, BLACK)
    pygame.draw.rect(screen, GREEN, pygame.Rect(50, 170, 210, 460))
    screen.blit(winner_text, (55, 275))
    pygame.time.wait(3000)


def expose_start_game_board(board):
    game_tiles = initialize_exposed(False)
    tiles = []
    for x in range(BOARD_WIDTH):
        for y in range(BOARD_HEIGHT):
            tiles.append((x, y))
    random.shuffle(tiles)
    draw_board(board, game_tiles)
    pygame.time.wait(2000)
    box_groups = []
    for i in range(0, len(tiles), 4):
        sect = tiles[i: i + 4]
        box_groups.append(sect)

    for boxes in box_groups:
        reveal_card_slide(board, boxes)
        cover_card_slide(board, boxes)


def game_won(board):

    game_tiles = initialize_exposed(True)
    tiles = []
    for x in range(BOARD_WIDTH):
        for y in range(BOARD_HEIGHT):
            tiles.append((x, y))
    random.shuffle(tiles)

    draw_board(board, game_tiles, color=BG_COLOR)

    box_groups = []
    for i in range(0, len(tiles), 4):
        sect = tiles[i: i + 4]
        box_groups.append(sect)

    for boxes in box_groups:
        cover_card_slide(board, boxes, BG_COLOR)


def board_reveal_animation(board):

    game_tiles = initialize_exposed(False)
    tiles = []
    for x in range(BOARD_WIDTH):
        for y in range(BOARD_HEIGHT):
            tiles.append((x, y))
    random.shuffle(tiles)

    draw_board(board, game_tiles, color=BG_COLOR)

    box_groups = []
    for i in range(0, len(tiles), 4):
        sect = tiles[i: i + 4]
        box_groups.append(sect)

    for boxes in box_groups:
        cover_card_slide(board, boxes, TILE_FRONT_COL, False)


def reveal_card_slide(board, cards):
    
    for width in range(TILE_WIDTH, (-UNCOVER_SPEED), -UNCOVER_SPEED):
        draw_board_covers(board, cards, width)


def cover_card_slide(board, cards, color=TILE_FRONT_COL, image=True):
    
    for width in range(0, TILE_WIDTH + 1, UNCOVER_SPEED):
        draw_board_covers(board, cards, width, color, image)


def create_random_board():
    """ Creates a random board of image tiles.
    """
    all_images = img_lst * 2
    random.shuffle(all_images)

    game_board: List[List[str]] = []  # Initializes an empty board
    for y in range(BOARD_HEIGHT):
        row = []
        for x in range(BOARD_WIDTH):
            row.append(all_images[0])
            del all_images[0]
        game_board.append(row)
    return game_board


def initialize_exposed(val):
    
    exposed = []
    for y in range(BOARD_HEIGHT):
        exposed.append([val] * BOARD_WIDTH)
    return exposed


def draw_board(board, exposed, width=TILE_WIDTH, color=TILE_FRONT_COL):
    
    for dummy_row in range(BOARD_HEIGHT):
        for dummy_col in range(BOARD_WIDTH):
            card = (dummy_row, dummy_col)
            coord_pos = top_coord(card)
            if not exposed[dummy_row][dummy_col]:
                pygame.draw.rect(screen, color, (coord_pos[0], coord_pos[1], width, TILE_HEIGHT))
            else:
                draw_board_icons(board, dummy_row, dummy_col, coord_pos)
    pygame.display.update()


def draw_board_icons(board, row, col, coord_pos):
    
    board_image = pygame.image.load(board[row][col]).convert()
    board_image = pygame.transform.scale(board_image, (TILE_WIDTH, TILE_HEIGHT))
    screen.blit(board_image, coord_pos)


def draw_board_covers(board, cards, width=TILE_WIDTH, color=TILE_FRONT_COL, image=True):
    
    for card in cards:
        coord_pos = top_coord(card)
        if image:
            draw_board_icons(board, card[0], card[1], coord_pos)
        if width > 0:
            pygame.draw.rect(screen, color, (coord_pos[0], coord_pos[1], width, TILE_HEIGHT))
    pygame.display.update()
    fps_clock.tick(FPS)


def top_coord(card):

    top_x = LEFT_PANEL + BORDER_GAP_X + card[0] * (TILE_WIDTH + GAP_SIZE)
    top_y = BORDER_GAP_Y + card[1] * (TILE_HEIGHT + GAP_SIZE)
    return top_x, top_y


def get_tile_at_pos(pos_x, pos_y):

    for x in range(BOARD_WIDTH):
        for y in range(BOARD_HEIGHT):
            top_x, top_y = top_coord((x, y))
            card_rect = pygame.Rect(top_x, top_y, TILE_WIDTH, TILE_HEIGHT)
            if card_rect.collidepoint(pos_x, pos_y):
                return x, y
    return None, None


def game_complete(revealed_sect):

    for item in revealed_sect:
        if False in item:
            return False
    return True


def draw_control_panel():
    text1 = "Player 1: score {}  ".format(SCORE_1)
    text2 = "Player 2: score {}  ".format(SCORE_2)
    text_turn = "Turn {}  ".format('PLAYER 1' if turn_player1 else 'PLAYER 2')
    score_1_text = font_small.render(text1, True, BLACK)
    score_2_text = font_small.render(text2, True, BLACK)
    turn_text = font_small.render(text_turn, True, BLACK)
    pygame.draw.rect(screen, DARK_RED, pygame.Rect(50, 170, 210, 460))
    screen.blit(score_1_text, (55, 175))
    screen.blit(score_2_text, (55, 250))
    screen.blit(turn_text, (55, 350))


def new_game():
    board = create_random_board()
    revealed_sects = initialize_exposed(False)
    draw_control_panel()
    pygame.time.wait(1000)
    board_reveal_animation(board)
    expose_start_game_board(board)

    return board, revealed_sects


main()
