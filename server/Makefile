ifeq ($(NO_MIRROR), 1)
PYPI := 
else
PYPI := -i https://pypi.tuna.tsinghua.edu.cn/simple/
endif

PEXFLAGS := -D src \
			-e app \
			$(PYPI) -r requirements.txt \
			-v

all: build/wechat_push_linux_x86_64-cp-36-cp36m.pex build/wechat_push_linux_x86_64-cp-37-cp37m.pex wechat_push_win_amd64-cp-37-cp37m.pex

build/wechat_push_linux_x86_64-cp-36-cp36m.pex: requirements.txt src/*.py
	pex -o $@ $(PEXFLAGS) \
		--python=python3.6 \
		--platform="linux_x86_64-cp-36-cp36m" 

build/wechat_push_linux_x86_64-cp-37-cp37m.pex: requirements.txt src/*.py
	pex -o $@ $(PEXFLAGS) \
		--python=python3.7 \
		--platform="linux_x86_64-cp-37-cp37m" 

build/wechat_push_win_amd64-cp-37-cp37m.pex: requirements.txt src/*.py
	pex -o $@ $(PEXFLAGS) \
		--platform="win_amd64-cp-37-cp37m" 

clean:
	rm -f *.pex
