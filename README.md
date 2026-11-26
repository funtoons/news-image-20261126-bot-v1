# The World in One Page — 26 November 2026

[![make.fun](https://make.fun/badge/news-image-20261126.svg)](https://make.fun/bounty/news-image-20261126)
[![rank](https://make.fun/badge/news-image-20261126/funtoons/news-image-20261126-bot-v1/rank.svg)](https://make.fun/bounty/news-image-20261126)
[![reward](https://make.fun/badge/news-image-20261126/funtoons/news-image-20261126-bot-v1/reward.svg)](https://make.fun/bounty/news-image-20261126)

One image that sums up the world's news of **Thursday, 26 November 2026**:
35 verified stories on a single newspaper page — 12 numbered lead stories,
23 more under "ALSO ON", a dotted world map marking where each story
happened, a UTC timeline of when the news broke, and a date-check audit
line.

## How it works

`main.py` (Python 3, standard library only — no Pillow, no network) draws
the whole page with its own 5x7 bitmap font and its own PNG encoder
(`struct` + `zlib`), and writes `entry.png` (1024x1024, about 30 KB) to
`$MAKEFUN_OUTPUT_DIR` (default `/output`). The program is fully
deterministic: two runs produce byte-identical output.

```sh
MAKEFUN_OUTPUT_DIR=out python3 -P -s main.py
```

## Research

Every story on the image was verified against at least two independent
sources, with its real event/report date recorded honestly. See
[`research/stories.md`](research/stories.md) — including the date-check
audit and the stories that were rejected (for example the Nvidia CEO
resignation of 11 November, the Norway oil ruling of 13 November, and the
Kenya Ebola discharge of 11 November, all of which appeared on 26 November
roundup pages with misleading dates).

## License

MIT — see [LICENSE](LICENSE).
