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

Then, in any app: **hold the right Alt/Option key, speak, and release.**
About a second later your words are pasted at the cursor.

Say **"new line"** or **"new paragraph"** while dictating to insert breaks.

### Options

| Flag | What it does |
|---|---|
| `--key f8` | Use a different hotkey (right_alt, right_cmd, right_ctrl, right_shift, caps_lock, f1–f12) |
| `--toggle` | Tap to start recording, tap again to stop (instead of holding) |
| `--model small.en` | Better accuracy, slower. Sizes: `tiny.en` → `base.en` → `small.en` → `medium` → `large-v3` |
| `--type-instead-of-paste` | Simulate real keystrokes for apps that block pasting |

`base.en` (the default) is a good speed/accuracy balance on a typical laptop.
If you have a fast machine (Apple Silicon, or any recent GPU), try
`--model small.en` or `medium` for noticeably better accuracy.

## Tips

- First run downloads the model (~75 MB for base.en) — after that it's fully
  offline.
- Keep it running in a spare terminal tab, or launch it at login.
- If pasting doesn't work in a particular app, use
  `--type-instead-of-paste`.
