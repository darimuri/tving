#!/bin/bash

rm -rf plugin.video.tving/api.py plugin.video.tving.zip ${HOME}/plugin.video.tving.zip
cp -a api.py plugin.video.tving/
zip -r plugin.video.tving.zip plugin.video.tving
mv plugin.video.tving.zip ${HOME}/
