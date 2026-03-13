"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { useAuth } from "@/lib/auth";

export default function LoginPage() {
  const router = useRouter();
  const { login, loginByEmail } = useAuth();
  const [mode, setMode] = useState<"phone" | "email">("phone");
  const [phone, setPhone] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      if (mode === "phone") {
        await login(phone, password);
      } else {
        await loginByEmail(email, password);
      }
      router.push("/");
    } catch (err: any) {
      setError(err.message || "登录失败");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-[60vh] flex items-center justify-center px-4">
      <div className="card w-full max-w-md p-8">
        <h1 className="text-2xl font-bold text-center mb-6">登录</h1>

        <div className="flex gap-2 mb-6">
          <button
            onClick={() => setMode("phone")}
            className={`flex-1 py-2 text-sm rounded-lg ${
              mode === "phone" ? "bg-primary-600 text-white" : "bg-gray-100 text-gray-600"
            }`}
          >
            手机号登录
          </button>
          <button
            onClick={() => setMode("email")}
            className={`flex-1 py-2 text-sm rounded-lg ${
              mode === "email" ? "bg-primary-600 text-white" : "bg-gray-100 text-gray-600"
            }`}
          >
            邮箱登录
          </button>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          {mode === "phone" ? (
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">手机号</label>
              <input
                type="tel"
                value={phone}
                onChange={(e) => setPhone(e.target.value)}
                placeholder="请输入手机号"
                className="input-field"
                required
              />
            </div>
          ) : (
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">邮箱</label>
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="请输入邮箱"
                className="input-field"
                required
              />
            </div>
          )}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">密码</label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="请输入密码"
              className="input-field"
              required
            />
          </div>
          {error && <p className="text-red-500 text-sm">{error}</p>}
          <button type="submit" disabled={loading} className="btn-primary w-full">
            {loading ? "登录中..." : "登录"}
          </button>
        </form>

        <p className="text-center text-sm text-gray-500 mt-4">
          还没有账号？
          <Link href="/user/register" className="text-primary-600 hover:underline ml-1">
            立即注册
          </Link>
        </p>
      </div>
    </div>
  );
}
