preview : 
	@echo "Serving the preview site with Nuxt ..."
	npm run dev

build : 
	@echo "\nBuilding the site with Nuxt ..."
	npm run generate
	@echo "Website finished building."

deploy : build
	@echo "Deploying the site to dev with rsync ..."
	rsync -avz --delete --itemize-changes --omit-dir-times \
			--checksum --no-perms --exclude-from=rsync-excludes \
			dist/ susanoo:/websites/database.deathbynumbers.org/ | egrep -v '^\.'
	@echo "Finished deploying the site to dev with rsync."

.PHONY : preview build deploy