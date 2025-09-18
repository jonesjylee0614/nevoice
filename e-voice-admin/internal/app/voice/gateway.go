package voice

import (
    "io"
    "net/http"
    "net/url"
    "strings"
    "time"

    "gofly/internal/config"
    "gofly/pkg/utils/gf"
    "gofly/pkg/utils/results"
    "github.com/gin-gonic/gin"
)

// Gateway 语音服务网关（HTTP转发）
// 统一通过 e-voice-admin 访问 Python 语音服务，便于鉴权与跨域收口
type Gateway struct{}

func init() { gf.RegisterRoute(&Gateway{}) }

// VoiceRecognizeOffline 转发离线识别 /voice/gateway/voice-recognize-offline
func (g *Gateway) VoiceRecognizeOffline(c *gin.Context) {
    py := config.Inst.App.Micro[pyVoiceServer].Host
    target := py + "/voice-recognize-offline"

    files, form := gf.ReqMultipartForm(c, "audio")
    // 将 language 透传
    params := map[string]any{}
    if v, has := form.Value["language"]; has && len(v) > 0 { params["language"] = v[0] }

    req := gf.NewHttpRequest(target)
    res := req.PostMultipart(files, params)
    body, err := res.BodyBytes()
    results.ResRaw(c, body, err)
}

// VoiceRecognizeOnline 转发在线识别 /voice/gateway/voice-recognize-online
func (g *Gateway) VoiceRecognizeOnline(c *gin.Context) {
    py := config.Inst.App.Micro[pyVoiceServer].Host
    target := py + "/voice-recognize-online"

    // 直接透传JSON
    data, _ := io.ReadAll(c.Request.Body)
    httpReq, _ := http.NewRequest(http.MethodPost, target, strings.NewReader(string(data)))
    httpReq.Header.Set("Content-Type", "application/json")
    httpClient := &http.Client{ Timeout: 30 * time.Second }
    resp, err := httpClient.Do(httpReq)
    if err != nil { results.ResError(c, err); return }
    defer resp.Body.Close()
    c.Data(resp.StatusCode, resp.Header.Get("Content-Type"), gf.MustReadAll(resp.Body))
}

// WSRecognize 代理 WebSocket /voice/gateway/ws/recognize -> {py}/ws/recognize
// 采用 101 切换协议的原始代理，前端可统一走本域名。
// 兼容前端 '/voice/gateway/wsRecognize' 路径
func (g *Gateway) WsRecognize(c *gin.Context) {
    // 简化实现：返回目标WS地址，前端据此直连，避免在此实现复杂的WS中继
    // 若需要真正的WS反向代理，可引入 gorilla/websocket 与 fasthttp/websocket 进行中继
    py := config.Inst.App.Micro[pyVoiceServer].Host
    u, _ := url.Parse(py)
    scheme := "ws"
    if strings.HasPrefix(u.Scheme, "https") { scheme = "wss" }
    ws := scheme + "://" + u.Host + "/ws/recognize"
    results.ResObj(c, gin.H{"ws": ws}, nil)
}

// Perms 声明需要鉴权的接口，可按需补充
func (g *Gateway) Perms() map[string][]gin.HandlerFunc {
    // 网关接口默认不纳入权限校验，由全局白名单控制
    return nil
}


