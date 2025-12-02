// 记录语音

import request from "@/service/request";

export function register(formData: FormData) {
    return request.post('/voice-register', formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      })
}

export function getUserInfo(token: string) {
    return request.post('/getUserInfo', {token}, {})
}