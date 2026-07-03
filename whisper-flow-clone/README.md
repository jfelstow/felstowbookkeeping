# Local Dictation (a free Wispr Flow alternative)

Push-to-talk voice dictation that runs entirely on your own computer. Hold a
hotkey, speak, release — your words appear in whatever app you're typing in
(email, docs, Slack, code editor, anything with a text field).

Built on OpenAI's open-source **Whisper** speech model via
[faster-whisper](https://github.com/SYSTRAN/faster-whisper), so there is:

- **No subscription** — completely free
- **No account** — nothing to sign up for
- **No cloud** — audio never leaves your machine (works offline after the
  first run downloads the model)

## Setup

Requires Python 3.9+. On Mac/Linux, one command does everything (first run
installs dependencies, later runs start instantly):

```bash
cd whisper-flow-clone
./run.sh
```

Or set up manually (Windows, or if you prefer):

```bash
cd whisper-flow-clone
python3 -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python dictate.py
```

### macOS permissions

macOS will prompt you to grant your terminal app two permissions the first
time (System Settings → Privacy & Security):

- **Microphone** — to hear you
- **Accessibility** + **Input Monitoring** — to detect the hotkey and paste
  the text into the frontmost app

### Linux

Needs PortAudio and an X11/Wayland session:

```bash
sudo apt install portaudio19-dev xclip
```

## Use

```bash
python dictate.py
```

Then, in any app: **hold the fn/globe key (bottom-left on Mac keyboards),
speak, and release.** On Windows/Linux the default is the right Alt key.
About a second later your words are pasted at the cursor.

Say **"new line"** or **"new paragraph"** while dictating to insert breaks.

**macOS tip:** set System Settings → Keyboard → "Press 🌐 key to" →
**Do Nothing**, so tapping fn doesn't also open the emoji picker or switch
input sources while you dictate.

### Options

| Flag | What it does |
|---|---|
| `--key f8` | Use a different hotkey (fn, right_alt, right_cmd, right_ctrl, right_shift, caps_lock, f1–f12) |
| `--toggle` | Tap to start recording, tap again to stop (instead of holding) |
| `--model small.en` | Better accuracy, slower. Sizes: `tiny.en` → `base.en` → `small.en` → `medium` → `large-v3` |
| `--type-instead-of-paste` | Simulate real keystrokes for apps that block pasting |

`base.en` (the default) is a good speed/accuracy balance on a typical laptop.
If you have a fast machine (Apple Silicon, or any recent GPU), try
`--model small.en` or `medium` for noticeably better accuracy.

## Teaching it your words

Two plain-text files next to `dictate.py` act as your personal dictionary
(edit them any time; restart the app to pick up changes):

- **`vocabulary.txt`** — one word or phrase per line. The recognizer is
  biased toward these spellings, so names, businesses, and jargon come out
  right the first time (e.g. `Felstow`, `QuickBooks`).
- **`replacements.txt`** — forced corrections in the form
  `what whisper writes => what you want`. Applied to every transcript, so
  if a word keeps coming out wrong you can pin the exact spelling
  (e.g. `fell stow => Felstow`).

Unlike Wispr Flow, it doesn't learn automatically from your edits — you add
words yourself — but nothing you say is stored anywhere to make that work.

## Privacy & security

- Audio is processed in memory and never written to disk; transcription
  happens on-device and the app makes no network requests after the
  one-time model download (from the official Systran repos on Hugging Face).
- Transcripts are printed to your terminal for feedback but not logged to
  any file.
- Text is inserted via the clipboard. If you run a clipboard-history
  manager, your dictations will appear in its history; use
  `--type-instead-of-paste` to bypass the clipboard entirely.
- The macOS permissions you granted (Microphone, Accessibility, Input
  Monitoring) apply to your whole terminal app — anything else you run in
  that terminal inherits them. Keep that in mind before piping untrusted
  scripts through the same terminal.

## Tips

- First run downloads the model (~75 MB for base.en) — after that it's fully
  offline.
- Keep it running in a spare terminal tab, or launch it at login.
- If pasting doesn't work in a particular app, use
  `--type-instead-of-paste`.
