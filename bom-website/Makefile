preview :
	@echo "Serving the preview site with Hugo ..."
	hugo serve --buildDrafts --buildFuture --disableFastRender 

build :
	@echo "\nBuilding the dev site with Hugo ..."
	hugo --cleanDestinationDir --buildDrafts --buildFuture --baseURL http://dev.deathbynumbers.org/
	@echo "Website finished building."

build-prod :
	@echo "\nBuilding the prod site with Hugo ..."
	hugo --cleanDestinationDir --minify --baseURL https://deathbynumbers.org/
	@echo "Website finished building."

.PHONY : preview build-prod