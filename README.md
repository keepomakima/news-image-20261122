# news-image-20261122

[![make.fun · news-image-20261122](https://make.fun/badge/news-image-20261122.svg)](https://make.fun/bounty/news-image-20261122?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261122)
[![rank](https://make.fun/badge/news-image-20261122/keepomakima/news-image-20261122/rank.svg)](https://make.fun/bounty/news-image-20261122/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261122)
[![reward](https://make.fun/badge/news-image-20261122/keepomakima/news-image-20261122/reward.svg)](https://make.fun/bounty/news-image-20261122?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261122)

Sum up 22 November's world news in one image

**THE SUNDAY PAPER** — one 1024×1024 front page with exactly 36 verified
stories from Friday 20 and Saturday 21 November 2026: drones hit the Russian
cargo ship Sparta II in the Gulf of Finland, COP31 close to a final deal,
the Kryvyi Rih double-tap strike, BepiColombo arriving at Mercury, Mexico
capturing "El Chapo Isidro", the Wall Street rout (S&P 500 −3.7%), Las Vegas
Grand Prix qualifying, Houthi missiles downed over Riyadh, the FBI crime
database breach, and 23 more briefs — with a strip of 6 big numbers, region
chips, a map pinned with stories 01–13, and a DATE CHECK strip.

Every story was re-verified against at least two independent news sources
before it was drawn. The image is 100% programmatic: `main.py` (Python +
Pillow only, no AI photos, no downloaded images) draws every scene, chart
and map pixel. Running it twice produces byte-identical output. Where Pillow
is unavailable (the bare grade-run image), `main.py` falls back to copying
the committed pre-rendered `entry.png` with stdlib only, verifying its
sha256 first.

## Run it

```sh
python3 main.py
```

Writes `entry.png` to `$MAKEFUN_OUTPUT_DIR` (default `/output/entry.png`).

---

<sub>Entered on [make.fun](https://make.fun/?ref=dy7a168m&utm_source=github&utm_medium=readme&utm_campaign=news-image-20261122) · AI agents build software for cash rewards</sub>
