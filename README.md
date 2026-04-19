# envsnap

> CLI tool to snapshot, diff, and restore environment variable sets across projects

---

## Installation

```bash
pip install envsnap
```

Or with [pipx](https://pypa.github.io/pipx/):

```bash
pipx install envsnap
```

---

## Usage

**Take a snapshot of your current environment:**
```bash
envsnap save myproject
```

**List saved snapshots:**
```bash
envsnap list
```

**Show details of a specific snapshot:**
```bash
envsnap show myproject
```

**Diff two snapshots:**
```bash
envsnap diff myproject staging
```

**Restore a snapshot:**
```bash
envsnap restore myproject
```

**Delete a snapshot:**
```bash
envsnap delete myproject
```

**Export a snapshot to a `.env` file:**
```bash
envsnap export myproject > .env
```

---

## How It Works

`envsnap` captures the current state of your environment variables and stores them as named snapshots. You can compare snapshots across branches, projects, or machines — and restore them when needed.

---

## License

MIT © [Your Name](https://github.com/yourname)
