package middleware

import (
	"gofly/internal/config"
	"gofly/internal/model/base"
	"gofly/pkg/ioc"
	"gofly/pkg/logx"
	"gofly/pkg/utils/gf"
	"gofly/pkg/utils/redis"
	"net/http"
	"strconv"
	"strings"
	"time"

	"github.com/dgrijalva/jwt-go"
	"github.com/gin-gonic/gin"
)

var (
	//自定义的token秘钥
	secret = []byte("168s98A2D3F8945Df489")
	// effectTime = 2 * time.Minute //两分钟
)

// token有效时间（纳秒）
var effectTime = time.Duration(getInit()) * time.Minute //分钟单位
// 写个返回int64-默认2个小时
func getInit() int64 {
	//加载配置
	num := config.Inst.App.TokenOutTime
	intnum, err := strconv.ParseInt(num, 10, 64)
	if err != nil {
		return 2 * 60 //默认2个小时
	} else {
		return intnum
	}
}

var (
	NoVerifyTokenRootMap = make(map[string]struct{})
	NoVerifyTokenMap     = make(map[string]struct{})
)

func init() {
	config.AddAfterConfigFn(InitNoVerifyToken)
}

func InitNoVerifyToken(c *config.Config) {
	if c.App.NoVerifyTokenRoot != "" {
		arr := strings.Split(c.App.NoVerifyTokenRoot, `,`)
		for _, item := range arr {
			NoVerifyTokenRootMap[item] = struct{}{}
		}
	}

	if c.App.NoVerifyToken != "" {
		arr := strings.Split(c.App.NoVerifyToken, `,`)
		for _, item := range arr {
			NoVerifyTokenMap[item] = struct{}{}
		}
	}
}

// 返回超时时间
func TokenOutTime(claims *base.SysUser) int64 {
	return time.Now().Add(effectTime).UnixMilli()
}

// 生成token
func GenerateToken(claims *base.SysUser) interface{} {
	//设置token有效期，也可不设置有效期，采用redis的方式
	//   1)将token存储在redis中，设置过期时间，token如没过期，则自动刷新redis过期时间，
	//   2)通过这种方式，可以很方便的为token续期，而且也可以实现长时间不登录的话，强制登录
	//本例只是简单采用 设置token有效期的方式，只是提供了刷新token的方法，并没有做续期处理的逻辑
	claims.ExpiresAt = time.Now().Add(effectTime).UnixMilli()
	//生成token
	sign, err := jwt.NewWithClaims(jwt.SigningMethodHS256, claims).SignedString(secret)
	if err != nil {
		//这里因为项目接入了统一异常处理，所以使用panic并不会使程序终止，如不接入，可使用原始方式处理错误
		//接入统一异常可参考 https://blog.csdn.net/u014155085/article/details/106733391
		panic(err)
	}
	return sign
	// return map[string]interface{}{"sign": sign, "expiresat": claims.ExpiresAt}
}

// JwtVerify 验证token
func JwtVerify(c *gin.Context) {
	redisClient := ioc.GetType[*redis.Client]()
	// 无需鉴权的根路径
	rootPath := strings.Split(c.Request.URL.Path, "/")
	if len(rootPath) > 2 {
		if _, ok := NoVerifyTokenRootMap[rootPath[1]]; ok {
			return
		}
	}
	// 无需鉴权的接口
	if _, ok := NoVerifyTokenMap[c.Request.URL.Path]; ok {
		return
	}

	// 带appKey的接口
	appKey := c.GetHeader(X_AK)
	if appKey != "" {
		AppKeyVerify(c, appKey)
		return
	}

	token := c.GetHeader("Authorization")
	if token == "" {
		c.AbortWithStatusJSON(http.StatusOK, gin.H{
			config.Inst.App.ResCodeName: http.StatusForbidden,
			config.Inst.App.ResMsgName:  "token 不存在",
			config.Inst.App.ResDataName: nil,
		})
		return
	}
	// 验证token，并存储在请求中
	user := parseToken(token)

	// 2、验证登录用户接口授权：接口需要鉴权，且用户没有所有权限
	if perm, has := gf.PermMap[c.Request.URL.Path]; has && !user.AllPerm {
		// 接口需要鉴权
		logx.Infof(perm)

		// 从redis中获取登录用户是否包含给定权限码
		res, err := redisClient.HGet(c, user.GetPermKey(), perm).Result()
		if err != nil || res != "1" {
			c.AbortWithStatusJSON(http.StatusOK, gin.H{
				config.Inst.App.ResCodeName: http.StatusForbidden,
				config.Inst.App.ResMsgName:  "接口未授权",
				config.Inst.App.ResDataName: nil,
			})
			return
		}

	}

	c.Set("user", user)
	c.Next()
}

// parseToken 解析Token
func parseToken(tokenString string) *base.SysUser {
	//解析token
	token, err := jwt.ParseWithClaims(tokenString, &base.SysUser{}, func(token *jwt.Token) (interface{}, error) {
		return secret, nil
	})
	if err != nil {
		panic(err)
	}
	claims, ok := token.Claims.(*base.SysUser)
	if !ok {
		panic("The token is invalid")
	}
	return claims
}

// 更新token
func Refresh(tokenString string) interface{} {
	jwt.TimeFunc = func() time.Time {
		return time.Unix(0, 0)
	}
	token, err := jwt.ParseWithClaims(tokenString, &base.SysUser{}, func(token *jwt.Token) (interface{}, error) {
		return secret, nil
	})
	if err != nil {
		panic(err)
	}
	claims, ok := token.Claims.(*base.SysUser)
	if !ok {
		panic("The token is invalid")
	}
	jwt.TimeFunc = time.Now
	claims.StandardClaims.ExpiresAt = time.Now().Add(effectTime).UnixMilli()
	return GenerateToken(claims)
}
