<script lang="ts">
  import { auth } from '$lib/stores/auth.svelte';
  import { goto } from '$app/navigation';
  let first_name = $state(''); let last_name = $state('');
  let email = $state(''); let password = $state(''); let password_confirm = $state('');
  let loading = $state(false); let error = $state('');

  async function handleRegister() {
    loading = true; error = '';
    try {
      const username = email.split('@')[0].replace(/[^a-zA-Z0-9]/g, '') + Math.floor(Math.random() * 1000);
      await auth.register({ email, username, password, password_confirm, first_name, last_name });
      goto('/dashboard');
    } catch (e: any) {
      error = e.message || 'Registration failed';
    } finally { loading = false; }
  }
</script>

<div class="w-full max-w-md">
  <div class="text-center mb-8">
    <div class="inline-flex items-center justify-center w-12 h-12 bg-blue-600 rounded-xl mb-4">
      <span class="text-white text-xl font-bold">P</span>
    </div>
    <h1 class="text-2xl font-bold text-gray-900 dark:text-white">Create your account</h1>
    <p class="text-gray-500 mt-1">Start winning more clients with AI</p>
  </div>
  <div class="bg-white dark:bg-gray-900 rounded-2xl shadow-xl border border-gray-100 dark:border-gray-800 p-8">
    {#if error}
      <div class="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg text-red-700 text-sm">{error}</div>
    {/if}
    <form onsubmit={(e) => { e.preventDefault(); handleRegister(); }} class="space-y-4">
      <div class="grid grid-cols-2 gap-3">
        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1.5">First name</label>
          <input bind:value={first_name} type="text" class="w-full px-3.5 py-2.5 rounded-lg border border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-800 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500 outline-none transition text-sm" />
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1.5">Last name</label>
          <input bind:value={last_name} type="text" class="w-full px-3.5 py-2.5 rounded-lg border border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-800 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500 outline-none transition text-sm" />
        </div>
      </div>
      <div>
        <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1.5">Email *</label>
        <input bind:value={email} type="email" required class="w-full px-3.5 py-2.5 rounded-lg border border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-800 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500 outline-none transition text-sm" />
      </div>
      <div>
        <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1.5">Password *</label>
        <input bind:value={password} type="password" required minlength={8} class="w-full px-3.5 py-2.5 rounded-lg border border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-800 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500 outline-none transition text-sm" />
      </div>
      <div>
        <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1.5">Confirm password *</label>
        <input bind:value={password_confirm} type="password" required class="w-full px-3.5 py-2.5 rounded-lg border border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-800 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500 outline-none transition text-sm" />
      </div>
      <button type="submit" disabled={loading} class="w-full py-2.5 px-4 bg-blue-600 hover:bg-blue-700 disabled:opacity-60 text-white font-semibold rounded-lg transition-colors text-sm">
        {loading ? 'Creating account...' : 'Create free account'}
      </button>
    </form>
    <p class="text-center text-sm text-gray-500 mt-4">Already have an account? <a href="/login" class="text-blue-600 hover:underline font-medium">Sign in</a></p>
  </div>
</div>
