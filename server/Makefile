ifeq ($(NO_MIRROR), 1)
PYPI := 
else
PYPI := -i https://pypi.tuna.tsinghua.edu.cn/simple/
endif

PEXFLAGS := -D src \
			-e app \
			-r requirements.txt \
			$(PYPI) -v

all: build/wechat_py36.pex build/wechat_py37.pex

build/wechat_py36.pex: requirements.txt src/*.py
	mkdir -p build
	pex -o $@ $(PEXFLAGS) \
		--python=python3.6 \
		--platform="linux_x86_64-cp-36-cp36m" 

build/wechat_py37.pex: requirements.txt src/*.py
	mkdir -p build
	pex -o $@ $(PEXFLAGS) \
		--python=python3.7 \
		--platform="linux_x86_64-cp-37-cp37m" 

clean:
	rm -f *.pex
