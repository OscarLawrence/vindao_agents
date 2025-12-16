<template>
    <UNavigationMenu :items="navigationItems" />
</template>

<script setup lang="ts">
import type {NavigationMenuItem} from '@nuxt/ui'

const navigationItems: NavigationMenuItem[] = [
  { label: 'Home', to: '/' },
  { label: 'Config', to: '/config' }
]

</script>

<style>

</style>