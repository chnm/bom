# bom-website

The website and blog for the [Death by Numbers](https://deathbynumbers.org/) project.

## Building and previewing the website

We use `make` to aid us in running regular tasks. The two primary ones are previewing the site locally and building the site for production. 

- `make preview`: This starts a local server and lets you view the site locally. 
- `make build`: This builds the site for dev. 
- `make build-prod`: This builds the site for production. 

The deployment of the site is handled by Ansible notebooks and can only be deployed by the senior developer or systems administrator. Please reach out to one of them if the site needs to be deployed.

## Theme updates

The theme is styled with plain CSS; there is no build step. The stylesheets live in `themes/dbn/assets/css/` and Hugo concatenates them (in the order listed in `layouts/partials/head.html`) into a single `site.css`, minified and fingerprinted in production:

- `base.css`: design tokens (colors, fonts, spacing) as custom properties, a small reset, element defaults, and a few utilities
- `prose.css`: typography for Markdown content (`.prose`, `.prose-lg`)
- `layout.css`: header, navigation, home hero, footer
- `components.css`: buttons, tags, panels, pagination, shortcodes
- `pages.css`: page-specific layouts (home, articles, section lists, authors, visualizations index)
- `database.css`: the database explorer
- `detail.css`: parish and cause detail pages, and controls on visualization pages

Change colors and fonts through the tokens at the top of `base.css`.

Note: Hugo's dev server does not notice a newly created stylesheet in `assets/css/`; restart `hugo serve` after adding one.
