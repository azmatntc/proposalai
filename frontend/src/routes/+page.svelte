<script lang="ts">
  import { onMount } from "svelte";
  import { goto } from "$app/navigation";
  import { auth } from "$lib/stores/auth.svelte";

  onMount(() => {
    if (auth.isAuthenticated) {
      goto("/dashboard");
    } else {
      goto("/login");
    }
  });
</script>

<div
  class="min-h-screen flex items-center justify-center bg-gray-50 dark:bg-gray-950"
>
  <div
    class="w-8 h-8 border-2 border-blue-500 border-t-transparent rounded-full animate-spin"
  ></div>
</div>
