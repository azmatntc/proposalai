<script lang="ts">
  import { auth } from '$lib/stores/auth.svelte';
  import { goto } from '$app/navigation';
  import { ui } from '$lib/stores/ui.svelte';

  let email = $state('demo@proposalai.com');
  let password = $state('Demo1234!');
  let loading = $state(false);
  let error = $state('');

  async function handleLogin() {
    loading = true; error = '';
    try {
      await auth.login(email, password);
      goto('/dashboard');
    } catch (e: any) {
      error = e.message || 'Login failed';
    } finally {
      loading = false;
    }
  }
</script>

<div class="w-full max-w-md">
  <div class="text-center mb-8">
    <div class="inline-flex items-center justify-center w-12 h-12 bg-blue-600 rounded-xl mb-4">
      <span class="text-white text-xl font-bold">P</span>
    </div>
    <h1 class="text-2xl font-bold text-gray-900 dark:text-white">Welcome back</h1>
    <p class="text-gray-500 mt-1">Sign in to ProposalAI</p>
  </div>

  <div class="bg-white dark:bg-gray-900 rounded-2xl shadow-xl border border-gray-100 dark:border-gray-800 p-8">
    {#if error}
      <div class="mb-4 p-3 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg text-red-700 dark:text-red-400 text-sm">{error}</div>
    {/if}

    <form onsubmit={(e) => { e.preventDefault(); handleLogin(); }} class="space-y-4">
      <div>
        <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1.5">Email</label>
        <input bind:value={email} type="email" required
          class="w-full px-3.5 py-2.5 rounded-lg border border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-800 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition text-sm" />
      </div>
      <div>
        <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1.5">Password</label>
        <input bind:value={password} type="password" required
          class="w-full px-3.5 py-2.5 rounded-lg border border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-800 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition text-sm" />
      </div>

      <button type="submit" disabled={loading}
        class="w-full py-2.5 px-4 bg-blue-600 hover:bg-blue-700 disabled:opacity-60 text-white font-semibold rounded-lg transition-colors text-sm">
        {loading ? 'Signing in...' : 'Sign in'}
      </button>
    </form>

    <div class="mt-6 text-center">
      <p class="text-sm text-gray-500">Demo credentials pre-filled ↑</p>
      <p class="text-sm text-gray-500 mt-2">No account? <a href="/register" class="text-blue-600 hover:underline font-medium">Create one free</a></p>
    </div>
  </div>
</div>
