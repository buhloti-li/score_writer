import axios from "axios";

const client = axios.create({
  baseURL: "/api/v1",
});

client.interceptors.request.use((config) => {
  const token = localStorage.getItem("admin_token");
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

client.interceptors.response.use(
  (res) => res,
  (err) => {
    if (err.response?.status === 401) {
      localStorage.removeItem("admin_token");
      window.location.href = "/login";
    }
    return Promise.reject(err);
  }
);

export default client;

// Auth
export const authApi = {
  login: (data: { email?: string; phone?: string; password: string }) =>
    client.post("/auth/login", data).then((r) => r.data),
  me: () => client.get("/auth/me").then((r) => r.data),
};

// Dashboard
export const dashboardApi = {
  get: () => client.get("/admin/dashboard").then((r) => r.data),
};

// Tasks
export const taskApi = {
  list: (params?: Record<string, any>) =>
    client.get("/tasks", { params }).then((r) => r.data),
  get: (id: string) => client.get(`/tasks/${id}`).then((r) => r.data),
  create: (data: any) => client.post("/tasks", data).then((r) => r.data),
  update: (id: string, data: any) =>
    client.put(`/tasks/${id}`, data).then((r) => r.data),
  approve: (id: string, data?: any) =>
    client.post(`/tasks/${id}/approve`, data || {}).then((r) => r.data),
  discard: (id: string) =>
    client.post(`/tasks/${id}/discard`).then((r) => r.data),
  assign: (id: string, adminId: string) =>
    client.post(`/tasks/${id}/assign`, null, { params: { admin_id: adminId } }).then((r) => r.data),
};

// Scores
export const scoreApi = {
  list: (params?: Record<string, any>) =>
    client.get("/scores", { params }).then((r) => r.data),
  get: (id: string) => client.get(`/scores/${id}`).then((r) => r.data),
  create: (data: any) => client.post("/scores", data).then((r) => r.data),
  update: (id: string, data: any) =>
    client.put(`/scores/${id}`, data).then((r) => r.data),
  delete: (id: string) => client.delete(`/scores/${id}`),
};

// Orders
export const orderApi = {
  list: (params?: Record<string, any>) =>
    client.get("/admin/orders", { params }).then((r) => r.data),
  get: (id: string) => client.get(`/orders/${id}`).then((r) => r.data),
  deliver: (id: string) =>
    client.post(`/orders/${id}/deliver`).then((r) => r.data),
  refund: (id: string) =>
    client.post(`/orders/${id}/refund`).then((r) => r.data),
};
