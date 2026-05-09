<script lang="ts">
    import { onMount } from "svelte";
    import { api } from "$lib/api/client";
    import { ui } from "$lib/stores/ui.svelte";
    import type { Template, PaginatedResponse } from "$lib/api/types";

    let templates = $state<Template[]>([]);
    let loading = $state(true);
    let search = $state("");
    let categoryFilter = $state("");
    let selected = $state<Template | null>(null);
    let showModal = $state(false);

    const categories = [
        { value: "web_dev", label: "Web Development" },
        { value: "mobile_app", label: "Mobile App" },
        { value: "design", label: "Design" },
        { value: "marketing", label: "Marketing" },
        { value: "writing", label: "Writing" },
        { value: "consulting", label: "Consulting" },
        { value: "other", label: "Other" },
    ];

    const tones = [
        "professional",
        "friendly",
        "casual",
        "technical",
        "persuasive",
        "formal",
    ];

    const catColors: Record<string, string> = {
        web_dev: "bg-blue-100 text-blue-700",
        mobile_app: "bg-violet-100 text-violet-700",
        design: "bg-pink-100 text-pink-700",
        marketing: "bg-orange-100 text-orange-700",
        writing: "bg-amber-100 text-amber-700",
        consulting: "bg-teal-100 text-teal-700",
        other: "bg-gray-100 text-gray-600",
    };

    let newForm = $state({
        name: "",
        description: "",
        category: "web_dev",
        tone: "professional",
        structure: {
            sections: [
                {
                    order: 1,
                    name: "greeting",
                    prompt: "Warm personalized greeting",
                    required: true,
                },
                {
                    order: 2,
                    name: "understanding",
                    prompt: "Show deep understanding of their needs",
                    required: true,
                },
                {
                    order: 3,
                    name: "approach",
                    prompt: "Describe your approach and methodology",
                    required: true,
                },
                {
                    order: 4,
                    name: "cta",
                    prompt: "Strong call to action with next steps",
                    required: true,
                },
            ],
        },
        default_variables: { hourly_rate: 75, availability: "2 weeks" },
    });

    async function load() {
        loading = true;
        try {
            const params = new URLSearchParams();
            if (search) params.set("search", search);
            if (categoryFilter) params.set("category", categoryFilter);
            const data = await api.get<PaginatedResponse<Template>>(
                `/templates/?${params}`,
            );
            templates = data.results;
        } catch (e: any) {
            ui.error(e.message || "Failed to load templates");
        } finally {
            loading = false;
        }
    }

    async function clone(id: string) {
        try {
            const t = await api.post<Template>(`/templates/${id}/clone/`, {});
            templates = [t, ...templates];
            ui.success("Template cloned!");
        } catch (e: any) {
            ui.error(e.message || "Failed to clone");
        }
    }

    async function deleteTemplate(id: string) {
        if (!confirm("Delete this template?")) return;
        await api.delete(`/templates/${id}/`);
        templates = templates.filter((t) => t.id !== id);
        if (selected?.id === id) selected = null;
        ui.success("Template deleted");
    }

    async function create() {
        if (!newForm.name) {
            ui.error("Template name is required.");
            return;
        }
        try {
            const t = await api.post<Template>("/templates/", newForm);
            templates = [t, ...templates];
            showModal = false;
            ui.success("Template created!");
        } catch (e: any) {
            ui.error(e.message || "Failed to create template");
        }
    }

    function addSection() {
        const next = newForm.structure.sections.length + 1;
        newForm.structure.sections = [
            ...newForm.structure.sections,
            { order: next, name: "", prompt: "", required: false },
        ];
    }

    function removeSection(i: number) {
        newForm.structure.sections = newForm.structure.sections.filter(
            (_, idx) => idx !== i,
        );
    }

    function catLabel(value: string) {
        return categories.find((c) => c.value === value)?.label ?? value;
    }

    onMount(load);

    let debounce: ReturnType<typeof setTimeout>;
    $effect(() => {
        search;
        categoryFilter;
        clearTimeout(debounce);
        debounce = setTimeout(load, 350);
    });
</script>

