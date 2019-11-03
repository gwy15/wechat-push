VUE := wechat-push-vue
VUE_SRC = $(VUE)/src/* $(VUE)/public/* $(VUE)/.env $(VUE)/vue.config.js
INDEX_HTML := release/dist/index.html

ifeq ($(NO_MIRROR), 1)
PYPI := " "
else
PYPI := -i https://pypi.tuna.tsinghua.edu.cn/simple/
endif
PEXFLAGS := -D src -e app \
			$(PYPI) -r requirements.txt -v -v
PY_SRC := server/requirements.txt server/src/*.py
EXAMPLES = server/.env.example server/logging.json.example

WIN_36_PLAT := win_amd64-cp-36-cp36m
WIN_37_PLAT := win_amd64-cp-37-cp37m
LINUX_36_PLAT = linux_x86_64-cp-36-cp36m
LINUX_37_PLAT = linux_x86_64-cp-37-cp37m

WIN_TARGET := wechat_push_win_amd64-cp-37-cp37m
LINUX_TARGET := wechat_push_linux_x86_64


.PHONY: windows linux

windows: release/$(WIN_TARGET).zip

linux: release/$(LINUX_TARGET).zip

# define zips
release/$(WIN_TARGET).zip: $(INDEX_HTML) release/$(WIN_TARGET).pex
	cp $(EXAMPLES) release/
	cd release && zip ../$@ .env.example logging.json.example -r dist $(WIN_TARGET).pex
	@echo $@ Done.

release/$(LINUX_TARGET).zip: $(INDEX_HTML) release/$(LINUX_TARGET).pex
	cp $(EXAMPLES) release/
	cd release &&  zip ../$@ .env.example logging.json.example -r dist $(LINUX_TARGET).pex
	@echo $@ Done.

# define vue page build
$(INDEX_HTML): $(VUE_SRC)
	cd $(VUE) && npm run build
	cp -rf $(VUE)/dist release/dist

# define pex build
release/$(WIN_TARGET).pex: $(PY_SRC)
	cd server && pex -o ../$@ $(PEXFLAGS) \
		--platform=$(WIN_37_PLAT)

release/$(LINUX_TARGET).pex: $(PY_SRC)
	cd server && pex -o ../$@ $(PEXFLAGS) \
		--python=python3.6 --python=python3.7 \
		--platform=$(LINUX_36_PLAT) --platform=$(LINUX_37_PLAT)

