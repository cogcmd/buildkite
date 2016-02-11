BUILD_DIR          = _build
BUNDLE_NAME        = buildkite
WORK_DIR           = $(BUILD_DIR)/$(BUNDLE_NAME)
SRC_FILES          = $(wildcard bin/*) $(wildcard commands/*) $(wildcard lib/*) $(wildcard meta/*) $(wildcard templates/*)

.PHONY: make-bundle validate-config

all: $(BUNDLE_NAME).cog

clean:
	rm -rf $(BUNDLE_NAME).cog _build manifest.json
	find . -name "*.pyc" | xargs rm -v

$(BUNDLE_NAME).cog: manifest.json config.json $(SRC_FILES)
	make validate-config
	mkdir -p $(WORK_DIR)
	cp manifest.json config.json $(WORK_DIR)
	cp -R bin $(WORK_DIR)
	cp -R commands $(WORK_DIR)
	cp -R lib $(WORK_DIR)
	cp -R meta $(WORK_DIR)
	cp -R templates $(WORK_DIR)
	cd $(BUILD_DIR) && zip -r $(BUNDLE_NAME).cog $(BUNDLE_NAME)
	mv $(BUILD_DIR)/$(BUNDLE_NAME).cog .

validate-config: scripts/validate.py
	@scripts/validate.py

manifest.json: $(SRC_FILES) scripts/package.py
	scripts/package.py
