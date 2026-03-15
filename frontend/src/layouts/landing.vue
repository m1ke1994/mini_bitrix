<template>
  <slot />
</template>

<script setup>
useHead({
  link: [{ key: "landing-style-css", rel: "stylesheet", href: "/landing_mock/css/main.css" }],
});
</script>
