# QUICK SORT TREE VISUALIZATION
import pygame
import sys

pygame.init()

win_w, win_h = 950, 600
win = pygame.display.set_mode((win_w, win_h))
pygame.display.set_caption("Quick Sort Tree")

bg_color = (20, 20, 25)
box_color = (40, 40, 45)
box_border = (60, 60, 70)
text_color = (240, 240, 245)
sub_color = (160, 160, 170)

accent_blue = (52, 152, 219)
accent_gold = (241, 196, 15)
accent_green = (46, 204, 113)
accent_red = (231, 76, 60)

btn_normal = (50, 50, 60)
btn_hover = (70, 70, 85)
btn_disabled = (40, 40, 45)
btn_disabled_text = (80, 80, 90)

font = pygame.font.SysFont("Inter, Arial", 19)
big_font = pygame.font.SysFont("Inter, Arial", 28, bold=True)

nums = []
txt = ""
typing = True
done = False
auto = False
ascending = True
msg = ""
count = 0

levels = {}
box_w = 30
gap = 4
level_h = 75
start_y = 150

tree_phase = ""

def draw_button(rect, text, is_hovered, color=None, text_col=None, border=True):
    c = color if color else (btn_hover if is_hovered else btn_normal)
    t_c = text_col if text_col else text_color
    pygame.draw.rect(win, c, rect, border_radius=8)
    if border:
        pygame.draw.rect(win, box_border, rect, 1, border_radius=8)
    s = font.render(text, True, t_c)
    r = s.get_rect(center=rect.center)
    win.blit(s, r)


def draw_node(node, level_idx, current_phase=""):
    vals = node["values"]
    x = node["x"]
    y = node["y"]
    active = node.get("active", False)
    comp = node.get("comparing", [])

    for i, val in enumerate(vals):
        rect = pygame.Rect(x + i * (box_w + gap), y, box_w, box_w)
        c = box_color
        bc = box_border

        if active:
            if current_phase == "partition":
                bc = accent_blue
            elif current_phase == "compare":
                bc = accent_gold
            elif current_phase in ["place", "pivot"]:
                bc = accent_green
            else:
                bc = accent_blue

        if i in comp:
            c = (60, 60, 20)
            bc = accent_gold

        pygame.draw.rect(win, (10, 10, 15), (rect.x, rect.y + 3, box_w, box_w), border_radius=5)
        pygame.draw.rect(win, c, rect, border_radius=5)
        pygame.draw.rect(win, bc, rect, 2, border_radius=5)

        if val is not None:
            txt_s = font.render(str(val), True, text_color)
            win.blit(txt_s, txt_s.get_rect(center=rect.center))


