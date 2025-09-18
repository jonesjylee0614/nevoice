package statics

import "embed"

//go:embed openapi/*
var ApiFiles embed.FS
