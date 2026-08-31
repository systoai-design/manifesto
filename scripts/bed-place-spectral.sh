#!/usr/bin/env bash
# Build the film's music bed from the raw track.
#
# The bed is placed SPECTRALLY, not by level. manifesto.mp3 has a 17.5 dB tilt
# toward bass, so simply turning it down leaves audible rumble and no air --
# which is what "muffled" was. Instead: clear the sub, carve the band the voice
# actually occupies, restore the top end the level drop kills, and only then
# duck, gently.
#
# The duck is 1.5:1 at a high threshold on purpose. An earlier 9:1 pulled 13.4 dB
# under speech, which is why the music sounded like it stopped every time Bella
# opened her mouth. This pulls 3.9 dB at her loudest and 0.1 dB in the gaps.
#
# usage: build-music.sh <track.mp3> <vo.wav> <out.wav> <cut> <resume> <total> [gain]
set -euo pipefail

TRACK=$1; VO=$2; OUT=$3; CUT=$4; RESUME=$5; TOTAL=$6; GAIN=${7:-0.30}

# Measured, not guessed. A Welch PSD of the track against the voiced frames of
# the read: the music peaks at 96.7 Hz and carries 82.9% of its energy below
# 250 Hz with only 5.0% above 1 kHz; the voice peaks at 216.8 Hz. The fight is
# in 120-250 Hz, where the music has 22.4% and the voice has 48.8%.
#
# An earlier pass notched 420 Hz, which is ABOVE the collision -- it moved the
# music's energy share in the fight band UP from 22.4% to 30.7%.
#
# 70 Hz   - the sub is inaudible at bed level and only eats headroom.
# 200 Hz  - shelf, -9. Takes the bottom two octaves down as a block; this is the
#           single biggest win and it costs the voice nothing.
# 215 Hz  - bell, -6, Q 1.2. Sits exactly on the voice's own peak.
# 1.4 kHz - second formant, gentle.
# 5 kHz   - shelf ABOVE the intelligibility band, so it restores the air that
#           the level drop killed without stacking onto sibilance.
#
# Result: below-250 falls 82.9% -> 39.5%, the collision band 22.4% -> 12.4%,
# and above-1k rises 5.0% -> 32.0%. The bed gets brighter and gets OUT of the
# way at the same time, which is what leaves the duck almost nothing to do.
SHAPE="highpass=f=70,lowshelf=f=200:g=-9,equalizer=f=215:t=q:w=1.2:g=-6,equalizer=f=1400:t=q:w=1.4:g=-2,treble=g=4:f=5000,volume=${GAIN}"

FADEOUT=$(python -c "print(max(0.1, $TOTAL - $RESUME - 4.5))")

ffmpeg -y -v error -i "$TRACK" -i "$VO" -filter_complex "
[0:a]atrim=0:${CUT},asetpts=PTS-STARTPTS,${SHAPE},
     afade=t=in:st=0:d=2.5,apad=pad_dur=1.8,
     aecho=0.8:0.88:380|760:0.42|0.26[a];
[0:a]atrim=${RESUME}:${TOTAL},asetpts=PTS-STARTPTS,${SHAPE},
     afade=t=in:st=0:d=1.2,afade=t=out:st=${FADEOUT}:d=4.5,
     adelay=$(python -c "print(int($RESUME*1000))")|$(python -c "print(int($RESUME*1000))")[b];
[a][b]amix=inputs=2:normalize=0:duration=longest[bed];
[bed][1:a]sidechaincompress=threshold=0.09:ratio=1.5:attack=40:release=900:knee=8[duck];
[duck]apad=whole_dur=${TOTAL},atrim=0:${TOTAL}[out]
" -map "[out]" -ar 48000 -ac 2 "$OUT"

echo "bed -> $OUT"
ffmpeg -v info -i "$OUT" -af ebur128 -f null - 2>&1 | grep -A4 "Integrated loudness" | grep "I:" | tail -1
