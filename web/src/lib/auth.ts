import { create } from "zustand";
import { authApi, type UserResponse } from "./api";

interface AuthState {
  user: UserResponse | null;
  isLoading: boolean;
  login: (phone: string, password: string) => Promise<void>;
  loginByEmail: (email: string, password: string) => Promise<void>;
  register: (data: { phone?: string; email?: string; nickname: string; password: string }) => Promise<void>;
  logout: () => void;
  loadUser: () => Promise<void>;
}

export const useAuth = create<AuthState>((set) => ({
  user: null,
  isLoading: true,

  login: async (phone, password) => {
    const res = await authApi.login({ phone, password });
    localStorage.setItem("access_token", res.access_token);
    localStorage.setItem("refresh_token", res.refresh_token);
    const user = await authApi.me();
    set({ user });
  },

  loginByEmail: async (email, password) => {
    const res = await authApi.login({ email, password });
    localStorage.setItem("access_token", res.access_token);
    localStorage.setItem("refresh_token", res.refresh_token);
    const user = await authApi.me();
    set({ user });
  },

  register: async (data) => {
    await authApi.register(data);
  },

  logout: () => {
    localStorage.removeItem("access_token");
    localStorage.removeItem("refresh_token");
    set({ user: null });
  },

  loadUser: async () => {
    try {
      const token = localStorage.getItem("access_token");
      if (!token) {
        set({ isLoading: false });
        return;
      }
      const user = await authApi.me();
      set({ user, isLoading: false });
    } catch {
      localStorage.removeItem("access_token");
      set({ user: null, isLoading: false });
    }
  },
}));
