"""Capture real application screens and playback for the README.

Run from the repository with pygame-ce and Pillow installed:
    python scripts/capture_readme.py
"""
import os
from pathlib import Path
import sys

os.environ.setdefault('SDL_VIDEODRIVER', 'dummy')
os.environ.setdefault('SDL_AUDIODRIVER', 'dummy')
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import pygame
from PIL import Image
from studio.app import Studio


def capture():
    destination = ROOT / 'docs' / 'images'
    destination.mkdir(parents=True, exist_ok=True)
    app = Studio((1280, 960))
    frames, durations = [], []

    def draw():
        app.draw()
        return Image.frombytes('RGB', app.surface.get_size(), pygame.image.tobytes(app.surface, 'RGB'))

    def record(duration):
        frames.append(draw().quantize(colors=128, method=Image.Quantize.MEDIANCUT))
        durations.append(duration)

    try:
        # Each PNG is a native application render, including real trace state.
        app.advance(2)
        draw().save(destination / 'algorithms.png')
        app.choose_section('Data Structures')
        app.choose_algorithm('AVL tree')
        app.advance(len(app.frames) - 2)
        draw().save(destination / 'data-structures.png')

        # Bubble-sort playback, followed by stack construction and a pop.
        app.choose_section('Algorithms')
        app.input = '64, 34, 25, 12, 22, 11, 48, 18'
        app.choose_algorithm('Bubble sort')
        record(1000)
        app.toggle_play()
        for position in range(1, len(app.frames)):
            app.position = position
            app.playing = position < len(app.frames) - 1
            record(140 if app.playing else 1400)

        app.choose_section('Data Structures')
        app.choose_algorithm('Stack')
        record(900)
        app.toggle_play()
        for position in range(1, len(app.frames)):
            app.position = position
            app.playing = position < len(app.frames) - 1
            record(350 if app.playing else 1000)
        app.remove_item()
        record(1000)

        output = destination / 'demo.gif'
        frames[0].save(output, save_all=True, append_images=frames[1:], duration=durations,
                       loop=0, optimize=True, disposal=2)
        with Image.open(output) as animation:
            assert animation.size == (1280, 960)
            assert animation.n_frames > 1
            assert animation.info['loop'] == 0
            total_duration = 0
            for i in range(animation.n_frames):
                animation.seek(i)
                animation.load()
                total_duration += animation.info['duration']
            assert total_duration == sum(durations)
            print(f'Created {animation.n_frames} GIF frames ({total_duration / 1000:.1f}s, {output.stat().st_size / 1024 / 1024:.2f} MB).')
        print(f'Screenshots and GIF saved to {destination}')
    finally:
        pygame.quit()


if __name__ == '__main__':
    capture()
