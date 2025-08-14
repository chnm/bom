# bom-website

The website and blog for the [Death by Numbers](https://deathbynumbers.org/) project.

## Building and previewing the website

We use `make` to aid us in running regular tasks. The two primary ones are previewing the site locally and building the site for production. 

- `make preview`: This starts a local server and lets you view the site locally. 
- `make build`: This builds the site for dev. 
- `make build-prod`: This builds the site for production. 

The deployment of the site is handled by Ansible notebooks and can only be deployed by the senior developer or systems administrator. Please reach out to one of them if the site needs to be deployed.

## Theme updates

The theme is custom-designed using TailwindCSS. To get started with developing the theme, you'll need to install the necessary dependencies. **Navigate to `themes/dbn/` before running these commands**.

```
npm install -y
```

Then, anytime TailwindCSS components are added to a layout or content file, you can re-generate the side-wide CSS using the script in `package.js`. Note, again, you need to be in `themes/dbn` for this to work:

```
npm run build-tw
```

or 

```
make tailwind
```
