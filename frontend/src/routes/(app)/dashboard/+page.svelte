<script lang="ts">
  import { onMount } from "svelte";
  import { api } from "$lib/api/client";
  import { auth } from "$lib/stores/auth.svelte";
  import type { DashboardStats } from "$lib/api/types";

  let stats = $state<DashboardStats | null>(null);
  let activity = $state<any[]>([]);
  let pipeline = $state<any[]>([]);
  let loading = $state(true);

  onMount(async () => {
    try {
      const [s, a, p] = await Promise.all([
        api.get<DashboardStats>("/dashboard/stats/"),
        api.get<any>("/dashboard/activity/?limit=8"),
        api.get<{ stages: any[] }>("/dashboard/pipeline/"),
      ]);
      stats = s;
      activity = Array.isArray(a) ? a : ((a as any).results ?? []);
      pipeline = p.stages ?? [];
    } catch (e) {
      console.error(e);
    } finally {
      loading = false;
    }
  });

  function greeting() {
    const h = new Date().getHours();
    return h < 12 ? "Good morning" : h < 17 ? "Good afternoon" : "Good evening";
  }

  const tierColors: Record<string, string> = {
    cold: "bg-slate-200 text-slate-600",
    warm: "bg-amber-100 text-amber-700",
    hot: "bg-orange-100 text-orange-700",
    qualified: "bg-green-100 text-green-700",
  };

  const tierEmoji: Record<string, string> = {
    cold: "❄️",
    warm: "🌡️",
    hot: "🔥",
    qualified: "✅",
  };
</script>

