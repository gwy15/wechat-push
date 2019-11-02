wechat.pex: requirements.txt src/*.py
	pex -o wechat.pex \
		-D src \
		-e app \
		-r requirements.txt \
		-i https://pypi.tuna.tsinghua.edu.cn/simple/ \
		--platform="linux_x86_64-cp-37-cp37m" \
		-v
