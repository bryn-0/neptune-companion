import subprocess
import signal

# Ignore SIGPIPE to prevent broken pipe error killing the Python process
signal.signal(signal.SIGPIPE, signal.SIG_DFL)

# Send text to Piper via stdin
def tts(text):
    for i in range(0, len(text)):

        # CHANGE PATH IN FINAL VERSION******************
        piper_proc = subprocess.Popen(
            ["piper", "--model", "/home/Bryan/Downloads/en_US-lessac-high.onnx", "--output_raw"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
        )

        # Run aplay process to play Piper's output, with matching audio params
        aplay_proc = subprocess.Popen(
            ["aplay", "-D", "pulse", "-f", "S16_LE", "-r", "22050", "-c", "1"],
            stdin=piper_proc.stdout
        )

        try:
            piper_proc.stdin.write(text[i].encode("utf-8"))
            piper_proc.stdin.close()
        except BrokenPipeError:
            pass  # Ignore broken pipe on write

        # Wait for processes to finish cleanly
        aplay_proc.wait()
        piper_proc.wait()


musket = ["I own a musket for home defense, since that's what the founding fathers intended.",
"Four ruffians break into my house. I shouted, What the devil? ",
"I grab my powdered wig and Kentucky rifle, and blow a golf ball sized hole through the first man, he's dead on the spot. Draw my pistol on the second man, miss him entirely because it's smoothbore and nails the neighbors dog.",
"I have to resort to the cannon mounted at the top of the stairs loaded with grape shot,"," Tally ho lads! The grape shot shreds two men in the blast, the sound and extra shrapnel set off car alarms.",
"Fix bayonet and charge the last terrified rapscallion.", "He bleeds out waiting on the police to arrive since triangular bayonet wounds are impossible to stitch up.","Ah yes,Just as the founding fathers intended"]

tts(musket)