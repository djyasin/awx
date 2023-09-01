# UI TASKS
# --------------------------------------

UI_BUILD_FLAG_FILE = awx/ui/.ui-built

clean-ui:
	rm -rf node_modules
	rm -rf awx/ui/node_modules
	rm -rf awx/ui/build
	rm -rf awx/ui/src/locales/_build
	rm -rf $(UI_BUILD_FLAG_FILE)
        # the collectstatic command doesn't like it if this dir doesn't exist.
	mkdir -p awx/ui/build/static

awx/ui/node_modules:
	NODE_OPTIONS=--max-old-space-size=6144 $(NPM_BIN) --prefix awx/ui --loglevel warn --force ci

$(UI_BUILD_FLAG_FILE):
	$(MAKE) awx/ui/node_modules
	$(PYTHON) tools/scripts/compilemessages.py
	$(NPM_BIN) --prefix awx/ui --loglevel warn run compile-strings
	$(NPM_BIN) --prefix awx/ui --loglevel warn run build
	touch $@

ui-release: $(UI_BUILD_FLAG_FILE)

ui-devel: awx/ui/node_modules
	@$(MAKE) -B $(UI_BUILD_FLAG_FILE)
	@if [ -d "/var/lib/awx" ] ; then \
		mkdir -p /var/lib/awx/public/static/css; \
		mkdir -p /var/lib/awx/public/static/js; \
		mkdir -p /var/lib/awx/public/static/media; \
		cp -r awx/ui/build/static/css/* /var/lib/awx/public/static/css; \
		cp -r awx/ui/build/static/js/* /var/lib/awx/public/static/js; \
		cp -r awx/ui/build/static/media/* /var/lib/awx/public/static/media; \
	fi

ui-devel-instrumented: awx/ui/node_modules
	$(NPM_BIN) --prefix awx/ui --loglevel warn run start-instrumented

ui-devel-test: awx/ui/node_modules
	$(NPM_BIN) --prefix awx/ui --loglevel warn run start

ui-lint:
	$(NPM_BIN) --prefix awx/ui install
	$(NPM_BIN) run --prefix awx/ui lint
	$(NPM_BIN) run --prefix awx/ui prettier-check

ui-test:
	$(NPM_BIN) --prefix awx/ui install
	$(NPM_BIN) run --prefix awx/ui test

ui-test-screens:
	$(NPM_BIN) --prefix awx/ui install
	$(NPM_BIN) run --prefix awx/ui pretest
	$(NPM_BIN) run --prefix awx/ui test-screens --runInBand

ui-test-general:
	$(NPM_BIN) --prefix awx/ui install
	$(NPM_BIN) run --prefix awx/ui pretest
	$(NPM_BIN) run --prefix awx/ui/ test-general --runInBand
