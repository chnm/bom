preview :
	@echo "Serving the preview site with Hugo ..."
	hugo serve --buildDrafts --buildFuture --disableFastRender 

build :
	@echo "\nBuilding the site with Hugo ..."
	hugo --cleanDestinationDir --buildDrafts --buildFuture --baseURL http://dev.deathbynumbers.org/
	@echo "Website finished building."

build-dev : build
	@echo "\nDeploying the site to development with rsync ..."
	rsync --delete --itemize-changes --omit-dir-times \
		--checksum -avz --no-t --no-perms --exclude-from=rsync-excludes \
		public/ susanoo:/websites/dev.deathbynumbers.org/ | egrep -v '^\.'
	@echo "Finished deploying the site to development with rsync."

build-prod :
	@echo "\nBuilding the site with Hugo ..."
	hugo --cleanDestinationDir --minify --baseURL https://deathbynumbers.org/
	@echo "Website finished building."

deploy-prod : build-prod
	@echo "\nDeploying the site to production with rsync ..."
	rsync --delete --itemize-changes --omit-dir-times \
		--checksum -avz --no-t --no-perms --exclude-from=rsync-excludes \
		public/ susanoo:/websites/deathbynumbers.org/ | egrep -v '^\.'
	@echo "Finished deploying the site to production with rsync."

.PHONY : preview build deploy-prod