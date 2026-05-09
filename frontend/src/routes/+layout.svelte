<script lang="ts">
  import "../app.css";
  import { onMount } from "svelte";
  import { auth } from "$lib/stores/auth.svelte";
  import { ui } from "$lib/stores/ui.svelte";

  let { children } = $props();

  onMount(() => {
    auth.init();
    const saved = localStorage.getItem("theme") as
      | "light"
      | "dark"
      | "system"
      | null;
    if (saved) ui.theme = saved;
    applyTheme();
    window
      .matchMedia("(prefers-color-scheme: dark)")
      .addEventListener("change", applyTheme);
  });

  function applyTheme() {
    const dark =
      ui.theme === "dark" ||
      (ui.theme === "system" &&
        window.matchMedia("(prefers-color-scheme: dark)").matches);
    document.documentElement.classList.toggle("dark", dark);
  }

  $effect(() => {
    if (typeof window !== "undefined") applyTheme();
  });
</script>

{@render children()}

<!-- Global toast notifications -->
{#if ui.toasts.length > 0}
  <div
    class="fixed bottom-4 right-4 z-[100] flex flex-col gap-2 pointer-events-none"
  >
    {#each ui.toasts as toast (toast.id)}
      <div
        class="pointer-events-auto flex items-center gap-3 px-4 py-3 rounded-xl shadow-xl
          text-sm font-medium max-w-xs animate-in slide-in-from-right duration-200
          {toast.type === 'success'
          ? 'bg-green-500 text-white'
          : toast.type === 'error'
            ? 'bg-red-500 text-white'
            : toast.type === 'warning'
              ? 'bg-amber-500 text-white'
              : 'bg-gray-800 text-white'}"
      >
        <span class="flex-1">{toast.message}</span>
        <button
          onclick={() => ui.removeToast(toast.id)}
          class="opacity-70 hover:opacity-100 transition-opacity text-base leading-none"
        >
          ✕
        </button>
      </div>
    {/each}
  </div>
{/if}
