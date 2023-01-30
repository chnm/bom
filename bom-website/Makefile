preview :
	@echo "Serving the preview site with Hugo ..."
	hugo serve --buildDrafts --buildFuture --disableFastRender 

build :
	@echo "\nBuilding the site with Hugo ..."
	hugo --cleanDestinationDir --buildDrafts --buildFuture --baseURL http://hugo.deathbynumbers.org/
	@echo "Website finished building."

.PHONY : preview build