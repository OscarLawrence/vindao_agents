<template>
    <div id="message-container" class="flex flex-col p-4" v-if="session">
        <Message v-for="msg, i in session.state.messages" :key="i" :message="msg" />
        <UChatPrompt v-model="message" @submit="onSubmit" />
    </div>
    <div v-else>
        <USkeleton />
    </div>
    
</template>

<script setup lang="ts">
import { nextTick, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import {getTextFromMessage} from '@nuxt/ui/utils/ai'

const route = useRoute()

const { session } = useSession(route.params.session)

const message = ref('')

const messages = computed(() => session.value ? session.value.state.messages.map(message => {
    return {
        role: message.role,
        parts: [
            {
                type: 'markdown',
                text: message.content
            }
        ]
    }
}) : [])

const scrollToBottom = () => {
    nextTick(() => {
        const container = document.querySelector('#message-container')
        if (container) {
            container.scrollTop = container.scrollHeight
        }
    })
}

const onSubmit = () => {
    if (message.value.trim() === '') return
    session.value.state.messages.push({
        role: 'user',
        content: message.value
    })
    message.value = ''
    nextTick(() => {
        scrollToBottom()
    })
    sendMessage(JSON.stringify(session.value))
}

const onmessage = (event: MessageEvent) => {
    const data = JSON.parse(event.data)
    if (data.type === 'content') {
        const lastMessage = session.value.state.messages[session.value.state.messages.length - 1]
        if (lastMessage.role !== 'assistant') {
            session.value.state.messages.push({
                role: 'assistant',
                content: ''
            })
        }
        session.value.state.messages[session.value.state.messages.length - 1] = {
            ...session.value.state.messages[session.value.state.messages.length - 1],
            content: session.value.state.messages[session.value.state.messages.length - 1].content + data.data
        }
        nextTick(() => {
            scrollToBottom()
        })
    }
    console.log(data)
    if (data.type === 'tool') {
        session.value.state.messages.push({
            role: 'tool',
            content: data.data
        })
        nextTick(() => {
            scrollToBottom()
        })
    }
}

onMounted(() => {
    scrollToBottom()
})

const {sendMessage} = useWebsocket(onmessage)


</script>