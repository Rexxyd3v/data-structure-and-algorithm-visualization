# BUBBLE SORT VISUALIZATION
import pygame
import sys

pygame.init()
win_w, win_h = 950, 600
win = pygame.display.set_mode((win_w, win_h))
pygame.display.set_caption("Bubble Sort")

bg_color = (20, 20, 25)
box_color = (40, 40, 45)
box_border = (60, 60, 70)
text_color = (240, 240, 245)
sub_color = (160, 160, 170)
accent_blue = (52, 152, 219)
accent_gold = (241, 196, 15)
accent_green = (46, 204, 113)
btn_normal = (50, 50, 60)
btn_hover = (70, 70, 85)
btn_disabled = (40, 40, 45)
btn_disabled_text = (80, 80, 90)

font = pygame.font.SysFont("Inter, Arial", 19)
big_font = pygame.font.SysFont("Inter, Arial", 28, bold=True)
small_font = pygame.font.SysFont("Inter, Arial", 16)

nums = []
pos = []
txt = ""
typing = True
done = False
auto = False
ascending = True
msg = ""
count = 0
i = j = 0
state = "none"
box_w = 60
gap = 15
y_pos = 300

def draw_button(rect, text, is_hovered, color=None, text_col=None, border=True):
    c = color if color else (btn_hover if is_hovered else btn_normal)
    t_c = text_col if text_col else text_color
    pygame.draw.rect(win, c, rect, border_radius=8)
    if border:
        pygame.draw.rect(win, box_border, rect, 1, border_radius=8)
    s = font.render(text, True, t_c)
    r = s.get_rect(center=rect.center)
    win.blit(s, r)

