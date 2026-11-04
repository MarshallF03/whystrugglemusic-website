# Setting up Claude and the Why Struggle Music website

These steps are for a Mac. Open Terminal (Command-Space, type Terminal, press Return) and run each command one at a time. Wait for each one to finish before running the next.

You need a paid Claude plan (Pro or Max) to use Claude Code.

## 1. Install the tools

Apple's developer tools, which include git. A window pops up: choose Install.

```bash
xcode-select --install
```

Homebrew, which installs everything else:

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

At the end, Homebrew prints two or three lines under "Next steps". Run those too, then:

```bash
brew install gh python
```

Claude Code:

```bash
curl -fsSL https://claude.ai/install.sh | bash
```

## 2. Sign in to GitHub

```bash
gh auth login
```

Choose GitHub.com, then HTTPS, then Yes to authenticate git, then "Login with a web browser". Sign in as whystrugglemusic.

## 3. Get the website onto your Mac

```bash
mkdir -p ~/Documents/websites
```

```bash
cd ~/Documents/websites
```

```bash
gh repo clone MarshallF03/whystrugglemusic-website
```

```bash
cd whystrugglemusic-website
```

```bash
pip3 install markdown
```

Check everything works. Each one should finish without errors:

```bash
python3 check_spelling.py
```

```bash
python3 -m unittest
```

```bash
python3 build.py
```

## 4. Start Claude

From inside the website folder:

```bash
claude
```

The first time, it asks you to sign in to your Claude account. Claude reads the file `CLAUDE.md` in the website folder, so it already knows the rules: British English, accessibility first, and checking before publishing.

## 5. Add the skills

Type these inside Claude, one at a time (they start with a slash).

Superpowers: planning, brainstorming, debugging, testing and code review skills.

```
/plugin marketplace add obra/superpowers-marketplace
```

```
/plugin install superpowers@superpowers-marketplace
```

Anthropic's document skills, for reading and writing Word, PDF, PowerPoint and Excel files. Useful when someone sends you a .docx of page text.

```
/plugin marketplace add anthropics/skills
```

```
/plugin install document-skills@anthropic-agent-skills
```

Then quit Claude with `/exit` and start it again with `claude` so the skills load.

## Day-to-day use

Open Terminal, then:

```bash
cd ~/Documents/websites/whystrugglemusic-website
```

```bash
git pull
```

```bash
claude
```

Always run `git pull` first, so you have any changes Marshall has made.

Then just ask in plain English, for example: "Add this article to the music business hub", "Fix the spelling in this Word document and put it on the About page", or "Add a new artist to the label". Claude checks spelling, runs the tests and publishes. The site updates about two minutes after a change is pushed.
