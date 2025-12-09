import { defineStore } from 'pinia'
import type { Meeting, MeetingDetail, MeetingDialog, Participant } from '@/api/types'

export const useMeetingStore = defineStore('meeting', {
  state: () => ({
    // 会议列表
    meetings: [] as Meeting[],
    // 当前会议详情
    currentMeeting: null as MeetingDetail | null,
    // 加载状态
    loading: false,
    // 人员列表（用于指定发言人）
    staffList: [] as Participant[]
  }),

  getters: {
    // 获取进行中的会议
    ongoingMeetings: (state) => state.meetings.filter(m => m.status === 1),
    // 获取已结束的会议
    completedMeetings: (state) => state.meetings.filter(m => m.status === 2)
  },

  actions: {
    setMeetings(meetings: Meeting[]) {
      this.meetings = meetings
    },
    
    setCurrentMeeting(meeting: MeetingDetail | null) {
      this.currentMeeting = meeting
    },

    addDialog(dialog: MeetingDialog) {
      if (this.currentMeeting) {
        this.currentMeeting.dialogs = [...(this.currentMeeting.dialogs || []), dialog]
        this.currentMeeting.dialogCount = this.currentMeeting.dialogs.length
      }
    },

    updateDialog(dialogId: number, updates: Partial<MeetingDialog>) {
      if (this.currentMeeting?.dialogs) {
        const index = this.currentMeeting.dialogs.findIndex(d => d.id === dialogId)
        if (index !== -1) {
          this.currentMeeting.dialogs[index] = {
            ...this.currentMeeting.dialogs[index],
            ...updates
          }
        }
      }
    },

    clearDialogs() {
      if (this.currentMeeting) {
        this.currentMeeting.dialogs = []
        this.currentMeeting.dialogCount = 0
      }
    },

    setSummary(summary: string) {
      if (this.currentMeeting) {
        this.currentMeeting.summary = summary
        this.currentMeeting.summaryStatus = 2
      }
    },

    setStaffList(list: Participant[]) {
      this.staffList = list
    },

    setLoading(loading: boolean) {
      this.loading = loading
    }
  }
})
