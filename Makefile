preview :
	@echo "Serving the preview site with Hugo ..."
	hugo serve --buildDrafts --buildFuture --disableFastRender

build :
	@echo "\nBuilding the site with Hugo ..."
	hugo --cleanDestinationDir --minify
	@echo "Website finished building."

deploy : build
	@echo "\nDeploying the site with rsync ..."
	rsync --delete --itemize-changes --omit-dir-times \
		--checksum -avz --no-perms \
		public/ athena:/websites/bom/www/ | egrep -v '^\.'
	@echo "Finished deploying the site with rsync."

.PHONY : preview build deploy