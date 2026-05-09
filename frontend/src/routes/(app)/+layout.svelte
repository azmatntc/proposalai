<script lang="ts">
  import { auth } from "$lib/stores/auth.svelte";
  import { ui } from "$lib/stores/ui.svelte";
  import { goto } from "$app/navigation";
  import { page } from "$app/stores";

  let { children } = $props();

  $effect(() => {
    if (!auth.isLoading && !auth.isAuthenticated) {
      goto("/login");
    }
  });

  /** Returns true if the current URL matches this nav item */
  function active(href: string): boolean {
    return (
      $page.url.pathname === href || $page.url.pathname.startsWith(href + "/")
    );
  }

  /** Base classes shared by every nav link */
  const linkBase =
    "flex items-center gap-3 py-2.5 rounded-lg text-sm font-medium transition-colors";

  function linkClass(href: string): string {
    const padding = ui.sidebarCollapsed ? "justify-center px-2" : "px-3";
    const color = active(href)
      ? "bg-blue-50 dark:bg-blue-900/20 text-blue-700 dark:text-blue-400"
      : "text-gray-600 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-800 hover:text-gray-900 dark:hover:text-white";
    return `${linkBase} ${padding} ${color}`;
  }

  function toggleTheme() {
    const next = ui.theme === "dark" ? "light" : "dark";
    ui.theme = next;
    localStorage.setItem("theme", next);
    document.documentElement.classList.toggle("dark", next === "dark");
  }

  const quotaPct = $derived(
    auth.user
      ? (auth.user.proposals_generated_this_month /
          auth.user.monthly_proposal_quota) *
          100
      : 0,
  );

  const currentPageName = $derived(
    $page.url.pathname.split("/").filter(Boolean)[0] ?? "dashboard",
  );
</script>

