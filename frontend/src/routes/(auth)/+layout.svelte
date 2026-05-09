<script lang="ts">
  import { auth } from '$lib/stores/auth.svelte';
  import { goto } from '$app/navigation';
  let { children } = $props();
  $effect(() => {
    if (!auth.isLoading && auth.isAuthenticated) goto('/dashboard');
  });
</script>
<div class="min-h-screen bg-gradient-to-br from-blue-50 via-white to-indigo-50 dark:from-gray-950 dark:via-gray-900 dark:to-gray-950 flex items-center justify-center p-4">
  {@render children()}
</div>
