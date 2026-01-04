import pygame
import sys

pygame.init()

WIDTH, HEIGHT = 950, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Bubble Sort Visualization")

BG_COLOR = (250, 250, 250)
BOX_COLOR = (255, 255, 255)
TEXT_COLOR = (50, 50, 50)
HL_COLOR = (255, 235, 59)
SWAP_COLOR = (76, 175, 80)
BTN_COLOR = (235, 235, 235)
INPUT_HL = (33, 150, 243)

FONT = pygame.font.SysFont("Arial", 19)
L_FONT = pygame.font.SysFont("Arial", 26, bold=True)

numbers = []
positions = []
typing_text = ""
auto_play = False
sorting_done = False
comparisons = 0
BOX_W = 60
GAP = 15
Y = 300
gen = None
state = None
cur_i = cur_j = -1
is_typing = True

def prepare_sort():
    global positions, gen, sorting_done, comparisons, state, cur_i, cur_j, is_typing
    if len(numbers) < 2: return
    is_typing = False
    n = len(numbers)
    start_x = (WIDTH - (n * (BOX_W + GAP) - GAP)) // 2
    positions = [start_x + i * (BOX_W + GAP) for i in range(n)]
    comparisons = 0
    sorting_done = False
    state = None
    cur_i = cur_j = -1
    gen = bubble_sort_gen()

def bubble_sort_gen():
    global comparisons, sorting_done
    n = len(numbers)
    for i in range(n):
        for j in range(n - i - 1):
            yield ("compare", j, j + 1)
            comparisons += 1
            if numbers[j] > numbers[j + 1]:
                yield ("swap", j, j + 1)
                numbers[j], numbers[j + 1] = numbers[j + 1], numbers[j]
    sorting_done = True
    yield ("done", -1, -1)

def draw_screen(active=None, swapping=None):
    screen.fill(BG_COLOR)
    
    title = L_FONT.render("BUBBLE SORT VISUALIZATION", True, TEXT_COLOR)
    screen.blit(title, (20, 30))
    
    if is_typing:
        msg = FONT.render("Type a number and press [ENTER] for next box", True, TEXT_COLOR)
        screen.blit(msg, (30, 70))
    else:
        info = FONT.render(f"Comparisons: {comparisons}", True, TEXT_COLOR)
        screen.blit(info, (30, 90))
        if sorting_done:
            done = FONT.render("Sorting Complete!", True, SWAP_COLOR)
            screen.blit(done, (50, 130))

    display_nums = numbers + ([typing_text] if is_typing else [])
    count = len(display_nums)
    if count > 0:
        row_w = count * (BOX_W + GAP) - GAP
        row_x = (WIDTH - row_w) // 2
        for i, val in enumerate(display_nums):
            color = BOX_COLOR
            b_color = (200, 200, 200)
            
            if is_typing and i == len(display_nums) - 1:
                b_color = INPUT_HL
            elif not is_typing:
                if active and i in active: color = HL_COLOR
                if swapping and i in swapping: color = SWAP_COLOR
            
            x_pos = row_x + i * (BOX_W + GAP) if is_typing else positions[i]
            rect = pygame.Rect(x_pos, Y, BOX_W, BOX_W)
            pygame.draw.rect(screen, color, rect, border_radius=5)
            pygame.draw.rect(screen, b_color, rect, 2, border_radius=5)
            
            txt_surf = FONT.render(str(val), True, TEXT_COLOR)
            txt_rect = txt_surf.get_rect(center=rect.center)
            screen.blit(txt_surf, txt_rect)

    if not is_typing:
        pygame.draw.rect(screen, BTN_COLOR, (50, 500, 100, 40), border_radius=5)
        screen.blit(FONT.render("STEP", True, TEXT_COLOR), (75, 510))
        pygame.draw.rect(screen, BTN_COLOR, (170, 500, 120, 40), border_radius=5)
        screen.blit(FONT.render("AUTO PLAY", True, TEXT_COLOR), (185, 510))
        pygame.draw.rect(screen, BTN_COLOR, (310, 500, 100, 40), border_radius=5)
        screen.blit(FONT.render("RESET", True, TEXT_COLOR), (330, 510))
    elif len(numbers) >= 2:
        pygame.draw.rect(screen, INPUT_HL, (50, 500, 150, 40), border_radius=5)
        screen.blit(FONT.render("START SORT", True, (255,255,255)), (65, 510))

def animate_swap(i, j):
    speed = 5
    target_i = positions[j]
    target_j = positions[i]
    while abs(positions[i] - target_i) > speed:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
        if positions[i] < target_i: positions[i] += speed
        else: positions[i] -= speed
        if positions[j] > target_j: positions[j] -= speed
        else: positions[j] += speed
        draw_screen(swapping=(i, j))
        pygame.display.update()
        pygame.time.Clock().tick(60)
    
    n = len(numbers)
    start_x = (WIDTH - (n * (BOX_W + GAP) - GAP)) // 2
    for k in range(n):
        positions[k] = start_x + (k * (BOX_W + GAP))

while True:
    draw_screen(active=(cur_i, cur_j) if state == "compare" else None)
    pygame.display.update()
    
    do_step = False
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.KEYDOWN:
            if is_typing:
                if event.key == pygame.K_RETURN and typing_text:
                    numbers.append(int(typing_text))
                    typing_text = ""
                elif event.key == pygame.K_BACKSPACE:
                    if typing_text: typing_text = typing_text[:-1]
                    elif numbers: numbers.pop()
                elif event.key == pygame.K_SPACE:
                    prepare_sort()
                elif event.unicode.isdigit():
                    typing_text += event.unicode
            else:
                if event.key == pygame.K_SPACE: do_step = True
        if event.type == pygame.MOUSEBUTTONDOWN:
            x, y = event.pos
            if is_typing and 50 <= x <= 200 and 500 <= y <= 540:
                prepare_sort()
            elif not is_typing:
                if 50 <= x <= 150 and 500 <= y <= 540: do_step = True
                if 170 <= x <= 290 and 500 <= y <= 540: auto_play = not auto_play
                if 310 <= x <= 410 and 500 <= y <= 540:
                    numbers = []
                    typing_text = ""
                    is_typing = True
                    auto_play = False

    if (do_step or (auto_play and not sorting_done)) and gen and not sorting_done:
        try:
            state, cur_i, cur_j = next(gen)
            if state == "swap": animate_swap(cur_i, cur_j)
            if auto_play: pygame.time.delay(400)
        except StopIteration: pass
