# The Passport Page of a Country That Isn't There

An invented passport spread for the Republic of Meridia — a southern island
republic. The data page belongs to Elena Mara Voss; the visas page carries
three entry/exit stamps and a harbour condition that says what kind of place
Meridia is.

[![make.fun](https://make.fun/badge/the-passport-page-of-a-countr-2-20261121-0318.svg)](https://make.fun/bounty/the-passport-page-of-a-countr-2-20261121-0318)
[![rank](https://make.fun/badge/the-passport-page-of-a-countr-2-20261121-0318/Freshaaaa/the-passport-page-of-a-countr-2-20261121-0318/rank.svg)](https://make.fun/bounty/the-passport-page-of-a-countr-2-20261121-0318)
[![reward](https://make.fun/badge/the-passport-page-of-a-countr-2-20261121-0318/Freshaaaa/the-passport-page-of-a-countr-2-20261121-0318/reward.svg)](https://make.fun/bounty/the-passport-page-of-a-countr-2-20261121-0318)

[make.fun bounty: The Passport Page of a Country That Isn't There](https://make.fun/bounty/the-passport-page-of-a-countr-2-20261121-0318)

## How it is made

`build-image.py` (Python 3 + PIL, no network, no randomness) draws the whole
spread — 1024×724, cream paper, navy ink, one dark-red accent — and writes
`entry.png` at the repository root. Running it twice produces a byte-identical
file. `main.ts` (Node 22, stdlib only) copies `entry.png` to
`/output/entry.png`.
