<script lang="ts">
  import { onMount } from "svelte";
  import { api } from "$lib/api/client";
  import { ui } from "$lib/stores/ui.svelte";
  import type { Lead, PaginatedResponse } from "$lib/api/types";

  let leads = $state<Lead[]>([]);
  let loading = $state(true);
  let search = $state("");
  let statusFilter = $state("");
  let priorityFilter = $state("");
  let selected = $state<Lead | null>(null);
  let showModal = $state(false);
  let converting = $state<string | null>(null);

  let form = $state({
    first_name: "",
    last_name: "",
    email: "",
    phone: "",
    company: "",
    job_title: "",
    source: "website_form",
    status: "new",
    priority: "medium",
    estimated_value: "",
    notes: "",
  });

  const tierBadge: Record<string, string> = {
    cold: "tier-cold",
    warm: "tier-warm",
    hot: "tier-hot",
    qualified: "tier-qualified",
  };
  const tierEmoji: Record<string, string> = {
    cold: "❄️",
    warm: "🌡️",
    hot: "🔥",
    qualified: "✅",
  };
  const statusColors: Record<string, string> = {
    new: "bg-indigo-100 text-indigo-700 dark:bg-indigo-900/30 dark:text-indigo-400",
    contacted:
      "bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-400",
    qualified:
      "bg-violet-100 text-violet-700 dark:bg-violet-900/30 dark:text-violet-400",
    proposal_sent:
      "bg-amber-100 text-amber-700 dark:bg-amber-900/30 dark:text-amber-400",
    negotiating:
      "bg-orange-100 text-orange-700 dark:bg-orange-900/30 dark:text-orange-400",
    closed_won:
      "bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400",
    closed_lost: "bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400",
    nurture: "bg-cyan-100 text-cyan-700 dark:bg-cyan-900/30 dark:text-cyan-400",
    disqualified:
      "bg-gray-100 text-gray-500 dark:bg-gray-800 dark:text-gray-500",
  };
  const priorityBorder: Record<string, string> = {
    low: "bg-gray-300",
    medium: "bg-blue-500",
    high: "bg-orange-500",
    urgent: "bg-red-500",
  };

  const statusOptions = [
    "new",
    "contacted",
    "qualified",
    "proposal_sent",
    "negotiating",
    "closed_won",
    "closed_lost",
    "nurture",
    "disqualified",
  ];

  async function load() {
    loading = true;
    try {
      const params = new URLSearchParams();
      if (search) params.set("search", search);
      if (statusFilter) params.set("status", statusFilter);
      if (priorityFilter) params.set("priority", priorityFilter);
      const data = await api.get<PaginatedResponse<Lead>>(`/leads/?${params}`);
      leads = data.results;
    } catch (e: any) {
      ui.error(e.message || "Failed to load leads");
    } finally {
      loading = false;
    }
  }

  async function createLead() {
    if (!form.first_name || !form.email) {
      ui.error("First name and email are required.");
      return;
    }
    try {
      const payload: Record<string, unknown> = { ...form };
      if (payload.estimated_value) {
        payload.estimated_value = parseFloat(payload.estimated_value as string);
      } else {
        delete payload.estimated_value;
      }
      const lead = await api.post<Lead>("/leads/", payload);
      leads = [lead, ...leads];
      showModal = false;
      resetForm();
      ui.success(`Lead "${lead.full_name}" created!`);
    } catch (e: any) {
      ui.error(e.message || "Failed to create lead");
    }
  }

  async function convertLead(id: string) {
    converting = id;
    try {
      const updated = await api.post<Lead>(`/leads/${id}/convert/`, {});
      leads = leads.map((l) => (l.id === id ? updated : l));
      if (selected?.id === id) selected = updated;
      ui.success("Lead marked as Won! 🎉");
    } catch (e: any) {
      ui.error(e.message || "Failed to convert lead");
    } finally {
      converting = null;
    }
  }

  function resetForm() {
    form = {
      first_name: "",
      last_name: "",
      email: "",
      phone: "",
      company: "",
      job_title: "",
      source: "website_form",
      status: "new",
      priority: "medium",
      estimated_value: "",
      notes: "",
    };
  }

  onMount(load);

  let debounce: ReturnType<typeof setTimeout>;
  $effect(() => {
    // eslint-disable-next-line @typescript-eslint/no-unused-expressions
    search;
    statusFilter;
    priorityFilter;
    clearTimeout(debounce);
    debounce = setTimeout(load, 350);
  });
