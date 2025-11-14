#!/usr/bin/env python3

# prerequisites: as described in https://alphacephei.com/vosk/install and also python module `sounddevice` (simply run command `pip install sounddevice`)
# Example usage using Dutch (nl) recognition model: `python test_microphone.py -m nl`
# For more help run: `python test_microphone.py -h`

import argparse
import queue
import sys
import sounddevice as sd
sd.default.device = 5,0
from vosk import Model, KaldiRecognizer

import time
import json
from rapidfuzz import process
from tts import tts
import pygame
from pyvidplayer2 import Video
#from audioplayer import AudioPlayer

q = queue.Queue()

def load_commands(filename = "commands.json"):
    with open(filename, "r") as f:
        return json.load(f)

def get_response(input, commands):
    choices = list(commands.keys())
    match, score, _ = process.extractOne(input.lower(), choices)

    if score > 80:
        return commands[match]
    else:
        return "Command not found"

def parseResponse(key):
    if key[0] == 'm':
        print()
    if key[0] == 'v':
        print()
    if key[0] == 'c':
        print()

def int_or_str(text):
    """Helper function for argument parsing."""
    try:
        return int(text)
    except ValueError:
        return text


def callback(indata, frames, time, status):
    """This is called (from a separate thread) for each audio block."""
    if status:
        print(status, file=sys.stderr)
    q.put(bytes(indata))

def listen(Data, Rec):
    if Rec.AcceptWaveform(Data):
        print("It worked")
        #print(Rec.Result())
    else:
        print("this also worked")
        return 0

parser = argparse.ArgumentParser(add_help=False)
parser.add_argument(
    "-l", "--list-devices", action="store_true",
    help="show list of audio devices and exit")
args, remaining = parser.parse_known_args()
if args.list_devices:
    print(sd.query_devices())
    parser.exit(0)
parser = argparse.ArgumentParser(
    description=__doc__,
    formatter_class=argparse.RawDescriptionHelpFormatter,
    parents=[parser])
parser.add_argument(
    "-f", "--filename", type=str, metavar="FILENAME",
    help="audio file to store recording to")
parser.add_argument(
    "-d", "--device", type=int_or_str,
    help="input device (numeric ID or substring)")
parser.add_argument(
    "-r", "--samplerate", type=int, help="sampling rate")
parser.add_argument(
    "-m", "--model", type=str, help="language model; e.g. en-us, fr, nl; default is en-us")
args = parser.parse_args(remaining)

commands = load_commands()

try:
    if args.samplerate is None:
        device_info = sd.query_devices(args.device, "input")
        # soundfile expects an int, sounddevice provides a float:
        args.samplerate = int(device_info["default_samplerate"])

    if args.model is None:
        model = Model(lang="en-us")
    else:
        model = Model(lang=args.model)

    if args.filename:
        dump_fn = open(args.filename, "wb")
    else:
        dump_fn = None

    with sd.RawInputStream(samplerate=args.samplerate, blocksize=8000, device=args.device,
                           dtype="int16", channels=1, callback=callback):
        print("#" * 80)
        print("Press Ctrl+C to stop the recording")
        print("#" * 80)

        rec = KaldiRecognizer(model, args.samplerate)
        while True:
            data = q.get()
            if rec.AcceptWaveform(data):
                words = (rec.Result().split())
                words.remove("{")
                words.remove('"text"')
                words.remove(':')
                words.remove('}')
                print(words)
                for x in range(len(words)):
                    if words[x] == "neptune" or words[x] == 'neptune"'  or words[x] == '"neptune' :
                        #t = Timer(5.0, listen(data,rec))
                        #t.start()
                        t = time.monotonic()
                        q.empty()
                        while True:
                            data = q.get()
                            elapsed_time = time.monotonic() - t
                            if elapsed_time >= 8:
                                break
                            elif(rec.AcceptWaveform(data)):
                                print("something")
                                string = rec.Result()
                                print(string)
                                print(get_response(string, commands))
                                parseResponse(get_response(string, commands))
                                #print(rec.Result())
                                break




            #else:
            #    print(rec.PartialResult())
            if dump_fn is not None:
                dump_fn.write(data)

except KeyboardInterrupt:
    print("\nDone")
    parser.exit(0)
except Exception as e:
    parser.exit(type(e).__name__ + ": " + str(e))