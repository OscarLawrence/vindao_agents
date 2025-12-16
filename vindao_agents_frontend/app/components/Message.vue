<template>
    <div :class="`${message.role}_message`" class="p-2 m-4">
       <article v-if="message.role === 'assistant'" v-html="md.render(message.content)" />
        <article v-else-if="message.role !== 'user'" v-html="message.content.replace(/\n/g, '<br />').replaceAll('    ', '&nbsp;&nbsp;&nbsp;&nbsp;')" />
        <article v-else>{{ message.content }}</article>
    </div>
</template>

<script setup lang="ts">
import markdownit from 'markdown-it'

const md = markdownit({
  html: true,
  linkify: true,
  typographer: true
})

interface MessageI {
    role: 'user' | 'assistant' | 'system' | 'tool'
    content: string
}

const props = defineProps<{
  message: MessageI
}>()
</script>

<style scoped>
.system_message {
    color: gray;
    font-style: italic;
}
.user_message {
    text-align: left;
    background-color: #DCF8C6;
    border-radius: 8px;
    max-width: 50%;
    margin-left: auto;
}
.assistant_message {
    text-align: left;
    background-color: #F0F0F0;
    border-radius: 8px;
    max-width: 50%;
    margin-right: auto;
    list-style: initial;
}
.tool_message {
    text-align: left;
    background-color: #F0F0F0;
    border-radius: 8px;
    font-family: monospace;
    max-width: 80%;
    margin: 0 auto
}
</style>