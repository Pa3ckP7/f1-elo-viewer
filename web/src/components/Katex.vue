<script setup lang="ts">
import { computed } from 'vue'
import katex from 'katex'

const props = withDefaults(defineProps<{ expr: string; display?: boolean }>(), {
  display: false,
})

const html = computed(() =>
  katex.renderToString(props.expr, { displayMode: props.display, throwOnError: false }),
)
</script>

<template>
  <span v-html="html" />
</template>
