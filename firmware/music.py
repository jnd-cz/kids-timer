"""Note frequencies and short, monophonic children's melodies.

Events are (MIDI pitch, eighth-note units); 0 means a rest. Songs are
traditional or public-domain tunes; arrangements below are intentionally simple.
"""

NOTE_NAMES = ('C', 'C', 'd', 'd', 'E', 'F', 'F', 'G', 'G', 'A', 'A', 'b')
SHARPS = (False, True, False, True, False, False, True, False, True, False, True, False)


def frequency(midi):
    return int(440 * (2 ** ((midi - 69) / 12)) + 0.5)


def note_label(midi):
    return NOTE_NAMES[midi % 12] + str(midi // 12 - 1), SHARPS[midi % 12]


def events(pitches, units):
    if len(pitches) != len(units):
        raise ValueError("mismatched melody notes and durations")
    return tuple(zip(pitches, units))


SONGS = (
    # Czech folk transcriptions: https://badatelska.pisnovna.cz/pisen/An.EOR3-0003/anonym-skakal-pes-pres-oves
    ('Skakal pes', 220, events((67,67,64,67,67,64,67,67,69,64,67,65,65,65,62,62,65,65,64,65,65,67,62,65,64),
                              (1,1,2,1,1,2,1,1,1,1,2,2,1,1,1,1,1,1,2,1,1,1,1,2,2))),
    # https://badatelska.pisnovna.cz/pisen/Hol.R_VII-0034/holas-cenek-prsi-prsi-jen-se-lije
    ('Prsi prsi', 220, events((74,74,71,71,76,76,74,74,72,72,71,71,69,69,67,67,74,74,71,71,76,76,74,72,72,71,71,69,69,67),
                             (1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,2,1,1,1,1,1,1,2))),
    ('Twinkle Twinkle', 260, events((60,60,67,67,69,69,67,65,65,64,64,62,62,60,67,67,65,65,64,64,62,67,67,65,65,64,64,62,60,60,67,67,69,69,67,65,65,64,64,62,62,60),
                                    (2,2,2,2,2,2,4,2,2,2,2,2,2,4,2,2,2,2,2,2,4,2,2,2,2,2,2,4,2,2,2,2,2,2,4,2,2,2,2,2,2,4))),
    ('Frere Jacques', 240, events((60,62,64,60,60,62,64,60,64,65,67,64,65,67,67,69,67,65,64,60,67,69,67,65,64,60,60,55,60,60,55,60),
                                  (2,2,2,2,2,2,2,2,2,2,4,2,2,4,1,1,1,1,2,2,1,1,1,1,2,2,2,2,4,2,2,4))),
    ('Mary Had a Little Lamb', 240, events((64,62,60,62,64,64,64,62,62,62,64,67,67,64,62,60,62,64,64,64,64,62,62,64,62,60),
                                          (2,2,2,2,2,2,4,2,2,4,2,2,4,2,2,2,2,2,2,2,2,2,2,2,2,4))),
    ('London Bridge', 240, events((67,69,67,65,64,65,67,62,64,65,64,65,67,67,69,67,65,64,65,67,62,67,64,60),
                                  (2,2,2,2,2,2,4,2,2,4,2,2,4,2,2,2,2,2,2,4,4,4,4,4))),
    ('Old MacDonald', 220, events((60,60,60,55,57,57,55,64,64,62,62,60,55,60,60,60,55,57,57,55,64,64,62,62,60),
                                  (2,2,2,2,2,2,4,2,2,2,2,4,4,2,2,2,2,2,2,4,2,2,2,2,4))),
    ('Row Row Row Your Boat', 250, events((60,60,60,62,64,64,62,64,65,67,72,72,72,67,67,67,64,64,64,60,60,60,67,65,64,62,60),
                                         (4,4,3,1,4,3,1,3,1,8,1,1,2,1,1,2,1,1,2,1,1,2,3,1,3,1,8))),
    ('Ode to Joy', 240, events((64,64,65,67,67,65,64,62,60,60,62,64,64,62,62,64,64,65,67,67,65,64,62,60,60,62,64,62,60,60),
                               (2,2,2,2,2,2,2,2,2,2,2,2,3,1,4,2,2,2,2,2,2,2,2,2,2,2,2,3,1,4))),
    ('Happy Birthday', 250, events((55,55,57,55,60,59,55,55,57,55,62,60,55,55,67,64,60,59,57,65,65,64,60,62,60),
                                   (1,1,4,4,4,8,1,1,4,4,4,8,1,1,4,4,4,4,8,1,1,4,4,4,8))),
    ('Bingo', 220, events((60,65,65,65,65,64,62,62,62,62,60,60,60,60,60,62,64,65,65,65,65,64,62,62,62,62,60),
                          (2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,4,2,2,2,2,2,2,2,2,4))),
    ('Jingle Bells', 220, events((64,64,64,64,64,64,64,67,60,62,64,65,65,65,65,65,64,64,64,64,62,62,64,62,67),
                                 (2,2,4,2,2,4,2,2,3,1,8,2,2,3,1,2,2,2,1,1,2,2,2,4,4))),
)


class Player:
    def __init__(self, audio, ticks_add, ticks_diff):
        self.audio = audio
        self.ticks_add = ticks_add
        self.ticks_diff = ticks_diff
        self.playing = False
        self.index = 0
        self.next_at = 0

    def start(self, song, now, volume):
        self.stop()
        self.song = song
        self.volume = volume
        self.index = 0
        self.next_at = now
        self.playing = True
        self.update(now)

    def update(self, now):
        if not self.playing or self.ticks_diff(now, self.next_at) < 0:
            return
        _, unit_ms, tune = SONGS[self.song]
        if self.index >= len(tune):
            self.stop()
            return
        pitch, units = tune[self.index]
        self.index += 1
        length = unit_ms * units
        if pitch:
            self.audio.beep(now, frequency(pitch), max(1, length * 85 // 100), self.volume)
        else:
            self.audio.stop()
        self.next_at = self.ticks_add(now, length)

    def stop(self):
        if self.playing:
            self.audio.stop()
        self.playing = False
