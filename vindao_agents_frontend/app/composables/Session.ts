import {useSessions} from './Sessions'

export const useSession = (sessionId: string) => {
    const { sessions } = useSessions()

    const session = computed(() => {
        if (!sessions.value) {
            return null
        }
        return sessions.value[sessionId] || null
    })

    return {
        session
    }
}