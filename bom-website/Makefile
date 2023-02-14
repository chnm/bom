preview :
	@echo "Serving the preview site with Hugo ..."
	hugo serve --buildDrafts --buildFuture --disableFastRender 

build :
	@echo "\nBuilding the site with Hugo ..."
	hugo --cleanDestinationDir --buildDrafts --buildFuture --baseURL https://deathbynumbers.org/
	@echo "Website finished building."

build-prod :
	@echo "\nBuilding the site with Hugo ..."
	hugo --cleanDestinationDir --minify
	@echo "Website finished building."

deploy-prod : build-prod
	@echo "\nDeploying the site to production with rsync ..."
	rsync --delete --itemize-changes --omit-dir-times \
		--checksum -avz --no-t --no-perms --exclude-from=rsync-excludes \
		public/ susanoo:/websites/deathbynumbers.org/ | egrep -v '^\.'
	@echo "Finished deploying the site to production with rsync."

.PHONY : preview build deploy