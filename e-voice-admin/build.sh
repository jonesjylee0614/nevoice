#!/bin/bash

ADMIN_NAME=admin-front.tar.gz
H5_NAME=h5-record-front.tar.gz
PYTHON_NAME=python-backend.tar.gz
BACKEND_NAME=gofly

ADMIN_PATH=../e-voice-admin-front/
H5_PATH=../e-voice-record-front/
PYTHON_PATH=../e-voice/
BACKEND_PATH=../e-voice-admin/

# 打包cms前端
cd $ADMIN_PATH
pnpm i
pnpm run build
tar -zcf ../$ADMIN_NAME dist/

# 打包h5前端
cd $H5_PATH
pnpm i
pnpm run build
tar -zcf ../$H5_NAME dist/

# 打包python
cd ..
tar -zcf $PYTHON_NAME e-voice/

cd ./e-voice-admin
# 打包go后端
go mod tidy
rm -rf $BACKEND_NAME
CGO_ENABLED=0 GOOS=linux GOARCH=amd64 go build -ldflags="-s -w" -o ../$BACKEND_NAME main.go
upx --best --lzma $BACKEND_NAME

# 打包多个压缩包为一个压缩包
cd ..
tar -czf evoice.tar.gz --remove-files $ADMIN_NAME  $H5_NAME $PYTHON_NAME $BACKEND_NAME
