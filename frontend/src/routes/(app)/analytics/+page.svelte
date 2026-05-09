<script lang="ts">
  import { onMount } from "svelte";
  import { BarChart3, TrendingUp, Users, FileText } from "lucide-svelte";

  let stats = $state({
    total_proposals: 0,
    total_leads: 0,
    conversion_rate: 0,
    revenue: 0,
  });

  let loading = $state(true);

  onMount(async () => {
    try {
      const res = await fetch("/api/v1/dashboard/stats/");
      if (res.ok) {
        const data = await res.json();
        stats = data;
      }
    } catch (e) {
      console.error("Failed to load analytics:", e);
    } finally {
      loading = false;
    }
  });
</script>

<div class="p-6 max-w-7xl mx-auto">
  <h1 class="text-2xl font-bold text-gray-900 dark:text-white mb-6">
    Analytics
  </h1>

  {#if loading}
    <div class="flex items-center justify-center h-64">
      <div
        class="w-8 h-8 border-2 border-blue-500 border-t-transparent rounded-full animate-spin"
      ></div>
    </div>
  {:else}
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
      <div
        class="bg-white dark:bg-gray-900 rounded-xl border border-gray-200 dark:border-gray-800 p-5"
      >
        <div class="flex items-center gap-3 mb-3">
          <div
            class="w-10 h-10 bg-blue-100 dark:bg-blue-900/30 rounded-lg flex items-center justify-center"
          >
            <FileText size={20} class="text-blue-600" />
          </div>
          <span class="text-sm text-gray-500">Proposals</span>
        </div>
        <p class="text-2xl font-bold text-gray-900 dark:text-white">
          {stats.total_proposals}
        </p>
      </div>

      <div
        class="bg-white dark:bg-gray-900 rounded-xl border border-gray-200 dark:border-gray-800 p-5"
      >
        <div class="flex items-center gap-3 mb-3">
          <div
            class="w-10 h-10 bg-green-100 dark:bg-green-900/30 rounded-lg flex items-center justify-center"
          >
            <Users size={20} class="text-green-600" />
          </div>
          <span class="text-sm text-gray-500">Leads</span>
        </div>
        <p class="text-2xl font-bold text-gray-900 dark:text-white">
          {stats.total_leads}
        </p>
      </div>

      <div
        class="bg-white dark:bg-gray-900 rounded-xl border border-gray-200 dark:border-gray-800 p-5"
      >
        <div class="flex items-center gap-3 mb-3">
          <div
            class="w-10 h-10 bg-amber-100 dark:bg-amber-900/30 rounded-lg flex items-center justify-center"
          >
            <TrendingUp size={20} class="text-amber-600" />
          </div>
          <span class="text-sm text-gray-500">Conversion</span>
        </div>
        <p class="text-2xl font-bold text-gray-900 dark:text-white">
          {stats.conversion_rate}%
        </p>
      </div>

      <div
        class="bg-white dark:bg-gray-900 rounded-xl border border-gray-200 dark:border-gray-800 p-5"
      >
        <div class="flex items-center gap-3 mb-3">
          <div
            class="w-10 h-10 bg-violet-100 dark:bg-violet-900/30 rounded-lg flex items-center justify-center"
          >
            <BarChart3 size={20} class="text-violet-600" />
          </div>
          <span class="text-sm text-gray-500">Pipeline</span>
        </div>
        <p class="text-2xl font-bold text-gray-900 dark:text-white">
          ${stats.revenue?.toLocaleString() || 0}
        </p>
      </div>
    </div>
  {/if}
</div>
