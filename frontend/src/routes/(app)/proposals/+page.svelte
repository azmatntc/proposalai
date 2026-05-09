<script lang="ts">
  import { onMount } from 'svelte';
  import { api } from '$lib/api/client';
  import { ui } from '$lib/stores/ui.svelte';
  import type { Proposal, PaginatedResponse } from '$lib/api/types';
  import { Plus, Search, Star, Send, Copy, Trash2, Sparkles, Filter } from 'lucide-svelte';

  let proposals = $state<Proposal[]>([]);
  let loading = $state(true);
  let search = $state('');
  let statusFilter = $state('');
  let showNewModal = $state(false);
  let generating = $state<string | null>(null);

  // New proposal form
  let form = $state({
    title: '', client_name: '', client_company: '', client_email: '',
    job_description: '', job_platform: 'upwork', tone_used: 'professional',
    custom_variables: {}
  });

  async function loadProposals() {
    loading = true;
    try {
      const params = new URLSearchParams();
      if (search) params.set('search', search);
      if (statusFilter) params.set('status', statusFilter);
      const data = await api.get<PaginatedResponse<Proposal>>(`/proposals/?${params}`);
      proposals = data.results;
    } finally { loading = false; }
  }

  async function createAndGenerate() {
    if (!form.title || !form.client_name || !form.job_description) {
      ui.error('Please fill in title, client name, and job description.');
      return;
    }
    try {
      const proposal = await api.post<Proposal>('/proposals/', form);
      proposals = [proposal, ...proposals];
      showNewModal = false;
      form = { title: '', client_name: '', client_company: '', client_email: '', job_description: '', job_platform: 'upwork', tone_used: 'professional', custom_variables: {} };
      ui.success('Proposal created!');
      // Auto-generate
      await triggerGenerate(proposal.id);
    } catch (e: any) {
      ui.error(e.message || 'Failed to create proposal');
    }
  }

  async function triggerGenerate(id: string) {
    generating = id;
    try {
      await api.post(`/proposals/${id}/generate/`, {});
      ui.success('AI generation started! Refreshing in 15s...');
      setTimeout(loadProposals, 15000);
    } catch (e: any) {
      ui.error(e.message || 'Generation failed');
    } finally { generating = null; }
  }

  async function toggleFavorite(id: string) {
    const data = await api.post<{is_favorite: boolean}>(`/proposals/${id}/favorite/`, {});
    proposals = proposals.map(p => p.id === id ? { ...p, is_favorite: data.is_favorite } : p);
  }

  async function deleteProposal(id: string) {
    if (!confirm('Delete this proposal?')) return;
    await api.delete(`/proposals/${id}/`);
    proposals = proposals.filter(p => p.id !== id);
    ui.success('Proposal deleted');
  }

  const statusColors: Record<string, string> = {
    draft: 'bg-gray-100 text-gray-600', generated: 'bg-blue-100 text-blue-700',
    edited: 'bg-indigo-100 text-indigo-700', sent: 'bg-amber-100 text-amber-700',
    accepted: 'bg-green-100 text-green-700', rejected: 'bg-red-100 text-red-700',
    archived: 'bg-gray-100 text-gray-500',
  };

  onMount(loadProposals);
  let debounceTimer: ReturnType<typeof setTimeout>;
  $effect(() => { search; statusFilter; clearTimeout(debounceTimer); debounceTimer = setTimeout(loadProposals, 400); });
</script>

