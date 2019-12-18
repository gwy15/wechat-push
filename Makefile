VUE := wechat-push-vue
VUE_SRC = $(VUE)/src/* $(VUE)/public/* $(VUE)/.env $(VUE)/vue.config.js
INDEX_HTML := release/dist/index.html

ifeq ($(NO_MIRROR), 1)
PYPI :=
else
PYPI := -i https://pypi.tuna.tsinghua.edu.cn/simple/
endif
PEXFLAGS := -D src --no-index \
			$(PYPI) -r requirements.txt -v \
			-e app
PY_SRC := server/requirements.txt server/src/*.py
EXAMPLES = server/.env.example server/logging.json.example config/your-site.conf
PACK_EXAMPLES = .env.example logging.json.example your-site.conf

WIN_36_PLAT := win_amd64-cp-36-cp36m
WIN_37_PLAT := win_amd64-cp-37-cp37m
LINUX_36_PLAT = linux_x86_64-cp-36-cp36m
LINUX_37_PLAT = linux_x86_64-cp-37-cp37m

WIN_37_TARGET := wechat_push_win_amd64-cp-37-cp37m
LINUX_36_TARGET := wechat_push_linux_x86_64-cp-36-cp36m
LINUX_37_TARGET := wechat_push_linux_x86_64-cp-37-cp37m

.PHONY: windows linux docker

windows: release/$(WIN_37_TARGET).zip

linux: release/$(LINUX_36_TARGET).zip release/$(LINUX_37_TARGET).zip

docker:
	docker-compose build

# define zips
release/$(WIN_37_TARGET).zip: $(INDEX_HTML) release/$(WIN_37_TARGET).pex
	cp $(EXAMPLES) release/
	cd release && zip ../$@ $(PACK_EXAMPLES) -r dist $(WIN_37_TARGET).pex
	@echo $@ Done.

release/$(LINUX_36_TARGET).zip: $(INDEX_HTML) release/$(LINUX_36_TARGET).pex
	cp $(EXAMPLES) release/
	cd release && zip ../$@ $(PACK_EXAMPLES) -r dist $(LINUX_36_TARGET).pex
	@echo $@ Done.

release/$(LINUX_37_TARGET).zip: $(INDEX_HTML) release/$(LINUX_37_TARGET).pex
	cp $(EXAMPLES) release/
	cd release && zip ../$@ $(PACK_EXAMPLES) -r dist $(LINUX_37_TARGET).pex
	@echo $@ Done.

# define vue page build
$(INDEX_HTML): $(VUE_SRC)
	mkdir -p release
	cd $(VUE) && npm run build
	cp -rf $(VUE)/dist release/dist

# define pex build
release/$(WIN_37_TARGET).pex: $(PY_SRC)
	cd server && pex -o ../$@ $(PEXFLAGS) \
		--platform=$(WIN_37_PLAT)

release/$(LINUX_36_TARGET).pex: $(PY_SRC)
	cd server && pex -o ../$@ $(PEXFLAGS) \
		--python=python3.6 --platform=$(LINUX_36_PLAT)

release/$(LINUX_37_TARGET).pex: $(PY_SRC)
	cd server && pex -o ../$@ $(PEXFLAGS) \
		--python=python3.7 --platform=$(LINUX_37_PLAT)