</script>

<div class="flex h-full">
  <!-- ── Lead list ─────────────────────────────────────────── -->
  <div
    class="flex-1 p-6 overflow-auto {selected
      ? 'hidden lg:block lg:max-w-[55%]'
      : ''}"
  >
    <div class="flex items-center justify-between mb-5">
      <div>
        <h1 class="text-2xl font-bold text-gray-900 dark:text-white">
          Leads CRM
        </h1>
        <p class="text-sm text-gray-500 mt-0.5">{leads.length} leads</p>
      </div>
      <button
        onclick={() => (showModal = true)}
        class="flex items-center gap-2 px-4 py-2.5 bg-blue-600 hover:bg-blue-700
          text-white text-sm font-semibold rounded-lg transition-colors"
      >
        <svg
          width="16"
          height="16"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          stroke-width="2.5"
        >
          <line x1="12" y1="5" x2="12" y2="19" /><line
            x1="5"
            y1="12"
            x2="19"
            y2="12"
          />
        </svg>
        New Lead
      </button>
    </div>

    <!-- Filters -->
    <div class="flex flex-wrap gap-2 mb-4">
      <div class="relative flex-1 min-w-36">
        <svg
          class="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400"
          width="13"
          height="13"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          stroke-width="2"
        >
          <circle cx="11" cy="11" r="8" /><line
            x1="21"
            y1="21"
            x2="16.65"
            y2="16.65"
          />
        </svg>
        <input
          bind:value={search}
          placeholder="Search leads…"
          class="w-full pl-8 pr-3 py-2 text-sm border border-gray-300 dark:border-gray-700
            rounded-lg bg-white dark:bg-gray-900 text-gray-900 dark:text-white
            focus:ring-2 focus:ring-blue-500 outline-none"
        />
      </div>
      <select
        bind:value={statusFilter}
        class="px-3 py-2 text-sm border border-gray-300 dark:border-gray-700 rounded-lg
          bg-white dark:bg-gray-900 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500 outline-none"
      >
        <option value="">All Status</option>
        {#each statusOptions as s}
          <option value={s}
            >{s
              .replace("_", " ")
              .replace(/\b\w/g, (c) => c.toUpperCase())}</option
          >
        {/each}
      </select>
      <select
        bind:value={priorityFilter}
        class="px-3 py-2 text-sm border border-gray-300 dark:border-gray-700 rounded-lg
          bg-white dark:bg-gray-900 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500 outline-none"
      >
        <option value="">All Priority</option>
        {#each ["low", "medium", "high", "urgent"] as p}
          <option value={p}>{p.charAt(0).toUpperCase() + p.slice(1)}</option>
        {/each}
      </select>
    </div>

    <!-- Lead rows -->
    {#if loading}
      <div class="space-y-2">
        {#each [0, 1, 2, 3, 4, 5] as _}
          <div
            class="h-16 bg-white dark:bg-gray-900 rounded-xl border border-gray-200 dark:border-gray-800 animate-pulse"
          ></div>
        {/each}
      </div>
    {:else if leads.length === 0}
      <div
        class="text-center py-16 bg-white dark:bg-gray-900 rounded-xl border border-gray-200 dark:border-gray-800"
      >
        <svg
          class="mx-auto mb-3 text-gray-300"
          width="40"
          height="40"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          stroke-width="1.5"
        >
          <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2" />
          <circle cx="9" cy="7" r="4" />
        </svg>
        <h3 class="text-sm font-semibold text-gray-900 dark:text-white mb-1">
          No leads found
        </h3>
        <p class="text-sm text-gray-500">Add your first lead to get started</p>
      </div>
    {:else}
      <div
        class="bg-white dark:bg-gray-900 rounded-xl border border-gray-200 dark:border-gray-800 overflow-hidden"
      >
        {#each leads as lead, i (lead.id)}
          <div
            role="button"
            tabindex="0"
            onclick={() => (selected = lead)}
            onkeydown={(e) => e.key === "Enter" && (selected = lead)}
            class="flex items-center gap-3 px-4 py-3.5 cursor-pointer transition-colors
              {i > 0 ? 'border-t border-gray-50 dark:border-gray-800/60' : ''}
              {selected?.id === lead.id
              ? 'bg-blue-50 dark:bg-blue-900/10'
              : 'hover:bg-gray-50 dark:hover:bg-gray-800/40'}"
          >
            <!-- Priority stripe -->
            <div
              class="w-1 h-9 rounded-full flex-shrink-0 {priorityBorder[
                lead.priority
              ] || 'bg-gray-300'}"
            ></div>

            <!-- Avatar initials -->
            <div
              class="w-9 h-9 rounded-full bg-gradient-to-br from-blue-500 to-violet-500
              flex items-center justify-center flex-shrink-0"
            >
              <span class="text-white text-xs font-bold">{lead.initials}</span>
            </div>

            <!-- Name + company -->
            <div class="flex-1 min-w-0">
              <div class="flex items-center gap-1.5">
                <span
                  class="text-sm font-semibold text-gray-900 dark:text-white truncate"
                >
                  {lead.full_name}
                </span>
                {#if lead.is_hot}
                  <span class="text-orange-500 text-xs flex-shrink-0">🔥</span>
                {/if}
              </div>
              <p class="text-xs text-gray-500 truncate">
                {lead.company || lead.email}
              </p>
            </div>

            <!-- Score + Status -->
            <div class="flex flex-col items-end gap-1 flex-shrink-0">
              {#if lead.score_summary}
                <span
                  class="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-semibold
                  {tierBadge[lead.score_summary.tier] || 'tier-cold'}"
                >
                  {tierEmoji[lead.score_summary.tier]}
                  {lead.score_summary.total}
                </span>
              {/if}
              <span
                class="text-xs px-1.5 py-0.5 rounded
                {statusColors[lead.status] || 'bg-gray-100 text-gray-600'}"
              >
                {lead.status.replace("_", " ")}
              </span>
            </div>
          </div>
        {/each}
      </div>
    {/if}
  </div>

  <!-- ── Lead detail panel ──────────────────────────────────── -->
  {#if selected}
    <div
      class="w-full lg:w-[45%] lg:border-l border-gray-200 dark:border-gray-800
      bg-white dark:bg-gray-900 flex flex-col overflow-hidden flex-shrink-0"
    >
      <div
        class="flex items-center justify-between px-5 py-4 border-b border-gray-200 dark:border-gray-800 flex-shrink-0"
      >
        <h2 class="text-sm font-semibold text-gray-900 dark:text-white">
          Lead Detail
        </h2>
        <button
          onclick={() => (selected = null)}
          class="text-gray-400 hover:text-gray-600"
        >
          <svg
            width="18"
            height="18"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            stroke-width="2"
          >
            <line x1="18" y1="6" x2="6" y2="18" /><line
              x1="6"
              y1="6"
              x2="18"
              y2="18"
            />
          </svg>
        </button>
      </div>

      <div class="flex-1 overflow-auto p-5 space-y-4">
        <!-- Header -->
        <div class="flex items-start gap-4">
          <div
            class="w-14 h-14 rounded-xl bg-gradient-to-br from-blue-500 to-violet-500
            flex items-center justify-center flex-shrink-0"
          >
            <span class="text-white text-xl font-bold">{selected.initials}</span
            >
          </div>
          <div class="flex-1 min-w-0">
            <div class="flex items-center gap-2 flex-wrap">
              <h3 class="text-lg font-bold text-gray-900 dark:text-white">
                {selected.full_name}
              </h3>
              {#if selected.is_hot}<span class="text-orange-500">🔥</span>{/if}
            </div>
            {#if selected.job_title || selected.company}
              <p class="text-sm text-gray-500">
                {selected.job_title || ""}{selected.job_title &&
                selected.company
                  ? " · "
                  : ""}{selected.company || ""}
              </p>
            {/if}
            <p class="text-sm text-blue-600">{selected.email}</p>
          </div>
          {#if selected.score_summary}
            <div class="text-center flex-shrink-0">
              <p
                class="text-3xl font-black text-gray-900 dark:text-white leading-none"
              >
                {selected.score_summary.total}
              </p>
              <span
                class="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-medium mt-1
                {tierBadge[selected.score_summary.tier] || 'tier-cold'}"
              >
                {tierEmoji[selected.score_summary.tier]}
                {selected.score_summary.tier.toUpperCase()}
              </span>
            </div>
          {/if}
        </div>

        <!-- Quick stats -->
        <div class="grid grid-cols-3 gap-2">
          <div class="bg-gray-50 dark:bg-gray-800 rounded-lg p-3 text-center">
            <p class="text-xs text-gray-500 mb-1">Status</p>
            <span
              class="text-xs font-semibold {statusColors[selected.status] ||
                ''} px-2 py-0.5 rounded-full capitalize"
            >
              {selected.status.replace("_", " ")}
            </span>
          </div>
          <div class="bg-gray-50 dark:bg-gray-800 rounded-lg p-3 text-center">
            <p class="text-xs text-gray-500 mb-1">Priority</p>
            <p
              class="text-sm font-bold text-gray-900 dark:text-white capitalize"
            >
              {selected.priority}
            </p>
          </div>
          <div class="bg-gray-50 dark:bg-gray-800 rounded-lg p-3 text-center">
            <p class="text-xs text-gray-500 mb-1">Value</p>
            <p class="text-sm font-bold text-gray-900 dark:text-white">
              {selected.estimated_value
                ? `$${parseFloat(selected.estimated_value).toLocaleString()}`
                : "—"}
            </p>
          </div>
        </div>

        <!-- Score breakdown -->
        {#if selected.score_summary}
          <div class="bg-gray-50 dark:bg-gray-800 rounded-xl p-4">
            <h4
              class="text-xs font-semibold text-gray-500 uppercase tracking-wide mb-3"
            >
              Score Breakdown
            </h4>
            {#each [{ label: "Engagement", pct: 70 }, { label: "Recency", pct: 85 }, { label: "Frequency", pct: 60 }, { label: "Depth", pct: 75 }, { label: "Demographic", pct: 80 }, { label: "Intent", pct: selected.score_summary.total }] as dim}
              <div class="flex items-center gap-2 mb-2">
                <span class="text-xs text-gray-500 w-24">{dim.label}</span>
                <div
                  class="flex-1 h-1.5 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden"
                >
                  <div
                    class="h-full rounded-full transition-all
                      {selected.score_summary.tier === 'qualified'
                      ? 'bg-green-500'
                      : selected.score_summary.tier === 'hot'
                        ? 'bg-orange-400'
                        : selected.score_summary.tier === 'warm'
                          ? 'bg-amber-400'
                          : 'bg-slate-400'}"
                    style="width: {dim.pct}%"
                  ></div>
                </div>
                <span class="text-xs text-gray-400 w-7 text-right"
                  >{dim.pct}</span
                >
              </div>
            {/each}
          </div>
        {/if}

        <!-- Actions -->
        <div class="grid grid-cols-2 gap-2">
          {#if selected.status !== "closed_won"}
            <button
              onclick={() => convertLead(selected!.id)}
              disabled={converting === selected.id}
              class="py-2.5 px-3 bg-green-600 hover:bg-green-700 text-white text-xs font-semibold
                rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {converting === selected.id ? "Converting…" : "✓ Mark as Won"}
            </button>
          {:else}
            <div
              class="py-2.5 px-3 bg-green-100 text-green-700 text-xs font-semibold rounded-lg text-center"
            >
              ✅ Closed Won
            </div>
          {/if}
          <a
            href="/proposals"
            class="py-2.5 px-3 bg-blue-600 hover:bg-blue-700 text-white text-xs font-semibold
              rounded-lg transition-colors text-center"
          >
            + New Proposal
          </a>
        </div>

        <!-- Contact info -->
        <div
          class="space-y-2 text-sm pt-1 border-t border-gray-100 dark:border-gray-800"
        >
          {#if selected.phone}
            <div class="flex gap-2">
              <span class="text-gray-500 w-20">Phone</span>
              <span class="text-gray-900 dark:text-white">{selected.phone}</span
              >
            </div>
          {/if}
          {#if selected.source}
            <div class="flex gap-2">
              <span class="text-gray-500 w-20">Source</span>
              <span class="text-gray-900 dark:text-white capitalize"
                >{selected.source.replace("_", " ")}</span
              >
            </div>
          {/if}
          {#if selected.industry}
            <div class="flex gap-2">
              <span class="text-gray-500 w-20">Industry</span>
              <span class="text-gray-900 dark:text-white capitalize"
                >{selected.industry}</span
              >
            </div>
          {/if}
          {#if selected.notes}
            <div class="flex gap-2">
              <span class="text-gray-500 w-20">Notes</span>
              <span class="text-gray-700 dark:text-gray-300 flex-1"
                >{selected.notes}</span
              >
            </div>
          {/if}
          <div class="flex gap-2">
            <span class="text-gray-500 w-20">Added</span>
            <span class="text-gray-900 dark:text-white"
              >{new Date(selected.created_at).toLocaleDateString()}</span
            >
          </div>
        </div>
      </div>
    </div>
  {/if}
</div>

<!-- ── New Lead Modal ─────────────────────────────────────── -->
{#if showModal}
  <div class="fixed inset-0 z-50 flex items-center justify-center p-4">
    <div
      class="absolute inset-0 bg-black/50"
      role="button"
      tabindex="-1"
      aria-label="Close"
      onclick={() => {
        showModal = false;
        resetForm();
      }}
      onkeydown={(e) => e.key === "Escape" && (showModal = false)}
    ></div>

    <div
      class="relative bg-white dark:bg-gray-900 rounded-2xl shadow-2xl w-full max-w-lg max-h-[90vh] overflow-y-auto"
    >
      <div
        class="sticky top-0 bg-white dark:bg-gray-900 px-6 py-4 border-b border-gray-200 dark:border-gray-800 flex items-center justify-between z-10"
      >
        <h2 class="text-lg font-semibold text-gray-900 dark:text-white">
          Add New Lead
        </h2>
        <button
          onclick={() => {
            showModal = false;
            resetForm();
          }}
          class="text-gray-400 hover:text-gray-600"
        >
          <svg
            width="20"
            height="20"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            stroke-width="2"
          >
            <line x1="18" y1="6" x2="6" y2="18" /><line
              x1="6"
              y1="6"
              x2="18"
              y2="18"
            />
          </svg>
        </button>
      </div>

      <div class="p-6 space-y-4">
        <div class="grid grid-cols-2 gap-3">
          <div>
            <label
              class="block text-xs font-medium text-gray-700 dark:text-gray-300 mb-1"
              >First Name *</label
            >
            <input
              bind:value={form.first_name}
              class="w-full px-3 py-2 rounded-lg border border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-800 text-gray-900 dark:text-white text-sm focus:ring-2 focus:ring-blue-500 outline-none"
            />
          </div>
          <div>
            <label
              class="block text-xs font-medium text-gray-700 dark:text-gray-300 mb-1"
              >Last Name</label
            >
            <input
              bind:value={form.last_name}
              class="w-full px-3 py-2 rounded-lg border border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-800 text-gray-900 dark:text-white text-sm focus:ring-2 focus:ring-blue-500 outline-none"
            />
          </div>
        </div>

        <div>
          <label
            class="block text-xs font-medium text-gray-700 dark:text-gray-300 mb-1"
            >Email *</label
          >
          <input
            bind:value={form.email}
            type="email"
            class="w-full px-3 py-2 rounded-lg border border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-800 text-gray-900 dark:text-white text-sm focus:ring-2 focus:ring-blue-500 outline-none"
          />
        </div>

        <div class="grid grid-cols-2 gap-3">
          <div>
            <label
              class="block text-xs font-medium text-gray-700 dark:text-gray-300 mb-1"
              >Company</label
            >
            <input
              bind:value={form.company}
              class="w-full px-3 py-2 rounded-lg border border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-800 text-gray-900 dark:text-white text-sm focus:ring-2 focus:ring-blue-500 outline-none"
            />
          </div>
          <div>
            <label
              class="block text-xs font-medium text-gray-700 dark:text-gray-300 mb-1"
              >Est. Value ($)</label
            >
            <input
              bind:value={form.estimated_value}
              type="number"
              placeholder="5000"
              class="w-full px-3 py-2 rounded-lg border border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-800 text-gray-900 dark:text-white text-sm focus:ring-2 focus:ring-blue-500 outline-none"
            />
          </div>
        </div>

        <div class="grid grid-cols-2 gap-3">
          <div>
            <label
              class="block text-xs font-medium text-gray-700 dark:text-gray-300 mb-1"
              >Source</label
            >
            <select
              bind:value={form.source}
              class="w-full px-3 py-2 rounded-lg border border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-800 text-gray-900 dark:text-white text-sm focus:ring-2 focus:ring-blue-500 outline-none"
            >
              {#each ["website_form", "upwork", "linkedin", "referral", "cold_outreach", "networking", "other"] as s}
                <option value={s}
                  >{s
                    .replace(/_/g, " ")
                    .replace(/\b\w/g, (c) => c.toUpperCase())}</option
                >
              {/each}
            </select>
          </div>
          <div>
            <label
              class="block text-xs font-medium text-gray-700 dark:text-gray-300 mb-1"
              >Priority</label
            >
            <select
              bind:value={form.priority}
              class="w-full px-3 py-2 rounded-lg border border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-800 text-gray-900 dark:text-white text-sm focus:ring-2 focus:ring-blue-500 outline-none"
            >
              {#each ["low", "medium", "high", "urgent"] as p}
                <option value={p}
                  >{p.charAt(0).toUpperCase() + p.slice(1)}</option
                >
              {/each}
            </select>
          </div>
        </div>

        <div>
          <label
            class="block text-xs font-medium text-gray-700 dark:text-gray-300 mb-1"
            >Notes</label
          >
          <textarea
            bind:value={form.notes}
            rows={3}
            class="w-full px-3 py-2 rounded-lg border border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-800 text-gray-900 dark:text-white text-sm focus:ring-2 focus:ring-blue-500 outline-none resize-none"
          ></textarea>
        </div>

        <div class="flex gap-2 pt-1">
          <button
            onclick={createLead}
            class="flex-1 py-2.5 bg-blue-600 hover:bg-blue-700 text-white text-sm font-semibold rounded-lg transition-colors"
          >
            Create Lead
          </button>
          <button
            onclick={() => {
              showModal = false;
              resetForm();
            }}
            class="px-4 py-2.5 text-sm text-gray-600 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-800 rounded-lg transition-colors"
          >
            Cancel
          </button>
        </div>
      </div>
    </div>
  </div>
{/if}
