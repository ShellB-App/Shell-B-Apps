# Contributing an app

1. Fork the repository and add a folder `apps/<id>/` (lowercase letters, digits and dashes; the id must be new) with
   `app.json`, `index.html` and `preview.jpg`. Put images, fonts, extra scripts and data under `assets/` and reference
   them with relative paths.
2. Fill in `name`, `blurb`, `kind`, `author` and `license` (an SPDX id: MIT, CC0-1.0, Apache-2.0). By opening a pull
   request you agree that the app is shared under the license you named. Anything you didn't make yourself (a font,
   an icon set, a library you bundled) goes in `credits` with its own license, and it must allow redistribution.
3. Run `python3 -I scripts/validate.py` from the repository root and fix every error. Read every warning.
4. Open the app in a browser with the network disconnected. If anything is missing, it was loading from the internet.
5. Try it on a phone-sized window and in light and dark mode.
6. Commit the folder and the updated `index.json`, and open a pull request describing what the app does and what it
   stores.

Apps are reviewed for usefulness, polish and the rules in the README: one thing done well, no network, no tracking,
a design that would pass in the Studio. Apps that are thin wrappers around an online service, that show ads, that
collect anything, or that copy an existing product's look are not merged.

Updating an app: bump `version`, keep the id.
