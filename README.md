# xiejiayun.github.io

Personal blog built with [Hugo](https://gohugo.io/) and [Stack](https://github.com/CaiJimmy/hugo-theme-stack) theme.

## Local Development

```bash
# Install Hugo (macOS)
brew install hugo

# Clone with submodules
git clone --recurse-submodules https://github.com/Xiejiayun/xiejiayun.github.io.git

# Run local server
hugo server -D
```

## Writing

Create a new post:

```bash
hugo new content post/my-post/index.md
```

## Deployment

Push to `main` branch triggers automatic deployment via GitHub Actions.

## Setup Note

In GitHub repo Settings > Pages, set Source to **GitHub Actions**.
