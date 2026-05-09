const API_BASE = '/api/v1';

export class APIError extends Error {
  constructor(
    public status: number,
    message: string,
    public data?: unknown
  ) {
    super(message);
    this.name = 'APIError';
  }
}

class APIClient {
  private getToken(): string | null {
    if (typeof localStorage === 'undefined') return null;
    return localStorage.getItem('access_token');
  }

  private async refreshToken(): Promise<boolean> {
    if (typeof localStorage === 'undefined') return false;
    const refresh = localStorage.getItem('refresh_token');
    if (!refresh) return false;
    try {
      const res = await fetch(`${API_BASE}/auth/refresh/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ refresh }),
      });
      if (!res.ok) return false;
      const data = await res.json();
      localStorage.setItem('access_token', data.access);
      return true;
    } catch {
      return false;
    }
  }

  clearTokens() {
    if (typeof localStorage === 'undefined') return;
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
  }

  private async request<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
    const token = this.getToken();
    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
      ...(options.headers as Record<string, string> || {}),
    };
    if (token) headers['Authorization'] = `Bearer ${token}`;

    const res = await fetch(`${API_BASE}${endpoint}`, { ...options, headers });

    if (res.status === 401 && token) {
      const refreshed = await this.refreshToken();
      if (refreshed) {
        headers['Authorization'] = `Bearer ${this.getToken()}`;
        const retry = await fetch(`${API_BASE}${endpoint}`, { ...options, headers });
        return this.handleResponse<T>(retry);
      }
      this.clearTokens();
      if (typeof window !== 'undefined') window.location.href = '/login';
      throw new APIError(401, 'Session expired');
    }

    return this.handleResponse<T>(res);
  }

  private async handleResponse<T>(res: Response): Promise<T> {
    if (res.status === 204) return undefined as T;
    const data = await res.json().catch(() => ({}));
    if (!res.ok) {
      const msg = (data as any)?.error || (data as any)?.detail || 'Request failed';
      throw new APIError(res.status, msg, data);
    }
    return data as T;
  }

  get<T>(endpoint: string) { return this.request<T>(endpoint); }
  post<T>(endpoint: string, body?: unknown) {
    return this.request<T>(endpoint, {
      method: 'POST',
      body: body !== undefined ? JSON.stringify(body) : undefined,
    });
  }
  patch<T>(endpoint: string, body: unknown) {
    return this.request<T>(endpoint, { method: 'PATCH', body: JSON.stringify(body) });
  }
  delete<T>(endpoint: string) {
    return this.request<T>(endpoint, { method: 'DELETE' });
  }
}

export const api = new APIClient();