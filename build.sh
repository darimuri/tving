#!/bin/bash

rm -rf plugin.video.tving/resources/lib/*
cp -a tving plugin.video.tving/resources/lib/
zip -r plugin.video.tving.zip plugin.video.tving