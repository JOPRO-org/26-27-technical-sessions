# 2026–27 Technical Sessions

The shared space for JOPRO's weekly Thursday and Friday sessions.

- **Thursday** is a reading session. We read a paper and talk it through.
- **Friday** is a technical session. We build, run, and pick apart small models: homeostats, perceptrons, thermostats, Braitenberg vehicles, agent-based models, and whatever else people bring.

The sessions draw on cognitive science, cybernetics, and multi-agent work. No background in any of them is needed, and nobody needs to be an experienced programmer.

## What's here

| Folder | What it's for |
|---|---|
| [`sessions/`](sessions/) | One folder per Friday session, plus the Thursday reading list |
| [`templates/`](templates/) | The short template for describing a model |
| [`primer/`](primer/) | A growing guide to what can and can't usefully be simulated, built from what we try |
| [`projects/`](projects/) | Work that has grown beyond a single session |

## Taking part

1. Pick something small to model, or find an existing model you want to understand.
2. Make a folder for it inside that week's session folder, named `yourname-model` (for example `sam-homeostat`). Use whatever name you like.
3. Copy [`templates/show-and-tell.md`](templates/show-and-tell.md) into it as `README.md` and fill it in.
4. Add your code, notebook, NetLogo file, screenshots, or just a sketch. A model that only exists on paper is fine.

If you don't use Git, post in [Discussions](https://github.com/JOPRO-org/26-27-technical-sessions/discussions) or send your files to a session organizer and they'll add them.

AI-assisted code is welcome. Say so in your README, and check that you understand what it does.

## Running Python entries

Most entries need only Python 3.10 or newer and the packages in `requirements.txt`:

```bash
python3 -m venv .venv            # Windows: py -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

Notebooks can also be opened in Google Colab straight from GitHub. Each entry's README says how to run it.

## License

[pending]
