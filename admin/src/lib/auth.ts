import { create } from "zustand";
import { authApi } from "./api";

interface User {
  id: string;
  phone: string | null;
  email: string | null;
  nickname: string;
  role: string;
}

interface AuthState {
  user: User | null;
  isLoading: boolean;
  login: (credentials: { email?: string; phone?: string; password: string }) => Promise<void>;
  logout: () => void;
  loadUser: () => Promise<void>;
}

export const useAuth = create<AuthState>((set) => ({
  user: null,
  isLoading: true,

  login: async (credentials) => {
    const res = await authApi.login(credentials);
    localStorage.setItem("admin_token", res.access_token);
    const user = await authApi.me();
    if (user.role !== "admin") {
      localStorage.removeItem("admin_token");
      throw new Error("需要管理员权限");
    }
    set({ user });
  },

  logout: () => {
    localStorage.removeItem("admin_token");
    set({ user: null });
  },

  loadUser: async () => {
    try {
      const token = localStorage.getItem("admin_token");
      if (!token) {
        set({ isLoading: false });
        return;
      }
      const user = await authApi.me();
      if (user.role !== "admin") {
        localStorage.removeItem("admin_token");
        set({ user: null, isLoading: false });
        return;
      }
      set({ user, isLoading: false });
    } catch {
      localStorage.removeItem("admin_token");
      set({ user: null, isLoading: false });
    }
  },
}));
