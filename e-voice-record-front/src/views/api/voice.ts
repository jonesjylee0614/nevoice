// 记录语音

import request from "@/service/request";

export function saveUserPrint(formData: FormData) {
    return request.post('/voice/print/saveUserPrint', formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      })
}

export function getUserInfo() {
    return request.get('/user/get_userinfo', {})
}
export function getUserPrints(userId:any) {
    return request.get('/voice/print/getUserPrints', {params:  {userId, pageSize: 100}})
}
