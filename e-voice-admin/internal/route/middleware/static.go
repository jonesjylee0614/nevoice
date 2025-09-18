package middleware

import (
	"compress/gzip"
	"embed"
	"fmt"
	"gofly/internal/config"
	"gofly/pkg/utils/collx"
	"net/http"
	"path"
	"strings"

	"github.com/gin-gonic/gin"
)

type StaticConfig struct {
	// 嵌入的文件系统
	FS *embed.FS
	// 静态资源在embed.FS中的路径前缀
	URLPrefix string
	// 浏览器缓存过期时间(秒)
	MaxAge int
	// 是否启用压缩
	EnableGzip bool
	// 需要压缩的文件类型
	CompressibleTypes []string
}

func Static(sc StaticConfig) gin.HandlerFunc {
	// 默认配置
	if sc.MaxAge == 0 {
		sc.MaxAge = 86400 // 1天
	}

	if len(sc.CompressibleTypes) == 0 {
		sc.CompressibleTypes = []string{
			".html", ".css", ".js", ".json", ".txt", ".xml",
			".svg", ".ttf", ".otf", ".eot", ".woff", ".woff2",
		}
	}

	contextPath := config.Inst.App.ContextPath

	return func(c *gin.Context) {

		// 判断是否为前端路径
		if !strings.HasPrefix(c.Request.URL.Path, contextPath+"/"+sc.URLPrefix) {
			c.Next()
			return
		}
		// 获取请求路径
		urlPath := c.Request.URL.Path
		index := false
		if strings.HasSuffix(urlPath, "/") {
			urlPath += "index.html"
			index = true
		}

		// 如果设置了URL前缀，需要将其添加到文件路径中
		filePath := strings.TrimPrefix(urlPath, contextPath)
		filePath = strings.TrimPrefix(filePath, "/")

		// 从embed.FS读取文件
		content, err := sc.FS.ReadFile(filePath)
		if err != nil {
			c.Next()
			return
		}

		c.Status(http.StatusOK)

		if index {
			_, _ = c.Writer.Write(content)
			c.Abort()
			return
		}

		// 设置基本响应头
		c.Header("Accept-Ranges", "bytes")
		c.Header("Cache-Control", fmt.Sprintf("public, max-age=%d", sc.MaxAge))

		// 检查是否需要压缩
		ext := strings.ToLower(path.Ext(filePath))
		needCompress := collx.ArrayAnyContains(sc.CompressibleTypes, ext)

		// 设置 Content-Type
		c.Header("Content-Type", getContentType(filePath))

		if sc.EnableGzip && needCompress {
			ae := c.Request.Header.Get("Accept-Encoding")

			if strings.Contains(ae, "gzip") {
				c.Header("Content-Encoding", "gzip")
				w := newGzipWriter(c)
				defer func(writer *gzip.Writer) {
					_ = writer.Close()
				}(w.writer)

				c.Writer = w
			}
		}

		// 发送完整文件
		_, _ = c.Writer.Write(content)
		c.Abort()
		return
	}
}

// 辅助函数：获取文件的 Content-Type
func getContentType(filepath string) string {
	ext := strings.ToLower(path.Ext(filepath))
	switch ext {
	case ".html":
		return "text/html; charset=utf-8"
	case ".css":
		return "text/css; charset=utf-8"
	case ".js":
		return "application/javascript; charset=utf-8"
	case ".json":
		return "application/json; charset=utf-8"
	case ".png":
		return "image/png"
	case ".jpg", ".jpeg":
		return "image/jpeg"
	case ".gif":
		return "image/gif"
	case ".svg":
		return "image/svg+xml"
	case ".woff":
		return "font/woff"
	case ".woff2":
		return "font/woff2"
	default:
		return "application/octet-stream"
	}
}

// gzip写入器
type gzipWriter struct {
	gin.ResponseWriter
	writer *gzip.Writer
}

func (g *gzipWriter) Write(data []byte) (int, error) {
	return g.writer.Write(data)
}

func (g *gzipWriter) WriteString(s string) (int, error) {
	return g.writer.Write([]byte(s))
}

func newGzipWriter(c *gin.Context) *gzipWriter {
	gz := gzip.NewWriter(c.Writer)
	return &gzipWriter{c.Writer, gz}
}