def draw():
    win.fill(bg_color)
    mx, my = pygame.mouse.get_pos()
    
    t = big_font.render("BUBBLE SORT VISUALIZATION", True, text_color)
    win.blit(t, (30, 40))
    
    if typing:
        m = font.render("Type a number and press [ENTER] to add", True, sub_color)
        win.blit(m, (30, 90))
    else:
        info_str = f"Comparisons: {count} | Mode: {'Ascending' if ascending else 'Descending'}"
        info = font.render(info_str, True, text_color)
        win.blit(info, (35, 110))

    items = nums + ([txt] if typing else [])
    n = len(items)
    if n > 0:
        total_w = n * (box_w + gap) - gap
        start_x = (win_w - total_w) // 2
        for idx, val in enumerate(items):
            c = box_color
            bc = box_border
            
            if typing and idx == n - 1:
                bc = accent_blue
            elif not typing:
                if state == "compare" and (idx == j or idx == j + 1):
                    c = (60, 60, 20)
                    bc = accent_gold
                if state == "swap" and (idx == j or idx == j + 1):
                    c = (20, 60, 30)
                    bc = accent_green
            
            x = pos[idx] if (not typing and idx < len(pos)) else start_x + idx * (box_w + gap)
            rect = pygame.Rect(x, y_pos, box_w, box_w)
            
            shadow = rect.copy()
            shadow.y += 4
            pygame.draw.rect(win, (10, 10, 15), shadow, border_radius=10)
            
            pygame.draw.rect(win, c, rect, border_radius=10)
            pygame.draw.rect(win, bc, rect, 2, border_radius=10)
            
            s = font.render(str(val), True, text_color)
            r = s.get_rect(center=rect.center)
            win.blit(s, r)
        
        if msg:
            m_surf = font.render(msg, True, accent_gold if "swapping" in msg.lower() else sub_color)
            m_rect = m_surf.get_rect(center=(win_w // 2, y_pos + box_w + 60))
            win.blit(m_surf, m_rect)
        

    if not typing:
        draw_button(pygame.Rect(50, 500, 100, 45), "STEP", 50 <= mx <= 150 and 500 <= my <= 545)
        draw_button(pygame.Rect(170, 500, 140, 45), "AUTO PLAY", 170 <= mx <= 310 and 500 <= my <= 545, accent_blue if auto else None, (255,255,255) if auto else None)
        draw_button(pygame.Rect(330, 500, 110, 45), "RESET", 330 <= mx <= 440 and 500 <= my <= 545)
    else:
        can_start = len(nums) + (1 if txt else 0) >= 2
        sort_btn_color = accent_blue if can_start else btn_disabled
        sort_txt_color = (255, 255, 255) if can_start else btn_disabled_text
        draw_button(pygame.Rect(50, 500, 160, 45), "START SORT", 50 <= mx <= 210 and 500 <= my <= 545 and can_start, sort_btn_color, sort_txt_color, border=not can_start)
        
        draw_button(pygame.Rect(230, 500, 130, 45), "ASCENDING", 230 <= mx <= 360 and 500 <= my <= 545, accent_gold if ascending else None, (255,255,255) if ascending else None)
        draw_button(pygame.Rect(380, 500, 130, 45), "DESCENDING", 380 <= mx <= 510 and 500 <= my <= 545, accent_gold if not ascending else None, (255,255,255) if not ascending else None)

def move_boxes(idx1, idx2):
    step = 5
    goal1 = pos[idx2]
    goal2 = pos[idx1]
    while abs(pos[idx1] - goal1) > step:
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT: pygame.quit(); sys.exit()
        if pos[idx1] < goal1: pos[idx1] += step
        else: pos[idx1] -= step
        if pos[idx2] > goal2: pos[idx2] -= step
        else: pos[idx2] += step
        draw()
        pygame.display.update()
        pygame.time.Clock().tick(60)
    
    n = len(nums)
    total_w = n * (box_w + gap) - gap
    start_x = (win_w - total_w) // 2
    for k in range(n):
        pos[k] = start_x + (k * (box_w + gap))

def start_sort():
    global typing, nums, txt, pos, i, j, count, done, state, msg
    if txt:
        nums.append(int(txt))
        txt = ""
    if len(nums) < 2: return
    typing = False
    n = len(nums)
    total_w = n * (box_w + gap) - gap
    sx = (win_w - total_w) // 2
    pos = [sx + k * (box_w + gap) for k in range(n)]
    i = j = count = 0
    done = False
    state = "compare"
    msg = ""

while True:
    draw()
    pygame.display.update()
    
    step_now = False
    for ev in pygame.event.get():
        if ev.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        
        if ev.type == pygame.KEYDOWN:
            if typing:
                if ev.key == pygame.K_RETURN and txt:
                    nums.append(int(txt))
                    txt = ""
                elif ev.key == pygame.K_BACKSPACE:
                    if txt: txt = txt[:-1]
                    elif nums: nums.pop()
                elif ev.key == pygame.K_SPACE:
                    start_sort()
                elif ev.unicode.isdigit():
                    txt += ev.unicode
            else:
                if ev.key == pygame.K_SPACE: step_now = True
        
        if ev.type == pygame.MOUSEBUTTONDOWN:
            mx, my = ev.pos
            if typing:
                if 50 <= mx <= 210 and 500 <= my <= 545:
                    if len(nums) + (1 if txt else 0) >= 2:
                        start_sort()
                if 230 <= mx <= 360 and 500 <= my <= 545:
                    ascending = True
                if 380 <= mx <= 510 and 500 <= my <= 545:
                    ascending = False
            elif not typing:
                if 50 <= mx <= 150 and 500 <= my <= 545: step_now = True
                if 170 <= mx <= 310 and 500 <= my <= 545: auto = not auto
                if 330 <= mx <= 440 and 500 <= my <= 545:
                    nums = []
                    txt = ""
                    typing = True
                    auto = False
                    done = False
                    msg = ""

    if (step_now or (auto and not done)) and not typing and not done:
        if state == "compare":
            count += 1
            v1, v2 = nums[j], nums[j + 1]
            should_swap = (v1 > v2) if ascending else (v1 < v2)
            
            symbol = ">" if ascending else "<"
            if should_swap:
                msg = f"{v1} {symbol} {v2}: Out of order, swapping!"
                state = "swap"
            else:
                msg = f"{v1} {'<=' if ascending else '>='} {v2}: In order, skipping."
                j += 1
                if j >= len(nums) - i - 1:
                    j = 0
                    i += 1
                    if i >= len(nums) - 1:
                        done = True
                        state = "none"
                        msg = "Sorting Finished!"
                else: state = "compare"
        
        elif state == "swap":
            move_boxes(j, j + 1)
            nums[j], nums[j + 1] = nums[j + 1], nums[j]
            j += 1
            if j >= len(nums) - i - 1:
                j = 0
                i += 1
                if i >= len(nums) - 1:
                    done = True
                    state = "none"
                    msg = "Sorting Finished!"
                else: state = "compare"
            else: state = "compare"
        
        if auto: pygame.time.delay(400)
