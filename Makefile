BUILD_DIR          = _build
BUNDLE_NAME        = buildkite
WORK_DIR           = $(BUILD_DIR)/$(BUNDLE_NAME)
SRC_DIRS           = bin commands meta templates lib
SRC_FILES          = $(foreach dir, $(SRC_DIRS), $(wildcard $(dir)/*))

.PHONY: make-bundle validate-config

all: $(BUNDLE_NAME).cog

clean:
	rm -rf $(BUNDLE_NAME).cog _build manifest.json
	find . -name "*.pyc" | xargs rm -v

install:
	pip install -r meta/requirements.txt --user

$(BUNDLE_NAME).cog: Makefile manifest.json config.yml $(SRC_FILES)
	make validate-config
	mkdir -p $(WORK_DIR)
	cp manifest.json config.yml $(WORK_DIR)
	cp -R $(SRC_DIRS) $(WORK_DIR)/
	cd $(BUILD_DIR) && zip -r $(BUNDLE_NAME).cog $(BUNDLE_NAME)
	mv $(BUILD_DIR)/$(BUNDLE_NAME).cog .

validate-config: scripts/validate.py
	@scripts/validate.py

manifest.json: $(SRC_FILES) scripts/package.py
	scripts/package.py
