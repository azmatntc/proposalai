python3 << 'PYEOF'
import os

layout = '''<script lang="ts">
  import { auth } from '$lib/stores/auth.svelte';
  import { ui } from '$lib/stores/ui.svelte';
  import { goto } from '$app/navigation';
  import { page } from '$app/stores';
  import {
    Bell, LayoutDashboard, FileText, Users, Settings,
    ChevronLeft, ChevronRight, LogOut, Sparkles,
    Sun, Moon, Menu, X, Layers, BarChart2
  } from 'lucide-svelte';

  let { children } = $props();

  $effect(() => {
    if (!auth.isLoading && !auth.isAuthenticated) goto('/login');
  });

  function isActive(href: string) {
    return $page.url.pathname === href || $page.url.pathname.startsWith(href + '/');
  }

  function toggleTheme() {
    const next = ui.theme === 'dark' ? 'light' : 'dark';
    ui.theme = next;
    if (typeof localStorage !== 'undefined') localStorage.setItem('theme', next);
    document.documentElement.classList.toggle('dark', next === 'dark');
  }

  const quotaPct = $derived(
    auth.user
      ? (auth.user.proposals_generated_this_month / auth.user.monthly_proposal_quota) * 100
      : 0
  );
</script>

{#if auth.isLoading}
  <div class="min-h-screen flex items-center justify-center bg-gray-50 dark:bg-gray-950">
    <div class="w-8 h-8 border-2 border-blue-500 border-t-transparent rounded-full animate-spin"></div>
  </div>
{:else if auth.isAuthenticated}
  <div class="flex h-screen overflow-hidden bg-gray-50 dark:bg-gray-950">

    <!-- Sidebar -->
    <aside class="relative hidden md:flex flex-col {ui.sidebarCollapsed ? \'w-16\' : \'w-64\'}
      bg-white dark:bg-gray-900 border-r border-gray-200 dark:border-gray-800
      transition-all duration-200 flex-shrink-0">

      <!-- Logo -->
      <div class="flex items-center {ui.sidebarCollapsed ? \'justify-center\' : \'px-5\'}
        h-16 border-b border-gray-200 dark:border-gray-800 flex-shrink-0">
        <div class="flex items-center gap-2.5">
          <div class="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center flex-shrink-0">
            <Sparkles size={16} class="text-white" />
          </div>
          {#if !ui.sidebarCollapsed}
            <span class="font-bold text-gray-900 dark:text-white text-sm">ProposalAI</span>
          {/if}
        </div>
      </div>

      <!-- Nav -->
      <nav class="flex-1 py-3 {ui.sidebarCollapsed ? \'px-2\' : \'px-3\'} space-y-0.5 overflow-y-auto">

        <a href="/dashboard"
          class="flex items-center {ui.sidebarCollapsed ? \'justify-center px-2\' : \'px-3\'}
            py-2.5 rounded-lg text-sm font-medium transition-colors gap-3
            {isActive(\'/dashboard\') ? \'bg-blue-50 dark:bg-blue-900/20 text-blue-700 dark:text-blue-400\' : \'text-gray-600 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-800 hover:text-gray-900 dark:hover:text-white\'}">
          <LayoutDashboard size={18} class="flex-shrink-0" />
          {#if !ui.sidebarCollapsed}<span>Dashboard</span>{/if}
        </a>

        <a href="/proposals"
          class="flex items-center {ui.sidebarCollapsed ? \'justify-center px-2\' : \'px-3\'}
            py-2.5 rounded-lg text-sm font-medium transition-colors gap-3
            {isActive(\'/proposals\') ? \'bg-blue-50 dark:bg-blue-900/20 text-blue-700 dark:text-blue-400\' : \'text-gray-600 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-800 hover:text-gray-900 dark:hover:text-white\'}">
          <FileText size={18} class="flex-shrink-0" />
          {#if !ui.sidebarCollapsed}<span>Proposals</span>{/if}
        </a>

        <a href="/leads"
          class="flex items-center {ui.sidebarCollapsed ? \'justify-center px-2\' : \'px-3\'}
            py-2.5 rounded-lg text-sm font-medium transition-colors gap-3
            {isActive(\'/leads\') ? \'bg-blue-50 dark:bg-blue-900/20 text-blue-700 dark:text-blue-400\' : \'text-gray-600 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-800 hover:text-gray-900 dark:hover:text-white\'}">
          <Users size={18} class="flex-shrink-0" />
          {#if !ui.sidebarCollapsed}<span>Leads CRM</span>{/if}
        </a>

        <a href="/templates"
          class="flex items-center {ui.sidebarCollapsed ? \'justify-center px-2\' : \'px-3\'}
            py-2.5 rounded-lg text-sm font-medium transition-colors gap-3
            {isActive(\'/templates\') ? \'bg-blue-50 dark:bg-blue-900/20 text-blue-700 dark:text-blue-400\' : \'text-gray-600 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-800 hover:text-gray-900 dark:hover:text-white\'}">
          <Layers size={18} class="flex-shrink-0" />
          {#if !ui.sidebarCollapsed}<span>Templates</span>{/if}
        </a>

        <a href="/analytics"
          class="flex items-center {ui.sidebarCollapsed ? \'justify-center px-2\' : \'px-3\'}
            py-2.5 rounded-lg text-sm font-medium transition-colors gap-3
            {isActive(\'/analytics\') ? \'bg-blue-50 dark:bg-blue-900/20 text-blue-700 dark:text-blue-400\' : \'text-gray-600 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-800 hover:text-gray-900 dark:hover:text-white\'}">
          <BarChart2 size={18} class="flex-shrink-0" />
          {#if !ui.sidebarCollapsed}<span>Analytics</span>{/if}
        </a>

        <a href="/settings"
          class="flex items-center {ui.sidebarCollapsed ? \'justify-center px-2\' : \'px-3\'}
            py-2.5 rounded-lg text-sm font-medium transition-colors gap-3
            {isActive(\'/settings\') ? \'bg-blue-50 dark:bg-blue-900/20 text-blue-700 dark:text-blue-400\' : \'text-gray-600 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-800 hover:text-gray-900 dark:hover:text-white\'}">
          <Settings size={18} class="flex-shrink-0" />
          {#if !ui.sidebarCollapsed}<span>Settings</span>{/if}
        </a>

      </nav>

      <!-- Quota + user footer -->
      {#if !ui.sidebarCollapsed && auth.user}
        <div class="p-4 border-t border-gray-200 dark:border-gray-800 flex-shrink-0">
          <div class="mb-3">
            <div class="flex justify-between text-xs text-gray-500 mb-1.5">
              <span>AI Quota</span>
              <span>{auth.user.proposals_generated_this_month}/{auth.user.monthly_proposal_quota}</span>
            </div>
            <div class="h-1.5 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden">
              <div class="h-full rounded-full transition-all duration-300
                {quotaPct > 80 ? \'bg-red-500\' : quotaPct > 60 ? \'bg-amber-500\' : \'bg-blue-500\'}"
                style="width: {Math.min(quotaPct, 100)}%"></div>
            </div>
          </div>
          <div class="flex items-center gap-2.5">
            <img src={auth.user.avatar_url} alt={auth.user.short_name}
              class="w-7 h-7 rounded-full bg-gray-200 flex-shrink-0" />
            <div class="flex-1 min-w-0">
              <p class="text-xs font-semibold text-gray-900 dark:text-white truncate">{auth.user.full_name}</p>
              <p class="text-xs text-gray-400 capitalize">{auth.user.subscription_tier}</p>
            </div>
            <button onclick={() => auth.logout().then(() => goto(\'/login\'))}
              title="Sign out"
              class="text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 transition-colors">
              <LogOut size={14} />
            </button>
          </div>
        </div>
      {/if}

      <!-- Collapse toggle button -->
      <button onclick={ui.toggleCollapse}
        class="absolute -right-3 top-20 w-6 h-6 bg-white dark:bg-gray-900
          border border-gray-200 dark:border-gray-700 rounded-full flex items-center
          justify-center shadow-sm hover:bg-gray-50 dark:hover:bg-gray-800 z-10 transition-colors">
        {#if ui.sidebarCollapsed}
          <ChevronRight size={12} class="text-gray-500" />
        {:else}
          <ChevronLeft size={12} class="text-gray-500" />
        {/if}
      </button>
    </aside>

    <!-- Main content -->
    <div class="flex-1 flex flex-col overflow-hidden min-w-0">

      <!-- Top bar -->
      <header class="h-16 bg-white dark:bg-gray-900 border-b border-gray-200 dark:border-gray-800
        flex items-center px-4 md:px-6 gap-4 flex-shrink-0">
        <button class="md:hidden text-gray-500" onclick={ui.toggleSidebar}>
          <Menu size={20} />
        </button>
        <div class="flex-1"></div>
        <button onclick={toggleTheme}
          class="w-9 h-9 flex items-center justify-center rounded-lg text-gray-500
            hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors">
          {#if ui.theme === \'dark\'}<Sun size={18} />{:else}<Moon size={18} />{/if}
        </button>
        <button class="w-9 h-9 flex items-center justify-center rounded-lg text-gray-500
          hover:bg-gray-100 dark:hover:bg-gray-800 relative transition-colors">
          <Bell size={18} />
          <span class="absolute top-2 right-2 w-2 h-2 bg-blue-500 rounded-full"></span>
        </button>
        {#if auth.user}
          <button onclick={() => goto(\'/settings\')}>
            <img src={auth.user.avatar_url} alt=""
              class="w-8 h-8 rounded-full ring-2 ring-transparent hover:ring-blue-300 transition-all" />
          </button>
        {/if}
      </header>

      <!-- Page content -->
      <main class="flex-1 overflow-auto">
        <div class="page-transition h-full">
          {@render children()}
        </div>
      </main>
    </div>

    <!-- Mobile sidebar overlay -->
    {#if ui.sidebarOpen}
      <div class="fixed inset-0 z-40 md:hidden">
        <div class="absolute inset-0 bg-black/50 backdrop-blur-sm" onclick={ui.toggleSidebar}></div>
        <div class="absolute left-0 top-0 bottom-0 w-64 bg-white dark:bg-gray-900 shadow-2xl flex flex-col">
          <div class="flex items-center justify-between px-5 h-16 border-b border-gray-200 dark:border-gray-800">
            <div class="flex items-center gap-2.5">
              <div class="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center">
                <Sparkles size={16} class="text-white" />
              </div>
              <span class="font-bold text-gray-900 dark:text-white">ProposalAI</span>
            </div>
            <button onclick={ui.toggleSidebar} class="text-gray-400"><X size={20} /></button>
          </div>
          <nav class="flex-1 py-3 px-3 space-y-0.5 overflow-y-auto">
            <a href="/dashboard" onclick={ui.toggleSidebar} class="flex items-center px-3 py-2.5 rounded-lg text-sm font-medium gap-3 text-gray-600 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-800">
              <LayoutDashboard size={18} /><span>Dashboard</span>
            </a>
            <a href="/proposals" onclick={ui.toggleSidebar} class="flex items-center px-3 py-2.5 rounded-lg text-sm font-medium gap-3 text-gray-600 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-800">
              <FileText size={18} /><span>Proposals</span>
            </a>
            <a href="/leads" onclick={ui.toggleSidebar} class="flex items-center px-3 py-2.5 rounded-lg text-sm font-medium gap-3 text-gray-600 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-800">
              <Users size={18} /><span>Leads CRM</span>
            </a>
            <a href="/templates" onclick={ui.toggleSidebar} class="flex items-center px-3 py-2.5 rounded-lg text-sm font-medium gap-3 text-gray-600 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-800">
              <Layers size={18} /><span>Templates</span>
            </a>
            <a href="/analytics" onclick={ui.toggleSidebar} class="flex items-center px-3 py-2.5 rounded-lg text-sm font-medium gap-3 text-gray-600 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-800">
              <BarChart2 size={18} /><span>Analytics</span>
            </a>
            <a href="/settings" onclick={ui.toggleSidebar} class="flex items-center px-3 py-2.5 rounded-lg text-sm font-medium gap-3 text-gray-600 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-800">
              <Settings size={18} /><span>Settings</span>
            </a>
          </nav>
          {#if auth.user}
            <div class="p-4 border-t border-gray-200 dark:border-gray-800">
              <div class="flex items-center gap-2.5">
                <img src={auth.user.avatar_url} alt="" class="w-7 h-7 rounded-full" />
                <div class="flex-1 min-w-0">
                  <p class="text-xs font-semibold text-gray-900 dark:text-white truncate">{auth.user.full_name}</p>
                  <p class="text-xs text-gray-400">{auth.user.email}</p>
                </div>
              </div>
              <button onclick={() => auth.logout().then(() => goto(\'/login\'))}
                class="mt-3 w-full py-2 text-sm text-red-600 hover:bg-red-50 dark:hover:bg-red-900/20 rounded-lg flex items-center justify-center gap-2">
                <LogOut size={14} /> Sign out
              </button>
            </div>
          {/if}
        </div>
      </div>
    {/if}python3 << 'PYEOF'
import os

layout = '''<script lang="ts">
  import { auth } from '$lib/stores/auth.svelte';
  import { ui } from '$lib/stores/ui.svelte';
  import { goto } from '$app/navigation';
  import { page } from '$app/stores';
  import {
    Bell, LayoutDashboard, FileText, Users, Settings,
    ChevronLeft, ChevronRight, LogOut, Sparkles,
    Sun, Moon, Menu, X, Layers, BarChart2
  } from 'lucide-svelte';

  let { children } = $props();

  $effect(() => {
    if (!auth.isLoading && !auth.isAuthenticated) goto('/login');
  });

  function isActive(href: string) {
    return $page.url.pathname === href || $page.url.pathname.startsWith(href + '/');
  }

  function toggleTheme() {
    const next = ui.theme === 'dark' ? 'light' : 'dark';
    ui.theme = next;
    if (typeof localStorage !== 'undefined') localStorage.setItem('theme', next);
    document.documentElement.classList.toggle('dark', next === 'dark');
  }

  const quotaPct = $derived(
    auth.user
      ? (auth.user.proposals_generated_this_month / auth.user.monthly_proposal_quota) * 100
      : 0
  );
