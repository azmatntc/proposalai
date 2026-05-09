<script lang="ts">
  import { auth } from '$lib/stores/auth.svelte';
  import { api } from '$lib/api/client';
  import { ui } from '$lib/stores/ui.svelte';

  let form = $state({
    first_name: auth.user?.first_name || '',
    last_name: auth.user?.last_name || '',
    company_name: auth.user?.company_name || '',
    bio: '',
    website: '',
  });

  $effect(() => {
    if (auth.user) {
      form.first_name = auth.user.first_name;
      form.last_name = auth.user.last_name;
      form.company_name = auth.user.company_name;
    }
  });

  let saving = $state(false);

  async function saveProfile() {
    saving = true;
    try {
      await api.patch('/auth/me/', form);
      await auth.refreshUser();
      ui.success('Profile updated!');
    } catch (e: any) {
      ui.error(e.message || 'Failed to save');
    } finally { saving = false; }
  }
</script>

<div class="p-6 max-w-2xl mx-auto">
  <h1 class="text-2xl font-bold text-gray-900 dark:text-white mb-6">Settings</h1>

  <div class="bg-white dark:bg-gray-900 rounded-xl border border-gray-200 dark:border-gray-800 p-6">
    <h2 class="text-base font-semibold text-gray-900 dark:text-white mb-4">Profile</h2>
    <div class="space-y-4">
      <div class="flex items-center gap-4 mb-5">
        <img src={auth.user?.avatar_url} alt="" class="w-16 h-16 rounded-full" />
        <div>
          <p class="font-semibold text-gray-900 dark:text-white">{auth.user?.full_name}</p>
          <p class="text-sm text-gray-500">{auth.user?.email}</p>
          <span class="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-700 mt-1 capitalize">
            {auth.user?.subscription_tier} plan
          </span>
        </div>
      </div>
      <div class="grid grid-cols-2 gap-4">
        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1.5">First Name</label>
          <input bind:value={form.first_name} class="w-full px-3.5 py-2.5 rounded-lg border border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-800 text-sm focus:ring-2 focus:ring-blue-500 outline-none" />
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1.5">Last Name</label>
          <input bind:value={form.last_name} class="w-full px-3.5 py-2.5 rounded-lg border border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-800 text-sm focus:ring-2 focus:ring-blue-500 outline-none" />
        </div>
      </div>
      <div>
        <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1.5">Company</label>
        <input bind:value={form.company_name} class="w-full px-3.5 py-2.5 rounded-lg border border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-800 text-sm focus:ring-2 focus:ring-blue-500 outline-none" />
      </div>
      <button onclick={saveProfile} disabled={saving}
        class="px-5 py-2.5 bg-blue-600 hover:bg-blue-700 disabled:opacity-60 text-white text-sm font-semibold rounded-lg transition-colors">
        {saving ? 'Saving...' : 'Save Changes'}
      </button>
    </div>
  </div>

  <!-- Quota info -->
  <div class="bg-white dark:bg-gray-900 rounded-xl border border-gray-200 dark:border-gray-800 p-6 mt-4">
    <h2 class="text-base font-semibold text-gray-900 dark:text-white mb-4">AI Usage</h2>
    <div class="flex justify-between text-sm mb-2">
      <span class="text-gray-600 dark:text-gray-400">Proposals generated this month</span>
      <span class="font-semibold text-gray-900 dark:text-white">{auth.user?.proposals_generated_this_month}/{auth.user?.monthly_proposal_quota}</span>
    </div>
    <div class="h-2 bg-gray-100 dark:bg-gray-800 rounded-full overflow-hidden">
      <div class="h-full bg-blue-500 rounded-full" style="width: {auth.user ? (auth.user.proposals_generated_this_month / auth.user.monthly_proposal_quota) * 100 : 0}%"></div>
    </div>
    {#if !auth.isPro}
      <div class="mt-4 p-4 bg-gradient-to-r from-blue-50 to-violet-50 dark:from-blue-900/20 dark:to-violet-900/20 rounded-lg border border-blue-100 dark:border-blue-800">
        <p class="text-sm font-semibold text-gray-900 dark:text-white mb-1">Upgrade to Pro</p>
        <p class="text-xs text-gray-500 mb-3">Get 100 AI proposals/month, priority generation, and advanced analytics.</p>
        <button class="px-4 py-2 bg-blue-600 text-white text-xs font-semibold rounded-lg hover:bg-blue-700 transition-colors">Upgrade · $29/mo</button>
      </div>
    {/if}
  </div>
</div>
