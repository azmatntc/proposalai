type ToastType = 'success' | 'error' | 'warning' | 'info';

interface Toast {
  id: string;
  message: string;
  type: ToastType;
}

function createUIState() {
  let sidebarOpen = $state(false);
  let sidebarCollapsed = $state(false);
  let theme = $state<'light' | 'dark' | 'system'>('system');
  let toasts = $state<Toast[]>([]);
  let activeModal = $state<string | null>(null);
  let modalData = $state<Record<string, unknown>>({});

  function addToast(message: string, type: ToastType = 'info', duration = 4000) {
    const id = crypto.randomUUID();
    toasts = [...toasts, { id, message, type }];
    setTimeout(() => {
      toasts = toasts.filter((t) => t.id !== id);
    }, duration);
  }

  function removeToast(id: string) {
    toasts = toasts.filter((t) => t.id !== id);
  }

  function openModal(id: string, data: Record<string, unknown> = {}) {
    activeModal = id;
    modalData = data;
  }

  function closeModal() {
    activeModal = null;
    modalData = {};
  }

  function toggleSidebar() {
    sidebarOpen = !sidebarOpen;
  }

  function toggleCollapse() {
    sidebarCollapsed = !sidebarCollapsed;
  }

  return {
    get sidebarOpen() { return sidebarOpen; },
    get sidebarCollapsed() { return sidebarCollapsed; },
    get theme() { return theme; },
    set theme(v: 'light' | 'dark' | 'system') { theme = v; },
    get toasts() { return toasts; },
    get activeModal() { return activeModal; },
    get modalData() { return modalData; },
    addToast,
    removeToast,
    openModal,
    closeModal,
    toggleSidebar,
    toggleCollapse,
    success: (msg: string) => addToast(msg, 'success'),
    error: (msg: string) => addToast(msg, 'error'),
    warning: (msg: string) => addToast(msg, 'warning'),
    info: (msg: string) => addToast(msg, 'info'),
  };
}

export const ui = createUIState();