</script>

{#if auth.isLoading}
  <div class="min-h-screen flex items-center justify-center bg-gray-50 dark:bg-gray-950">
    <div class="w-8 h-8 border-2 border-blue-500 border-t-transparent rounded-full animate-spin"></div>
  </div>
{:else if auth.isAuthenticated}
  <div class="flex h-screen overflow-hidden bg-gray-50 dark:bg-gray-950">

    <!-- Sidebar -->
    <aside class="relative hidden md:flex flex-col {ui.sidebarCollapsed ? \'w-16\' : \'w-64\'}
      bg-white dark:bg-gray-900 border-r border-gray-200 dark:border-gray-800
      transition-all duration-200 flex-shrink-0">

      <!-- Logo -->
      <div class="flex items-center {ui.sidebarCollapsed ? \'justify-center\' : \'px-5\'}
        h-16 border-b border-gray-200 dark:border-gray-800 flex-shrink-0">
        <div class="flex items-center gap-2.5">
          <div class="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center flex-shrink-0">
            <Sparkles size={16} class="text-white" />
          </div>
          {#if !ui.sidebarCollapsed}
            <span class="font-bold text-gray-900 dark:text-white text-sm">ProposalAI</span>
          {/if}
        </div>
      </div>

      <!-- Nav -->
      <nav class="flex-1 py-3 {ui.sidebarCollapsed ? \'px-2\' : \'px-3\'} space-y-0.5 overflow-y-auto">

        <a href="/dashboard"
          class="flex items-center {ui.sidebarCollapsed ? \'justify-center px-2\' : \'px-3\'}
            py-2.5 rounded-lg text-sm font-medium transition-colors gap-3
            {isActive(\'/dashboard\') ? \'bg-blue-50 dark:bg-blue-900/20 text-blue-700 dark:text-blue-400\' : \'text-gray-600 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-800 hover:text-gray-900 dark:hover:text-white\'}">
          <LayoutDashboard size={18} class="flex-shrink-0" />
          {#if !ui.sidebarCollapsed}<span>Dashboard</span>{/if}
        </a>

        <a href="/proposals"
          class="flex items-center {ui.sidebarCollapsed ? \'justify-center px-2\' : \'px-3\'}
            py-2.5 rounded-lg text-sm font-medium transition-colors gap-3
            {isActive(\'/proposals\') ? \'bg-blue-50 dark:bg-blue-900/20 text-blue-700 dark:text-blue-400\' : \'text-gray-600 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-800 hover:text-gray-900 dark:hover:text-white\'}">
          <FileText size={18} class="flex-shrink-0" />
          {#if !ui.sidebarCollapsed}<span>Proposals</span>{/if}
        </a>

        <a href="/leads"
          class="flex items-center {ui.sidebarCollapsed ? \'justify-center px-2\' : \'px-3\'}
            py-2.5 rounded-lg text-sm font-medium transition-colors gap-3
            {isActive(\'/leads\') ? \'bg-blue-50 dark:bg-blue-900/20 text-blue-700 dark:text-blue-400\' : \'text-gray-600 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-800 hover:text-gray-900 dark:hover:text-white\'}">
          <Users size={18} class="flex-shrink-0" />
          {#if !ui.sidebarCollapsed}<span>Leads CRM</span>{/if}
        </a>

        <a href="/templates"
          class="flex items-center {ui.sidebarCollapsed ? \'justify-center px-2\' : \'px-3\'}
            py-2.5 rounded-lg text-sm font-medium transition-colors gap-3
            {isActive(\'/templates\') ? \'bg-blue-50 dark:bg-blue-900/20 text-blue-700 dark:text-blue-400\' : \'text-gray-600 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-800 hover:text-gray-900 dark:hover:text-white\'}">
          <Layers size={18} class="flex-shrink-0" />
          {#if !ui.sidebarCollapsed}<span>Templates</span>{/if}
        </a>

        <a href="/analytics"
          class="flex items-center {ui.sidebarCollapsed ? \'justify-center px-2\' : \'px-3\'}
            py-2.5 rounded-lg text-sm font-medium transition-colors gap-3
            {isActive(\'/analytics\') ? \'bg-blue-50 dark:bg-blue-900/20 text-blue-700 dark:text-blue-400\' : \'text-gray-600 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-800 hover:text-gray-900 dark:hover:text-white\'}">
          <BarChart2 size={18} class="flex-shrink-0" />
          {#if !ui.sidebarCollapsed}<span>Analytics</span>{/if}
        </a>

        <a href="/settings"
          class="flex items-center {ui.sidebarCollapsed ? \'justify-center px-2\' : \'px-3\'}
            py-2.5 rounded-lg text-sm font-medium transition-colors gap-3
            {isActive(\'/settings\') ? \'bg-blue-50 dark:bg-blue-900/20 text-blue-700 dark:text-blue-400\' : \'text-gray-600 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-800 hover:text-gray-900 dark:hover:text-white\'}">
          <Settings size={18} class="flex-shrink-0" />
          {#if !ui.sidebarCollapsed}<span>Settings</span>{/if}
        </a>

      </nav>

      <!-- Quota + user footer -->
      {#if !ui.sidebarCollapsed && auth.user}
        <div class="p-4 border-t border-gray-200 dark:border-gray-800 flex-shrink-0">
          <div class="mb-3">
            <div class="flex justify-between text-xs text-gray-500 mb-1.5">
              <span>AI Quota</span>
              <span>{auth.user.proposals_generated_this_month}/{auth.user.monthly_proposal_quota}</span>
            </div>
            <div class="h-1.5 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden">
              <div class="h-full rounded-full transition-all duration-300
                {quotaPct > 80 ? \'bg-red-500\' : quotaPct > 60 ? \'bg-amber-500\' : \'bg-blue-500\'}"
                style="width: {Math.min(quotaPct, 100)}%"></div>
            </div>
          </div>
          <div class="flex items-center gap-2.5">
            <img src={auth.user.avatar_url} alt={auth.user.short_name}
              class="w-7 h-7 rounded-full bg-gray-200 flex-shrink-0" />
            <div class="flex-1 min-w-0">
              <p class="text-xs font-semibold text-gray-900 dark:text-white truncate">{auth.user.full_name}</p>
              <p class="text-xs text-gray-400 capitalize">{auth.user.subscription_tier}</p>
            </div>
            <button onclick={() => auth.logout().then(() => goto(\'/login\'))}
              title="Sign out"
              class="text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 transition-colors">
              <LogOut size={14} />
            </button>
          </div>
        </div>
      {/if}

      """<!-- Collapse toggle button -->"""
      <button onclick={ui.toggleCollapse}
        class="absolute -right-3 top-20 w-6 h-6 bg-white dark:bg-gray-900
          border border-gray-200 dark:border-gray-700 rounded-full flex items-center
          justify-center shadow-sm hover:bg-gray-50 dark:hover:bg-gray-800 z-10 transition-colors">
        {#if ui.sidebarCollapsed}
          <ChevronRight size={12} class="text-gray-500" />
        {:else}
          <ChevronLeft size={12} class="text-gray-500" />
        {/if}
      </button>
    </aside>

    <!-- Main content -->
    <div class="flex-1 flex flex-col overflow-hidden min-w-0">

      <!-- Top bar -->
      <header class="h-16 bg-white dark:bg-gray-900 border-b border-gray-200 dark:border-gray-800
        flex items-center px-4 md:px-6 gap-4 flex-shrink-0">
        <button class="md:hidden text-gray-500" onclick={ui.toggleSidebar}>
          <Menu size={20} />
        </button>
        <div class="flex-1"></div>
        <button onclick={toggleTheme}
          class="w-9 h-9 flex items-center justify-center rounded-lg text-gray-500
            hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors">
          {#if ui.theme === \'dark\'}<Sun size={18} />{:else}<Moon size={18} />{/if}
        </button>
        <button class="w-9 h-9 flex items-center justify-center rounded-lg text-gray-500
          hover:bg-gray-100 dark:hover:bg-gray-800 relative transition-colors">
          <Bell size={18} />
          <span class="absolute top-2 right-2 w-2 h-2 bg-blue-500 rounded-full"></span>
        </button>
        {#if auth.user}
          <button onclick={() => goto(\'/settings\')}>
            <img src={auth.user.avatar_url} alt=""
              class="w-8 h-8 rounded-full ring-2 ring-transparent hover:ring-blue-300 transition-all" />
          </button>
        {/if}
      </header>

      <!-- Page content -->
      <main class="flex-1 overflow-auto">
        <div class="page-transition h-full">
          {@render children()}
        </div>
      </main>
    </div>

    <!-- Mobile sidebar overlay -->
    {#if ui.sidebarOpen}
      <div class="fixed inset-0 z-40 md:hidden">
        <div class="absolute inset-0 bg-black/50 backdrop-blur-sm" onclick={ui.toggleSidebar}></div>
        <div class="absolute left-0 top-0 bottom-0 w-64 bg-white dark:bg-gray-900 shadow-2xl flex flex-col">
          <div class="flex items-center justify-between px-5 h-16 border-b border-gray-200 dark:border-gray-800">
            <div class="flex items-center gap-2.5">
              <div class="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center">
                <Sparkles size={16} class="text-white" />
              </div>
              <span class="font-bold text-gray-900 dark:text-white">ProposalAI</span>
            </div>
            <button onclick={ui.toggleSidebar} class="text-gray-400"><X size={20} /></button>
          </div>
          <nav class="flex-1 py-3 px-3 space-y-0.5 overflow-y-auto">
            <a href="/dashboard" onclick={ui.toggleSidebar} class="flex items-center px-3 py-2.5 rounded-lg text-sm font-medium gap-3 text-gray-600 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-800">
              <LayoutDashboard size={18} /><span>Dashboard</span>
            </a>
            <a href="/proposals" onclick={ui.toggleSidebar} class="flex items-center px-3 py-2.5 rounded-lg text-sm font-medium gap-3 text-gray-600 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-800">
              <FileText size={18} /><span>Proposals</span>
            </a>
            <a href="/leads" onclick={ui.toggleSidebar} class="flex items-center px-3 py-2.5 rounded-lg text-sm font-medium gap-3 text-gray-600 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-800">
              <Users size={18} /><span>Leads CRM</span>
            </a>
            <a href="/templates" onclick={ui.toggleSidebar} class="flex items-center px-3 py-2.5 rounded-lg text-sm font-medium gap-3 text-gray-600 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-800">
              <Layers size={18} /><span>Templates</span>
            </a>
            <a href="/analytics" onclick={ui.toggleSidebar} class="flex items-center px-3 py-2.5 rounded-lg text-sm font-medium gap-3 text-gray-600 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-800">
              <BarChart2 size={18} /><span>Analytics</span>
            </a>
            <a href="/settings" onclick={ui.toggleSidebar} class="flex items-center px-3 py-2.5 rounded-lg text-sm font-medium gap-3 text-gray-600 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-800">
              <Settings size={18} /><span>Settings</span>
            </a>
          </nav>
          {#if auth.user}
            <div class="p-4 border-t border-gray-200 dark:border-gray-800">
              <div class="flex items-center gap-2.5">
                <img src={auth.user.avatar_url} alt="" class="w-7 h-7 rounded-full" />
                <div class="flex-1 min-w-0">
                  <p class="text-xs font-semibold text-gray-900 dark:text-white truncate">{auth.user.full_name}</p>
                  <p class="text-xs text-gray-400">{auth.user.email}</p>
                </div>
              </div>
              <button onclick={() => auth.logout().then(() => goto(\'/login\'))}
                class="mt-3 w-full py-2 text-sm text-red-600 hover:bg-red-50 dark:hover:bg-red-900/20 rounded-lg flex items-center justify-center gap-2">
                <LogOut size={14} /> Sign out
              </button>
            </div>
          {/if}
        </div>
      </div>
    {/if}

  </div>
{/if}
'''

path = '/home/azmat/projects/proposalai/frontend/src/routes/(app)/+layout.svelte'
os.makedirs(os.path.dirname(path), exist_ok=True)
with open(path, 'w') as f:
    f.write(layout)
print(
    f'Nav items in file: {layout.count("href=\"/templates\"") 
    + layout.count("href=\"/analytics\"") 
    + layout.count("href=\"/leads\"") 
    + layout.count("href=\"/proposals\"") 
    + layout.count("href=\"/dashboard\"") 
    + layout.count("href=\"/settings\"")} links total'
)
PYEOF

  </div>
{/if}
'''

path = '/home/azmat/projects/proposalai/frontend/src/routes/(app)/+layout.svelte'
os.makedirs(os.path.dirname(path), exist_ok=True)
with open(path, 'w') as f:
    f.write(layout)
print(f'Written {path}')
print(f'Nav items in file: {layout.count("href=\\"/templates\\"") + layout.count("href=\\"/analytics\\"") + layout.count("href=\\"/leads\\"") + layout.count("href=\\"/proposals\\"") + layout.count("href=\\"/dashboard\\"") + layout.count("href=\\"/settings\\"")} links total')
PYEOF