# Contributing

Thanks for being here. Merge Cheer is a small composite Action:
stdlib Python in `src/celebrate.py`, grouped GIFs in `gifs/<group>/`,
tests in `tests/test_celebrate.py`.

## Rules that are not negotiable

- Do not check out the pull request head from `pull_request_target`
- The title stays in an environment variable. Do not interpolate it into a shell
- Do not commit secrets, tokens, or `.env`
- GIFs stay G-rated and under 180 KB
- Keep `src/celebrate.py` stdlib-only

## Getting set up

```bash
git clone https://github.com/YauhenBichel/merge-cheer.git
cd merge-cheer
python3 -m unittest discover -s tests -q
```

No Giphy key, no token, and no extra packages for the tests.

## Rebuild the GIFs

Only if you change `stills/` or `scripts/make_gifs.py`:

```bash
python3 -m pip install -r requirements-dev.txt
python3 scripts/make_gifs.py
```

Each GIF must stay under 180 KB. The test suite fails if one grows.

## What a good first change looks like

If [`good first issue`](https://github.com/YauhenBichel/merge-cheer/labels/good%20first%20issue)
has an open issue, start there. The label is often empty — pick from
the list below and [open an issue](https://github.com/YauhenBichel/merge-cheer/issues/new)
first so two people do not take the same change.

Locale, Marketplace screenshot, first-timer welcome, a third comic
GIF, and the title-keyword / skip / co-author work already landed.

A good first change is one of:

- a title keyword that maps to an **existing** group, plus a test
- another GIF in `gifs/<group>/` (under 180 KB, G-rated)
- another `locale` in the static catalog (`en`, `es`, `de`, `fr`, `pt`, `uk`, `it`, `be`, `ja` are there)

Groups today: `ship`, `fix`, `docs`, `tests`, `cleanup`,
`celebration`, `welcome`, `party`, `space`, `magic`, `coffee`, `robot`,
`comic`, `sunny`, `game`, `sticker`, `yeah`, `devops`, `sre`, `qa`,
`design`, `architecture`, `engineering`, `backend`, `frontend`, `java`,
`python`, `cpp`, `golang`.

Design questions go in [Discussions](https://github.com/YauhenBichel/merge-cheer/discussions), not a drive-by PR.

## Before you open a pull request

- [ ] `python3 -m unittest discover -s tests -q` passes
- [ ] New or rebuilt GIFs are under 180 KB
- [ ] No secrets, tokens, or `.env`
- [ ] One concern per PR

## Branch protection (maintainers)

`main` is not locked from a script. Recommended Settings → Branches
rule for `main`:

- Require a pull request before merging
- Require status checks to pass: **CI / test**
- Do not require administrator lockout unless a second owner exists

Enabling admin-enforced protection as the only owner can lock you out
of your own repository.

## Reporting security issues

Use GitHub private vulnerability reporting. See [SECURITY.md](./SECURITY.md).
Do not paste live keys. Do not open a public issue for a working exploit.

## Licence

By contributing you agree that your contributions are licensed under the
[MIT License](./LICENSE) that covers this project.