def draw():
    global tree_phase
    win.fill(bg_color)
    mx, my = pygame.mouse.get_pos()

    title = big_font.render("QUICK SORT TREE VISUALIZATION", True, text_color)
    win.blit(title, (30, 40))

    if typing:
        m = font.render("Type a number and press [ENTER] to add", True, sub_color)
        win.blit(m, (30, 90))

        items = nums + ([txt] if typing else [])
        n = len(items)
        if n > 0:
            bw = 60
            bgp = 15
            total_w = n * (bw + bgp) - bgp
            start_x = (win_w - total_w) // 2
            y_pos = 300
            for idx, val in enumerate(items):
                bc = accent_blue if idx == n - 1 else box_border
                rect = pygame.Rect(start_x + idx * (bw + bgp), y_pos, bw, bw)
                pygame.draw.rect(win, (10, 10, 15), (rect.x, rect.y + 4, bw, bw), border_radius=10)
                pygame.draw.rect(win, box_color, rect, border_radius=10)
                pygame.draw.rect(win, bc, rect, 2, border_radius=10)
                s = font.render(str(val), True, text_color)
                win.blit(s, s.get_rect(center=rect.center))

        can_start = len(nums) + (1 if txt else 0) >= 2
        draw_button(pygame.Rect(50, 500, 160, 45), "START SORT",
                     50 <= mx <= 210 and 500 <= my <= 545 and can_start,
                     accent_blue if can_start else btn_disabled,
                     (255, 255, 255) if can_start else btn_disabled_text,
                     border=not can_start)
        draw_button(pygame.Rect(230, 500, 130, 45), "ASCENDING",
                     230 <= mx <= 360 and 500 <= my <= 545,
                     accent_gold if ascending else None,
                     (255, 255, 255) if ascending else None)
        draw_button(pygame.Rect(380, 500, 130, 45), "DESCENDING",
                     380 <= mx <= 510 and 500 <= my <= 545,
                     accent_gold if not ascending else None,
                     (255, 255, 255) if not ascending else None)
    else:
        for l_idx in levels:
            for node in levels[l_idx]:
                if node.get("parent_pos") is not None:
                    px, py = node["parent_pos"]
                    vals_len = len(node["values"])
                    node_w = vals_len * box_w + (vals_len - 1) * gap
                    nx, ny = node["x"] + node_w // 2, node["y"]
                    pygame.draw.line(win, (60, 60, 70), (px, py + box_w), (nx, ny), 1)

        if msg:
            current_phase = ""
            lower_msg = msg.lower()
            tree_phase = current_phase
            if "partition" in lower_msg or "pivot selected" in lower_msg:
                current_phase = "partition"
            elif "comparing" in lower_msg or "compare" in lower_msg:
                current_phase = "compare"
            elif "placing" in lower_msg or "pivot" in lower_msg or "in correct position" in lower_msg:
                current_phase = "place"
            elif "pivot" in lower_msg:
                current_phase = "pivot"

            m_color = sub_color
            if current_phase == "partition":
                m_color = accent_blue
            elif current_phase == "compare":
                m_color = accent_gold
            elif current_phase in ["place", "pivot"]:
                m_color = accent_green

            m_s = font.render(msg, True, m_color)
            m_rect = m_s.get_rect(center=(win_w // 2, 470))
            win.blit(m_s, m_rect)

            for l_idx in levels:
                for node in levels[l_idx]:
                    draw_node(node, l_idx, current_phase)
        else:
            for l_idx in levels:
                for node in levels[l_idx]:
                    draw_node(node, l_idx)

        draw_button(pygame.Rect(50, 500, 100, 45), "STEP", 50 <= mx <= 150 and 500 <= my <= 545)
        draw_button(pygame.Rect(170, 500, 140, 45), "AUTO PLAY",
                     170 <= mx <= 310 and 500 <= my <= 545,
                     accent_blue if auto else None,
                     (255, 255, 255) if auto else None)
        draw_button(pygame.Rect(330, 500, 110, 45), "RESET", 330 <= mx <= 440 and 500 <= my <= 545)


def get_node_x(level, idx_in_level, total_on_level, node_w):
    section_w = win_w / total_on_level
    return section_w * idx_in_level + (section_w - node_w) / 2


def quick_sort_tree_gen(arr, level, idx_in_level, total_on_level, parent_pos=None):
    global count

    n = len(arr)
    node_w = n * (box_w + gap) - gap
    x = get_node_x(level, idx_in_level, total_on_level, node_w)
    y = start_y + level * level_h

    node = {"values": list(arr), "x": x, "y": y, "active": True, "parent_pos": parent_pos}

    if level not in levels:
        levels[level] = []
    levels[level].append(node)

    if n <= 1:
        yield {"msg": f"Base case: {arr}"}
        node["active"] = False
        return arr

    pivot = arr[-1]
    rest = arr[:-1]

    yield {"msg": f"Partitioning with pivot selected: {pivot}"}

    node["active"] = False

    left = []
    right = []

    for i, v in enumerate(rest):
        count += 1
        yield {"msg": f"Comparing {v} with pivot {pivot}", "comparing": [i]}
        if ascending:
            if v <= pivot:
                left.append(v)
            else:
                right.append(v)
        else:
            if v >= pivot:
                left.append(v)
            else:
                right.append(v)

    node["active"] = True
    node["values"] = left + [pivot] + right

    yield {"msg": f"Placing pivot {pivot} in correct position"}

    pivot_pos = len(left)

    left_sorted = yield from quick_sort_tree_gen(left, level + 1, idx_in_level * 2, total_on_level * 2,
                                                  (x + node_w // 2, y))
    right_sorted = yield from quick_sort_tree_gen(right, level + 1, idx_in_level * 2 + 1, total_on_level * 2,
                                                   (x + node_w // 2, y))

    node["active"] = True
    node["values"] = left_sorted + [pivot] + right_sorted

    node["active"] = False

    return left_sorted + [pivot] + right_sorted


sort_gen = None


def start_sort():
    global typing, sort_gen, levels, done, count, msg, nums, txt
    if txt:
        nums.append(int(txt))
        txt = ""

    if len(nums) < 2:
        return

    typing = False
    levels = {}
    count = 0
    sort_gen = quick_sort_tree_gen(list(nums), 0, 0, 1)
    done = False
    msg = "Starting Tree-based Quick Sort..."


def next_step():
    global done, msg
    try:
        step = next(sort_gen)
        msg = step["msg"]
    except StopIteration:
        done = True
        msg = "Sorting Finished!"


auto_delay_ms = 500

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
                    if txt:
                        txt = txt[:-1]
                    elif nums:
                        nums.pop()
                elif ev.key == pygame.K_SPACE:
                    start_sort()
                elif ev.unicode.isdigit():
                    txt += ev.unicode
            else:
                if ev.key == pygame.K_SPACE:
                    step_now = True

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
            else:
                if 50 <= mx <= 150 and 500 <= my <= 545:
                    step_now = True
                if 170 <= mx <= 310 and 500 <= my <= 545:
                    auto = not auto
                if 330 <= mx <= 440 and 500 <= my <= 545:
                    nums = []
                    txt = ""
                    typing = True
                    auto = False
                    done = False
                    msg = ""
                    levels = {}
                    sort_gen = None

    if (step_now or (auto and not done)) and not typing and not done:
        next_step()
        if auto:
            pygame.time.delay(auto_delay_ms)

