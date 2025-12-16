

export const useSessions = () => {
    const loading = useState('sessions_loading', () => true)
  const sessions = useState('sessions', () => (null))

    if (loading.value) {
      // Fetch sessions data
      $fetch('http://localhost:8000/sessions')
        .then((data) => {
          sessions.value = data
        })
        .finally(() => {
          loading.value = false
        })
    }

    const navSessions = computed(() => {
        if (!sessions.value) {
            return []
        }
      return Object.values(sessions.value).sort((a, b) => b['state']['updated_at'] < a['state']['updated_at'] ? -1 : 1).map((session) => {
      return { label: session['state']['session_id'], to: `/session/${session['state']['session_id']}` }
    })
    })

  return {
    sessions,
    navSessions
  }
}