<div class="flex h-full">
    <!-- Template grid -->
    <div
        class="flex-1 p-6 overflow-auto {selected
            ? 'hidden lg:block lg:max-w-[55%]'
            : ''}"
    >
        <div class="flex items-center justify-between mb-5">
            <div>
                <h1 class="text-2xl font-bold text-gray-900 dark:text-white">
                    Templates
                </h1>
                <p class="text-sm text-gray-500 mt-0.5">
                    {templates.length} templates
                </p>
            </div>
            <button
                onclick={() => (showModal = true)}
                class="flex items-center gap-2 px-4 py-2.5 bg-blue-600 hover:bg-blue-700
          text-white text-sm font-semibold rounded-lg transition-colors"
            >
                + New Template
            </button>
        </div>

        <!-- Filters -->
        <div class="flex flex-wrap gap-2 mb-5">
            <input
                bind:value={search}
                placeholder="Search templates…"
                class="flex-1 min-w-36 px-3 py-2 text-sm border border-gray-300 dark:border-gray-700
          rounded-lg bg-white dark:bg-gray-900 text-gray-900 dark:text-white
          focus:ring-2 focus:ring-blue-500 outline-none"
            />
            <select
                bind:value={categoryFilter}
                class="px-3 py-2 text-sm border border-gray-300 dark:border-gray-700 rounded-lg
          bg-white dark:bg-gray-900 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500 outline-none"
            >
                <option value="">All Categories</option>
                {#each categories as cat}
                    <option value={cat.value}>{cat.label}</option>
                {/each}
            </select>
        </div>

        {#if loading}
            <div class="grid grid-cols-1 md:grid-cols-2 gap-3">
                {#each [0, 1, 2, 3, 4, 5] as _}
                    <div
                        class="h-36 bg-white dark:bg-gray-900 rounded-xl border border-gray-200 dark:border-gray-800 animate-pulse"
                    ></div>
                {/each}
            </div>
        {:else if templates.length === 0}
            <div
                class="text-center py-16 bg-white dark:bg-gray-900 rounded-xl border border-gray-200 dark:border-gray-800"
            >
                <p
                    class="text-sm font-semibold text-gray-900 dark:text-white mb-1"
                >
                    No templates found
                </p>
                <p class="text-sm text-gray-500 mb-4">
                    Create a custom template to get started
                </p>
                <button
                    onclick={() => (showModal = true)}
                    class="px-4 py-2 bg-blue-600 text-white text-sm font-semibold rounded-lg hover:bg-blue-700"
                >
                    Create Template
                </button>
            </div>
        {:else}
            <div class="grid grid-cols-1 md:grid-cols-2 gap-3">
                {#each templates as t (t.id)}
                    <!--
            IMPORTANT: This outer element is a DIV with role="button".
            Never use <button> here because clone/delete buttons are inside it.
            Nested <button> inside <button> is invalid HTML and breaks Svelte SSR.
          -->
                    <div
                        role="button"
                        tabindex="0"
                        onclick={() => (selected = t)}
                        onkeydown={(e) => e.key === "Enter" && (selected = t)}
                        class="bg-white dark:bg-gray-900 rounded-xl border p-5 cursor-pointer
              transition-all hover:border-gray-300 dark:hover:border-gray-700
              {selected?.id === t.id
                            ? 'border-blue-500 ring-2 ring-blue-100 dark:ring-blue-900/30'
                            : 'border-gray-200 dark:border-gray-800'}"
                    >
                        <!-- Badges row -->
                        <div
                            class="flex items-center justify-between gap-2 mb-2 flex-wrap"
                        >
                            <div class="flex items-center gap-1.5 flex-wrap">
                                {#if t.is_system_template}
                                    <span
                                        class="px-1.5 py-0.5 rounded text-xs font-medium bg-blue-600 text-white"
                                    >
                                        System
                                    </span>
                                {/if}
                                <span
                                    class="px-2 py-0.5 rounded-full text-xs font-medium
                  {catColors[t.category] || 'bg-gray-100 text-gray-600'}"
                                >
                                    {catLabel(t.category)}
                                </span>
                            </div>
                            <span class="text-xs text-gray-400">
                                ⭐ {parseFloat(t.average_rating || "0").toFixed(
                                    1,
                                )}
                            </span>
                        </div>

                        <p
                            class="text-sm font-semibold text-gray-900 dark:text-white mb-1 truncate"
                        >
                            {t.name}
                        </p>
                        {#if t.description}
                            <p class="text-xs text-gray-500 line-clamp-2 mb-3">
                                {t.description}
                            </p>
                        {/if}

                        <!-- Footer: stats + action buttons -->
                        <div class="flex items-center justify-between mt-3">
                            <div
                                class="flex items-center gap-3 text-xs text-gray-400"
                            >
                                <span>{t.section_count} sections</span>
                                <span>{t.usage_count} uses</span>
                                <span class="capitalize">{t.tone}</span>
                            </div>

                            <!--
                stopPropagation prevents the card's onclick from firing
                when clicking the action buttons.
                These <button> elements are safe here because the parent is a <div>.
              -->
                            <div
                                class="flex items-center gap-1"
                                role="presentation"
                                onclick={(e) => e.stopPropagation()}
                            >
                                <button
                                    type="button"
                                    onclick={() => clone(t.id)}
                                    title="Clone"
                                    class="p-1.5 text-gray-400 hover:text-blue-600 transition-colors"
                                >
                                    <svg
                                        width="13"
                                        height="13"
                                        viewBox="0 0 24 24"
                                        fill="none"
                                        stroke="currentColor"
                                        stroke-width="2"
                                    >
                                        <rect
                                            x="9"
                                            y="9"
                                            width="13"
                                            height="13"
                                            rx="2"
                                            ry="2"
                                        />
                                        <path
                                            d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"
                                        />
                                    </svg>
                                </button>
                                {#if !t.is_system_template}
                                    <button
                                        type="button"
                                        onclick={() => deleteTemplate(t.id)}
                                        title="Delete"
                                        class="p-1.5 text-gray-400 hover:text-red-500 transition-colors"
                                    >
                                        <svg
                                            width="13"
                                            height="13"
                                            viewBox="0 0 24 24"
                                            fill="none"
                                            stroke="currentColor"
                                            stroke-width="2"
                                        >
                                            <polyline points="3,6 5,6 21,6" />
                                            <path
                                                d="M19,6l-1,14a2,2,0,0,1-2,2H8a2,2,0,0,1-2-2L5,6"
                                            />
                                        </svg>
                                    </button>
                                {/if}
                            </div>
                        </div>
                    </div>
                {/each}
            </div>
        {/if}
    </div>

    <!-- Template detail panel -->
    {#if selected}
        <div
            class="w-full lg:w-[45%] lg:border-l border-gray-200 dark:border-gray-800
      bg-white dark:bg-gray-900 flex flex-col overflow-hidden flex-shrink-0"
        >
            <div
                class="flex items-center justify-between px-5 py-4
        border-b border-gray-200 dark:border-gray-800 flex-shrink-0"
            >
                <h2
                    class="text-sm font-semibold text-gray-900 dark:text-white truncate mr-4"
                >
                    {selected.name}
                </h2>
                <button
                    type="button"
                    onclick={() => (selected = null)}
                    class="text-gray-400 hover:text-gray-600 flex-shrink-0"
                >
                    ✕
                </button>
            </div>

            <div class="flex-1 overflow-auto p-5 space-y-4">
                <div class="flex flex-wrap gap-2">
                    <span
                        class="px-2.5 py-1 rounded-full text-xs font-medium
            {catColors[selected.category] || 'bg-gray-100 text-gray-600'}"
                    >
                        {catLabel(selected.category)}
                    </span>
                    <span
                        class="px-2.5 py-1 rounded-full text-xs font-medium
            bg-gray-100 dark:bg-gray-800 text-gray-600 dark:text-gray-400 capitalize"
                    >
                        {selected.tone} tone
                    </span>
                    {#if selected.is_system_template}
                        <span
                            class="px-2.5 py-1 rounded-full text-xs font-medium bg-blue-600 text-white"
                        >
                            System
                        </span>
                    {/if}
                </div>

                {#if selected.description}
                    <p class="text-sm text-gray-600 dark:text-gray-400">
                        {selected.description}
                    </p>
                {/if}

                <div class="grid grid-cols-3 gap-2">
                    <div
                        class="bg-gray-50 dark:bg-gray-800 rounded-lg p-3 text-center"
                    >
                        <p
                            class="text-xl font-bold text-gray-900 dark:text-white"
                        >
                            {selected.section_count}
                        </p>
                        <p class="text-xs text-gray-500">Sections</p>
                    </div>
                    <div
                        class="bg-gray-50 dark:bg-gray-800 rounded-lg p-3 text-center"
                    >
                        <p
                            class="text-xl font-bold text-gray-900 dark:text-white"
                        >
                            {selected.usage_count}
                        </p>
                        <p class="text-xs text-gray-500">Uses</p>
                    </div>
                    <div
                        class="bg-gray-50 dark:bg-gray-800 rounded-lg p-3 text-center"
                    >
                        <p
                            class="text-xl font-bold text-gray-900 dark:text-white"
                        >
                            {parseFloat(selected.average_rating || "0").toFixed(
                                1,
                            )}
                        </p>
                        <p class="text-xs text-gray-500">Rating</p>
                    </div>
                </div>

                <div class="flex gap-2">
                    <button
                        type="button"
                        onclick={() => clone(selected!.id)}
                        class="flex-1 py-2.5 bg-blue-600 hover:bg-blue-700 text-white
              text-sm font-semibold rounded-lg transition-colors"
                    >
                        Clone & Edit
                    </button>
                    <a
                        href="/proposals"
                        class="flex-1 py-2.5 text-center bg-gray-100 dark:bg-gray-800
              hover:bg-gray-200 dark:hover:bg-gray-700 text-gray-700 dark:text-gray-300
              text-sm font-semibold rounded-lg transition-colors"
                    >
                        Use in Proposal
                    </a>
                </div>

                <p class="text-xs text-gray-400">
                    Created {new Date(selected.created_at).toLocaleDateString()}
                </p>
            </div>
        </div>
    {/if}
</div>

<!-- New Template Modal -->
{#if showModal}
    <div class="fixed inset-0 z-50 flex items-center justify-center p-4">
        <div
            class="absolute inset-0 bg-black/50"
            role="button"
            tabindex="-1"
            aria-label="Close"
            onclick={() => (showModal = false)}
            onkeydown={(e) => e.key === "Escape" && (showModal = false)}
        ></div>

        <div
            class="relative bg-white dark:bg-gray-900 rounded-2xl shadow-2xl
      w-full max-w-2xl max-h-[90vh] overflow-y-auto"
        >
            <div
                class="sticky top-0 bg-white dark:bg-gray-900 px-6 py-4
        border-b border-gray-200 dark:border-gray-800 flex items-center justify-between z-10"
            >
                <h2 class="text-lg font-semibold text-gray-900 dark:text-white">
                    Create Template
                </h2>
                <button
                    type="button"
                    onclick={() => (showModal = false)}
                    class="text-gray-400 hover:text-gray-600 text-xl leading-none"
                >
                    ✕
                </button>
            </div>

            <div class="p-6 space-y-4">
                <div>
                    <label
                        class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1.5"
                    >
                        Template Name *
                    </label>
                    <input
                        bind:value={newForm.name}
                        placeholder="e.g. SaaS Development Proposal"
                        class="w-full px-3.5 py-2.5 rounded-lg border border-gray-300 dark:border-gray-700
              bg-white dark:bg-gray-800 text-gray-900 dark:text-white text-sm
              focus:ring-2 focus:ring-blue-500 outline-none"
                    />
                </div>

                <div>
                    <label
                        class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1.5"
                    >
                        Description
                    </label>
                    <textarea
                        bind:value={newForm.description}
                        rows={2}
                        placeholder="When to use this template…"
                        class="w-full px-3.5 py-2.5 rounded-lg border border-gray-300 dark:border-gray-700
              bg-white dark:bg-gray-800 text-gray-900 dark:text-white text-sm
              focus:ring-2 focus:ring-blue-500 outline-none resize-none"
                    ></textarea>
                </div>

                <div class="grid grid-cols-2 gap-3">
                    <div>
                        <label
                            class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1.5"
                        >
                            Category
                        </label>
                        <select
                            bind:value={newForm.category}
                            class="w-full px-3.5 py-2.5 rounded-lg border border-gray-300 dark:border-gray-700
                bg-white dark:bg-gray-800 text-gray-900 dark:text-white text-sm
                focus:ring-2 focus:ring-blue-500 outline-none"
                        >
                            {#each categories as cat}
                                <option value={cat.value}>{cat.label}</option>
                            {/each}
                        </select>
                    </div>
                    <div>
                        <label
                            class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1.5"
                        >
                            Default Tone
                        </label>
                        <select
                            bind:value={newForm.tone}
                            class="w-full px-3.5 py-2.5 rounded-lg border border-gray-300 dark:border-gray-700
                bg-white dark:bg-gray-800 text-gray-900 dark:text-white text-sm
                focus:ring-2 focus:ring-blue-500 outline-none"
                        >
                            {#each tones as t}
                                <option value={t}
                                    >{t.charAt(0).toUpperCase() +
                                        t.slice(1)}</option
                                >
                            {/each}
                        </select>
                    </div>
                </div>

                <!-- Section builder -->
                <div>
                    <div class="flex items-center justify-between mb-2">
                        <label
                            class="text-sm font-medium text-gray-700 dark:text-gray-300"
                            >Sections</label
                        >
                        <button
                            type="button"
                            onclick={addSection}
                            class="text-xs text-blue-600 hover:text-blue-700 font-medium"
                        >
                            + Add Section
                        </button>
                    </div>
                    <div class="space-y-2">
                        {#each newForm.structure.sections as section, i}
                            <div
                                class="bg-gray-50 dark:bg-gray-800 rounded-lg p-3 space-y-2"
                            >
                                <div class="flex items-center gap-2">
                                    <span
                                        class="w-5 h-5 bg-blue-600 text-white rounded text-xs font-bold
                    flex items-center justify-center flex-shrink-0"
                                    >
                                        {i + 1}
                                    </span>
                                    <input
                                        bind:value={section.name}
                                        placeholder="Section name (e.g. greeting)"
                                        class="flex-1 px-2.5 py-1.5 rounded border border-gray-300 dark:border-gray-700
                      bg-white dark:bg-gray-900 text-gray-900 dark:text-white text-xs
                      focus:ring-1 focus:ring-blue-500 outline-none"
                                    />
                                    <label
                                        class="flex items-center gap-1 text-xs text-gray-500 cursor-pointer flex-shrink-0"
                                    >
                                        <input
                                            type="checkbox"
                                            bind:checked={section.required}
                                            class="rounded"
                                        />
                                        Req.
                                    </label>
                                    <button
                                        type="button"
                                        onclick={() => removeSection(i)}
                                        class="text-gray-400 hover:text-red-500 transition-colors flex-shrink-0"
                                    >
                                        ✕
                                    </button>
                                </div>
                                <input
                                    bind:value={section.prompt}
                                    placeholder="AI prompt for this section…"
                                    class="w-full px-2.5 py-1.5 rounded border border-gray-300 dark:border-gray-700
                    bg-white dark:bg-gray-900 text-gray-900 dark:text-white text-xs
                    focus:ring-1 focus:ring-blue-500 outline-none"
                                />
                            </div>
                        {/each}
                    </div>
                </div>

                <div class="flex gap-2 pt-2">
                    <button
                        type="button"
                        onclick={create}
                        class="flex-1 py-2.5 bg-blue-600 hover:bg-blue-700 text-white
              text-sm font-semibold rounded-lg transition-colors"
                    >
                        Create Template
                    </button>
                    <button
                        type="button"
                        onclick={() => (showModal = false)}
                        class="px-4 py-2.5 text-sm text-gray-600 dark:text-gray-400
              hover:bg-gray-100 dark:hover:bg-gray-800 rounded-lg transition-colors"
                    >
                        Cancel
                    </button>
                </div>
            </div>
        </div>
    </div>
{/if}
