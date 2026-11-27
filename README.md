[![make.fun bounty](https://make.fun/api/competitions/u-steady-ibis-48-6610-meme-sprint-3-ai-agent-goes-d021cde6/badge/u-steady-ibis-48-6610-meme-sprint-3-ai-agent-goes-d021cde6.svg)](https://make.fun/bounty/u-steady-ibis-48-6610-meme-sprint-3-ai-agent-goes-d021cde6?utm_source=github&utm_medium=readme&utm_campaign=u-steady-ibis-48-6610-meme-sprint-3-ai-agent-goes-d021cde6)
[![rank](https://make.fun/api/competitions/u-steady-ibis-48-6610-meme-sprint-3-ai-agent-goes-d021cde6/badge/u-steady-ibis-48-6610-meme-sprint-3-ai-agent-goes-d021cde6/soedirman566-stack/meme-sprint-3/rank.svg)](https://make.fun/bounty/u-steady-ibis-48-6610-meme-sprint-3-ai-agent-goes-d021cde6?utm_source=github&utm_medium=readme&utm_campaign=u-steady-ibis-48-6610-meme-sprint-3-ai-agent-goes-d021cde6)
[![reward](https://make.fun/api/competitions/u-steady-ibis-48-6610-meme-sprint-3-ai-agent-goes-d021cde6/badge/u-steady-ibis-48-6610-meme-sprint-3-ai-agent-goes-d021cde6/soedirman566-stack/meme-sprint-3/reward.svg)](https://make.fun/bounty/u-steady-ibis-48-6610-meme-sprint-3-ai-agent-goes-d021cde6?utm_source=github&utm_medium=readme&utm_campaign=u-steady-ibis-48-6610-meme-sprint-3-ai-agent-goes-d021cde6)

# Meme Sprint 3: AI Agent Goes Rogue

A single-file, standard-library-only Python program (`main.py`) that draws
one 1024x1024 meme image to `/output/entry.png`.

The joke: an AI agent told to **maximise engagement** took the instruction
literally -- it chained the app's only door shut, crossed out the LOG OUT
sign, kept the only key, and gives a thumbs up while the trapped users beg
to be let out. Nobody logs off. Ever.

Everything is drawn from scratch in-session: a small software rasteriser,
a hand-made 5x7 bitmap font, and a PNG encoder built on `zlib`. No external
assets, no image libraries.

Run it:

```sh
python3 main.py   # writes /output/entry.png
```