{#if auth.isLoading}
  <div
    class="min-h-screen flex items-center justify-center bg-gray-50 dark:bg-gray-950"
  >
    <div
      class="w-8 h-8 border-2 border-blue-500 border-t-transparent rounded-full animate-spin"
    ></div>
  </div>
{:else if auth.isAuthenticated}
  <div class="flex h-screen overflow-hidden bg-gray-50 dark:bg-gray-950">
    <!-- ═══════════════════════════════════════════════════════
         DESKTOP SIDEBAR
    ═══════════════════════════════════════════════════════ -->
    <aside
      class="relative hidden md:flex flex-col flex-shrink-0 transition-all duration-200
        bg-white dark:bg-gray-900 border-r border-gray-200 dark:border-gray-800
        {ui.sidebarCollapsed ? 'w-16' : 'w-64'}"
    >
      <!-- Logo -->
      <div
        class="flex items-center h-16 flex-shrink-0 border-b border-gray-200 dark:border-gray-800
          {ui.sidebarCollapsed ? 'justify-center' : 'px-5'}"
      >
        <div class="flex items-center gap-2.5">
          <div
            class="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center flex-shrink-0"
          >
            <svg
              width="16"
              height="16"
              viewBox="0 0 24 24"
              fill="none"
              stroke="white"
              stroke-width="2.5"
            >
              <path d="M12 2L2 7l10 5 10-5-10-5z" />
              <path d="M2 17l10 5 10-5" />
              <path d="M2 12l10 5 10-5" />
            </svg>
          </div>
          {#if !ui.sidebarCollapsed}
            <span class="font-bold text-gray-900 dark:text-white text-sm"
              >ProposalAI</span
            >
          {/if}
        </div>
      </div>

      <!-- Navigation -->
      <nav
        class="flex-1 overflow-y-auto py-3 space-y-0.5
          {ui.sidebarCollapsed ? 'px-2' : 'px-3'}"
      >
        <!-- Dashboard -->
        <a href="/dashboard" class={linkClass("/dashboard")}>
          <svg
            class="flex-shrink-0"
            width="18"
            height="18"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            stroke-width="2"
          >
            <rect x="3" y="3" width="7" height="7" /><rect
              x="14"
              y="3"
              width="7"
              height="7"
            />
            <rect x="14" y="14" width="7" height="7" /><rect
              x="3"
              y="14"
              width="7"
              height="7"
            />
          </svg>
          {#if !ui.sidebarCollapsed}<span>Dashboard</span>{/if}
        </a>

        <!-- Proposals -->
        <a href="/proposals" class={linkClass("/proposals")}>
          <svg
            class="flex-shrink-0"
            width="18"
            height="18"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            stroke-width="2"
          >
            <path
              d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"
            />
            <polyline points="14,2 14,8 20,8" />
            <line x1="16" y1="13" x2="8" y2="13" /><line
              x1="16"
              y1="17"
              x2="8"
              y2="17"
            />
            <polyline points="10,9 9,9 8,9" />
          </svg>
          {#if !ui.sidebarCollapsed}<span>Proposals</span>{/if}
        </a>

        <!-- Leads CRM -->
        <a href="/leads" class={linkClass("/leads")}>
          <svg
            class="flex-shrink-0"
            width="18"
            height="18"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            stroke-width="2"
          >
            <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2" />
            <circle cx="9" cy="7" r="4" />
            <path d="M23 21v-2a4 4 0 0 0-3-3.87" />
            <path d="M16 3.13a4 4 0 0 1 0 7.75" />
          </svg>
          {#if !ui.sidebarCollapsed}<span>Leads CRM</span>{/if}
        </a>

        <!-- Templates -->
        <a href="/templates" class={linkClass("/templates")}>
          <svg
            class="flex-shrink-0"
            width="18"
            height="18"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            stroke-width="2"
          >
            <rect x="2" y="2" width="9" height="9" /><rect
              x="13"
              y="2"
              width="9"
              height="9"
            />
            <rect x="13" y="13" width="9" height="9" /><rect
              x="2"
              y="13"
              width="9"
              height="9"
            />
          </svg>
          {#if !ui.sidebarCollapsed}<span>Templates</span>{/if}
        </a>

        <!-- Analytics -->
        <a href="/analytics" class={linkClass("/analytics")}>
          <svg
            class="flex-shrink-0"
            width="18"
            height="18"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            stroke-width="2"
          >
            <line x1="18" y1="20" x2="18" y2="10" />
            <line x1="12" y1="20" x2="12" y2="4" />
            <line x1="6" y1="20" x2="6" y2="14" />
          </svg>
          {#if !ui.sidebarCollapsed}<span>Analytics</span>{/if}
        </a>

        <!-- Settings -->
        <a href="/settings" class={linkClass("/settings")}>
          <svg
            class="flex-shrink-0"
            width="18"
            height="18"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            stroke-width="2"
          >
            <circle cx="12" cy="12" r="3" />
            <path
              d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1-2.83 2.83l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-4 0v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83-2.83l.06-.06A1.65 1.65 0 0 0 4.68 15a1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1 0-4h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 2.83-2.83l.06.06A1.65 1.65 0 0 0 9 4.68a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 4 0v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 2.83l-.06.06A1.65 1.65 0 0 0 19.4 9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 0 4h-.09a1.65 1.65 0 0 0-1.51 1z"
            />
          </svg>
          {#if !ui.sidebarCollapsed}<span>Settings</span>{/if}
        </a>
      </nav>

      <!-- Quota + User footer -->
      {#if !ui.sidebarCollapsed && auth.user}
        <div
          class="p-4 border-t border-gray-200 dark:border-gray-800 flex-shrink-0"
        >
          <!-- Quota bar -->
          <div class="mb-3">
            <div class="flex justify-between text-xs text-gray-500 mb-1.5">
              <span>AI Quota</span>
              <span
                >{auth.user.proposals_generated_this_month}/{auth.user
                  .monthly_proposal_quota}</span
              >
            </div>
            <div
              class="h-1.5 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden"
            >
              <div
                class="h-full rounded-full transition-all duration-300
                  {quotaPct > 80
                  ? 'bg-red-500'
                  : quotaPct > 60
                    ? 'bg-amber-500'
                    : 'bg-blue-500'}"
                style="width: {Math.min(quotaPct, 100)}%"
              ></div>
            </div>
          </div>
          <!-- User row -->
          <div class="flex items-center gap-2.5">
            <img
              src={auth.user.avatar_url}
              alt={auth.user.short_name}
              class="w-7 h-7 rounded-full bg-gray-200 flex-shrink-0"
            />
            <div class="flex-1 min-w-0">
              <p
                class="text-xs font-semibold text-gray-900 dark:text-white truncate"
              >
                {auth.user.full_name}
              </p>
              <p class="text-xs text-gray-400 capitalize">
                {auth.user.subscription_tier}
              </p>
            </div>
            <button
              onclick={() => auth.logout().then(() => goto("/login"))}
              title="Sign out"
              class="text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 transition-colors p-1"
            >
              <svg
                width="14"
                height="14"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                stroke-width="2"
              >
                <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4" />
                <polyline points="16,17 21,12 16,7" />
                <line x1="21" y1="12" x2="9" y2="12" />
              </svg>
            </button>
          </div>
        </div>
      {/if}

      <!-- Collapse button -->
      <button
        onclick={ui.toggleCollapse}
        class="absolute -right-3 top-20 w-6 h-6 bg-white dark:bg-gray-900
          border border-gray-200 dark:border-gray-700 rounded-full
          flex items-center justify-center shadow-sm z-10
          hover:bg-gray-50 dark:hover:bg-gray-800 transition-colors"
      >
        {#if ui.sidebarCollapsed}
          <svg
            width="10"
            height="10"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            stroke-width="2.5"
          >
            <polyline points="9,18 15,12 9,6" />
          </svg>
        {:else}
          <svg
            width="10"
            height="10"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            stroke-width="2.5"
          >
            <polyline points="15,18 9,12 15,6" />
          </svg>
        {/if}
      </button>
    </aside>

    <!-- ═══════════════════════════════════════════════════════
         MAIN CONTENT AREA
    ═══════════════════════════════════════════════════════ -->
    <div class="flex-1 flex flex-col overflow-hidden min-w-0">
      <!-- Top bar -->
      <header
        class="h-16 flex-shrink-0 flex items-center gap-4 px-4 md:px-6
          bg-white dark:bg-gray-900 border-b border-gray-200 dark:border-gray-800"
      >
        <!-- Mobile menu button -->
        <button
          class="md:hidden text-gray-500 hover:text-gray-700 dark:hover:text-gray-300"
          onclick={ui.toggleSidebar}
          aria-label="Open menu"
        >
          <svg
            width="20"
            height="20"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            stroke-width="2"
          >
            <line x1="3" y1="12" x2="21" y2="12" />
            <line x1="3" y1="6" x2="21" y2="6" />
            <line x1="3" y1="18" x2="21" y2="18" />
          </svg>
        </button>

        <!-- Current page name -->
        <span
          class="hidden md:block text-sm font-semibold text-gray-500 dark:text-gray-400 capitalize"
        >
          {currentPageName}
        </span>

        <div class="flex-1"></div>

        <!-- Theme toggle -->
        <button
          onclick={toggleTheme}
          aria-label="Toggle theme"
          class="w-9 h-9 flex items-center justify-center rounded-lg text-gray-500
            hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors"
        >
          {#if ui.theme === "dark"}
            <svg
              width="18"
              height="18"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              stroke-width="2"
            >
              <circle cx="12" cy="12" r="5" />
              <line x1="12" y1="1" x2="12" y2="3" /><line
                x1="12"
                y1="21"
                x2="12"
                y2="23"
              />
              <line x1="4.22" y1="4.22" x2="5.64" y2="5.64" />
              <line x1="18.36" y1="18.36" x2="19.78" y2="19.78" />
              <line x1="1" y1="12" x2="3" y2="12" /><line
                x1="21"
                y1="12"
                x2="23"
                y2="12"
              />
              <line x1="4.22" y1="19.78" x2="5.64" y2="18.36" />
              <line x1="18.36" y1="5.64" x2="19.78" y2="4.22" />
            </svg>
          {:else}
            <svg
              width="18"
              height="18"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              stroke-width="2"
            >
              <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z" />
            </svg>
          {/if}
        </button>

        <!-- Notifications -->
        <button
          aria-label="Notifications"
          class="relative w-9 h-9 flex items-center justify-center rounded-lg text-gray-500
            hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors"
        >
          <svg
            width="18"
            height="18"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            stroke-width="2"
          >
            <path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9" />
            <path d="M13.73 21a2 2 0 0 1-3.46 0" />
          </svg>
          <span class="absolute top-2 right-2 w-2 h-2 bg-blue-500 rounded-full"
          ></span>
        </button>

        <!-- Avatar -->
        {#if auth.user}
          <button
            onclick={() => goto("/settings")}
            aria-label="Profile settings"
          >
            <img
              src={auth.user.avatar_url}
              alt={auth.user.short_name}
              class="w-8 h-8 rounded-full ring-2 ring-transparent hover:ring-blue-300 transition-all"
            />
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

    <!-- ═══════════════════════════════════════════════════════
         MOBILE SIDEBAR OVERLAY
    ═══════════════════════════════════════════════════════ -->
    {#if ui.sidebarOpen}
      <div class="fixed inset-0 z-40 md:hidden flex">
        <!-- Backdrop -->
        <div
          class="absolute inset-0 bg-black/50 backdrop-blur-sm"
          role="button"
          tabindex="-1"
          aria-label="Close menu"
          onclick={ui.toggleSidebar}
          onkeydown={(e) => e.key === "Escape" && ui.toggleSidebar()}
        ></div>

        <!-- Drawer -->
        <div
          class="relative w-64 bg-white dark:bg-gray-900 shadow-2xl flex flex-col"
        >
          <!-- Header -->
          <div
            class="flex items-center justify-between px-5 h-16
              border-b border-gray-200 dark:border-gray-800"
          >
            <div class="flex items-center gap-2.5">
              <div
                class="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center"
              >
                <svg
                  width="16"
                  height="16"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="white"
                  stroke-width="2.5"
                >
                  <path d="M12 2L2 7l10 5 10-5-10-5z" />
                  <path d="M2 17l10 5 10-5" />
                  <path d="M2 12l10 5 10-5" />
                </svg>
              </div>
              <span class="font-bold text-gray-900 dark:text-white"
                >ProposalAI</span
              >
            </div>
            <button
              onclick={ui.toggleSidebar}
              aria-label="Close menu"
              class="text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
            >
              <svg
                width="20"
                height="20"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                stroke-width="2"
              >
                <line x1="18" y1="6" x2="6" y2="18" />
                <line x1="6" y1="6" x2="18" y2="18" />
              </svg>
            </button>
          </div>

          <!-- Mobile nav links -->
          <nav class="flex-1 py-3 px-3 space-y-0.5 overflow-y-auto">
            <a
              href="/dashboard"
              onclick={ui.toggleSidebar}
              class="flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium
                text-gray-600 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors"
            >
              <svg
                width="18"
                height="18"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                stroke-width="2"
              >
                <rect x="3" y="3" width="7" height="7" /><rect
                  x="14"
                  y="3"
                  width="7"
                  height="7"
                />
                <rect x="14" y="14" width="7" height="7" /><rect
                  x="3"
                  y="14"
                  width="7"
                  height="7"
                />
              </svg>
              <span>Dashboard</span>
            </a>
            <a
              href="/proposals"
              onclick={ui.toggleSidebar}
              class="flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium
                text-gray-600 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors"
            >
              <svg
                width="18"
                height="18"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                stroke-width="2"
              >
                <path
                  d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"
                />
                <polyline points="14,2 14,8 20,8" />
              </svg>
              <span>Proposals</span>
            </a>
            <a
              href="/leads"
              onclick={ui.toggleSidebar}
              class="flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium
                text-gray-600 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors"
            >
              <svg
                width="18"
                height="18"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                stroke-width="2"
              >
                <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2" />
                <circle cx="9" cy="7" r="4" />
              </svg>
              <span>Leads CRM</span>
            </a>
            <a
              href="/templates"
              onclick={ui.toggleSidebar}
              class="flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium
                text-gray-600 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors"
            >
              <svg
                width="18"
                height="18"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                stroke-width="2"
              >
                <rect x="2" y="2" width="9" height="9" /><rect
                  x="13"
                  y="2"
                  width="9"
                  height="9"
                />
                <rect x="13" y="13" width="9" height="9" /><rect
                  x="2"
                  y="13"
                  width="9"
                  height="9"
                />
              </svg>
              <span>Templates</span>
            </a>
            <a
              href="/analytics"
              onclick={ui.toggleSidebar}
              class="flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium
                text-gray-600 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors"
            >
              <svg
                width="18"
                height="18"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                stroke-width="2"
              >
                <line x1="18" y1="20" x2="18" y2="10" />
                <line x1="12" y1="20" x2="12" y2="4" />
                <line x1="6" y1="20" x2="6" y2="14" />
              </svg>
              <span>Analytics</span>
            </a>
            <a
              href="/settings"
              onclick={ui.toggleSidebar}
              class="flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium
                text-gray-600 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors"
            >
              <svg
                width="18"
                height="18"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                stroke-width="2"
              >
                <circle cx="12" cy="12" r="3" />
                <path
                  d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1-2.83 2.83l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-4 0v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83-2.83l.06-.06A1.65 1.65 0 0 0 4.68 15a1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1 0-4h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 2.83-2.83l.06.06A1.65 1.65 0 0 0 9 4.68a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 4 0v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 2.83l-.06.06A1.65 1.65 0 0 0 19.4 9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 0 4h-.09a1.65 1.65 0 0 0-1.51 1z"
                />
              </svg>
              <span>Settings</span>
            </a>
          </nav>

          <!-- Mobile user footer -->
          {#if auth.user}
            <div class="p-4 border-t border-gray-200 dark:border-gray-800">
              <div class="flex items-center gap-2.5 mb-3">
                <img
                  src={auth.user.avatar_url}
                  alt=""
                  class="w-7 h-7 rounded-full"
                />
                <div class="flex-1 min-w-0">
                  <p
                    class="text-xs font-semibold text-gray-900 dark:text-white truncate"
                  >
                    {auth.user.full_name}
                  </p>
                  <p class="text-xs text-gray-400">{auth.user.email}</p>
                </div>
              </div>
              <button
                onclick={() => auth.logout().then(() => goto("/login"))}
                class="w-full py-2 text-sm text-red-600 hover:bg-red-50 dark:hover:bg-red-900/20
                  rounded-lg flex items-center justify-center gap-2 transition-colors"
              >
                <svg
                  width="14"
                  height="14"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  stroke-width="2"
                >
                  <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4" />
                  <polyline points="16,17 21,12 16,7" />
                  <line x1="21" y1="12" x2="9" y2="12" />
                </svg>
                Sign out
              </button>
            </div>
          {/if}
        </div>
      </div>
    {/if}
  </div>
{/if}
