import os
os.environ['SDL_VIDEODRIVER'] = 'dummy'
os.environ['SDL_AUDIODRIVER'] = 'dummy'
import unittest
from unittest.mock import patch
try:
    import pygame
    from studio.app import Studio, initial_window_size
except ImportError:
    pygame = None
from studio.algorithms import CATEGORIES


@unittest.skipIf(pygame is None, 'Install requirements.txt to test the interface')
class InterfaceTests(unittest.TestCase):
    def setUp(self): self.app = Studio()
    def tearDown(self): pygame.quit()

    def test_render_every_trace_start_middle_end(self):
        for category, algorithms in CATEGORIES.items():
            for algorithm in algorithms:
                self.app.choose_algorithm(algorithm, category)
                for position in [0, len(self.app.frames) // 2, len(self.app.frames) - 1]:
                    with self.subTest(algorithm=algorithm, position=position):
                        self.app.position = position; self.app.draw()
                        self.assertTrue(self.app.hits)
                        self.app.present()

    def test_validation_preserves_trace(self):
        original = self.app.frames
        for value in ['', '1,', 'a', '3.5', '10000', ','.join('1' for _ in range(25))]:
            self.app.input = value
            self.assertFalse(self.app.rebuild())
            self.assertIs(self.app.frames, original)
            self.assertTrue(self.app.error)
        self.app.input = '-4, 0, 4, 4'
        self.assertTrue(self.app.rebuild())
        self.assertFalse(self.app.error)

    def test_playback_and_removal(self):
        self.app.draw()
        self.app.mouse = self.app.timeline.midright
        self.app.event(pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1))
        self.assertEqual(self.app.position, len(self.app.frames) - 1)
        self.app.mouse = self.app.timeline.midleft
        self.app.event(pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1))
        self.assertEqual(self.app.position, 0)
        self.app.advance(1); self.assertEqual(self.app.position, 1)
        self.app.advance(-1000); self.assertEqual(self.app.position, 0)
        self.app.toggle_play(); self.assertTrue(self.app.playing)
        self.app.advance(1); self.assertFalse(self.app.playing)
        for algorithm in ['Stack', 'Queue']:
            self.app.input = '1, 2, 3'; self.app.choose_algorithm(algorithm, 'Data structures')
            self.app.advance(1000); self.app.remove_item()
            self.assertEqual(self.app.frames[-1].values, [1, 2] if algorithm == 'Stack' else [2, 3])
            self.app.remove_item(); self.app.remove_item()
            self.assertEqual(self.app.frames[-1].values, [])
            self.app.draw(); self.app.remove_item()

    def test_input_keyboard(self):
        self.app.set_focus('input')
        self.app.event(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_a, mod=pygame.KMOD_CTRL, unicode='a'))
        for char in '8, 2':
            self.app.event(pygame.event.Event(pygame.KEYDOWN, key=ord(char), mod=0, unicode=char))
        self.app.event(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RETURN, mod=0, unicode='\r'))
        self.assertEqual(self.app.frames[0].values, [8, 2])
        self.assertIsNone(self.app.focus)

    def test_native_resolution_and_reflow(self):
        for width, height in [(240, 320), (294, 412), (320, 480), (390, 844), (768, 1024), (1024, 600), (1366, 768), (1920, 1080), (3840, 2160)]:
            self.app.window = pygame.display.set_mode((width, height), pygame.RESIZABLE)
            for category, algorithms in CATEGORIES.items():
                for name in algorithms:
                    with self.subTest(size=(width, height), algorithm=name):
                        self.app.choose_algorithm(name, category)
                        self.app.advance(100000)
                        self.app.draw()
                        self.assertEqual(self.app.surface.get_size(), (width, height))
                        bounds = self.app.surface.get_rect()
                        for rect, _ in self.app.hits:
                            self.assertTrue(bounds.contains(rect), rect)
                        self.assertLessEqual(self.app.layout['plot'].right, width)
                        self.assertGreater(self.app.font(16).get_height(), 12)
                        self.app.scroll = self.app.scroll_max
                        self.app.draw()
                        self.assertLessEqual(self.app.scroll, self.app.scroll_max)

    def test_small_window_scroll_menu_and_pan(self):
        self.app.window = pygame.display.set_mode((320, 480), pygame.RESIZABLE)
        self.app.draw()
        self.assertGreater(self.app.scroll_max, 0)
        self.assertGreater(self.app.pan_max, 0)
        self.app.event(pygame.event.Event(pygame.MOUSEWHEEL, x=0, y=-3))
        self.assertGreater(self.app.scroll, 0)
        self.app.scroll = self.app.scroll_max
        self.app.draw()
        self.assertTrue(any(rect.collidepoint(self.app.timeline.center) for rect, _ in self.app.hits))
        self.app.choose_category('Data structures')
        self.app.menu_open = True
        self.app.draw()
        self.app.event(pygame.event.Event(pygame.MOUSEWHEEL, x=0, y=-100))
        self.app.draw()
        last_rect, action = self.app.hits[-1]
        self.app.event(pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1, pos=last_rect.center))
        self.assertEqual(self.app.algorithm, 'Hash table')
        self.assertFalse(self.app.menu_open)
        self.app.draw()
        self.app.set_focus('input')
        self.app.event(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_ESCAPE, mod=0, unicode=''))
        self.app.event(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_TAB, mod=0, unicode=''))
        self.assertEqual(self.app.focus, 'input')
        self.app.draw()
        field = self.app.layout['field'].move(0, -int(self.app.scroll))
        self.assertGreaterEqual(field.top, 0)
        self.assertLessEqual(field.bottom, self.app.viewport_height)

    def test_screen_detection_and_fullscreen_restore(self):
        for desktop in [(320, 480), (800, 600), (1366, 768), (1920, 1080), (3840, 2160)]:
            width, height = initial_window_size(desktop)
            self.assertLess(width, desktop[0])
            self.assertLess(height, desktop[1])
        with patch('studio.app.pygame.display.get_desktop_sizes', return_value=[(800, 600)]):
            self.app = Studio()
            self.assertEqual(self.app.window.get_size(), initial_window_size((800, 600)))
        original = self.app.window.get_size()
        self.app.draw()
        self.app.event(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_F11, mod=0, unicode=''))
        self.assertTrue(self.app.fullscreen)
        self.app.draw()
        self.app.event(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_F11, mod=0, unicode=''))
        self.assertFalse(self.app.fullscreen)
        self.assertEqual(self.app.window.get_size(), original)

    def test_two_sections_and_silent_start(self):
        self.app.draw()
        self.assertEqual([name for name, _ in self.app.layout['tabs']], ['Algorithms', 'Data Structures'])
        self.assertLess(self.app.layout['field'].bottom, self.app.layout['plot'].top)
        algorithm_names = {name for name, _ in self.app.menu_entries() if name is not None}
        expected = {name for category, names in CATEGORIES.items() if category != 'Data structures' for name in names}
        self.assertEqual(algorithm_names, expected)
        self.app.choose_algorithm('Quick sort')
        self.app.choose_section('Data Structures')
        self.assertEqual(self.app.algorithm, 'Stack')
        self.assertEqual({name for name, _ in self.app.menu_entries()}, set(CATEGORIES['Data structures']))
        self.app.choose_section('Algorithms')
        self.assertEqual(self.app.algorithm, 'Quick sort')
        self.app.toggle_play()
        self.assertTrue(self.app.playing)
        self.assertIsNone(pygame.mixer.get_init())


if __name__ == '__main__': unittest.main()
