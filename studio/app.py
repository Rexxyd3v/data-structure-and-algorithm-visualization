"""Resizable Pygame interface for the learning studio."""
import argparse
import os
import random
import re
import pygame
from .algorithms import CATEGORIES, INFO, SORTS, SEARCHES, STRUCTURES, GRAPHS, trace

TITLE = 'Algorthm and data structure visualization'
BG = '#FFFFFF'
INK = '#203B4E'
MUTED = '#526C7D'
LINE = '#C6D6DF'
ACCENT = '#B76B20'
GREEN = '#277B55'
BLUE = '#367DA1'
PANEL = '#EFF7FB'
BAR = '#76AAC4'
SECTIONS = ('Algorithms', 'Data Structures')


def initial_window_size(desktop):
    """Leave room for the OS taskbar and window frame, including small displays."""
    return max(1, min(1440, int(desktop[0] * .92))), max(1, min(920, int(desktop[1] * .86)))


class Studio:
    WIDTH, HEIGHT = 1440, 920

    def __init__(self, window_size=None):
        pygame.display.init()
        pygame.font.init()
        self.desktop_size = pygame.display.get_desktop_sizes()[0]
        self.windowed_size = window_size or initial_window_size(self.desktop_size)
        self.fullscreen = False
        os.environ.setdefault('SDL_VIDEO_CENTERED', '1')
        self.window = pygame.display.set_mode(self.windowed_size, pygame.RESIZABLE)
        pygame.display.set_caption(TITLE)
        self.surface = pygame.Surface(self.window.get_size())
        self.clock = pygame.time.Clock()
        self.fonts = {}
        self.hits = []
        self.category = 'Sorting'
        self.algorithm = 'Bubble sort'
        self.input = '64, 34, 25, 12, 22, 11, 90, 48, 72, 38, 56, 18'
        self.target = '42'
        self.descending = False
        self.focus = None
        self.select_all = False
        self.error = ''
        self.speed = 5
        self.playing = False
        self.position = 0
        self.elapsed = 0
        self.mouse = (0, 0)
        self.running = True
        self.scroll = 0
        self.pan = 0
        self.pan_max = 0
        self.menu_open = False
        self.menu_scroll = 0
        self.dragging = None
        self.timeline = pygame.Rect(0, 0, 1, 1)
        self.last_selection = {'Algorithms': ('Bubble sort', 'Sorting'), 'Data Structures': ('Stack', 'Data structures')}
        self.rebuild()

    @property
    def section(self):
        return 'Data Structures' if self.algorithm in STRUCTURES else 'Algorithms'

    def choose_section(self, section):
        if section == self.section: return
        self.last_selection[self.section] = (self.algorithm, self.category)
        name, category = self.last_selection[section]
        self.choose_algorithm(name, category)
        self.scroll = 0

    def menu_entries(self):
        if self.section == 'Data Structures':
            return [(name, 'Data structures') for name in STRUCTURES]
        entries = []
        for category, names in CATEGORIES.items():
            if category == 'Data structures': continue
            entries.append((None, category))
            entries.extend((name, category) for name in names)
        return entries

    def font(self, size=16, bold=False, mono=False, serif=False):
        key = (size, bold, mono, serif)
        if key not in self.fonts:
            # SysFont('arial') can resolve to Arial Narrow on Windows.
            font_path = os.path.join(os.environ.get('WINDIR', 'C:/Windows'), 'Fonts', 'arialbd.ttf' if bold else 'arial.ttf')
            self.fonts[key] = pygame.font.Font(font_path, size) if os.path.isfile(font_path) else pygame.font.SysFont('dejavusans,liberationsans,arial', size, bold=bold)
        return self.fonts[key]

    def text(self, value, x, y, size=16, color=INK, bold=False, mono=False, center=False, serif=False):
        img = self.font(size, bold, mono, serif).render(str(value), True, color)
        rect = img.get_rect(center=(x, y)) if center else img.get_rect(topleft=(x, y))
        self.surface.blit(img, rect)
        return rect

    def wrapped(self, value, x, y, width, size=16, color=MUTED, line_height=25):
        words = str(value).split(); line = ''; start = y
        for word in words:
            if line and self.font(size).size(line + ' ' + word)[0] > width:
                self.text(line, x, y, size, color); y += line_height; line = word
            else: line = (line + ' ' + word).strip()
        if line: self.text(line, x, y, size, color); y += line_height
        return y - start

    def panel(self, rect, color=PANEL, border=LINE, radius=4):
        pygame.draw.rect(self.surface, color, rect, border_radius=radius)
        if border: pygame.draw.rect(self.surface, border, rect, 1, border_radius=radius)

    def button(self, rect, label, action, primary=False, active=False, disabled=False, dark=False, size=15):
        rect = pygame.Rect(rect); hover = rect.collidepoint(self.mouse)
        color = '#DCEEF8' if active else BG
        text_color = INK
        if primary: color, text_color = GREEN, '#FFFFFF'
        if hover and not disabled: color = '#1C6242' if primary else '#E9F3F9'
        if disabled: color, text_color = '#F1F4F6', '#899BA6'
        pygame.draw.rect(self.surface, '#173D2B' if primary else '#BACCD7', rect.move(0, 3), border_radius=3)
        self.panel(rect, color, '#1B6743' if primary else LINE, 3)
        self.text(label, *rect.center, size, text_color, bold=primary or active, center=True)
        if not disabled: self.hits.append((rect, action))

    def field(self, rect, name, value, placeholder=''):
        rect = pygame.Rect(rect)
        self.panel(rect, '#FFFFFF', ACCENT if self.focus == name else LINE, 5)
        old = self.surface.get_clip(); self.surface.set_clip(rect.inflate(-20, -4))
        shown = value or placeholder
        if self.focus == name and self.select_all:
            pygame.draw.rect(self.surface, '#D5EAF6', (rect.x + 12, rect.y + 10, min(self.font(15, mono=True).size(value)[0], rect.w - 24), 22))
        scroll = max(0, self.font(15, mono=True).size(value)[0] - rect.w + 30) if self.focus == name and not self.select_all else 0
        self.text(shown, rect.x + 12 - scroll, rect.y + 10, 15, INK if value else MUTED, mono=True)
        if self.focus == name and pygame.time.get_ticks() % 1000 < 550:
            cursor = rect.x + 12 + self.font(15, mono=True).size(value)[0] - scroll
            pygame.draw.line(self.surface, ACCENT, (cursor, rect.y + 10), (cursor, rect.y + 31), 2)
        self.surface.set_clip(old)
        self.hits.append((rect, lambda: self.set_focus(name)))

    def set_focus(self, name):
        self.focus = name; self.select_all = False; self.playing = False

    def values(self):
        raw = self.input.strip()
        if not re.fullmatch(r'[+-]?\d+(?:[\s,]+[+-]?\d+)*', raw):
            raise ValueError('Use integers separated by commas or spaces, with no trailing comma.')
        values = [int(v) for v in re.split(r'[\s,]+', raw)]
        if any(abs(v) > 9999 for v in values): raise ValueError('Values must be between -9999 and 9999.')
        return values

    def rebuild(self):
        self.playing = False; self.elapsed = 0
        try:
            target = int(self.target) if self.algorithm in SEARCHES else 0
            frames = trace(self.algorithm, [1] if self.algorithm in GRAPHS else self.values(), self.descending, target)
        except (ValueError, OverflowError) as error:
            self.error = str(error); return False
        self.frames = frames; self.position = 0; self.error = ''; self.focus = None
        self.pan = 0
        return True

    def choose_category(self, name):
        self.choose_algorithm(CATEGORIES[name][0], name)
        self.scroll = 0

    def choose_algorithm(self, name, category=None):
        previous = self.algorithm, self.category
        self.algorithm = name
        self.category = category or next(group for group, names in CATEGORIES.items() if name in names)
        if not self.rebuild(): self.algorithm, self.category = previous
        self.menu_open = False

    def randomize(self):
        self.input = ', '.join(str(random.randint(5, 95)) for _ in range(8 if self.category in ['Data structures', 'Compression'] else 12))
        self.rebuild()

    def toggle_order(self):
        self.descending = not self.descending; self.rebuild()

    def advance(self, delta):
        self.playing = False
        self.position = max(0, min(len(self.frames) - 1, self.position + delta))

    def toggle_play(self):
        if self.position == len(self.frames) - 1: self.position = 0
        self.playing = not self.playing; self.elapsed = 0; self.focus = None

    def remove_item(self):
        values = self.frames[-1].values
        if not values: return
        removed = values[-1] if self.algorithm == 'Stack' else values[0]
        values = values[:-1] if self.algorithm == 'Stack' else values[1:]
        from .algorithms import Frame
        self.frames = self.frames[:self.position + 1] + [Frame(values, f"{'Pop' if self.algorithm == 'Stack' else 'Dequeue'} {removed}. {len(values)} values remain.")]
        self.position = len(self.frames) - 1; self.playing = False

    def draw_bars(self, frame, rect):
        x, y, w, h = rect; values = frame.values
        if not values: return
        low, high = min(0, min(values)), max(0, max(values))
        span = max(1, high - low); chart_h = h - 75
        baseline = y + 30 + high / span * chart_h
        pygame.draw.line(self.surface, LINE, (x, baseline), (x + w, baseline))
        step = w / len(values); bw = min(56, step - 9)
        for i, value in enumerate(values):
            cx = x + step * (i + .5); height = max(3, abs(value) / span * chart_h)
            top = baseline - height if value >= 0 else baseline
            color = ACCENT if i in frame.active else GREEN if i in frame.settled else BAR
            pygame.draw.rect(self.surface, color, (cx - bw / 2, top, bw, height), border_radius=2)
            pygame.draw.rect(self.surface, '#647760' if i not in frame.active else ACCENT, (cx - bw / 2, top, bw, 2))
            self.text(value, cx, top - 16 if value >= 0 else top + height + 15, 13 if len(values) > 18 else 15, INK, True, center=True)
            self.text(i, cx, y + h - 8, 11, MUTED, mono=True, center=True)

    def draw_tree(self, frame, rect, graph=False):
        x, y, w, h = rect; nodes = frame.nodes; edges = frame.edges
        if not nodes: return
        positions = {}
        if graph:
            spots = [(0.08, .48), (.32, .17), (.32, .8), (.61, .12), (.57, .58), (.83, .32), (.89, .82)]
            positions = {k: (x + spots[k][0] * w, y + spots[k][1] * h) for k in nodes}
        else:
            children = {k: [] for k in nodes}; child_ids = set()
            for parent, child, _ in edges: children[parent].append(child); child_ids.add(child)
            roots = [k for k in nodes if k not in child_ids]
            leaves = sum(not children[k] for k in nodes); leaf_index = 0
            depths = {}
            def place(k, depth):
                nonlocal leaf_index
                depths[k] = depth
                if children[k]:
                    xs = [place(c, depth + 1) for c in children[k]]; px = sum(xs) / len(xs)
                else:
                    px = (leaf_index + .5) / max(1, leaves); leaf_index += 1
                positions[k] = (x + px * w, depth); return px
            for root in roots: place(root, 0)
            max_depth = max(depths.values(), default=0)
            positions = {k: (px, y + 24 + depth / max(1, max_depth) * (h - 48)) for k, (px, depth) in positions.items()}
        radius = 27 if graph else max(13, min(24, w / (max(1, sum(k not in {e[0] for e in edges} for k in nodes)) * 2.5)))
        for u, v, weight in edges:
            a, b = positions[u], positions[v]
            selected = graph and ((u, v) in frame.settled or (v, u) in frame.settled)
            pygame.draw.line(self.surface, GREEN if selected else '#B9C3B4', a, b, 4 if selected else 2)
            if graph or self.algorithm == 'Huffman coding':
                mx, my = (a[0] + b[0]) / 2, (a[1] + b[1]) / 2
                self.panel((mx - 12, my - 11, 24, 22), PANEL, None, 2)
                self.text(weight, mx, my, 12, GREEN if selected else MUTED, True, center=True)
        for k, value in nodes.items():
            px, py = positions[k]; active = k in frame.active; visited = k in frame.visited
            color = ACCENT if active else GREEN if visited else '#F5F6F0'
            pygame.draw.circle(self.surface, color, (px, py), radius)
            pygame.draw.circle(self.surface, color if active or visited else '#A9BAA2', (px, py), radius, 2)
            label = str(value)
            self.text(label, px, py, 14 if graph else 11 if len(label) > 4 or radius < 20 else 14, BG if active or visited else INK, True, center=True)

    def draw_structure(self, frame, rect):
        x, y, w, h = rect; a = frame.values; name = self.algorithm
        if name in ['Binary search tree', 'AVL tree']:
            self.draw_tree(frame, rect); return
        if name in ['Min heap', 'Max heap']:
            from .algorithms import Frame
            tree = Frame(a, frame.message, frame.active, nodes=dict(enumerate(a)), edges=[((i - 1) // 2, i, 0) for i in range(1, len(a))])
            self.draw_tree(tree, rect); return
        if name == 'Hash table':
            for bucket in range(7):
                cy = y + 10 + bucket * 36
                self.panel((x, cy, 44, 32), '#E7EDE1', None, 6); self.text(bucket, x + 22, cy + 16, 13, BLUE, True, center=True)
                vals = [(i, v) for i, v in enumerate(a) if v % 7 == bucket]
                for j, (i, value) in enumerate(vals):
                    xx = x + 64 + j * 62
                    if xx + 54 > x + w:
                        self.text(f'+{len(vals) - j}', xx - 3, cy + 6, 12, MUTED); break
                    self.panel((xx, cy, 54, 32), '#F0DECE' if i in frame.active else '#E7EDE1', None, 6)
                    self.text(value, xx + 27, cy + 16, 12, INK, True, center=True)
                    if j < len(vals) - 1: self.text('›', xx + 55, cy + 3, 17, MUTED)
            return
        if name == 'Stack':
            step = min(35, (h - 35) / max(1, len(a))); cx = x + w / 2
            for i, value in enumerate(a):
                yy = y + h - (i + 1) * step
                self.panel((cx - 90, yy, 180, step - 3), '#F0DECE' if i in frame.active else '#E7EDE1', None, 4)
                self.text(value, cx, yy + (step - 3) / 2, 13, INK, True, center=True)
            self.text('TOP ↑', cx + 112, y + h - len(a) * step, 12, ACCENT, True)
            self.text('LAST IN / FIRST OUT', x + w - 196, y + 8, 11, MUTED, mono=True); return
        columns = max(1, min(8, int(w // 85))); step = w / columns
        for i, value in enumerate(a):
            col, row = i % columns, i // columns; xx, yy = x + col * step, y + 45 + row * 90
            self.panel((xx, yy, step - 19, 46), '#F0DECE' if i in frame.active else '#E7EDE1', None, 8)
            self.text(value, xx + (step - 19) / 2, yy + 23, 14, INK, True, center=True)
            if i + 1 < len(a): self.text('↔' if name == 'Doubly linked list' else '→', xx + step - 16, yy + 13, 16, MUTED)
            if i == 0: self.text('FRONT' if name == 'Queue' else 'HEAD', xx, yy - 24, 10, BLUE, True)
            if i == len(a) - 1: self.text('REAR' if name == 'Queue' else 'TAIL → null', xx, yy + 54, 10, MUTED, True)
        if not a: self.text('Empty structure', x + w / 2, y + h / 2, 20, MUTED, center=True)

    def draw(self):
        from .view import draw
        draw(self)

    def scrub(self):
        fraction = max(0, min(1, (self.mouse[0] - self.timeline.x) / max(1, self.timeline.w)))
        self.position = round(fraction * (len(self.frames) - 1))
        self.playing = False

    def scroll_page(self, delta):
        self.scroll = max(0, min(self.scroll_max, self.scroll + delta))

    def move_drag(self):
        if self.dragging == 'timeline':
            self.scrub()
        elif self.dragging == 'pan':
            fraction = (self.mouse[0] - self.pan_track.x) / max(1, self.pan_track.w)
            self.pan = max(0, min(self.pan_max, fraction * self.pan_max))
        elif self.dragging == 'page':
            fraction = self.mouse[1] / max(1, self.viewport_height)
            self.scroll = max(0, min(self.scroll_max, fraction * self.content_height - self.viewport_height / 2))

    def event(self, event):
        if event.type == pygame.QUIT: self.running = False
        elif event.type == pygame.MOUSEWHEEL:
            if self.menu_open:
                self.menu_scroll = max(0, self.menu_scroll - event.y * 42)
            elif (event.x or pygame.key.get_mods() & pygame.KMOD_SHIFT) and self.pan_max:
                self.pan = max(0, min(self.pan_max, self.pan - (event.x or event.y) * 60))
            else:
                self.scroll_page(-event.y * 55)
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            self.dragging = None
        elif event.type == pygame.MOUSEMOTION:
            self.mouse = event.pos
            if self.dragging: self.move_drag()
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            self.mouse = getattr(event, 'pos', self.mouse)
            self.focus = None
            if self.menu_open and not self.menu_rect.collidepoint(self.mouse):
                self.menu_open = False
                return
            if not self.menu_open:
                if self.timeline.inflate(12, 20).collidepoint(self.mouse): self.dragging = 'timeline'
                elif self.pan_max and self.pan_track.inflate(0, 12).collidepoint(self.mouse): self.dragging = 'pan'
                elif self.scroll_max and self.page_track.collidepoint(self.mouse): self.dragging = 'page'
                if self.dragging:
                    self.move_drag()
                    return
            for rect, action in reversed(self.hits):
                if rect.collidepoint(self.mouse): action(); break
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_F11:
                if self.fullscreen:
                    self.window = pygame.display.set_mode(self.windowed_size, pygame.RESIZABLE)
                else:
                    self.windowed_size = self.window.get_size()
                    self.window = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
                self.fullscreen = not self.fullscreen
                self.dragging = None
                return
            if self.menu_open:
                if event.key == pygame.K_ESCAPE: self.menu_open = False
                elif event.key == pygame.K_DOWN: self.menu_scroll += 42
                elif event.key == pygame.K_UP: self.menu_scroll = max(0, self.menu_scroll - 42)
                return
            if self.focus:
                value = getattr(self, self.focus)
                if event.key == pygame.K_ESCAPE: self.focus = None
                elif event.key == pygame.K_RETURN: self.rebuild()
                elif event.key == pygame.K_a and event.mod & pygame.KMOD_CTRL: self.select_all = True
                elif event.key == pygame.K_BACKSPACE:
                    setattr(self, self.focus, '' if self.select_all else value[:-1]); self.select_all = False
                elif event.key == pygame.K_v and event.mod & pygame.KMOD_CTRL:
                    try:
                        if not pygame.scrap.get_init(): pygame.scrap.init()
                        pasted = pygame.scrap.get(pygame.SCRAP_TEXT)
                        if pasted:
                            text = pasted.decode('utf-8', errors='ignore').strip('\x00')
                            setattr(self, self.focus, (( '' if self.select_all else value) + text)[:240]); self.select_all = False
                    except pygame.error: pass
                elif event.unicode and not event.mod & pygame.KMOD_CTRL:
                    setattr(self, self.focus, (('' if self.select_all else value) + event.unicode)[:240]); self.select_all = False
            elif event.key == pygame.K_SPACE: self.toggle_play()
            elif event.key == pygame.K_RIGHT: self.advance(1)
            elif event.key == pygame.K_LEFT: self.advance(-1)
            elif event.key == pygame.K_r: self.advance(-len(self.frames))
            elif event.key == pygame.K_PAGEDOWN: self.scroll_page(self.viewport_height * .8)
            elif event.key == pygame.K_PAGEUP: self.scroll_page(-self.viewport_height * .8)
            elif event.key == pygame.K_HOME: self.scroll = 0
            elif event.key == pygame.K_END: self.scroll = self.scroll_max
            elif event.key == pygame.K_TAB:
                if self.algorithm not in GRAPHS:
                    self.scroll = min(self.scroll_max, max(0, self.input_top - 50))
                    self.set_focus('input')

    def present(self):
        self.window.blit(self.surface, (0, 0))
        pygame.display.flip()

    def run(self):
        self.draw()
        while self.running:
            dt = self.clock.tick(60)
            self.mouse = pygame.mouse.get_pos()
            if self.surface.get_size() != self.window.get_size(): self.draw()
            for event in pygame.event.get(): self.event(event)
            if self.playing:
                self.elapsed += dt
                if self.elapsed >= 1500 / self.speed:
                    self.elapsed = 0
                    if self.position < len(self.frames) - 1: self.position += 1
                    if self.position == len(self.frames) - 1: self.playing = False
            self.draw(); self.present()
        pygame.quit()


def main():
    parser = argparse.ArgumentParser(description=TITLE)
    parser.add_argument('--screenshot', help='Render the initial view to a PNG and exit')
    parser.add_argument('--size', metavar='WIDTHxHEIGHT', help='Override the automatically detected window size')
    args = parser.parse_args()
    size = None
    if args.size:
        match = re.fullmatch(r'(\d+)x(\d+)', args.size)
        if not match or min(map(int, match.groups())) < 240:
            parser.error('--size must be WIDTHxHEIGHT with both dimensions at least 240')
        size = tuple(map(int, match.groups()))
    if args.screenshot: os.environ.setdefault('SDL_VIDEODRIVER', 'dummy')
    app = Studio(size)
    if args.screenshot:
        app.draw(); pygame.image.save(app.surface, args.screenshot); pygame.quit()
    else: app.run()
