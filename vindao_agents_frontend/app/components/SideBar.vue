<template>
    <div class="w-[10vw] min-h-screen">
      <UNavigationMenu orientation="vertical" :items="navigationItems" />
    </div>
 
</template>

<script setup lang="ts">
import type {NavigationMenuItem} from '@nuxt/ui'
import { useAsyncData } from 'nuxt/app'

const {sessions, navSessions} = useSessions()  



const navigationItems: NavigationMenuItem[] = computed(() =>[
  navSessions.value
])

</script>

<style>

</style>