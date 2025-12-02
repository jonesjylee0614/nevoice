package voice

import (
	"gofly/internal/app/voice"
	"gofly/internal/domain/dto"
	"gofly/internal/model/base"
	"gofly/internal/model/core"
	"gofly/pkg/ioc"
	"gofly/pkg/openapi"
)

func Init() {
	t := ioc.GetType[*voice.Print]()
	reqs := []*openapi.PathDoc{

		openapi.NewPathDoc().
			Handler(t.GetUserList).State(1).
			Name("获取用户列表").
			Note("该列表的用户需要有[声纹注册用户]角色权限").
			ReqType(openapi.ReqTypeForm).
			Req(dto.VoicePrintPageReq{}).
			Res(base.PageResult[core.BusinessAccount]{}),

		openapi.NewPathDoc().
			Handler(t.GetUserPrints).
			Name("获取用户声纹列表").State(1).
			ReqType(openapi.ReqTypeForm).
			Req(dto.VoiceUserPrintPageReq{}).
			Res(base.PageResult[dto.VoiceUserPrintPageData]{}),

		openapi.NewPathDoc().
			Handler(t.SaveUserPrint).
			Name("保存用户声纹信息").State(1).
			ReqType(openapi.ReqTypeForm).
			ReqParams(
				openapi.NewPathParameter("userId", "query", "用户id", "int", "form", true),
				openapi.NewPathParameter("userName", "query", "用户姓名", "string", "form", true),
				openapi.NewPathParameter("audio", "query", "音频文件", "file", "form", true),
			),

		openapi.NewPathDoc().
			Handler(t.Del).
			Name("删除用户声纹").State(1).
			ReqType(openapi.ReqTypeJson).
			Req(dto.VoiceUserPrintDelReq{}),

		openapi.NewPathDoc().
			Handler(t.H5url).
			Name("生成用户h5url").State(1).
			ReqType(openapi.ReqTypeJson).
			Req(dto.BaseUserIdReq{}),

		openapi.NewPathDoc().
			Handler(t.Identify).State(1).
			Name("声纹鉴定").
			Note("上传或录制音频,返回声纹鉴定结果及文字信息").
			ReqType(openapi.ReqTypeForm).
			ReqParams(openapi.NewPathParameter("audio", "query", "音频文件", "file", "form", true)).
			Res(dto.UserPrintIdentifyRes{}),
	}

	doc := &openapi.GroupDoc{
		GroupName: "声纹管理",
		Order:     1,
		Paths:     reqs,
	}
	openapi.RegisterGroupDoc(doc)
}

func init() {
	ioc.AddPostIocFunc(Init)
}
