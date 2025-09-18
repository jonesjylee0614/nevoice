package meeting

import (
	"gofly/internal/app/meeting"
	"gofly/pkg/ioc"
	"gofly/pkg/openapi"
)

func Init() {
	t := ioc.GetType[*meeting.Offline]()
	reqs := []*openapi.PathDoc{

		//
		openapi.NewPathDoc().
			Handler(t.Save).State(1).
			Name("创建离线会议").
			Note("通过上传离线会议音频，自动识别发言人，拆分发言文字").
			ReqType(openapi.ReqTypeForm).
			ReqParams(
				openapi.NewPathParameter("name", "query", "会议名", "string", "form", true),
				openapi.NewPathParameter("meetingTime", "query", "会议时间 格式 yyyy-MM-dd HH:mm:ss", "string", "form", true),
				openapi.NewPathParameter("audio", "query", "音频文件", "file", "form", true),
			),
	}

	doc := &openapi.GroupDoc{
		GroupName: "离线会议",
		Order:     2,
		Paths:     reqs,
	}
	openapi.RegisterGroupDoc(doc)
}

func init() {
	ioc.AddPostIocFunc(Init)
}
