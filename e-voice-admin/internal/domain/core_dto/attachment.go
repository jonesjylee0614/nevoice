package core_dto

import (
	"gofly/internal/model/base"
)

type AttachmentPage struct {
	base.IPage
	CreatedTime string `form:"createdTime" json:"createdTime"`
	Name        string `form:"name" json:"name"`
	Status      string `form:"status" json:"status"`
}
type CommonPicturePage struct {
	base.IPage
	CreatedTime string `form:"createdTime" json:"createdTime"`
	Cid         int64  `form:"cid" json:"cid"`
	Type        int64  `form:"type" json:"type"`
	Title       string `form:"title" json:"title"`
}

type MyAttachmentReq struct {
	Searchword string `form:"searchword" json:"searchword"`
	Filetype   string `form:"filetype" json:"filetype" default:"image"`
	Pid        int64  `form:"pid" json:"pid" default:"0"`
}

type UpImgPidReq struct {
	Imgid int64 `form:"imgid" json:"imgid" binding:"required"`
	Pid   int64 `form:"pid" json:"pid" binding:"required"`
}
