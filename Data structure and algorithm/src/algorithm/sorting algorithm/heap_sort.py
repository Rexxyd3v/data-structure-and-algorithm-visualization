import pygame
import sys

pygame.init()
win_w, win_h = 950, 600
win = pygame.display.set_mode((win_w, win_h))
pygame.display.set_caption("Heap Sort Tree")

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
            if current_phase == "build":
                bc = accent_blue
            elif current_phase == "compare":
                bc = accent_gold
            elif current_phase in ["swap", "heapify", "place"]:
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


def get_node_x(level, idx_in_level, total_on_level, node_w):
    section_w = win_w / total_on_level
    return section_w * idx_in_level + (section_w - node_w) / 2


def heap_sort_tree_gen(arr, level=0, idx_in_level=0, total_on_level=1, parent_pos=None):
    """Tree-style visualization (like quick/merge sort): create a node per heapify/extract action.

    Each STEP advances one compare/swap/place yield.
    """
    global levels, count

    n = len(arr)
    node_w = n * (box_w + gap) - gap
    x = get_node_x(level, idx_in_level, total_on_level, node_w)
    y = start_y + level * level_h

    node = {"values": list(arr), "x": x, "y": y, "active": True, "parent_pos": parent_pos}
    levels.setdefault(level, []).append(node)

    def better(a_idx, b_idx):
        if ascending:
            return arr[a_idx] > arr[b_idx]
        return arr[a_idx] < arr[b_idx]

    def new_child(pos, values, msg_text):
        """Create a child node under current node for a single action."""
        child_n = len(values)
        child_w = child_n * (box_w + gap) - gap
        cx = get_node_x(level + 1, pos, total_on_level * 2, child_w)
        cy = start_y + (level + 1) * level_h
        child = {"values": list(values), "x": cx, "y": cy, "active": True, "parent_pos": (node["x"] + node_w // 2, node["y"])}
        levels.setdefault(level + 1, []).append(child)
        yield {"msg": msg_text, "active": True}
        return child

    # We'll implement heapify/extraction, but each time we do compare/swap/place,
    # we update the current node AND spawn a short-lived child node so the tree grows.
    yield {"msg": "Starting heap build", "active": True}
    node["active"] = False

    # Build heap
    for i in range(n // 2 - 1, -1, -1):
        node["active"] = True
        yield {"msg": f"Building heap: heapify from index {i}", "active": True}
        node["active"] = False

        heap_size = n
        j = i
        while True:
            left = 2 * j + 1
            right = 2 * j + 2
            largest = j

            if left < heap_size:
                count += 1
                node["active"] = True
                node["values"] = list(arr)
                yield {"msg": f"Comparing children at {left} with {largest}", "active": True}
                if better(left, largest):
                    largest = left

            if right < heap_size:
                count += 1
                node["active"] = True
                node["values"] = list(arr)
                yield {"msg": f"Comparing children at {right} with {largest}", "active": True}
                if better(right, largest):
                    largest = right

            if largest != j:
                count += 1
                arr[j], arr[largest] = arr[largest], arr[j]
                node["values"] = list(arr)
                node["active"] = True
                yield {"msg": f"Swapping indices {j} and {largest}", "active": True}
                # spawn a child under current level+1 to show the swap visually
                # pos uses heap indices to distribute children
                yield from new_child(largest % (2 ** (level + 1)), arr, f"Placed swap result at indices {j} & {largest}")
                node["active"] = False
                j = largest
            else:
                node["active"] = False
                break

    yield {"msg": "Heap built, starting extraction", "active": True}

    # Extract elements
    for end in range(n - 1, 0, -1):
        arr[0], arr[end] = arr[end], arr[0]
        node["values"] = list(arr)
        node["active"] = True
        yield {"msg": f"Placed max element at index {end}", "active": True}
        yield from new_child(end % (2 ** (level + 1)), arr, f"Extraction placed at {end}")
        node["active"] = False

        # heapify root for reduced heap
        heap_size = end
        j = 0
        while True:
            left = 2 * j + 1
            right = 2 * j + 2
            largest = j

            if left < heap_size:
                count += 1
                node["active"] = True
                node["values"] = list(arr)
                yield {"msg": f"Comparing children at {left} with {largest}", "active": True}
                if better(left, largest):
                    largest = left

            if right < heap_size:
                count += 1
                node["active"] = True
                node["values"] = list(arr)
                yield {"msg": f"Comparing children at {right} with {largest}", "active": True}
                if better(right, largest):
                    largest = right

            if largest != j:
                count += 1
                arr[j], arr[largest] = arr[largest], arr[j]
                node["values"] = list(arr)
                node["active"] = True
                yield {"msg": f"Swapping indices {j} and {largest}", "active": True}
                yield from new_child(largest % (2 ** (level + 1)), arr, f"Heapify swap result ({j} & {largest})")
                node["active"] = False
                j = largest
            else:
                node["active"] = False
                break

    node["active"] = False
    return arr



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
    sort_gen = heap_sort_tree_gen(list(nums), 0, 0, 1)
    done = False
    msg = "Starting Tree-based Heap Sort..."


def next_step():
    global done, msg
    try:
        step = next(sort_gen)
        msg = step["msg"]
    except StopIteration:
        done = True
        msg = "Sorting Finished!"


def draw():
    win.fill(bg_color)
    mx, my = pygame.mouse.get_pos()

    title = big_font.render("HEAP SORT TREE VISUALIZATION", True, text_color)
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
            for idx, val in enumerate(items):
                bc = accent_blue if idx == n - 1 else box_border
                rect = pygame.Rect(start_x + idx * (bw + bgp), y_pos, bw, bw)
                pygame.draw.rect(win, (10, 10, 15), (rect.x, rect.y + 4, bw, bw), border_radius=10)
                pygame.draw.rect(win, box_color, rect, border_radius=10)
                pygame.draw.rect(win, bc, rect, 2, border_radius=10)
                s = font.render(str(val), True, text_color)
                win.blit(s, s.get_rect(center=rect.center))

        can_start = len(nums) + (1 if txt else 0) >= 2
        sort_btn_color = accent_blue if can_start else btn_disabled
        sort_txt_color = (255, 255, 255) if can_start else btn_disabled_text
        draw_button(pygame.Rect(50, 500, 160, 45), "START SORT",
                     50 <= mx <= 210 and 500 <= my <= 545 and can_start,
                     sort_btn_color, sort_txt_color, border=not can_start)
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
            lower_msg = msg.lower()
            current_phase = ""
            m_color = sub_color
            if "building" in lower_msg or "heapify" in lower_msg:
                current_phase = "build"
                m_color = accent_blue
            elif "compare" in lower_msg or "comparing" in lower_msg:
                current_phase = "compare"
                m_color = accent_gold
            elif "swap" in lower_msg or "placed" in lower_msg:
                current_phase = "swap"
                m_color = accent_green

            m_s = font.render(msg, True, m_color)
            win.blit(m_s, m_s.get_rect(center=(win_w // 2, 470)))

            for l_idx in levels:
                for node in levels[l_idx]:
                    draw_node(node, l_idx, current_phase)
        else:
            for l_idx in levels:
                for node in levels[l_idx]:
                    draw_node(node, l_idx)

        draw_button(pygame.Rect(50, 500, 100, 45), "STEP", 50 <= mx <= 150 and 500 <= my <= 545)
        draw_button(pygame.Rect(170, 500, 140, 45), "AUTO PLAY", 170 <= mx <= 310 and 500 <= my <= 545,
                     accent_blue if auto else None, (255, 255, 255) if auto else None)
        draw_button(pygame.Rect(330, 500, 110, 45), "RESET", 330 <= mx <= 440 and 500 <= my <= 545)


while True:
    draw()
    pygame.display.update()

    step_now = False

    for ev in pygame.event.get():
        if ev.type == pygame.QUIT:
            pygame.quit(); sys.exit()

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
                    levels = {}
                    msg = ""

    if (step_now or (auto and not done)) and not typing and not done:
        next_step()
        if auto:
            pygame.time.delay(500)

