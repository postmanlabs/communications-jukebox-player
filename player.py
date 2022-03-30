import requests
import pygame
import time
from os import listdir
from os.path import isdir, isfile, join

# number of seconds to wait for each segment
song_segment_length = 3

# voting app hostname
voting_app_hostname = 'https://infobip-jukebox.herokuapp.com'

def play_music(filename):
    print(f'playing {filename}')
    pygame.mixer.music.load(filename)
    pygame.mixer.music.play()


def stop_music():
    pygame.mixer.music.stop()


def init_music_mixer():
    audio_frequency = 44100 # going lower than 22k will make the audio quality poor
    audio_bit_size = -16  # keep this at -16
    audio_channels = 2  # 1=mono, 2=stereo
    audio_buffer = 512  # good as a start, can increase if your system is laggy

    # there's a known bug/issue in PyGame where you have to set up the mixer
    # then initialize the whole game engine and then re-initialize the audio mixer
    # but in some circumstances that are not well-documented, you have to 'quit'
    # the mixer and initialize AGAIN to set everything properly
    pygame.mixer.pre_init(audio_frequency, audio_bit_size, audio_channels, audio_buffer)
    pygame.init()
    pygame.mixer.init(audio_frequency, audio_bit_size, audio_channels, audio_buffer)
    pygame.mixer.quit()
    pygame.mixer.init(audio_frequency, audio_bit_size, audio_channels, audio_buffer)


# keeps track of which 3-second segment we're on
time_marker = 0
# used for our 'easter egg' later
old_time_marker = 0
# track whether we've already started the easter egg or not
first_time_override = True

try:
    init_music_mixer()
    # we'll start by playing our radio-tuning audio until people start voting

    song_path = 'songs/'
    genres = ['.extra']
    eras = []

    songs = {}
    special_music = ['radio', '.extra']
    for dir in special_music:
        songs[dir] = {}
        files = sorted([f for f in listdir(f'songs/{dir}') if isfile(join(f'songs/{dir}', f))])
        last_file = files[-1]
        last_segment = int(last_file.split('-')[-1].split('.')[0])
        songs[dir] = {
            'filename': f'songs/{dir}/song.mp3',
            'last_segment': last_segment
        }

    file = f"{songs['radio']['filename']}-{songs['radio']['last_segment']:03}.mp3"
    play_music(file)

    dirs = [join(song_path, o) for o in listdir(song_path) if isdir(join(song_path, o))]
    for orig_dir in dirs:
        if 'genre' in orig_dir:
            genre = orig_dir.split('genre-')[-1]
            genres.append(genre)
            songs[genre] = {}
            era_list = [join(orig_dir, o) for o in listdir(orig_dir) if isdir(join(orig_dir, o))]
            for era in era_list:
                era = era.split('era-')[-1]
                files = sorted([f for f in listdir(f'songs/genre-{genre}/era-{era}') if isfile(join(
                    f'songs/genre-{genre}/era-{era}', f))])
                last_file = files[-1]
                last_segment = int(last_file.split('-')[-1].split('.')[0])
                songs[genre][era] = {
                    'filename': f'songs/genre-{genre}/era-{era}/song.mp3',
                    'last_segment': last_segment
                }
                if era not in eras:
                    eras.append(era)
    # print(eras)
    # print(genres)
    print(songs)

    res = requests.post(f'{voting_app_hostname}/init', json={
        "eras": eras,
        "genres": genres
    })
    print(res)

    res = requests.get(f'{voting_app_hostname}/reset')
    fetch_winner = True
    play_new_music = True

    while True:
        # print('getting start time')
        start_time = round(time.time() * 1000)
        # print('getting current winner')
        file = ''
        if fetch_winner:
            res = requests.get(f'{voting_app_hostname}/current-winner')
            winner = res.json()['winner']
            print('winner:', winner)

            if '-' in winner:
                genre, era = winner.split('-')
                file = f'{songs[genre][era]["filename"]}-{time_marker:03}.mp3'
                if time_marker > songs[genre][era]['last_segment']:
                    tmp_segment = time_marker % songs[genre][era]['last_segment']
                    file = f'{songs[genre][era]["filename"]}-{tmp_segment:03}.mp3'
            else:
                if winner == 'radio':
                    if time_marker > songs['radio']['last_segment']:
                        time_marker = 0
                    file = f'{songs[winner]["filename"]}-{time_marker:03}.mp3'

                elif winner == '.extra':
                    time_marker = 0
                    file = songs[winner]['filename']
                    play_music(file)
                    play_new_music = False
                    fetch_winner = False

        print(file)
        # queue up the next file segment to play
        if play_new_music:
            play_music(file)
            end_time = round(time.time() * 1000)

            # this tweak value was an attempt to get rid of the very tiny
            # audio delay between mp3 tracks
            tweak = 2 # milliseconds

            sleep_time = ((song_segment_length*1000) - (end_time - start_time) - tweak)/1000
            # sleep between instructions so the 3-second sound segment can finish playing
            # before we queue up another portion of music
            if sleep_time > 0:
                # print('sleeping')
                time.sleep(sleep_time)
                # print('awake')
            # print(round(time.time() * 1000))

            # increment our time marker for tracking the next 3-second segment
            # to queue up to play next time through the loop
            time_marker += 1
            print('time_marker:', time_marker)

except KeyboardInterrupt:
    # you can terminate the script at any time with CTRL-C in the terminal
    stop_music()
    print("\nPlay Stopped by user")

except Exception as e:
    # any other error condition will terminate the playing of music
    print("unknown error")
    print(e)

