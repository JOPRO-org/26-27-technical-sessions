# Notes for AI coding assistants working in this repo

This repo is used by people with mixed programming experience. Optimize for understanding, not cleverness.

- **Describe the model.** Every model folder has a README following `templates/show-and-tell.md`. The README says what the model is about in plain language. Someone who doesn't code should be able to follow it.
- **Name the parts.** In code, comment each block with the concept it implements, for example "essential variable", "uniselector", "sensor-to-motor connection". People want to point at the code and say what each part is.
- **Keep the model separate from the display.** In Python, put the model's state and update rule in `model.py` and plotting or notebooks elsewhere, so the model can be imported and reused.
- **Format is open.** Notebooks, scripts, NetLogo files, web pages, and written specs are all fine. Don't convert someone's entry to another format unless asked.
- **Sources.** Re-implement from papers and equations, and cite them in the README. Copy code from another repository only after checking its license, and credit it. Never invent a citation, link, DOI, or author; mark anything unchecked `[unverified]`.
- **Check behavior.** Run what you write. If a model doesn't behave as its source describes, say so in the README instead of tuning parameters until it looks right.
- **Say what it leaves out.** Every model's README states what it sets aside and why.
- **Mark AI-drafted work.** README files and code drafted by an assistant carry a line saying so until a person has reviewed them.
- **Ask before committing or pushing.**
- JOPRO is not an acronym. Don't expand it.
