const API_BASE = process.env.NEXT_PUBLIC_API_URL || "";

interface RequestOptions extends RequestInit {
  params?: Record<string, string | number | undefined>;
}

class ApiClient {
  private baseUrl: string;

  constructor(baseUrl: string) {
    this.baseUrl = baseUrl;
  }

  private getToken(): string | null {
    if (typeof window === "undefined") return null;
    return localStorage.getItem("access_token");
  }

  private buildUrl(path: string, params?: Record<string, string | number | undefined>): string {
    const url = new URL(`${this.baseUrl}${path}`, window.location.origin);
    if (params) {
      Object.entries(params).forEach(([key, value]) => {
        if (value !== undefined) url.searchParams.set(key, String(value));
      });
    }
    return url.toString();
  }

  async request<T>(path: string, options: RequestOptions = {}): Promise<T> {
    const { params, ...init } = options;
    const url = this.buildUrl(path, params);

    const headers: Record<string, string> = {
      "Content-Type": "application/json",
      ...(init.headers as Record<string, string>),
    };

    const token = this.getToken();
    if (token) {
      headers["Authorization"] = `Bearer ${token}`;
    }

    const response = await fetch(url, { ...init, headers });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: "Request failed" }));
      throw new ApiError(response.status, error.detail || "Request failed");
    }

    if (response.status === 204) return undefined as T;
    return response.json();
  }

  get<T>(path: string, params?: Record<string, string | number | undefined>) {
    return this.request<T>(path, { method: "GET", params });
  }

  post<T>(path: string, body?: unknown) {
    return this.request<T>(path, { method: "POST", body: JSON.stringify(body) });
  }

  put<T>(path: string, body?: unknown) {
    return this.request<T>(path, { method: "PUT", body: JSON.stringify(body) });
  }

  delete<T>(path: string) {
    return this.request<T>(path, { method: "DELETE" });
  }
}

export class ApiError extends Error {
  status: number;
  constructor(status: number, message: string) {
    super(message);
    this.status = status;
  }
}

export const api = new ApiClient(API_BASE);

// Auth
export const authApi = {
  login: (data: { phone?: string; email?: string; password: string }) =>
    api.post<{ access_token: string; refresh_token: string }>("/api/v1/auth/login", data),
  register: (data: { phone?: string; email?: string; nickname: string; password: string }) =>
    api.post<UserResponse>("/api/v1/auth/register", data),
  me: () => api.get<UserResponse>("/api/v1/auth/me"),
};

// Scores
export const scoreApi = {
  list: (params?: { page?: number; page_size?: number; instrument?: string; composer?: string }) =>
    api.get<ScoreListResponse>("/api/v1/scores", params),
  get: (id: string) => api.get<ScoreResponse>(`/api/v1/scores/${id}`),
  search: (params: { q?: string; instrument?: string; genre?: string; page?: number; page_size?: number }) =>
    api.get<ScoreListResponse>("/api/v1/search", params),
};

// Orders
export const orderApi = {
  create: (data: { score_id?: string; task_id?: string; amount: number; source?: string }) =>
    api.post<OrderResponse>("/api/v1/orders", data),
  list: (params?: { page?: number; page_size?: number }) =>
    api.get<OrderListResponse>("/api/v1/orders", params),
  get: (id: string) => api.get<OrderResponse>(`/api/v1/orders/${id}`),
};

// Types
export interface UserResponse {
  id: string;
  phone: string | null;
  email: string | null;
  nickname: string;
  avatar_url: string | null;
  role: "customer" | "admin";
  created_at: string;
}

export interface ScoreResponse {
  id: string;
  title: string;
  title_en: string | null;
  composer: string | null;
  arranger: string | null;
  lyricist: string | null;
  instrument: string | null;
  key_signature: string | null;
  time_signature: string | null;
  difficulty: number | null;
  genre: string | null;
  tags: string[] | null;
  page_count: number | null;
  price: string;
  status: "available" | "producing" | "offline";
  preview_image_url: string | null;
  pdf_watermarked_url: string | null;
  copyright_status: string;
  download_count: number;
  description: string | null;
  created_at: string;
}

export interface ScoreListResponse {
  items: ScoreResponse[];
  total: number;
  page: number;
  page_size: number;
}

export interface OrderResponse {
  id: string;
  user_id: string | null;
  score_id: string | null;
  task_id: string | null;
  source: string;
  amount: string;
  payment_method: string | null;
  payment_status: "pending" | "paid" | "refunded";
  delivery_status: "pending" | "delivered";
  delivered_at: string | null;
  created_at: string;
}

export interface OrderListResponse {
  items: OrderResponse[];
  total: number;
  page: number;
  page_size: number;
}
