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
			dist/ chnmdev:/websites/bomdev/www | egrep -v '^\.'
	@echo "Finished deploying the site to dev with rsync."

build-prod : 
	@echo "\nBuilding the site with Nuxt ..."
	npm run generate 
	@echo "Website finished building."

.PHONY : preview build deploy