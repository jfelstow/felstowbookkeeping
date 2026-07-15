#!/usr/bin/env python3
"""Local push-to-talk dictation.

Hold the hotkey, speak, release. Your speech is transcribed on-device by the
open-source Whisper model (via faster-whisper) and pasted into whichever app
has keyboard focus. No account, no subscription, no audio sent anywhere.

Usage:
    python dictate.py                 # hold fn/globe (macOS) or right Alt
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
from pathlib import Path

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
        if self._stream is not None:
            # A stale stream survived (e.g. the Mac slept mid-recording) —
            # release it before opening a fresh one so the mic isn't wedged.
            self.stop()
        self._chunks = queue.Queue()
        self._stream = sd.InputStream(
            samplerate=SAMPLE_RATE,
            channels=1,
            dtype="float32",
            callback=lambda data, *_: self._chunks.put(data.copy()),
        )
        self._stream.start()

    def stop(self) -> np.ndarray:
        stream, self._stream = self._stream, None
        if stream is not None:
            try:
                stream.stop()
                stream.close()
            except Exception:
                pass  # the device may be gone after sleep; keep the audio
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


def load_custom_words(base_dir: Path):
    """Read the user's personal dictionary.

    vocabulary.txt   — one word/phrase per line; biases the recognizer
                       toward these spellings (names, jargon, brands).
    replacements.txt — lines of the form `wrong => right`; applied to the
                       transcript afterwards to force exact spellings.
    """
    vocab, replacements = [], []
    vocab_file = base_dir / "vocabulary.txt"
    if vocab_file.exists():
        vocab = [
            line.strip()
            for line in vocab_file.read_text().splitlines()
            if line.strip() and not line.lstrip().startswith("#")
        ]
    repl_file = base_dir / "replacements.txt"
    if repl_file.exists():
        for line in repl_file.read_text().splitlines():
            if line.lstrip().startswith("#") or "=>" not in line:
                continue
            wrong, right = line.split("=>", 1)
            if wrong.strip():
                replacements.append((wrong.strip(), right.strip()))
    return vocab, replacements


def apply_replacements(text: str, replacements) -> str:
    for wrong, right in replacements:
        text = re.sub(rf"\b{re.escape(wrong)}\b", right, text, flags=re.IGNORECASE)
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


def listen_fn_key(on_press, on_release, debug=False):
    """macOS-only: watch the fn/globe key via a Quartz event tap. fn never
    arrives as a normal key event, only as a modifier-flags change."""
    import Quartz

    state = {"down": False, "tap": None}

    def callback(_proxy, type_, event, _refcon):
        # macOS disables taps it thinks are slow or during secure input;
        # re-enable instead of going silently deaf.
        if type_ in (
            Quartz.kCGEventTapDisabledByTimeout,
            Quartz.kCGEventTapDisabledByUserInput,
        ):
            Quartz.CGEventTapEnable(state["tap"], True)
            return event
        flags = Quartz.CGEventGetFlags(event)
        down = bool(flags & Quartz.kCGEventFlagMaskSecondaryFn)
        if debug:
            print(f"[keys] flags={flags:#010x} fn {'DOWN' if down else 'up'}")
        if down != state["down"]:
            state["down"] = down
            try:
                (on_press if down else on_release)()
            except Exception as exc:
                # Never let a handler error kill the key listener.
                print(f"(hotkey handler error: {exc})")
        return event

    tap = Quartz.CGEventTapCreate(
        Quartz.kCGSessionEventTap,
        Quartz.kCGHeadInsertEventTap,
        Quartz.kCGEventTapOptionListenOnly,
        Quartz.CGEventMaskBit(Quartz.kCGEventFlagsChanged),
        callback,
        None,
    )
    if tap is None:
        sys.exit(
            "Could not listen for the fn key. Check that your terminal is "
            "enabled under System Settings > Privacy & Security > Input "
            "Monitoring, then fully quit and reopen it."
        )
    state["tap"] = tap
    source = Quartz.CFMachPortCreateRunLoopSource(None, tap, 0)
    Quartz.CFRunLoopAddSource(
        Quartz.CFRunLoopGetCurrent(), source, Quartz.kCFRunLoopCommonModes
    )
    Quartz.CGEventTapEnable(tap, True)
    try:
        Quartz.CFRunLoopRun()
    except KeyboardInterrupt:
        print("\nBye.")


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
        default="fn" if sys.platform == "darwin" else "right_alt",
        help="hotkey to hold (default: fn/globe on macOS, right_alt elsewhere). "
        "Options: fn, " + ", ".join(HOTKEY_ALIASES),
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
    parser.add_argument(
        "--debug-keys",
        action="store_true",
        help="print every fn-key flag change (for troubleshooting the hotkey)",
    )
    parser.add_argument(
        "--max-seconds",
        type=float,
        default=120,
        help="safety cutoff: force-stop a recording after this many seconds "
        "so a missed key release can't leave the mic stuck on (default 120)",
    )
    args = parser.parse_args()

    use_fn = args.key.lower() in ("fn", "globe")
    if use_fn and sys.platform != "darwin":
        sys.exit("The fn/globe key is only supported on macOS. Pick another --key.")
    hotkey = None if use_fn else HOTKEY_ALIASES.get(args.key.lower())
    if hotkey is None and not use_fn:
        sys.exit(
            f"Unknown key '{args.key}'. Choose from: fn, {', '.join(HOTKEY_ALIASES)}"
        )

    print(f"Loading Whisper model '{args.model}' (first run downloads it)...")
    from faster_whisper import WhisperModel

    model = WhisperModel(args.model, device="auto", compute_type="auto")

    check_macos_permissions()

    vocab, replacements = load_custom_words(Path(__file__).resolve().parent)
    if vocab or replacements:
        print(
            f"Personal dictionary: {len(vocab)} vocabulary words, "
            f"{len(replacements)} replacements."
        )
    hotwords = ", ".join(vocab) if vocab else None

    recorder = Recorder()
    kbd = Controller()
    recording = threading.Event()
    lock = threading.Lock()

    watchdog = {"timer": None}

    def start_recording():
        with lock:
            if recording.is_set():
                return
            try:
                recorder.start()
            except Exception as exc:
                print(f"(mic unavailable: {exc} — tap the key to retry)")
                return
            recording.set()
            watchdog["timer"] = threading.Timer(args.max_seconds, safety_stop)
            watchdog["timer"].daemon = True
            watchdog["timer"].start()
            print("● recording... ", end="", flush=True)

    def safety_stop():
        if recording.is_set():
            print("(safety cutoff) ", end="", flush=True)
            stop_and_transcribe()

    def stop_and_transcribe():
        with lock:
            if not recording.is_set():
                return
            recording.clear()
            if watchdog["timer"] is not None:
                watchdog["timer"].cancel()
                watchdog["timer"] = None
            try:
                audio = recorder.stop()
            except Exception as exc:
                print(f"(recording lost: {exc})")
                return
        if audio.size < SAMPLE_RATE * 0.3:  # ignore accidental taps
            print("(too short, ignored)")
            return
        print("transcribing... ", end="", flush=True)
        segments, _ = model.transcribe(audio, vad_filter=True, hotwords=hotwords)
        text = clean_text("".join(s.text for s in segments))
        text = apply_replacements(text, replacements)
        if not text:
            print("(no speech detected)")
            return
        if args.type_instead_of_paste:
            kbd.type(text)
        else:
            paste_text(text, kbd)
        print(f"→ {text}")

    def handle_press():
        if args.toggle:
            if recording.is_set():
                threading.Thread(target=stop_and_transcribe).start()
            else:
                start_recording()
        else:
            start_recording()

    def handle_release():
        if not args.toggle:
            threading.Thread(target=stop_and_transcribe).start()

    mode = "tap to start/stop" if args.toggle else "hold to talk"
    print(f"Ready. {args.key} = {mode}. Focus any text field and speak. Ctrl+C quits.")
    if use_fn:
        print(
            "Tip: set System Settings > Keyboard > 'Press \U0001f310 key to' = "
            "'Do Nothing' so tapping fn doesn't also open the emoji picker."
        )
        listen_fn_key(handle_press, handle_release, debug=args.debug_keys)
        return

    def on_press(key):
        if key == hotkey:
            handle_press()

    def on_release(key):
        if key == hotkey:
            handle_release()

    with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
        try:
            listener.join()
        except KeyboardInterrupt:
            print("\nBye.")


if __name__ == "__main__":
    main()
