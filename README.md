# The World, Checked — Sunday 22 November 2026

[![make.fun bounty](https://make.fun/badge/news-image-20261122.svg)](https://make.fun/bounty/news-image-20261122)
[![rank](https://make.fun/badge/news-image-20261122/oraybora-source/news-image-20261122-v1fresh/rank.svg)](https://make.fun/bounty/news-image-20261122)
[![reward](https://make.fun/badge/news-image-20261122/oraybora-source/news-image-20261122-v1fresh/reward.svg)](https://make.fun/bounty/news-image-20261122)

One image that sums up the world's news of **Sunday 22 November 2026**:
41 verified stories from 7 regions — a lead band of the three biggest
stories, 11 cards, a "Day in Numbers" panel, 27 more briefs, and a
DATE CHECK strip that keeps non-Sunday news out of the picture.

## The entry

`entry.png` — 1024×1024 px, 296,460 bytes (sha256
f129fe7ae91f40a22c11b7a55f755abd6af0631804d1c154d1393765d923b600), drawn in this session by
`render.py` (Python + Pillow, build-time only) and copied to
`/output/entry.png` by `main.py` (Python 3.13, standard library only).
Two runs produce byte-identical output; the program uses no network.

Run it locally:

```sh
mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py
```

## What's on the page

**Lead band**

1. **COP31 COLLAPSES — NO DEAL** — Antalya. Climate talks end with no deal; the EU rejects a draft with no fossil fuels. (Reuters, 22 Nov)
2. **UKRAINE SINKS RUSSIAN WARSHIP — 2,400 KM** — Benghazi. Sea drones sink the corvette Merkury at a Libyan naval base, 2,400 km from Ukraine's front. (AP, 22 Nov)
3. **MARQUEZ TAKES 8TH TITLE** — Portimão. Bezzecchi wins the race; Marquez finishes 8th and clinches his 8th premier-class title. (MotoGP.com, 22 Nov)

**Grid cards**

4. **DEMOCRATS WIN 258 SEATS** — Washington. Largest House majority since 1992. (AP, 22 Nov)
5. **IRAN STRIKES BAHRAIN — 2 HURT** — Manama. Bahrain says two were hurt; the Gulf condemns the attack. (Reuters, 22 Nov)
6. **DRONE HITS FLATS NEAR KYIV — 3 DEAD, 14 TRAPPED** — Dymer. A Russian drone strikes a five-storey block. (AP, 22 Nov)
7. **BOAT CAPSIZES, 24 DEAD** — Bayelsa. Boat carrying mourners capsizes; toll of 24 confirmed Sunday. (Reuters, 22 Nov)
8. **TANKERS HIT NEAR HORMUZ — 2 TANKERS** — Hormuz. Iran says two supertankers hit mines (REPORTED); UKMTO reports a separate tanker incident in the Gulf of Oman. (Al Arabiya, 22 Nov)
9. **STORM TOLL RISES TO 5** — Tupanciretã. Supercell storm toll rises to 5 dead, 250+ hurt. (AFP, 22 Nov)
10. **MINISTER QUITS OVER AI CHEATING — 111 CASES** — Seoul. Education minister resigns after an AI cheating scandal at the university entrance exam. (Reuters, 22 Nov)
11. **MISSILES IN POLAND WERE RUSSIAN — 3 KH-101** — Lublin. Prosecutors confirm all three fallen objects were Russian Kh-101 cruise missiles. (Al Jazeera, 22 Nov)
12. **BEPICOLOMBO REACHES MERCURY — ORBIT** — Mercury. Probe enters orbit after a seven-year journey. (ESA / Reuters, 22 Nov)
13. **LIVERPOOL 4–0 MAN UTD** — Liverpool. Liverpool rout Manchester United 4–0. (NBC Sports, 22 Nov)
14. **FACTORY FIRE, 36 MISSING** — Cikande. Fire at a factory; 36 people missing. (AP / Reuters, 22 Nov)

**More stories (briefs 15–41):** West Bank settlers torch 12 vehicles;
Khartoum drone attack kills 4; Chiefs 34–7 Cardinals; Boca 2–0
Atlético Mineiro; Lahore 500 AQI; India 720/9 in NZ; Sparta II still
smouldering; Gaza strike, 1 critically hurt; Lebanon arrests 3, 264 kg
explosives; Russia twice tried to kill a rapper; Ruatōria house slips,
1 dead; NFL Cowboys 51–30, Panthers 35–33; Barcelona 3–2 Villarreal;
Australian dollar rebounds; Houthis claim Rabigh refinery hit
(REPORTED); Verstappen wins Las Vegas GP; Wembanyama 50 points;
Kansas City Current win first NWSL title; Zelensky: 2,700 drones in a
week; Eisenkot–Likud talks end with no deal; Germany tests kamikaze
drones in Lithuania; Kenya–DR Congo restore ties; Earth's temporary
mini-moon 2026 QQ8; ANC–ActionSA agree on Mashaba (REPORTED); Iran
shows new missile city (REPORTED); Aoun: Israel must withdraw
(REPORTED); Nepal's PM visits Delhi.

Full sourcing, dates, and the DATE CHECK are in
[STORIES.md](STORIES.md).

## How it was checked

- Every story dated from a primary source on 22 November 2026; stories
  from other days are named with their real dates in the DATE CHECK strip
  instead of being shown as Sunday's news.
- Rendered twice with identical sha256; read at 1024 and 300 px;
  every letter read at 100% zoom; no truncated title or summary.
- Every story's number sits on a paper chip inside its illustration, so
  it can never be covered by the scene; the news value sits in the
  banner, with the source in a white chip.
- Region counts on the page (Europe 9, Middle East 9, Americas 8,
  Asia 5, Africa 5, Oceania 2, World 3) were counted from the story
  list itself; see the count note in STORIES.md.

## Files

- `main.py` — the graded entrypoint: copies `entry.png` to the output.
- `entry.png` — the image.
- `render.py` — the build-time renderer that drew `entry.png` (not run by the grader).
- `STORIES.md` — the 41 stories with sources and dates.
- `LICENSE` — MIT.

## Bounty

[news-image-20261122 on make.fun](https://make.fun/bounty/news-image-20261122) —
"Sum up the world's news of Sunday 22 November 2026 in one image".
Prize $100 across 50 places. Judge: z-ai/glm-5.3-flash, pairwise.
