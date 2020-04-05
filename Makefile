VUE := wechat-push-vue
VUE_SRC = $(VUE)/src/* $(VUE)/public/* $(VUE)/.env $(VUE)/vue.config.js
INDEX_HTML := release/dist/index.html

ifeq ($(NO_MIRROR), 1)
PYPI :=
else
PYPI := -i https://pypi.tuna.tsinghua.edu.cn/simple/
endif
PEXFLAGS := -D src \
			$(PYPI) -r requirements.txt -v \
			-e app
PY_SRC := server/requirements.txt server/src/*.py
EXAMPLES = server/.env.example server/logging.json.example config/your-site.conf
PACK_EXAMPLES = .env.example logging.json.example your-site.conf

WIN_37_TARGET := wechat_push_win_amd64-cp-37-cp37m
LINUX_37_TARGET := wechat_push_linux_x86_64-cp-37-cp37m

.PHONY: windows linux docker

windows: release/$(WIN_37_TARGET).zip

linux: release/$(LINUX_37_TARGET).zip

docker:
	docker-compose build

# define zips
release/$(WIN_37_TARGET).zip: $(INDEX_HTML) release/$(WIN_37_TARGET).pex
	cp $(EXAMPLES) release/
	cd release && zip ../$@ $(PACK_EXAMPLES) -r dist $(WIN_37_TARGET).pex
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
	cd server && pex -o ../$@ $(PEXFLAGS)

release/$(LINUX_37_TARGET).pex: $(PY_SRC)
	cd server && python3.7 -m pex -o ../$@ $(PEXFLAGS)
