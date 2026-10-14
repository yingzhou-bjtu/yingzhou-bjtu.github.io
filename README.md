# Ying Zhou Academic Homepage Source

This repository contains the source for Ying Zhou's academic homepage published
at <https://yingzhou-bjtu.github.io/>.

The site is based on the AcadHomepage/Jekyll structure, but this repository is
the maintained public source for the personal homepage, not a template fork.

## Project Identity

See [docs/PROJECT_IDENTITY.md](docs/PROJECT_IDENTITY.md) for the public name, GitHub Pages slug constraint, scope, and directory contract.

## Repository Layout

```text
.
├── _config.yml                  # Jekyll site configuration
├── _pages/                      # profile, about, and evidence pages
├── _data/                       # navigation, news, and evidence data
├── _includes/, _layouts/        # Jekyll components and page shells
├── _sass/                       # site styles
├── images/                      # favicon, avatar, and public images
├── docs/                        # operations notes and screenshots
├── google_scholar_crawler/      # citation update helper
├── scripts/                     # maintenance scripts
├── run_server.sh                # local Jekyll server helper
└── docs/OPEN_SOURCE_STANDARD.md # repository hygiene and layout policy
```

## Local Preview

Install Ruby and Bundler, then run:

```bash
bundle install
bash run_server.sh
```

Open <http://127.0.0.1:4000>.

Override the local preview address when needed:

```bash
JEKYLL_HOST=0.0.0.0 JEKYLL_PORT=4001 bash run_server.sh
```

## Content Update Workflow

1. Update profile content in `_pages/` and structured data in `_data/`.
2. Put stable public images under `images/`.
3. Keep operational notes under `docs/`.
4. Run the local preview before pushing visual changes.

## Automation

The GitHub Actions workflow under `.github/workflows/` updates Google Scholar
metadata when configured with the required repository secret. Do not commit
private analytics keys, cookies, or service tokens.

Run the Scholar metadata helper manually with:

```bash
GOOGLE_SCHOLAR_ID=<author-id> python google_scholar_crawler/main.py
```

Set `GOOGLE_SCHOLAR_OUTPUT_DIR` or pass `--output-dir` to write generated JSON
outside the default `results/` directory.

## Validation

For documentation-only changes:

```bash
git diff --check
```

For site changes:

```bash
bundle exec jekyll build
```

## Credits

The site structure is derived from AcadHomepage and related Jekyll academic
homepage templates. Keep upstream license notices in `LICENSE` and related
documentation when modifying template-derived files.
