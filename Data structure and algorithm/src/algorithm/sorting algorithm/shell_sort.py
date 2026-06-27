# SHELL SORT VISUALIZATION 
import pygame
import sys

pygame.init()

win_w, win_h = 950, 600
win = pygame.display.set_mode((win_w, win_h))
pygame.display.set_caption("Shell Sort")

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
pos = []
txt = ""

typing = True
done = False
auto = False
ascending = True

msg = ""
count = 0

# Shell sort state machine
state = "none"  # compare, shift, place, finished
n = 0

gap = 0
i = 0
j = 0
key_val = None

box_w = 60
gap_x = 15
y_pos = 300


def draw_button(rect, text, is_hovered,
                color=None,
                text_col=None,
                border=True):
    c = color if color is not None else (btn_hover if is_hovered else btn_normal)
    t_c = text_col if text_col is not None else text_color

    pygame.draw.rect(win, c, rect, border_radius=8)
    if border:
        pygame.draw.rect(win, box_border, rect, 1, border_radius=8)

    s = font.render(text, True, t_c)
    r = s.get_rect(center=rect.center)
    win.blit(s, r)


def ease_in_out_cubic(t: float) -> float:
    # t in [0,1]
    if t < 0.5:
        return 4 * t * t * t
    return 1 - pow(-2 * t + 2, 3) / 2


def anim_move_index(idx, new_x, duration_ms=260):
    """Smoothly animate a single box from current pos[idx] to new_x."""
    start_x = pos[idx]
    if start_x == new_x:
        return

    clock = pygame.time.Clock()
    elapsed = 0
    # also pump events to keep window responsive during animation
    while elapsed < duration_ms:
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        dt = clock.tick(60)
        elapsed += dt
        t = 0 if duration_ms <= 0 else min(1.0, elapsed / duration_ms)
        e = ease_in_out_cubic(t)
        pos[idx] = int(round(start_x + (new_x - start_x) * e))
        draw()
        pygame.display.update()

    pos[idx] = new_x


def anim_swap_by_shift(shift_from_idx, shift_to_idx, duration_ms=260):
    """Animate shifting a value at shift_from_idx to shift_to_idx.

    This visualization shifts boxes along the row by moving the affected indices.
    """
    if shift_from_idx == shift_to_idx:
        return

    # We assume shift_to_idx is exactly shift_from_idx -/+ gap
    anim_move_index(shift_from_idx, pos[shift_to_idx], duration_ms=duration_ms)


