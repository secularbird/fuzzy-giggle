<script setup lang="ts">
import { computed } from 'vue';
import { useRoute } from 'vue-router';
import UserLayout from './components/UserLayout.vue';
import AdminLayout from './components/AdminLayout.vue';

const route = useRoute();
const isAdmin = computed(() => route.meta.layout === 'admin');
</script>

<template>
  <component :is="isAdmin ? AdminLayout : UserLayout">
    <router-view />
  </component>
</template>