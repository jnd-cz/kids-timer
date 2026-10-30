import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'firmware'))
from music import Player, SONGS, frequency, note_label
from timer_core import text_frame


class FakeAudio:
    def __init__(self):
        self.tones = []
        self.stops = 0
    def beep(self, now, hz, duration, volume):
        self.tones.append((now, hz, duration, volume))
    def stop(self):
        self.stops += 1


class MusicTests(unittest.TestCase):
    def test_note_range_and_glyphs(self):
        self.assertEqual(frequency(69), 440)
        self.assertEqual(note_label(48), ('C3', False))
        self.assertEqual(note_label(49), ('C3', True))
        self.assertEqual(note_label(119), ('b8', False))
        for note in range(48, 120):
            label, sharp = note_label(note)
            text_frame(label + '20')
            self.assertGreater(frequency(note), 0)

    def test_song_data(self):
        self.assertEqual(len(SONGS), 12)
        for name, unit, notes in SONGS:
            self.assertGreater(len(notes), 8, name)
            self.assertGreater(unit, 0)
            for note, duration in notes:
                self.assertTrue(note == 0 or 48 <= note <= 119, name)
                self.assertGreater(duration, 0)

    def test_player_timing_stop_and_restart(self):
        audio = FakeAudio()
        player = Player(audio, lambda a, b: a + b, lambda a, b: a - b)
        player.start(0, 100, 20)
        self.assertEqual(len(audio.tones), 1)
        player.update(319)
        self.assertEqual(len(audio.tones), 1)
        player.update(320)
        self.assertEqual(len(audio.tones), 2)
        player.stop()
        player.update(1000)
        self.assertEqual(len(audio.tones), 2)
        player.start(1, 1000, 30)
        self.assertEqual(audio.tones[-1][3], 30)
        for _ in range(100):
            if not player.playing:
                break
            player.update(player.next_at)
        self.assertFalse(player.playing)


if __name__ == '__main__':
    unittest.main()