def current_slot_x(k: int) -> int:
    return int((win_w - (n * (box_w + gap_x) - gap_x)) // 2 + k * (box_w + gap_x))


def reset_positions():
    global pos
    if n <= 0:
        pos = []
        return
    sx = (win_w - (n * (box_w + gap_x) - gap_x)) // 2
    pos = [sx + k * (box_w + gap_x) for k in range(n)]


def draw():
    global msg
    win.fill(bg_color)
    mx, my = pygame.mouse.get_pos()

    t = big_font.render("SHELL SORT VISUALIZATION", True, text_color)
    win.blit(t, (30, 40))

    if typing:
        m = font.render("Type a number and press [ENTER] to add", True, sub_color)
        win.blit(m, (30, 90))
    else:
        info_str = f"Comparisons: {count} | Gap: {gap} | Mode: {'Ascending' if ascending else 'Descending'}"
        info = font.render(info_str, True, text_color)
        win.blit(info, (35, 110))

    items = nums + ([txt] if typing else [])
    if not items:
        # buttons still drawn below
        pass
    else:
        total_items = len(items)
        start_x_typing = None
        if total_items > 0:
            total_w = total_items * (box_w + gap_x) - gap_x
            start_x_typing = (win_w - total_w) // 2

        for idx, val in enumerate(items):
            c = box_color
            bc = box_border

            if typing and idx == total_items - 1:
                bc = accent_blue
            elif not typing:
                # highlight the gapped insertion process
                if state == "compare":
                    if idx == j or idx == j - gap or idx == i:
                        bc = accent_gold
                    if idx == j:
                        c = (60, 60, 20)

                elif state == "shift":
                    if idx == j:
                        bc = accent_green
                        c = (20, 60, 30)

                elif state == "place":
                    if idx == j:
                        bc = accent_green
                        c = (20, 60, 30)

                elif state == "finished":
                    bc = accent_green

            if typing:
                x = start_x_typing + idx * (box_w + gap_x)
            else:
                x = pos[idx] if idx < len(pos) else start_x_typing + idx * (box_w + gap_x)

            rect = pygame.Rect(x, y_pos, box_w, box_w)

            shadow = rect.copy()
            shadow.y += 4
            pygame.draw.rect(win, (10, 10, 15), shadow, border_radius=10)

            pygame.draw.rect(win, c, rect, border_radius=10)
            pygame.draw.rect(win, bc, rect, 2, border_radius=10)

            s = font.render(str(val), True, text_color)
            win.blit(s, s.get_rect(center=rect.center))

        if not typing and msg:
            m_surf = font.render(msg, True, accent_gold)
            m_rect = m_surf.get_rect(center=(win_w // 2, y_pos + box_w + 60))
            win.blit(m_surf, m_rect)

    if not typing:
        draw_button(
            pygame.Rect(50, 500, 100, 45),
            "STEP",
            50 <= mx <= 150 and 500 <= my <= 545,
        )
        draw_button(
            pygame.Rect(170, 500, 140, 45),
            "AUTO PLAY",
            170 <= mx <= 310 and 500 <= my <= 545,
            accent_blue if auto else None,
            (255, 255, 255) if auto else None,
        )
        draw_button(
            pygame.Rect(330, 500, 110, 45),
            "RESET",
            330 <= mx <= 440 and 500 <= my <= 545,
        )
    else:
        can_start = len(nums) + (1 if txt else 0) >= 2
        sort_btn_color = accent_blue if can_start else btn_disabled
        sort_txt_color = (255, 255, 255) if can_start else btn_disabled_text

        draw_button(
            pygame.Rect(50, 500, 160, 45),
            "START SORT",
            50 <= mx <= 210 and 500 <= my <= 545 and can_start,
            sort_btn_color,
            sort_txt_color,
            border=not can_start,
        )
        draw_button(
            pygame.Rect(230, 500, 130, 45),
            "ASCENDING",
            230 <= mx <= 360 and 500 <= my <= 545,
            accent_gold if ascending else None,
            (255, 255, 255) if ascending else None,
        )
        draw_button(
            pygame.Rect(380, 500, 130, 45),
            "DESCENDING",
            380 <= mx <= 510 and 500 <= my <= 545,
            accent_gold if not ascending else None,
            (255, 255, 255) if not ascending else None,
        )


def compare_should_shift(a, b) -> bool:
    # returns True if a should be shifted right past b (i.e., in ascending we shift while a > b)
    if ascending:
        return a > b
    return a < b


def start_sort():
    global typing, done, auto, n, gap, i, j, key_val
    global nums, pos, msg, count
    global state

    if txt:
        nums.append(int(txt))
    txt_str = ""  # local placeholder
    # keep global txt untouched here; caller clears it

    if len(nums) < 2:
        return

    typing = False
    done = False
    auto = False

    n = len(nums)
    reset_positions()

    count = 0
    gap = n // 2
    i = gap
    j = i
    key_val = None

    state = "compare"
    msg = f"Starting Shell Sort..."


def start_gapped_insertion():
    """Initialize key & indices for current i under current gap."""
    global key_val, j
    key_val = nums[i]
    j = i
    # key sits logically; we will shift elements that need moving

    global msg, state
    msg = f"Gap={gap}: inserting key at index {i}..."
    state = "compare"


def shell_step():
    """One logical STEP; includes smooth animation for moves when shifting."""
    global done, state, msg, count
    global gap, i, j, key_val
    global nums

    if done:
        return

    if gap <= 0:
        done = True
        state = "finished"
        msg = "Sorting Finished!"
        return

    # When state is compare we may decide to shift or place
    if state == "compare":
        # if first time for this i, key_val may not be set
        if key_val is None:
            start_gapped_insertion()
            return

        # compare nums[j-gap] with key_val
        if j - gap >= 0:
            count += 1
            a = nums[j - gap]
            b = key_val
            if compare_should_shift(a, b):
                # shift a right by gap: nums[j] becomes nums[j-gap]
                state = "shift"
                msg = f"Gap={gap}: shifting {a} right (compare {a} vs key {b})"
                return
            else:
                # place key at position j
                state = "place"
                msg = f"Gap={gap}: placing key {key_val} at index {j}"
                return
        else:
            # out of bounds, place key at index j
            state = "place"
            msg = f"Gap={gap}: placing key {key_val} at index {j} (left boundary)"
            return

    elif state == "shift":
        # shift nums[j-gap] -> nums[j]
        from_idx = j - gap
        to_idx = j

        # animate movement of the box at from_idx to to_idx
        # (smooth easing instead of steady steps)
        anim_swap_by_shift(from_idx, to_idx, duration_ms=240)

        nums[to_idx] = nums[from_idx]
        nums[from_idx] = key_val  # temporary to keep values aligned during animation

        # update logical positions: after shift, next compare uses earlier element
        # visually, the key will end up after we place it; we keep key_val constant.
        j -= gap

        state = "compare"
        # keep msg updated in compare on next step
        return

    elif state == "place":
        # place key_val at index j
        # During shifts we kept key_val in nums[from_idx] placeholders; restore cleanly.
        nums[j] = key_val

        # animate the key placement by nudging box at j to its exact slot smoothly
        target_x = current_slot_x(j)
        if 0 <= j < len(pos):
            anim_move_index(j, target_x, duration_ms=220)

        # prepare next i within same gap
        key_val = None
        j = 0

        i += 1
        if i >= n:
            # move to next gap and restart
            gap //= 2
            i = gap
            j = i

            if gap <= 0:
                done = True
                state = "finished"
                msg = "Sorting Finished!"
                return

            key_val = None
            state = "compare"
            msg = f"Gap updated to {gap}. Starting next gapped insertion pass..."
            return

        state = "compare"
        msg = f"Gap={gap}: next insertion at index {i}"
        return

    else:
        # fallback
        state = "compare"


sort_gen = None  # unused; kept for consistency with other files

def next_step():
    global step_now, auto
    shell_step()


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
                        txt = ""  # clear entry
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
                    pos = []
                    state = "none"
                    gap = 0
                    i = j = 0
                    key_val = None
                    count = 0

    if (step_now or (auto and not done)) and not typing and not done:
        next_step()
        if auto:
            pygame.time.delay(180)

