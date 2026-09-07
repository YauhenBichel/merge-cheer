# Merge Cheer

Zero-config GitHub Action that comments a G-rated celebration GIF when a
pull request merges.

[![CI](https://github.com/YauhenBichel/merge-cheer/actions/workflows/ci.yml/badge.svg)](https://github.com/YauhenBichel/merge-cheer/actions/workflows/ci.yml)
[![Contributors](https://img.shields.io/github/contributors/YauhenBichel/merge-cheer)](https://github.com/YauhenBichel/merge-cheer/graphs/contributors)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![GitHub Marketplace](https://img.shields.io/badge/GitHub%20Marketplace-v1.6.0-6e5494)](https://github.com/marketplace/actions/merge-cheer)
[![Code of Conduct](https://img.shields.io/badge/Contributor%20Covenant-2.1-4baaaa.svg)](CODE_OF_CONDUCT.md)

Site: [yauhenbichel.github.io/merge-cheer](https://yauhenbichel.github.io/merge-cheer/) · Marketplace: [merge-cheer](https://github.com/marketplace/actions/merge-cheer)

GIF on merge, no Giphy key, no checkout of the pull request. The action
ships its own GIF groups and, by default, picks a **random theme**
(seeded by the pull request number so the same PR stays stable). Pin a
group with `topic` when you want one mood every time. Use `topic: title`
to pick from the title and body. A `no-cheer` / `skip-cheer` label (or
the same words in the title) skips the comment. The Action thanks
co-authors (`{authors}`) and will not post a second GIF on the same
pull request. Set an OpenAI-compatible `model` and `model-api-key` for
one G-rated line about what merged; generic thanks fall back to the
stdlib path.

![Merge Cheer demo](docs/merge-cheer-demo.mp4)

18 seconds. What the Action comments, then four shipped themes. Same
file as the [site demo](https://yauhenbichel.github.io/merge-cheer/#demo).

## Install

Pin `@v1.6.0` (current release). `@v1` is the older first release.
The Action never checks out the pull request head.

### GitHub

1. Add [.github/workflows/celebrate-merge.yml](examples/celebrate-merge.yml)
   on the **default** branch (this file is enough).
2. `pull_request_target` + `pull-requests: write` is what lets a fork
   merge get a comment. Bots are skipped.
3. Merge a human pull request. github-actions comments one GIF.

```yaml
name: Celebrate merge
on:
  pull_request_target:
    types: [closed]
permissions:
  pull-requests: write
jobs:
  celebrate:
    if: github.event.pull_request.merged && github.event.pull_request.user.type != 'Bot'
    runs-on: ubuntu-latest
    steps:
      - uses: YauhenBichel/merge-cheer@v1.6.0
```

Also comment when a pull request **closes without a merge**, or when a
reviewer asks for **more work**. Tone stays kind. Copy
[examples/celebrate-more.yml](examples/celebrate-more.yml). Close uses
the `coffee` group. A changes request uses `yeah`. The Action never
checks out the pull request head.

### GitLab

1. Copy [examples/gitlab-ci.yml](examples/gitlab-ci.yml) onto the default
   branch, or include the Catalog component after you publish one
   ([MARKETPLACES.md](MARKETPLACES.md)).
2. Add a project access token `GITLAB_TOKEN` with `api` scope.
   `CI_JOB_TOKEN` cannot post merge-request notes.
3. Push a merge to the default branch. The job finds that merged MR and
   comments the GIF.

```yaml
include:
  - component: $CI_SERVER_FQDN/YauhenBichel/merge-cheer/merge-cheer@v1.6.0
    inputs:
      topic: auto
      token: $GITLAB_TOKEN
```

Until the Catalog row exists, the curl job in
`examples/gitlab-ci.yml` is the working path.

### Bitbucket

1. Copy [examples/bitbucket-pipelines.yml](examples/bitbucket-pipelines.yml)
   onto `main` (or `master`).
2. Add a secured repository variable `BITBUCKET_ACCESS_TOKEN` with
   pullrequest write.
3. Merge a pull request into that branch. The step comments the GIF.

```yaml
script:
  - pipe: docker://eugenebichel/merge-cheer:1.5.0
    variables:
      TOPIC: auto
      BITBUCKET_ACCESS_TOKEN: $BITBUCKET_ACCESS_TOKEN
```

Until `eugenebichel/merge-cheer:1.5.0` is on Docker Hub, use the curl
job in the example. A Pipes UI listing needs an Atlassian review —
[MARKETPLACES.md](MARKETPLACES.md).

Pin a group:

```yaml
- uses: YauhenBichel/merge-cheer@v1.6.0
  with:
    topic: ship   # or party, comic, sunny, game, sticker, yeah
```

`topic` is `auto` when unset: a random shipped theme, then one GIF in
that group. Different PR numbers can land on different groups. Allowed
names: `auto`, `title`, `ship`, `fix`, `docs`, `tests`, `cleanup`,
`celebration`, `welcome`, `party`, `space`, `magic`, `coffee`, `robot`,
`comic`, `sunny`, `game`, `sticker`, `yeah`, `devops`, `sre`, `qa`,
`design`, `architecture`, `engineering`, `backend`, `frontend`, `java`,
`python`, `cpp`, `golang`. An unknown name falls back
to `celebration` and prints the list.

## Live demo

The video above is the walkthrough. What / why / where / how:

**What.** Merge Cheer comments one G-rated GIF when a human pull request
merges. Bots are skipped. The Action does not check out the pull request.

**Why.** The merge is the moment people actually did the work. No Giphy
key. The Action ships its own loops, so it works on a new repository
with the default token.

**Where.** Code is this repository. The same video and a walkthrough live
on the site:
[yauhenbichel.github.io/merge-cheer](https://yauhenbichel.github.io/merge-cheer/#demo).
Real comments already landed on
[py-harness #350](https://github.com/YauhenBichel/py-harness/pull/350#issuecomment-5559092736)
and
[molecare-desktop #26](https://github.com/MoleCare/molecare-desktop/pull/26#issuecomment-5559101123).

**How.** Pin `@v1.6.0` on the default branch (see [Install](#install)).
Leave `topic` unset (or `topic: auto`) for a random theme, seeded by the
pull request number. Pin `topic: comic` when you want the same mood
every time.

The loops below are the files the Action posts (open a file on GitHub to
see it move).

| ship | fix | docs | tests |
| --- | --- | --- | --- |
| ![ship](gifs/ship/ship-it.gif) | ![fix](gifs/fix/nailed-it.gif) | ![docs](gifs/docs/nice-work.gif) | ![tests](gifs/tests/high-five.gif) |

| cleanup | celebration | welcome | party |
| --- | --- | --- | --- |
| ![cleanup](gifs/cleanup/cleanup.gif) | ![celebration](gifs/celebration/celebration.gif) | ![welcome](gifs/welcome/high-five.gif) | ![party](gifs/party/confetti.gif) |

| space | magic | coffee | robot |
| --- | --- | --- | --- |
| ![space](gifs/space/planet.gif) | ![magic](gifs/magic/wand.gif) | ![coffee](gifs/coffee/mug.gif) | ![robot](gifs/robot/wave.gif) |

| comic | sunny | game | sticker | yeah |
| --- | --- | --- | --- | --- |
| ![comic](gifs/comic/burst.gif) | ![sunny](gifs/sunny/sun.gif) | ![game](gifs/game/levelup.gif) | ![sticker](gifs/sticker/star.gif) | ![yeah](gifs/yeah/pump.gif) |

| devops | sre | qa | design |
| --- | --- | --- | --- |
| ![devops](gifs/devops/loop.gif) | ![sre](gifs/sre/lighthouse.gif) | ![qa](gifs/qa/pass.gif) | ![design](gifs/design/palette.gif) |

| architecture | engineering | backend | frontend |
| --- | --- | --- | --- |
| ![architecture](gifs/architecture/blocks.gif) | ![engineering](gifs/engineering/wrench.gif) | ![backend](gifs/backend/db.gif) | ![frontend](gifs/frontend/browser.gif) |

| java | python | cpp | golang |
| --- | --- | --- | --- |
| ![java](gifs/java/mug.gif) | ![python](gifs/python/snake.gif) | ![cpp](gifs/cpp/plus.gif) | ![golang](gifs/golang/gopher.gif) |

The in-the-wild demo is the next merged pull request on this
repository: [.github/workflows/celebrate.yml](.github/workflows/celebrate.yml)
runs `uses: ./` and comments one of these GIFs. No merge comment exists
yet — that workflow is what will write it.

## Used by

6 public repositories already run Merge Cheer on the default branch.

**MoleCare:** [molecare-mcp](https://github.com/MoleCare/molecare-mcp),
[molecare-ml](https://github.com/MoleCare/molecare-ml),
[molecare-desktop](https://github.com/MoleCare/molecare-desktop),
[molecare-skin-llm](https://github.com/MoleCare/molecare-skin-llm),
[.github](https://github.com/MoleCare/.github).

**Personal:** [readme-contributors](https://github.com/YauhenBichel/readme-contributors).

To be listed, merge a celebrate workflow that
`uses: YauhenBichel/merge-cheer@v1.6.0` on the default branch.

## Topics

Each group is a folder of GIFs (`gifs/<group>/`). The action picks one
file in the group (stable for a given pull request number).

| `topic` | Title contains (when `topic: title`) | Preview |
| --- | --- | --- |
| `ship` | `feat`, `add `, `added`, `new `, `launch`, `ship:` | ![ship](gifs/ship/ship-it.gif) |
| `fix` | `fix`, `bug`, `hotfix`, `patch` | ![fix](gifs/fix/nailed-it.gif) |
| `docs` | `doc`, `readme` | ![docs](gifs/docs/nice-work.gif) |
| `tests` | `test`, `ci` | ![tests](gifs/tests/high-five.gif) |
| `cleanup` | `refactor`, `clean`, `typo`, `style`, `lint`, `format` | ![cleanup](gifs/cleanup/cleanup.gif) |
| `celebration` | anything else | ![celebration](gifs/celebration/celebration.gif) |
| `welcome` | `welcome`, `good first`, first-time contributor | ![welcome](gifs/welcome/high-five.gif) |
| `party` | `party`, `congrats`, `woo`, `hooray`, `celebrate` | ![party](gifs/party/confetti.gif) |
| `space` | `cosmos`, `galaxy`, `orbit`, `planet` | ![space](gifs/space/planet.gif) |
| `magic` | `magic`, `sparkle`, `wand`, `spell` | ![magic](gifs/magic/wand.gif) |
| `coffee` | `coffee`, `latte`, `caffeine`, `espresso` | ![coffee](gifs/coffee/mug.gif) |
| `robot` | `robot`, `android` | ![robot](gifs/robot/wave.gif) |
| `comic` | `comic`, `kapow` | ![comic](gifs/comic/burst.gif) |
| `sunny` | `sunny`, `sunshine`, `sunbeam` | ![sunny](gifs/sunny/sun.gif) |
| `game` | `level-up`, `level up`, `combo`, `high score` | ![game](gifs/game/levelup.gif) |
| `sticker` | `sticker` | ![sticker](gifs/sticker/star.gif) |
| `yeah` | `yeah`, `let's go`, `fist pump` | ![yeah](gifs/yeah/pump.gif) |
| `devops` | `devops`, `kubernetes`, `k8s`, `docker` | ![devops](gifs/devops/loop.gif) |
| `sre` | `sre`, `on-call`, `slo` | ![sre](gifs/sre/lighthouse.gif) |
| `qa` | `qa`, `sdet`, `quality` | ![qa](gifs/qa/pass.gif) |
| `design` | `design`, `figma`, `ux` | ![design](gifs/design/palette.gif) |
| `architecture` | `architecture`, `adr` | ![architecture](gifs/architecture/blocks.gif) |
| `engineering` | `software engineering`, `swe` | ![engineering](gifs/engineering/wrench.gif) |
| `backend` | `backend`, `graphql` | ![backend](gifs/backend/db.gif) |
| `frontend` | `frontend`, `javascript`, `react` | ![frontend](gifs/frontend/browser.gif) |
| `java` | `java:`, `jdk`, `jvm` | ![java](gifs/java/mug.gif) |
| `python` | `python`, `django`, `flask` | ![python](gifs/python/snake.gif) |
| `cpp` | `c++`, `cpp` | ![cpp](gifs/cpp/plus.gif) |
| `golang` | `golang`, `gopher` | ![golang](gifs/golang/gopher.gif) |

`welcome` also wins on `topic: title` when GitHub marks the author
`FIRST_TIME_CONTRIBUTOR` or `FIRST_TIMER` and the title did not match
another group. It reuses the tests and celebration loops — no extra art.

Conventional title types (`fix`, `feat`, `docs`, `test`, `refactor`)
win before mood keywords, so `feat: add party mode` still ships.

Aliases: `launch` → `ship`, `nailed-it` → `fix`, `nice-work` → `docs`,
`ci` / `high-five` → `tests`, `refactor` → `cleanup`, `first` → `welcome`,
`congrats` / `woo` → `party`, `cosmos` / `galaxy` → `space`,
`sparkle` → `magic`, `latte` → `coffee`, `bot` → `robot`,
`kapow` → `comic`, `sunshine` → `sunny`, `level-up` / `combo` → `game`,
`stickers` → `sticker`, `lets-go` / `fist-pump` → `yeah`,
`k8s` / `docker` → `devops`, `on-call` → `sre`, `testing` / `sdet` → `qa`,
`ux` / `figma` → `design`, `arch` → `architecture`, `swe` → `engineering`,
`js` / `react` → `frontend`, `jdk` → `java`, `py` → `python`,
`c++` → `cpp`, `go` / `gopher` → `golang`.

`javascript` does not match `java`. Conventional `test` / `ci` still win
before `qa`. `feat: add python client` still ships.

## Inputs

| Input | Default | What it does |
| --- | --- | --- |
| `github-token` | `${{ github.token }}` | Posts the comment |
| `topic` | `auto` | Group name, `auto` for a random theme, or `title` to pick from the PR title and body |
| `giphy-api-key` | empty | Optional. When set, try a G-rated Giphy GIF first |
| `message` | `Merged — thank you @{author}.` | `{author}` is the PR author; `{authors}` adds unique human co-authors |
| `closed-topic` / `closed-message` | `coffee` / closed thanks | Used when a pull request closes without a merge |
| `changes-topic` / `changes-message` | `yeah` / more-work line | Used when a reviewer asks for more work |
| `model` | empty | Optional chat model. `github` uses GitHub Models with `GITHUB_TOKEN` |
| `model-api-key` | empty | Optional OpenAI-compatible key. Unset keeps the stdlib path |
| `model-base-url` | empty | Optional OpenAI-compatible API root |
| `rating` | `g` | Giphy rating when a key is set |

```yaml
- uses: YauhenBichel/merge-cheer@v1.6.0
  with:
    topic: welcome
    giphy-api-key: ${{ secrets.GIPHY_API_KEY }}
    message: "Shipped. Thank you @{authors}."
    # model: gpt-4o-mini
    # model-api-key: ${{ secrets.OPENAI_API_KEY }}
```

## Why this instead of a random Giphy Action

Most merge-GIF actions need a Giphy key and post whatever the API
returns. Merge Cheer works on a new repository with zero secrets, and
the fallback is a set of owned looping GIFs — not a pixel parrot.

## Security

- The title is read from an environment variable, not interpolated into a shell.
- The action does not check out code.
- It only comments. It does not push, merge, or approve.

See [SECURITY.md](SECURITY.md).

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md). Please follow the
[Code of Conduct](CODE_OF_CONDUCT.md).

A good first change is another GIF in an existing group folder, or a
title keyword for a group, plus a test. Open issues:
[`good first issue`](https://github.com/YauhenBichel/merge-cheer/labels/good%20first%20issue).

```bash
python3 -m unittest discover -s tests -q
```

## Publish a release

Current release is `v1.6.0` (`@v1` is the first tag, not a floating
major). Listed on the [GitHub Marketplace](https://github.com/marketplace/actions/merge-cheer).
A reviewed Release is tests plus a human review — see [RELEASE.md](RELEASE.md).
Pushing a tag does not publish. Later releases update the existing listing.

The site is [yauhenbichel.github.io/merge-cheer](https://yauhenbichel.github.io/merge-cheer/).
The first Pages job 404s until you turn the site on in a browser:
**Settings → Pages → Build and deployment → Source → GitHub Actions**.
Then re-run the Pages workflow.

## Rebuild the GIFs

```bash
python3 -m pip install -r requirements-dev.txt
python3 scripts/make_gifs.py
```

Writes `gifs/<group>/<name>.gif`. Keep each file under 180 KB. A group
may hold several files; `alt.gif` is the same still with the pulse
inverted. Mood groups (`party`, `space`, `magic`, `coffee`, `robot`, `comic`,
`sunny`, `game`, `sticker`, `yeah`) each ship two original stills.

## License

[MIT](LICENSE). The GIFs are original stills animated for this Action.
See [NOTICE](NOTICE).

## Contributors

Thank you to everyone who has helped.

<!-- readme: contributors,bots/- -start -->
<p align="center">
  <a href="https://github.com/YauhenBichel" title="Yauhen Bichel" aria-label="Yauhen Bichel"><img src=".github/faces/YauhenBichel.svg" width="87" height="99" alt="Yauhen Bichel" /></a>
  <a href="https://github.com/HeaTTap" title="HeaTTap" aria-label="HeaTTap"><img src=".github/faces/HeaTTap.svg" width="66" height="75" alt="HeaTTap" /></a>
  <a href="https://github.com/Som0111" title="Soumya Padhi" aria-label="Soumya Padhi"><img src=".github/faces/Som0111.svg" width="72" height="82" alt="Soumya Padhi" /></a>
</p>
<p align="center"><em>Three contributors proudly showcased their achievements on the wall.</em></p>
<!-- readme: contributors,bots/- -end -->

Filled from GitHub commits (bots omitted). Live demo: [readme-contributors](https://github.com/YauhenBichel/readme-contributors#live-demo).
