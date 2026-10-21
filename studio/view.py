"""Responsive, scrollable workspace drawn at native window resolution."""
import math
import pygame
from .algorithms import CATEGORIES, INFO, SORTS, SEARCHES, STRUCTURES, GRAPHS
from .app import TITLE, BG, INK, MUTED, LINE, ACCENT, GREEN, BLUE, BAR, PANEL, SECTIONS


def split_lines(app, value, width, size, serif=False, bold=False):
    result, current = [], ''
    for word in str(value).split():
        trial = (current + ' ' + word).strip()
        if current and app.font(size, bold=bold, serif=serif).size(trial)[0] > width:
            result.append(current)
            current = word
        else:
            current = trial
    if current: result.append(current)
    return result


def layout(app, width, height):
    """Two sections, a topic selector, input, then the visualization."""
    margin = 18 if width < 600 else 32
    cw = min(1500, max(140, width - margin * 2))
    x = (width - cw) // 2
    small = width < 600
    footer_h = 132 if cw < 900 else 96
    viewport_h = max(40, height - footer_h)
    title_size = 17 if small else 21
    title_lines = split_lines(app, TITLE, cw - 34, title_size, bold=True)
    y = 18 + len(title_lines) * (title_size + 8) + 14
    tabw = min(184, (cw - 8) // 2)
    tabs = [(section, pygame.Rect(x + i * (tabw + 8), y, tabw, 38)) for i, section in enumerate(SECTIONS)]
    y += 59
    eyebrow_y = y
    side_by_side = cw >= 1100
    selector = pygame.Rect(x, y + 25, 330 if side_by_side else min(460, cw), 44)
    input_x = x + 354 if side_by_side else x
    input_cw = cw - 354 if side_by_side else cw
    input_y = y if side_by_side else selector.bottom + 22
    actions = [('Apply', 80), ('Shuffle', 90)]
    if app.algorithm in SEARCHES: actions.insert(0, ('target', 136))
    if app.algorithm in SORTS: actions.append(('order', 116))
    if app.algorithm in ['Stack', 'Queue']: actions.append(('remove', 98))
    action_rects = []
    if app.algorithm in GRAPHS:
        field = None
        input_end = input_y + 75
    else:
        total_actions = sum(item[1] + 10 for item in actions)
        wide_input = input_cw >= 700
        field = pygame.Rect(input_x, input_y + 25, input_cw - total_actions if wide_input else input_cw, 44)
        ax, ay = (field.right + 10, field.y) if wide_input else (input_x, field.bottom + 12)
        for name, aw in actions:
            if ax > input_x and ax + aw > input_x + input_cw:
                ax, ay = input_x, ay + 52
            action_rects.append((name, pygame.Rect(ax, ay, min(aw, input_cw), 44)))
            ax += aw + 10
        input_end = max(field.bottom, ay + 44) + 26
    if app.error:
        input_end += len(split_lines(app, app.error, input_cw, 13)) * 20 + 8
    metrics_y = max(selector.bottom, input_end) + 12
    chart_y = metrics_y + 34
    plotw = max(100, cw - 36)
    frame = app.frames[app.position]
    if app.algorithm in SORTS + SEARCHES:
        naturalw = max(plotw, len(frame.values) * 42 + 24)
        ploth = max(220, min(350, int(height * .28)))
    elif app.algorithm in GRAPHS:
        naturalw, ploth = max(plotw, 560), max(290, min(410, int(height * .38)))
    elif app.algorithm == 'Stack':
        naturalw, ploth = max(plotw, 460), max(310, len(frame.values) * 24 + 55)
    elif app.algorithm in ['Singly linked list', 'Doubly linked list', 'Queue']:
        naturalw = max(plotw, 550)
        columns = max(1, min(8, int((naturalw - 24) // 85)))
        ploth = max(300, math.ceil(len(frame.values) / columns) * 90 + 65)
    else:
        leaves = max(1, len(frame.nodes) - len({u for u, _, _ in frame.edges}))
        naturalw = max(plotw, 540, leaves * 57)
        depths = {}
        children = {k: [] for k in frame.nodes}
        for u, v, _ in frame.edges: children[u].append(v)
        def depth(k):
            if k not in depths: depths[k] = 1 + max((depth(c) for c in children[k]), default=0)
            return depths[k]
        levels = max((depth(k) for k in frame.nodes), default=1)
        ploth = max(310, levels * 58 + 10)
    plot = pygame.Rect(x + 18, chart_y + 48, plotw, ploth)
    chart_bottom = plot.bottom + (65 if naturalw > plotw else 43)
    message = 'Complete. Prefix codes are listed below.' if app.algorithm == 'Huffman coding' and app.position == len(app.frames) - 1 else frame.message
    message_y = chart_bottom + 22
    message_lines = split_lines(app, message, cw, 16)
    about_y = message_y + 28 + len(message_lines) * 24 + 24
    time, space, description = INFO[app.algorithm]
    descw = cw * .63 if cw >= 800 else cw
    desc_lines = split_lines(app, description, descw, 15)
    about_end = about_y + 42 + len(desc_lines) * 23 + (28 if cw >= 800 else 95)
    if app.algorithm == 'Huffman coding' and app.position == len(app.frames) - 1:
        about_end += 50 + len(split_lines(app, frame.message, cw, 14)) * 22
    return dict(x=x, cw=cw, small=small, title_size=title_size, title_lines=title_lines,
                tabs=tabs, eyebrow_y=eyebrow_y, selector=selector, metrics_y=metrics_y,
                chart_y=chart_y, plot=plot, naturalw=int(naturalw), chart_bottom=chart_bottom,
                message_y=message_y, message_lines=message_lines, input_y=input_y,
                input_x=input_x, input_cw=input_cw, field=field, actions=action_rects,
                input_end=input_end, about_y=about_y, about_end=about_end,
                descw=descw, desc_lines=desc_lines, viewport_h=viewport_h,
                footer_h=footer_h, content_h=about_end + 35)


def open_menu(app):
    app.menu_open = not app.menu_open
    app.menu_scroll = 0
    app.focus = None


def draw(app):
    width, height = app.window.get_size()
    if app.surface.get_size() != (width, height):
        app.surface = pygame.Surface((width, height))
    screen = app.surface
    screen.fill(BG)
    g = layout(app, width, height)
    app.layout = g
    app.viewport_height = g['viewport_h']
    app.content_height = g['content_h']
    app.scroll_max = max(0, g['content_h'] - g['viewport_h'])
    app.scroll = max(0, min(app.scroll_max, app.scroll))
    app.input_top = g['input_y']
    docsize = (width, max(g['content_h'], g['viewport_h']))
    if not hasattr(app, 'document') or app.document.get_size() != docsize:
        app.document = pygame.Surface(docsize)
    app.document.fill(BG)
    app.surface = app.document
    app.hits = []
    actual_mouse = app.mouse
    app.mouse = (actual_mouse[0], actual_mouse[1] + app.scroll)
    x, cw = g['x'], g['cw']
    frame = app.frames[app.position]
    finished = app.position == len(app.frames) - 1
    graph = app.algorithm in GRAPHS
    text = app.text
    rule = lambda y: pygame.draw.line(app.surface, LINE, (x, y), (x + cw, y))

    for dx, dy, color in [(0, 0, INK), (11, 0, BLUE), (0, 11, BLUE), (11, 11, GREEN)]:
        pygame.draw.rect(app.surface, color, (x + dx, 24 + dy, 8, 8), border_radius=1)
    for i, title_line in enumerate(g['title_lines']):
        text(title_line, x + 34, 22 + i * (g['title_size'] + 8), g['title_size'], INK, True)
    for section, rect in g['tabs']:
        selected = section == app.section
        app.panel(rect, INK if selected else '#EAF3F8' if rect.collidepoint(app.mouse) else BG, INK if selected else LINE, 3)
        size = 14
        while size > 10 and app.font(size, bold=selected).size(section)[0] > rect.w - 12: size -= 1
        text(section, *rect.center, size, '#FFFFFF' if selected else MUTED, selected, center=True)
        app.hits.append((rect, lambda name=section: app.choose_section(name)))
    rule(g['tabs'][-1][1].bottom + 12)
    text('Choose an algorithm' if app.section == 'Algorithms' else 'Choose a data structure', x, g['eyebrow_y'], 14, INK, True)
    selector_size = 17
    while selector_size > 12 and app.font(selector_size).size(app.algorithm)[0] > g['selector'].w - 50: selector_size -= 1
    app.button(g['selector'], app.algorithm, lambda: open_menu(app), size=selector_size)
    text('v', g['selector'].right - 22, g['selector'].y + 14, 13, MUTED)
    my = g['metrics_y']
    metrics = [(frame.comparisons, 'comparisons'), (frame.writes, 'writes')] if app.algorithm in SORTS + SEARCHES else [(len(frame.nodes) or len(frame.values), 'values'), (len(frame.visited) if graph else len(frame.edges), 'visited' if graph else 'links')]
    for i, (value, label) in enumerate(metrics):
        xx = x + i * (155 if cw > 440 else 134)
        text(str(value), xx, my - 4, 22, INK, bold=True)
        text(label, xx + app.font(22, mono=True).size(str(value))[0] + 10, my + 4, 13, MUTED)
    if cw > 500:
        text(f'Step {app.position + 1} of {len(app.frames)}', x + cw - 145, my + 4, 13, MUTED)

    # The plotting area has its own horizontal viewport for dense input.
    app.panel((x, g['chart_y'], cw, g['chart_bottom'] - g['chart_y']), PANEL, '#A9C6D6', 3)
    pygame.draw.line(app.surface, '#C4DCE8', (x + 1, g['chart_y'] + 39), (x + cw - 2, g['chart_y'] + 39))
    text('Graph' if graph else 'Structure' if app.algorithm in STRUCTURES else 'Prefix tree' if app.category == 'Compression' else 'Values', x + 18, g['chart_y'] + 15, 13, INK, True)
    status = 'Complete' if finished else 'Playing' if app.playing else 'Ready' if not app.position else 'Paused'
    pygame.draw.circle(app.surface, GREEN if finished else ACCENT if app.playing else BLUE, (x + cw - 95, g['chart_y'] + 22), 3)
    text(status, x + cw - 84, g['chart_y'] + 15, 12, GREEN if finished else MUTED, True)
    plot = g['plot']
    psize = (g['naturalw'], plot.h)
    if not hasattr(app, 'plot_surface') or app.plot_surface.get_size() != psize:
        app.plot_surface = pygame.Surface(psize)
    app.plot_surface.fill(PANEL)
    for gy in range(28, psize[1], 38):
        pygame.draw.line(app.plot_surface, '#E1EEF5', (0, gy), (psize[0], gy))
    app.surface = app.plot_surface
    inner = (12, 12, psize[0] - 24, psize[1] - 24)
    if app.algorithm in SORTS + SEARCHES:
        app.draw_bars(frame, inner)
    elif app.algorithm in STRUCTURES:
        if not frame.nodes and not frame.values:
            text('Press Start to build the structure.', psize[0] / 2, psize[1] / 2, 17, MUTED, center=True)
        else: app.draw_structure(frame, inner)
    else: app.draw_tree(frame, inner, graph)
    app.surface = app.document
    app.pan_max = max(0, psize[0] - plot.w)
    marker = (id(app.frames), app.position)
    if getattr(app, 'last_plot_marker', None) != marker and app.algorithm in SORTS + SEARCHES and frame.active and app.pan_max:
        step = (psize[0] - 24) / max(1, len(frame.values))
        left = 12 + min(frame.active) * step
        right = 12 + (max(frame.active) + 1) * step
        if right > app.pan + plot.w: app.pan = right - plot.w + 12
        if left < app.pan: app.pan = left - 12
    app.last_plot_marker = marker
    app.pan = max(0, min(app.pan_max, app.pan))
    app.document.blit(app.plot_surface, plot.topleft, pygame.Rect(int(app.pan), 0, plot.w, plot.h))
    pan_y = plot.bottom + 11
    app.pan_track = pygame.Rect(plot.x, pan_y - int(app.scroll), plot.w, 5) if app.pan_max else pygame.Rect(0, -100, 0, 0)
    if app.pan_max:
        pygame.draw.rect(app.surface, '#C9DFEB', (plot.x, pan_y, plot.w, 4), border_radius=2)
        handlew = max(30, plot.w * plot.w / psize[0])
        handlex = plot.x + app.pan / app.pan_max * (plot.w - handlew)
        pygame.draw.rect(app.surface, '#6999B3', (handlex, pan_y - 2, handlew, 8), border_radius=3)
    legend_y = g['chart_bottom'] - 25
    for i, (label, color) in enumerate([('Values', BAR), ('Active', ACCENT), ('Settled' if not graph else 'Visited', GREEN)]):
        xx = x + 20 + i * (110 if cw > 400 else 88)
        pygame.draw.circle(app.surface, color, (xx, legend_y + 8), 3)
        text(label, xx + 9, legend_y, 11, MUTED)
    text('CURRENT MOVE', x, g['message_y'], 11, MUTED, bold=True)
    for i, message_line in enumerate(g['message_lines']):
        text(message_line, x, g['message_y'] + 25 + i * 24, 16, INK)

    text('Input values' if not graph else 'Sample graph', g['input_x'], g['input_y'], 14, INK, True)
    if graph:
        app.wrapped('7 vertices · 9 weighted edges · Undirected · Start at A', g['input_x'], g['input_y'] + 29, g['input_cw'], 14, MUTED, 21)
    else:
        app.field(g['field'], 'input', app.input)
        for name, rect in g['actions']:
            if name == 'target':
                text('Target', rect.x, rect.y + 13, 12, MUTED)
                app.field((rect.x + 46, rect.y, rect.w - 46, rect.h), 'target', app.target)
            elif name == 'Apply': app.button(rect, name, app.rebuild)
            elif name == 'Shuffle': app.button(rect, name, app.randomize)
            elif name == 'order': app.button(rect, 'Descending' if app.descending else 'Ascending', app.toggle_order, size=13)
            elif name == 'remove': app.button(rect, 'Pop' if app.algorithm == 'Stack' else 'Dequeue', app.remove_item, disabled=not finished or not frame.values, size=13)
        if not app.error:
            text('1–24 integers' + (' · positive frequencies' if app.category == 'Compression' else ' · separated by commas or spaces'), g['input_x'], g['input_end'] - 17, 11, MUTED)
    if app.error:
        app.wrapped(app.error, g['input_x'], g['input_end'] - len(split_lines(app, app.error, g['input_cw'], 13)) * 20 - 8, g['input_cw'], 13, '#A43C2C', 20)

    rule(g['about_y'])
    text('How it works', x, g['about_y'] + 18, 17, INK, bold=True)
    for i, desc in enumerate(g['desc_lines']):
        text(desc, x, g['about_y'] + 50 + i * 23, 15, MUTED)
    time, space, _ = INFO[app.algorithm]
    complexity_x = x + g['descw'] + 40 if cw >= 800 else x
    complexity_y = g['about_y'] + 23 if cw >= 800 else g['about_y'] + 58 + len(g['desc_lines']) * 23
    text('Time: ' + time, complexity_x, complexity_y, 13, INK, mono=True)
    text('Space: ' + space, complexity_x, complexity_y + 25, 13, INK, mono=True)
    if app.algorithm == 'Huffman coding' and finished:
        app.wrapped(frame.message, x, g['about_end'] - len(split_lines(app, frame.message, cw, 14)) * 22 - 15, cw, 14, INK, 22)

    # Translate only the visible document controls into screen coordinates.
    viewport = pygame.Rect(0, 0, width, g['viewport_h'])
    screen.blit(app.document, (0, 0), pygame.Rect(0, int(app.scroll), width, g['viewport_h']))
    app.hits = [(r.move(0, -int(app.scroll)).clip(viewport), action) for r, action in app.hits if r.move(0, -int(app.scroll)).colliderect(viewport)]
    app.surface = screen
    app.mouse = actual_mouse
    app.page_track = pygame.Rect(width - 10, 0, 10, g['viewport_h'])
    if app.scroll_max:
        thumbh = max(30, g['viewport_h'] ** 2 / g['content_h'])
        thumby = app.scroll / app.scroll_max * (g['viewport_h'] - thumbh)
        pygame.draw.rect(screen, '#9DBBCB', (width - 6, thumby, 4, thumbh), border_radius=2)
    footer(app, g, width, height)
    if app.menu_open: menu(app, g, width, height)


def footer(app, g, width, height):
    top = g['viewport_h']
    pygame.draw.rect(app.surface, BG, (0, top, width, height - top))
    pygame.draw.line(app.surface, LINE, (0, top), (width, top))
    x, cw = g['x'], g['cw']
    app.timeline = pygame.Rect(x, top + 14, cw, 4)
    progress = app.position / max(1, len(app.frames) - 1)
    pygame.draw.rect(app.surface, '#D2E2EB', app.timeline, border_radius=2)
    pygame.draw.rect(app.surface, GREEN, (x, top + 14, max(1, cw * progress), 4), border_radius=2)
    pygame.draw.circle(app.surface, GREEN, (x + cw * progress, top + 16), 5)
    app.hits.append((app.timeline.inflate(12, 20), app.scrub))
    compact = cw < 600
    y = top + 33
    actions = [('Reset', 62, lambda: app.advance(-len(app.frames)), False, False),
               ('Prev' if compact else 'Previous', 48 if compact else 80, lambda: app.advance(-1), False, app.position == 0),
               ('Pause' if app.playing else 'Replay' if app.position == len(app.frames) - 1 else 'Start' if not app.position else 'Play', 82 if compact else 102, app.toggle_play, True, False),
               ('Next', 48 if compact else 62, lambda: app.advance(1), False, app.position == len(app.frames) - 1)]
    bx = x
    scale = min(1, (cw - 21) / sum(item[1] for item in actions))
    for label, bw, action, primary, disabled in actions:
        bw = int(bw * scale)
        app.button((bx, y, bw, 38), label, action, primary=primary, disabled=disabled, size=13)
        bx += bw + 7
    sx, sy = (bx + 24, y + 3) if cw >= 900 else (x, top + 83)
    app.text('Speed', sx, sy + 8, 12, MUTED)
    app.button((sx + 48, sy, 30, 32), '−', lambda: setattr(app, 'speed', max(1, app.speed - 1)))
    app.text(f'{app.speed}×', sx + 101, sy + 16, 13, INK, True, center=True)
    app.button((sx + 126, sy, 30, 32), '+', lambda: setattr(app, 'speed', min(10, app.speed + 1)))

def menu(app, g, width, height):
    anchor = g['selector'].move(0, -int(app.scroll))
    entries = app.menu_entries()
    row_heights = [28 if name is None else 42 for name, _ in entries]
    rows_height = sum(row_heights)
    mw = min(360, width - 24)
    mh = min(rows_height + 62, max(120, g['viewport_h'] - 24))
    mx = max(12, min(width - mw - 12, anchor.x))
    my = max(12, min(g['viewport_h'] - mh - 12, anchor.bottom + 6))
    app.menu_rect = pygame.Rect(mx, my, mw, mh)
    shade = pygame.Surface((width, height), pygame.SRCALPHA)
    shade.fill((32, 44, 32, 35))
    app.surface.blit(shade, (0, 0))
    app.panel(app.menu_rect, BG, '#9CB8C9', 3)
    app.hits = []
    app.text(app.section, mx + 16, my + 15, 15, INK, True)
    app.button((mx + mw - 47, my + 9, 34, 32), '×', lambda: setattr(app, 'menu_open', False), size=18)
    listh = mh - 62
    if rows_height > listh: listh -= 20
    listrect = pygame.Rect(mx + 8, my + 54, mw - 16, listh)
    max_scroll = max(0, rows_height - listrect.h)
    app.menu_scroll = max(0, min(max_scroll, app.menu_scroll))
    app.surface.set_clip(listrect)
    row_y = listrect.y - app.menu_scroll
    for (name, category), row_height in zip(entries, row_heights):
        rect = pygame.Rect(listrect.x, row_y, listrect.w, row_height - 3)
        row_y += row_height
        if not rect.colliderect(listrect): continue
        if name is None:
            app.text(category, rect.x + 12, rect.y + 7, 11, MUTED, True)
            continue
        selected = name == app.algorithm
        if selected or rect.collidepoint(app.mouse):
            app.panel(rect, '#E3F0F8', None, 3)
        app.text(name, rect.x + 12, rect.y + 10, 14, GREEN if selected else INK, selected)
        app.hits.append((rect.clip(listrect), lambda n=name, c=category: app.choose_algorithm(n, c)))
    app.surface.set_clip(None)
    if max_scroll:
        app.text('Scroll for more', mx + 17, my + mh - 17, 10, MUTED)
