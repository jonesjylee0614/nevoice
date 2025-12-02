#!/bin/bash
# 打包cms前端

# 打包h5前端

# 打包python

# 打包go后端
go mod tidy
CGO_ENABLED=0 GOOS=linux GOARCH=amd64 go build -ldflags="-s -w" -o gofly main.go
upx gofly