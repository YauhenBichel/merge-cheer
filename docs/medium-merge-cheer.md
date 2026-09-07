# Merge Cheer comments a GIF when your pull request merges

[Merge Cheer](https://github.com/YauhenBichel/merge-cheer) is a GitHub Action ([Marketplace](https://github.com/marketplace/actions/merge-cheer)). A human pull request merges. The Action writes one comment: a thank-you, plus a G-rated looping GIF it already ships. Bots are skipped. No Giphy key. No checkout of the pull request.

This is the 18-second walkthrough — the comment it posts, then four of the themes:

[![Merge Cheer demo](https://yauhenbichel.github.io/merge-cheer/merge-cheer-demo-poster.png)](https://yauhenbichel.github.io/merge-cheer/merge-cheer-demo.mp4)

https://yauhenbichel.github.io/merge-cheer/merge-cheer-demo.mp4

The same player lives on the site: [yauhenbichel.github.io/merge-cheer](https://yauhenbichel.github.io/merge-cheer/#demo).

Most merge-GIF Actions ask for a Giphy secret and then post whatever the API returns. I wanted the other shape. The loops are files in the Action repo. A new repository can use it with the default token.

The comment is boring on purpose:

```
Merged — thank you @alice.
```

Then one of these:

![comic](https://yauhenbichel.github.io/merge-cheer/gifs/comic/pop.gif)

![sunny](https://yauhenbichel.github.io/merge-cheer/gifs/sunny/sun.gif)

![game](https://yauhenbichel.github.io/merge-cheer/gifs/game/levelup.gif)

![python](https://yauhenbichel.github.io/merge-cheer/gifs/python/snake.gif)

That last one is an IT-section theme. The Action also ships DevOps, SRE, QA, design, architecture, engineering, backend, frontend, Java, C++, and Golang, next to the older packs (ship, fix, party, comic, …).

Default `topic: auto` picks a **random theme**, seeded by the pull request number, so the same PR stays stable if the job reruns. Pin a group when the repo has a home:

```yaml
- uses: YauhenBichel/merge-cheer@v1.7.0
  with:
    topic: python
```

Or leave `topic` unset:

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
      - uses: YauhenBichel/merge-cheer@v1.7.0
```

`topic: title` reads the PR title and body (`fix`, `feat`, `docs`, plus `typo` / `style` / `lint`). Conventional types still win, so `feat: add python client` ships. A `no-cheer` label skips the GIF. Co-authors are thanked. An unknown name falls back to `celebration`. Unset model keeps the stdlib path.

It is already posting on public repos. Two real merge comments:

- [py-harness #350](https://github.com/YauhenBichel/py-harness/pull/350#issuecomment-5559092736) — comic / burst
- [molecare-desktop #26](https://github.com/MoleCare/molecare-desktop/pull/26#issuecomment-5559101123) — game / level-up

Also on molecare-mcp, molecare-ml, molecare-skin-llm, MoleCare/.github, python-vibe, and [readme-contributors](https://github.com/YauhenBichel/readme-contributors), all pinned to `@v1.7.0`.

Code: [github.com/YauhenBichel/merge-cheer](https://github.com/YauhenBichel/merge-cheer)

Release: [v1.7.0](https://github.com/YauhenBichel/merge-cheer/releases/tag/v1.7.0)

Demo video: [merge-cheer-demo.mp4](https://yauhenbichel.github.io/merge-cheer/merge-cheer-demo.mp4)
