# Shell:B Apps

[![Validate](https://github.com/EveAeternam/Shell-B-Apps/actions/workflows/validate.yml/badge.svg)](https://github.com/EveAeternam/Shell-B-Apps/actions/workflows/validate.yml) [![MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

Community apps for [Shell:B](https://github.com/EveAeternam/Shell-B), the local-first AI workspace.
Part of the family with [Shell-B-Themes](https://github.com/EveAeternam/Shell-B-Themes), [Shell-B-Screensavers](https://github.com/EveAeternam/Shell-B-Screensavers), [Shell-B-Agents](https://github.com/EveAeternam/Shell-B-Agents) and [Shell-B-Studio-Templates](https://github.com/EveAeternam/Shell-B-Studio-Templates).

A Shell:B app is **a finished Studio project**: a folder of HTML, CSS, JavaScript and assets that does one thing well
and runs in Shell:B's sandboxed preview frame, with no network. Where a Studio template is a starting point for the
agents to build on, an app is ready to use the moment it is installed: a timer, a notebook, a converter, a board. It
keeps its data in the browser (`localStorage`) and can use Shell:B's offline libraries under `/vendor`.

## Install one

Each app is a Studio project folder. Download the folder (or clone this repository) and drop it into a new Studio
project: **Studio → New project**, pick *Dashboard / web app*, and copy the files in, or ask Hephaestus to import it
("import the Focus app from this folder"). The app opens in the preview, full screen with the expand button, and gets
its own `shellb://` link.

One-click install from Settings, the way themes and screensavers work, is planned.

## Catalogue

| App | What it does | Keeps |
|---|---|---|
| Focus | A Pomodoro-style timer with a dial, a chime and a row of dots for today's blocks | Lengths and today's count |
| Notebook | Markdown notes with a live preview (via `/vendor/marked.js`) and search | Your notes |
| Units | Length, mass, volume, area, speed, temperature, energy, pressure, data and time, every unit at once | Last category and units |
| Board | A three-column kanban: drag between To do, Doing and Done, `#tags`, stale cards marked | Your cards |

`index.json` is the machine-readable version of this table.

## Make one

Build it in the Studio with Daedalus or Hephaestus, use it for a week, then export the project. Every app is a
folder under `apps/`:

```
apps/focus-timer/
  app.json        name, blurb, kind, author, license, version, tags, entry (index.html by default), credits
  index.html      the app; relative paths only
  preview.jpg     a screenshot, about 640×360 (≤ 400 KB)
  assets/         optional: images, fonts, extra scripts, data files
```

`app.json`:

```json
{
  "name": "Focus",
  "blurb": "One or two sentences for the picker (≤ 200 characters).",
  "kind": "dashboard",
  "author": "Your name",
  "license": "MIT",
  "version": "1.0",
  "tags": ["productivity", "timer"],
  "credits": [{"what": "Inter font", "author": "Rasmus Andersson", "license": "OFL-1.1", "url": "https://rsms.me/inter/"}]
}
```

`kind` is the Studio project kind the app is installed as: `dashboard` for most apps, or `website`, `mobile`, `deck`,
`print`, `motion`, `game`, `design-system`, `brand`, `social`, `email`.

### The rules

- **No network.** Nothing loads from the internet: no CDN scripts, no web fonts, no API calls. Bundle it in the folder,
  or use Shell:B's offline copies at `/vendor/tailwind.js`, `/vendor/chart.js`, `/vendor/mermaid.js`,
  `/vendor/marked.js` and `/vendor/three/`. The validator refuses anything that fetches from a URL.
- **No tracking, no accounts.** Data stays in the browser; say so in the app if it stores anything.
- **Works at phone width** and at desktop width, light and dark (`prefers-color-scheme`).
- **Keyboard and focus.** Buttons are buttons, focus is visible, and the main action has a shortcut.
- **Files:** HTML, CSS, JS, JSON, SVG, PNG, JPEG, WebP, GIF, WOFF2, TXT, MD, CSV, GLB; 2 MB per file, 8 MB per folder,
  no dotfiles or symlinks.
- Design it properly: one aesthetic, a typographic scale, restrained colour, real copy, and loading, empty and error
  states. The same standard the Studio holds its own work to.

Then check it:

```bash
python3 -I scripts/validate.py
```

See [CONTRIBUTING.md](CONTRIBUTING.md) for the pull request checklist.

## Other collections

Shell:B installs from the whole family: [Shell-B-Themes](https://github.com/EveAeternam/Shell-B-Themes), [Shell-B-Screensavers](https://github.com/EveAeternam/Shell-B-Screensavers), [Shell-B-Agents](https://github.com/EveAeternam/Shell-B-Agents) and [Shell-B-Studio-Templates](https://github.com/EveAeternam/Shell-B-Studio-Templates) work the same way, with a validator, CI and a one-screen checklist each. Found a bug in the app itself? That goes to [Shell-B issues](https://github.com/EveAeternam/Shell-B/issues); questions and show-and-tell to [Discussions](https://github.com/EveAeternam/Shell-B/discussions).

## License

The scripts and this repository are MIT. Each app names its own license in `app.json`; the ones here are MIT.