<div class="p-6 max-w-7xl mx-auto space-y-6">
  <!-- Header -->
  <div>
    <h1 class="text-2xl font-bold text-gray-900 dark:text-white">
      {greeting()}, {auth.user?.first_name || "there"} 👋
    </h1>
    <p class="text-sm text-gray-500 mt-0.5">
      Here's what's happening with your pipeline today.
    </p>
  </div>

  {#if loading}
    <!-- Skeleton -->
    <div class="grid grid-cols-2 lg:grid-cols-4 gap-4">
      {#each [0, 1, 2, 3] as _}
        <div
          class="h-28 bg-white dark:bg-gray-900 rounded-xl border border-gray-200 dark:border-gray-800 animate-pulse"
        ></div>
      {/each}
    </div>
  {:else if stats}
    <!-- ── KPI Cards ─────────────────────────────────────────── -->
    <div class="grid grid-cols-2 lg:grid-cols-4 gap-4">
      <!-- Active Leads -->
      <div
        class="bg-white dark:bg-gray-900 rounded-xl border border-gray-200 dark:border-gray-800 p-5"
      >
        <div class="flex items-center justify-between mb-3">
          <span
            class="text-xs font-semibold text-gray-500 uppercase tracking-wide"
            >Active Leads</span
          >
          <div
            class="w-8 h-8 bg-blue-100 dark:bg-blue-900/30 rounded-lg flex items-center justify-center"
          >
            <svg
              width="15"
              height="15"
              viewBox="0 0 24 24"
              fill="none"
              stroke="#3b82f6"
              stroke-width="2"
            >
              <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2" />
              <circle cx="9" cy="7" r="4" />
            </svg>
          </div>
        </div>
        <p class="text-2xl font-bold text-gray-900 dark:text-white">
          {stats.leads.active}
        </p>
        <p class="text-xs text-gray-500 mt-1">
          {stats.leads.this_month} this month
          {#if stats.leads.mom_change > 0}
            <span class="text-green-600 font-medium"
              >↑{stats.leads.mom_change}</span
            >
          {:else if stats.leads.mom_change < 0}
            <span class="text-red-500 font-medium"
              >↓{Math.abs(stats.leads.mom_change)}</span
            >
          {/if}
        </p>
      </div>

      <!-- Conversion Rate -->
      <div
        class="bg-white dark:bg-gray-900 rounded-xl border border-gray-200 dark:border-gray-800 p-5"
      >
        <div class="flex items-center justify-between mb-3">
          <span
            class="text-xs font-semibold text-gray-500 uppercase tracking-wide"
            >Conv. Rate</span
          >
          <div
            class="w-8 h-8 bg-green-100 dark:bg-green-900/30 rounded-lg flex items-center justify-center"
          >
            <svg
              width="15"
              height="15"
              viewBox="0 0 24 24"
              fill="none"
              stroke="#22c55e"
              stroke-width="2"
            >
              <polyline points="23,6 13.5,15.5 8.5,10.5 1,18" />
              <polyline points="17,6 23,6 23,12" />
            </svg>
          </div>
        </div>
        <p class="text-2xl font-bold text-gray-900 dark:text-white">
          {stats.conversion.rate}%
        </p>
        <p class="text-xs text-gray-500 mt-1">
          {stats.conversion.closed_won} won / {stats.conversion.closed_total} closed
        </p>
      </div>

      <!-- Pipeline Value -->
      <div
        class="bg-white dark:bg-gray-900 rounded-xl border border-gray-200 dark:border-gray-800 p-5"
      >
        <div class="flex items-center justify-between mb-3">
          <span
            class="text-xs font-semibold text-gray-500 uppercase tracking-wide"
            >Pipeline</span
          >
          <div
            class="w-8 h-8 bg-violet-100 dark:bg-violet-900/30 rounded-lg flex items-center justify-center"
          >
            <svg
              width="15"
              height="15"
              viewBox="0 0 24 24"
              fill="none"
              stroke="#8b5cf6"
              stroke-width="2"
            >
              <line x1="12" y1="1" x2="12" y2="23" />
              <path d="M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6" />
            </svg>
          </div>
        </div>
        <p class="text-2xl font-bold text-gray-900 dark:text-white">
          ${stats.pipeline.value.toLocaleString()}
        </p>
        <p class="text-xs text-gray-500 mt-1">Total pipeline value</p>
      </div>

      <!-- Follow-ups Overdue -->
      <div
        class="bg-white dark:bg-gray-900 rounded-xl border border-gray-200 dark:border-gray-800 p-5"
      >
        <div class="flex items-center justify-between mb-3">
          <span
            class="text-xs font-semibold text-gray-500 uppercase tracking-wide"
            >Follow-ups</span
          >
          <div
            class="w-8 h-8 rounded-lg flex items-center justify-center
            {stats.follow_ups.overdue > 0
              ? 'bg-red-100 dark:bg-red-900/30'
              : 'bg-gray-100 dark:bg-gray-800'}"
          >
            <svg
              width="15"
              height="15"
              viewBox="0 0 24 24"
              fill="none"
              stroke={stats.follow_ups.overdue > 0 ? "#ef4444" : "#6b7280"}
              stroke-width="2"
            >
              <circle cx="12" cy="12" r="10" />
              <polyline points="12,6 12,12 16,14" />
            </svg>
          </div>
        </div>
        <p
          class="text-2xl font-bold {stats.follow_ups.overdue > 0
            ? 'text-red-600'
            : 'text-gray-900 dark:text-white'}"
        >
          {stats.follow_ups.overdue}
        </p>
        <p class="text-xs text-gray-500 mt-1">Overdue today</p>
      </div>
    </div>

    <!-- ── Middle Row ────────────────────────────────────────── -->
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-4">
      <!-- Pipeline stages -->
      <div
        class="bg-white dark:bg-gray-900 rounded-xl border border-gray-200 dark:border-gray-800 p-5"
      >
        <h3 class="text-sm font-semibold text-gray-900 dark:text-white mb-4">
          Sales Pipeline
        </h3>
        <div class="space-y-3">
          {#each pipeline as stage}
            {@const maxCount = Math.max(...pipeline.map((s) => s.count), 1)}
            <div class="flex items-center gap-3">
              <span class="text-xs text-gray-500 w-28 truncate"
                >{stage.label}</span
              >
              <div
                class="flex-1 h-2 bg-gray-100 dark:bg-gray-800 rounded-full overflow-hidden"
              >
                <div
                  class="h-full bg-blue-500 rounded-full transition-all"
                  style="width: {(stage.count / maxCount) * 100}%"
                ></div>
              </div>
              <span
                class="text-xs font-semibold text-gray-700 dark:text-gray-300 w-5 text-right"
              >
                {stage.count}
              </span>
              <span class="text-xs text-gray-400 w-20 text-right">
                ${stage.value.toLocaleString()}
              </span>
            </div>
          {/each}
          {#if pipeline.length === 0}
            <p class="text-sm text-gray-400 text-center py-4">
              No pipeline data yet
            </p>
          {/if}
        </div>
      </div>

      <!-- Score distribution -->
      <div
        class="bg-white dark:bg-gray-900 rounded-xl border border-gray-200 dark:border-gray-800 p-5"
      >
        <h3 class="text-sm font-semibold text-gray-900 dark:text-white mb-4">
          Lead Score Distribution
        </h3>
        {#if Object.keys(stats.score_distribution).length > 0}
          {@const total = Object.values(stats.score_distribution).reduce(
            (a, b) => a + b,
            0,
          )}
          <div class="space-y-3">
            {#each Object.entries(stats.score_distribution) as [tier, count]}
              <div class="flex items-center gap-3">
                <span
                  class="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium w-24 {tierColors[
                    tier
                  ] || 'bg-gray-100 text-gray-600'}"
                >
                  {tierEmoji[tier]}
                  {tier}
                </span>
                <div
                  class="flex-1 h-2 bg-gray-100 dark:bg-gray-800 rounded-full overflow-hidden"
                >
                  <div
                    class="h-full rounded-full transition-all
                      {tier === 'cold'
                      ? 'bg-slate-400'
                      : tier === 'warm'
                        ? 'bg-amber-400'
                        : tier === 'hot'
                          ? 'bg-orange-400'
                          : 'bg-green-500'}"
                    style="width: {total > 0 ? (count / total) * 100 : 0}%"
                  ></div>
                </div>
                <span
                  class="text-xs font-semibold text-gray-700 dark:text-gray-300 w-6 text-right"
                >
                  {count}
                </span>
              </div>
            {/each}
          </div>
        {:else}
          <p class="text-sm text-gray-400 text-center py-6">
            Add leads to see score distribution
          </p>
        {/if}
      </div>
    </div>

    <!-- ── Bottom Row ────────────────────────────────────────── -->
    <div class="grid grid-cols-1 lg:grid-cols-3 gap-4">
      <!-- Activity Feed -->
      <div
        class="lg:col-span-2 bg-white dark:bg-gray-900 rounded-xl border border-gray-200 dark:border-gray-800 p-5"
      >
        <div class="flex items-center justify-between mb-4">
          <h3 class="text-sm font-semibold text-gray-900 dark:text-white">
            Recent Activity
          </h3>
          <a href="/leads" class="text-xs text-blue-600 hover:underline"
            >View all →</a
          >
        </div>
        {#if activity.length === 0}
          <p class="text-sm text-gray-400 text-center py-6">
            No recent activity
          </p>
        {:else}
          <div class="space-y-3">
            {#each activity as act}
              <div class="flex items-start gap-3">
                <div
                  class="w-2 h-2 rounded-full bg-blue-400 mt-1.5 flex-shrink-0"
                ></div>
                <div class="flex-1 min-w-0">
                  <p class="text-sm text-gray-700 dark:text-gray-300 truncate">
                    {act.description}
                  </p>
                  <p class="text-xs text-gray-400 mt-0.5">
                    {new Date(act.created_at).toLocaleDateString()}
                  </p>
                </div>
              </div>
            {/each}
          </div>
        {/if}
      </div>

      <!-- AI Quota widget -->
      <div
        class="bg-white dark:bg-gray-900 rounded-xl border border-gray-200 dark:border-gray-800 p-5"
      >
        <div class="flex items-center gap-2 mb-4">
          <svg
            width="16"
            height="16"
            viewBox="0 0 24 24"
            fill="none"
            stroke="#8b5cf6"
            stroke-width="2"
          >
            <polygon points="13,2 3,14 12,14 11,22 21,10 12,10 13,2" />
          </svg>
          <h3 class="text-sm font-semibold text-gray-900 dark:text-white">
            AI Usage
          </h3>
        </div>
        <div class="space-y-4">
          <div>
            <div class="flex justify-between text-xs text-gray-500 mb-1.5">
              <span>Monthly quota</span>
              <span class="font-semibold text-gray-700 dark:text-gray-300">
                {stats.proposals.generated}/{stats.proposals.quota}
              </span>
            </div>
            <div
              class="h-2 bg-gray-100 dark:bg-gray-800 rounded-full overflow-hidden"
            >
              <div
                class="h-full rounded-full transition-all
                  {stats.proposals.generated / stats.proposals.quota > 0.8
                  ? 'bg-red-500'
                  : stats.proposals.generated / stats.proposals.quota > 0.6
                    ? 'bg-amber-500'
                    : 'bg-blue-500'}"
                style="width: {Math.min(
                  (stats.proposals.generated / stats.proposals.quota) * 100,
                  100,
                )}%"
              ></div>
            </div>
            <p class="text-xs text-gray-400 mt-1">
              {stats.proposals.remaining} remaining
            </p>
          </div>
          <div class="pt-3 border-t border-gray-100 dark:border-gray-800">
            <a
              href="/proposals"
              class="w-full flex items-center justify-center gap-2 py-2.5 px-4
                bg-blue-600 hover:bg-blue-700 text-white text-sm font-semibold
                rounded-lg transition-colors"
            >
              <svg
                width="14"
                height="14"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                stroke-width="2"
              >
                <polygon points="13,2 3,14 12,14 11,22 21,10 12,10 13,2" />
              </svg>
              New Proposal
            </a>
          </div>
        </div>
      </div>
    </div>
  {/if}
</div>