<div class="p-6 max-w-7xl mx-auto">
  <div class="flex items-center justify-between mb-6">
    <div>
      <h1 class="text-2xl font-bold text-gray-900 dark:text-white">Proposals</h1>
      <p class="text-sm text-gray-500 mt-0.5">{proposals.length} proposals</p>
    </div>
    <button onclick={() => showNewModal = true}
      class="flex items-center gap-2 px-4 py-2.5 bg-blue-600 hover:bg-blue-700 text-white text-sm font-semibold rounded-lg transition-colors">
      <Plus size={16} />
      New Proposal
    </button>
  </div>

  <!-- Filters -->
  <div class="flex gap-3 mb-5">
    <div class="relative flex-1 max-w-xs">
      <Search size={15} class="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
      <input bind:value={search} placeholder="Search proposals..."
        class="w-full pl-9 pr-3.5 py-2.5 text-sm border border-gray-300 dark:border-gray-700 rounded-lg bg-white dark:bg-gray-900 focus:ring-2 focus:ring-blue-500 outline-none" />
    </div>
    <select bind:value={statusFilter} class="px-3 py-2.5 text-sm border border-gray-300 dark:border-gray-700 rounded-lg bg-white dark:bg-gray-900 focus:ring-2 focus:ring-blue-500 outline-none">
      <option value="">All Status</option>
      {#each ['draft','generated','edited','sent','accepted','rejected','archived'] as s}
        <option value={s}>{s.charAt(0).toUpperCase() + s.slice(1)}</option>
      {/each}
    </select>
  </div>

  <!-- Table -->
  {#if loading}
    <div class="space-y-2">
      {#each [1,2,3,4,5] as _}
        <div class="h-16 bg-white dark:bg-gray-900 rounded-xl border border-gray-200 dark:border-gray-800 animate-pulse"></div>
      {/each}
    </div>
  {:else if proposals.length === 0}
    <div class="text-center py-16 bg-white dark:bg-gray-900 rounded-xl border border-gray-200 dark:border-gray-800">
      <Sparkles size={32} class="mx-auto text-gray-300 mb-3" />
      <h3 class="text-sm font-semibold text-gray-900 dark:text-white mb-1">No proposals yet</h3>
      <p class="text-sm text-gray-500 mb-4">Create your first AI-powered proposal</p>
      <button onclick={() => showNewModal = true} class="px-4 py-2 bg-blue-600 text-white text-sm font-semibold rounded-lg hover:bg-blue-700">
        Create Proposal
      </button>
    </div>
  {:else}
    <div class="bg-white dark:bg-gray-900 rounded-xl border border-gray-200 dark:border-gray-800 overflow-hidden">
      <table class="w-full text-sm">
        <thead>
          <tr class="border-b border-gray-100 dark:border-gray-800">
            <th class="text-left px-4 py-3 text-xs font-semibold text-gray-500 uppercase">Title</th>
            <th class="text-left px-4 py-3 text-xs font-semibold text-gray-500 uppercase">Client</th>
            <th class="text-left px-4 py-3 text-xs font-semibold text-gray-500 uppercase hidden md:table-cell">Status</th>
            <th class="text-left px-4 py-3 text-xs font-semibold text-gray-500 uppercase hidden lg:table-cell">Words</th>
            <th class="text-left px-4 py-3 text-xs font-semibold text-gray-500 uppercase hidden lg:table-cell">Created</th>
            <th class="px-4 py-3"></th>
          </tr>
        </thead>
        <tbody class="divide-y divide-gray-50 dark:divide-gray-800">
          {#each proposals as p (p.id)}
            <tr class="hover:bg-gray-50 dark:hover:bg-gray-800/50 transition-colors">
              <td class="px-4 py-3.5">
                <div class="flex items-center gap-2">
                  <button onclick={() => toggleFavorite(p.id)} class="text-gray-300 hover:text-amber-400 transition-colors flex-shrink-0">
                    <Star size={14} fill={p.is_favorite ? 'currentColor' : 'none'} class={p.is_favorite ? 'text-amber-400' : ''} />
                  </button>
                  <span class="font-medium text-gray-900 dark:text-white truncate max-w-[200px]">{p.title}</span>
                </div>
              </td>
              <td class="px-4 py-3.5 text-gray-600 dark:text-gray-400 truncate max-w-[150px]">
                {p.client_name}{p.client_company ? ` · ${p.client_company}` : ''}
              </td>
              <td class="px-4 py-3.5 hidden md:table-cell">
                <span class="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium capitalize {statusColors[p.status] || 'bg-gray-100 text-gray-600'}">
                  {p.status}
                </span>
              </td>
              <td class="px-4 py-3.5 text-gray-500 hidden lg:table-cell">{p.word_count || '—'}</td>
              <td class="px-4 py-3.5 text-gray-500 hidden lg:table-cell">{new Date(p.created_at).toLocaleDateString()}</td>
              <td class="px-4 py-3.5">
                <div class="flex items-center gap-1 justify-end">
                  {#if p.status === 'draft'}
                    <button onclick={() => triggerGenerate(p.id)} disabled={generating === p.id}
                      class="flex items-center gap-1.5 px-2.5 py-1.5 text-xs font-medium bg-blue-50 hover:bg-blue-100 text-blue-700 rounded-lg transition-colors disabled:opacity-50">
                      <Sparkles size={12} />
                      {generating === p.id ? 'Generating...' : 'Generate'}
                    </button>
                  {/if}
                  <button onclick={() => deleteProposal(p.id)} class="p-1.5 text-gray-400 hover:text-red-500 transition-colors">
                    <Trash2 size={14} />
                  </button>
                </div>
              </td>
            </tr>
          {/each}
        </tbody>
      </table>
    </div>
  {/if}
</div>

<!-- New Proposal Modal -->
{#if showNewModal}
  <div class="fixed inset-0 z-50 flex items-center justify-center p-4">
    <div class="absolute inset-0 bg-black/50" role="button" tabindex="0" onclick={() => showNewModal = false} onkeydown={(e) => e.key === "Enter" && (showNewModal = false)}></div>
    <div class="relative bg-white dark:bg-gray-900 rounded-2xl shadow-2xl w-full max-w-2xl max-h-[90vh] overflow-y-auto">
      <div class="sticky top-0 bg-white dark:bg-gray-900 px-6 py-4 border-b border-gray-200 dark:border-gray-800 flex items-center justify-between">
        <h2 class="text-lg font-semibold text-gray-900 dark:text-white">New Proposal</h2>
        <button onclick={() => showNewModal = false} class="text-gray-400 hover:text-gray-600 text-xl">✕</button>
      </div>
      <div class="p-6 space-y-4">
        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1.5">Proposal Title *</label>
          <input bind:value={form.title} placeholder="e.g. Web App Development for Acme Corp"
            class="w-full px-3.5 py-2.5 rounded-lg border border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-800 text-sm focus:ring-2 focus:ring-blue-500 outline-none" />
        </div>
        <div class="grid grid-cols-2 gap-3">
          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1.5">Client Name *</label>
            <input bind:value={form.client_name} placeholder="John Smith"
              class="w-full px-3.5 py-2.5 rounded-lg border border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-800 text-sm focus:ring-2 focus:ring-blue-500 outline-none" />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1.5">Company</label>
            <input bind:value={form.client_company} placeholder="Acme Corp"
              class="w-full px-3.5 py-2.5 rounded-lg border border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-800 text-sm focus:ring-2 focus:ring-blue-500 outline-none" />
          </div>
        </div>
        <div class="grid grid-cols-2 gap-3">
          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1.5">Platform</label>
            <select bind:value={form.job_platform} class="w-full px-3.5 py-2.5 rounded-lg border border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-800 text-sm focus:ring-2 focus:ring-blue-500 outline-none">
              {#each ['upwork','freelancer','fiverr','linkedin','direct','other'] as p}
                <option value={p}>{p.charAt(0).toUpperCase() + p.slice(1)}</option>
              {/each}
            </select>
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1.5">Tone</label>
            <select bind:value={form.tone_used} class="w-full px-3.5 py-2.5 rounded-lg border border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-800 text-sm focus:ring-2 focus:ring-blue-500 outline-none">
              {#each ['professional','friendly','casual','technical','persuasive','formal'] as t}
                <option value={t}>{t.charAt(0).toUpperCase() + t.slice(1)}</option>
              {/each}
            </select>
          </div>
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1.5">Job Description *</label>
          <textarea bind:value={form.job_description} rows={6} placeholder="Paste the full job posting or describe the project requirements..."
            class="w-full px-3.5 py-2.5 rounded-lg border border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-800 text-sm focus:ring-2 focus:ring-blue-500 outline-none resize-none"></textarea>
          <p class="text-xs text-gray-400 mt-1">{form.job_description.length}/10000 characters</p>
        </div>
        <div class="flex gap-3 pt-2">
          <button onclick={createAndGenerate}
            class="flex-1 flex items-center justify-center gap-2 py-2.5 bg-blue-600 hover:bg-blue-700 text-white text-sm font-semibold rounded-lg transition-colors">
            <Sparkles size={15} />
            Create & Generate with AI
          </button>
          <button onclick={() => showNewModal = false} class="px-4 py-2.5 text-sm text-gray-600 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-800 rounded-lg transition-colors">
            Cancel
          </button>
        </div>
      </div>
    </div>
  </div>
{/if}
