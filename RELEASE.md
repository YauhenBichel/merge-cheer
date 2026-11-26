# How to ship a Merge Cheer release

A Marketplace-facing Release is **tests plus a human review**. Pushing a
tag does not publish anything. GitHub also cannot tick the Marketplace
box through the API — this workflow only creates the GitHub Release.

## The review gate

The `release` job uses `environment: marketplace`. That environment is
set up, under [Settings → Environments](https://github.com/YauhenBichel/merge-cheer/settings/environments):

- **Required reviewers**: the repository owner. The job waits until the
  owner clicks Approve.
- **Self-review is allowed**. There is one reviewer, so the person who
  starts the run is also the one who approves it.
- **Admin bypass is off**. Nobody can skip the wait.

If the `release` job ever publishes without waiting, check these three
settings first.

## Cut a reviewed release

Land the work on the default branch. Wait until **CI / test** is green
on the commit you intend to ship. Then tag that commit. Semver only
(`vMAJOR.MINOR.PATCH`): a new input or topic is a minor version, a fix
is a patch.

```
git tag v1.10.0
git push origin v1.10.0
```

1. Actions → **Release** → Run workflow
2. Use the default branch (or the tag itself)
3. Version input: `v1.10.0` (leading `v`, three numbers)
4. The **test** job checks out that tag and runs
   `python3 -m unittest discover -s tests -q`
5. If tests fail, stop. Nothing is published.
6. The **release** job then waits on the `marketplace` environment.
   Open the deployment review and click **Approve**.
7. The job creates the GitHub Release for that tag, or updates notes if
   the Release already exists (safe to re-run). `action.yml` is not an
   asset — the tag **is** the Action version.
8. The **docker** job pushes the pipe image for that tag to Docker Hub.

## After the release

Three steps follow every release. None of them is automated.

1. **Move `v1`.** `uses: YauhenBichel/merge-cheer@v1` follows the 1.x
   line only because a person moves the tag after each release:

   ```
   git tag --force v1 v1.10.0^{commit}
   git push --force origin refs/tags/v1
   ```

   The Release workflow never moves `v1`, and no other automation may.
   Do this only after the Release run is green.
2. **Point the docs at the new version.** Replace the old version with
   the new one in the README, `docs/`, `examples/`, `templates/`,
   `pipe.yml`, `MARKETPLACES.md`, this file and the tests that check
   them, and open a pull request.
3. **Bump the pipe image tag.** `pipe.yml` names the Docker image
   without the leading `v` (`eugenebichel/merge-cheer:1.10.0`), so a
   search for `v1.10.0` does not find it. Change it in `pipe.yml`,
   `MARKETPLACES.md`, `examples/bitbucket-pipelines.yml` and
   `tests/test_celebrate.py`, in the same pull request as step 2.

## Marketplace

Listing: https://github.com/marketplace/actions/merge-cheer

The listing form needs a G-rated screenshot of a real merge comment
that uses a bundled GIF. Use [docs/marketplace.png](docs/marketplace.png)
(the [live #53 comment](https://github.com/YauhenBichel/merge-cheer/pull/53#issuecomment-5574024316)).

The first publish is a browser + 2FA step (no API). Prefer
Settings → Actions → **Publish this Action to the GitHub Marketplace**,
or:

https://github.com/YauhenBichel/merge-cheer/releases/edit/v1.7.0?marketplace=true

Later reviewed Releases update that listing automatically once it exists.

## Docker Hub + GitLab (from GitHub Actions)

1. **Docker Hub** — secrets `DOCKERHUB_USERNAME` (Hub username, not
   email) and `DOCKERHUB_TOKEN` (Access Token with Read & Write). Prefer
   `printf '%s' '…' | gh secret set …` so the value has no trailing
   newline. Workflows trim CR/LF before login. The **Release** workflow’s
   `docker` job pushes the image after the reviewed GitHub Release.
   Manual retry: Actions → **Publish Docker** → `v1.10.0`.
2. **GitLab Catalog** — create `YauhenBichel/merge-cheer` on GitLab,
   enable **CI/CD Catalog project**, then either configure a GitLab
   **pull mirror** or set `GITLAB_MIRROR_TOKEN` and run **Mirror to
   GitLab**. Tag pipelines on GitLab publish Catalog versions via the
   `release:` keyword.

Details: [MARKETPLACES.md](MARKETPLACES.md). Do not claim those rows
exist until their catalog URLs return 200.
