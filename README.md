# tving

#### VSCode development
##### Use venv for python2
```
py -2 -m pip install --upgrade pip
py -2 -m pip install virtualenv

py -2 -m virtualenv .venv
source .venv/bin/activate
```
##### Use venv for python3
```
py -3 -m venv .venv
source .venv/bin/activate
```

#### Build
```
rm -rf plugin.video.tving/api.py
cp -a api.py plugin.video.tving/
zip -r plugin.video.tving.zip plugin.video.tving
```