# make pex
cd server
cp .env.example ../release/.env # copy default env
cp logging.json ../release/logging.json # copy default logging settings
# make windows py37
make build/wechat_push_win_amd64-cp-37-cp37m.pex
cp build/wechat_push_win_amd64-cp-37-cp37m.pex ../release/
cd ..

# make zip
cd release
zip wechat_push_win_amd64-cp-37-cp37m.zip -0 -q -r dist wechat_push_win_amd64-cp-37-cp37m.pex .env logging.json

rm *.pex
