#!/usr/bin/env python3
"""Local push-to-talk dictation.

Hold the hotkey, speak, release. Your speech is transcribed on-device by the
open-source Whisper model (via faster-whisper) and pasted into whichever app
has keyboard focus. No account, no subscription, no audio sent anywhere.

Usage:
    python dictate.py                 # hold right Alt/Option to dictate
    python dictate.py --key f8        # hold F8 instead
    python dictate.py --toggle        # tap to start, tap again to stop
    python dictate.py --model small   # bigger model = better accuracy
"""

import argparse
import queue
import re
import sys
import threading
import time

import numpy as np
import pyperclip
import sounddevice as sd
from pynput import keyboard
from pynput.keyboard import Controller, Key

SAMPLE_RATE = 16000  # Whisper's native sample rate

# Spoken commands applied after transcription, Wispr-style.
SPOKEN_COMMANDS = [
    (r"\s*\bnew line\b[\s.,]*", "\n"),
    (r"\s*\bnew paragraph\b[\s.,]*", "\n\n"),
]

HOTKEY_ALIASES = {
    "right_alt": Key.alt_r,
    "right_option": Key.alt_r,
    "right_ctrl": Key.ctrl_r,
    "right_cmd": Key.cmd_r,
    "right_shift": Key.shift_r,
    "caps_lock": Key.caps_lock,
    **{f"f{n}": getattr(Key, f"f{n}") for n in range(1, 13)},
}


class Recorder:
    """Captures microphone audio between start() and stop()."""

    def __init__(self):
        self._chunks = queue.Queue()
        self._stream = None

    def start(self):
        self._chunks = queue.Queue()
        self._stream = sd.InputStream(
            samplerate=SAMPLE_RATE,
            channels=1,
            dtype="float32",
            callback=lambda data, *_: self._chunks.put(data.copy()),
        )
        self._stream.start()

    def stop(self) -> np.ndarray:
        self._stream.stop()
        self._stream.close()
        self._stream = None
        chunks = []
        while not self._chunks.empty():
            chunks.append(self._chunks.get())
        if not chunks:
            return np.zeros(0, dtype=np.float32)
        return np.concatenate(chunks).flatten()


def clean_text(text: str) -> str:
    text = text.strip()
    for pattern, replacement in SPOKEN_COMMANDS:
        text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
    return text


def paste_text(text: str, kbd: Controller):
    """Insert text into the focused app via clipboard paste, then restore
    whatever was on the clipboard before."""
    try:
        previous = pyperclip.paste()
    except pyperclip.PyperclipException:
        previous = None
    pyperclip.copy(text)
    modifier = Key.cmd if sys.platform == "darwin" else Key.ctrl
    time.sleep(0.05)  # let the clipboard settle
    with kbd.pressed(modifier):
        kbd.press("v")
        kbd.release("v")
    if previous is not None:
        # Restore after the paste has been consumed by the target app.
        threading.Timer(0.6, pyperclip.copy, args=[previous]).start()


def check_macos_permissions():
    """Warn loudly at startup if macOS Accessibility trust is missing —
    without it the simulated Cmd+V never reaches other apps."""
    if sys.platform != "darwin":
        return
    try:
        import ctypes
        import ctypes.util

        appserv = ctypes.cdll.LoadLibrary(
            ctypes.util.find_library("ApplicationServices")
        )
        if appserv.AXIsProcessTrusted():
            return
    except Exception:
        return  # can't check; let macOS report it
    print(
        "\n"
        "*** MISSING PERMISSION: text will NOT paste into other apps. ***\n"
        "Fix: System Settings > Privacy & Security > Accessibility ->\n"
        "     enable your terminal app (add it with '+' if not listed).\n"
        "     Also enable it under Input Monitoring.\n"
        "Then FULLY QUIT the terminal (Cmd+Q), reopen it, and rerun this.\n"
    )


def main():
    parser = argparse.ArgumentParser(description="Local push-to-talk dictation")
    parser.add_argument(
        "--key",
        default="right_alt",
        help="hotkey to hold (default: right_alt). Options: "
        + ", ".join(HOTKEY_ALIASES),
    )
    parser.add_argument(
        "--model",
        default="base.en",
        help="Whisper model size: tiny.en, base.en, small.en, medium, large-v3 "
        "(default: base.en; drop .en for multilingual)",
    )
    parser.add_argument(
        "--toggle",
        action="store_true",
        help="tap the hotkey to start/stop instead of holding it",
    )
    parser.add_argument(
        "--type-instead-of-paste",
        action="store_true",
        help="simulate keystrokes instead of pasting (for apps that block paste)",
    )
    args = parser.parse_args()

    hotkey = HOTKEY_ALIASES.get(args.key.lower())
    if hotkey is None:
        sys.exit(f"Unknown key '{args.key}'. Choose from: {', '.join(HOTKEY_ALIASES)}")

    print(f"Loading Whisper model '{args.model}' (first run downloads it)...")
    from faster_whisper import WhisperModel

    model = WhisperModel(args.model, device="auto", compute_type="auto")

    check_macos_permissions()

    recorder = Recorder()
    kbd = Controller()
    recording = threading.Event()
    lock = threading.Lock()

    def start_recording():
        with lock:
            if recording.is_set():
                return
            recording.set()
            recorder.start()
            print("● recording... ", end="", flush=True)

    def stop_and_transcribe():
        with lock:
            if not recording.is_set():
                return
            recording.clear()
            audio = recorder.stop()
        if audio.size < SAMPLE_RATE * 0.3:  # ignore accidental taps
            print("(too short, ignored)")
            return
        print("transcribing... ", end="", flush=True)
        segments, _ = model.transcribe(audio, vad_filter=True)
        text = clean_text("".join(s.text for s in segments))
        if not text:
            print("(no speech detected)")
            return
        if args.type_instead_of_paste:
            kbd.type(text)
        else:
            paste_text(text, kbd)
        print(f"→ {text}")

    def on_press(key):
        if key != hotkey:
            return
        if args.toggle:
            if recording.is_set():
                threading.Thread(target=stop_and_transcribe).start()
            else:
                start_recording()
        else:
            start_recording()

    def on_release(key):
        if key == hotkey and not args.toggle:
            threading.Thread(target=stop_and_transcribe).start()

    mode = "tap to start/stop" if args.toggle else "hold to talk"
    print(f"Ready. {args.key} = {mode}. Focus any text field and speak. Ctrl+C quits.")
    with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
        try:
            listener.join()
        except KeyboardInterrupt:
            print("\nBye.")


if __name__ == "__main__":
    main()
