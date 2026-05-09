import { api, APIError } from '$lib/api/client';
import type { User } from '$lib/api/types';

function createAuthState() {
  let user = $state<User | null>(null);
  let isLoading = $state(true);

  const isAuthenticated = $derived(!!user);
  const isPro = $derived(
    user?.subscription_tier === 'pro' || user?.subscription_tier === 'enterprise'
  );

  async function init() {
    if (typeof localStorage === 'undefined') {
      isLoading = false;
      return;
    }
    const token = localStorage.getItem('access_token');
    if (!token) {
      isLoading = false;
      return;
    }
    try {
      user = await api.get<User>('/auth/me/');
    } catch {
      api.clearTokens();
    } finally {
      isLoading = false;
    }
  }

  async function login(email: string, password: string) {
    const data = await api.post<{ access: string; refresh: string; user: User }>(
      '/auth/login/',
      { email, password }
    );
    localStorage.setItem('access_token', data.access);
    localStorage.setItem('refresh_token', data.refresh);
    user = data.user;
  }

  async function register(payload: {
    email: string;
    username: string;
    password: string;
    password_confirm: string;
    first_name?: string;
    last_name?: string;
    company_name?: string;
  }) {
    const data = await api.post<{ access: string; refresh: string; user: User }>(
      '/auth/register/',
      payload
    );
    localStorage.setItem('access_token', data.access);
    localStorage.setItem('refresh_token', data.refresh);
    user = data.user;
  }

  async function logout() {
    const refresh = typeof localStorage !== 'undefined'
      ? localStorage.getItem('refresh_token')
      : null;
    try {
      if (refresh) await api.post('/auth/logout/', { refresh });
    } catch { /* ignore */ }
    api.clearTokens();
    user = null;
  }

  async function refreshUser() {
    try {
      user = await api.get<User>('/auth/me/');
    } catch { /* ignore */ }
  }

  return {
    get user() { return user; },
    get isLoading() { return isLoading; },
    get isAuthenticated() { return isAuthenticated; },
    get isPro() { return isPro; },
    init,
    login,
    register,
    logout,
    refreshUser,
  };
}

export const auth = createAuthState();