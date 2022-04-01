# API-powered Jukebox Player

## setup/prep work

1. Create your folder structure
```bash
  # Important: don't let your genre have a dash in the name, eg "hip-hop" should just be "hiphop"
  $ mkdir songs
  $ cd songs
  $ mkdir .extra radio
  $ for i in rock pop; do 
    mkdir "genre-$i"
    touch "genre-$i/.keep"
    for j in 1980 1990 2000 2010; do 
      mkdir "genre-$i/era-$j"  
      touch "genre-$i/era-$j/.keep"
      done
    done
```

2. Set your song files and split them into 3-second segments

Place your MP3 files into their appropriate folders, including the 'radio' and '.extra' folders, and rename them all to be "song.mp3".

The '3' in the command below will change how many seconds of each song will play. You will need to alter the player.py variable called `song_segment_length` if you change this value so that the player actually plays the correct amount of the file and sleep an appropriate amount of time.
```bash
# this will split each song into 3-second segments
$ brew install ffmpeg
$ find . -name "song.mp3" -exec ffmpeg -i "{}" -f segment -segment_time 3 -c copy "{}-%03d.mp3" \;
```

3. Make a Python 3 Virtual Environment
```bash
$ python3 -m venv venv
$ source venv/bin/activate
$ pip3 install -r requirements.txt
```

## Run the Jukebox Player

Modify the 'hostname' variable in the script, if necessary.

```bash
$ python3 player.py
```

This should immediately start playing the 'radio' sound effect and will loop endlessly until voting starts.


## Notes about songs

1. If you need/want the radio tuner sound, you can grab it from here:
https://www.freesoundslibrary.com/radio-tuning-sound-effect/
2. Don't upload MP3 files to a repo, we don't want copyright issues. Use your own personal library, and the player.py should run everything locally on your system. Be sure to test audio playback at whatever event you are attending.
3. The song lengths don't have to be all the same duration. As the timer counts up every 3 seconds, it will do a check on the duration of the song and if the time marker exceeds the duration it'll start playing that song back over from the beginning using a modulo operator.
4. The '.extra' song is your easter egg. Once you 'override' the vote in the API, it'll play the whole 'song.mp3' file, not its segments. You can use Ctrl-C to stop the Python script from running to stop the song. Once that song runs out the jukebox player *should* remain silent unless someone resets the voting.
