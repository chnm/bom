preview :
	@echo "Serving the preview site with Hugo ..."
	hugo serve --buildDrafts --buildFuture --disableFastRender 

build :
	@echo "\nBuilding the dev site with Hugo ..."
	hugo --cleanDestinationDir --buildDrafts --buildFuture --baseURL http://dev.deathbynumbers.org/
	@echo "Building search index with Pagefind ..."
	npx -y pagefind --site public
	@echo "Website finished building."

build-prod :
	@echo "\nBuilding the prod site with Hugo ..."
	hugo --cleanDestinationDir --minify --baseURL https://deathbynumbers.org/
	@echo "Building search index with Pagefind ..."
	npx -y pagefind --site public
	@echo "Website finished building."

tailwind :
	@echo "\nBuilding the tailwind css ..."
	cd themes/dbn && npm run build-tw
	@echo "Tailwind css finished building."
	cd ../../

.PHONY : preview build-prod