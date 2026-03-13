"use client";

import { useAuth } from "@/lib/auth";
import { useRouter } from "next/navigation";
import { useEffect } from "react";
import Link from "next/link";

export default function ProfilePage() {
  const { user, isLoading, logout } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (!isLoading && !user) {
      router.push("/user/login");
    }
  }, [user, isLoading, router]);

  if (isLoading || !user) {
    return <div className="text-center py-20 text-gray-400">加载中...</div>;
  }

  return (
    <div className="max-w-2xl mx-auto px-4 py-8">
      <h1 className="text-2xl font-bold mb-6">个人中心</h1>

      <div className="card p-6 mb-6">
        <h2 className="font-semibold text-gray-900 mb-4">基本信息</h2>
        <div className="space-y-3">
          <div className="flex justify-between">
            <span className="text-gray-500">昵称</span>
            <span>{user.nickname || "未设置"}</span>
          </div>
          <div className="flex justify-between">
            <span className="text-gray-500">手机号</span>
            <span>{user.phone || "未绑定"}</span>
          </div>
          <div className="flex justify-between">
            <span className="text-gray-500">邮箱</span>
            <span>{user.email || "未绑定"}</span>
          </div>
          <div className="flex justify-between">
            <span className="text-gray-500">注册时间</span>
            <span>{new Date(user.created_at).toLocaleDateString("zh-CN")}</span>
          </div>
        </div>
      </div>

      <div className="card p-6 mb-6">
        <h2 className="font-semibold text-gray-900 mb-4">快捷入口</h2>
        <div className="grid grid-cols-2 gap-3">
          <Link href="/order" className="btn-secondary text-center">
            我的订单
          </Link>
          <Link href="/custom" className="btn-secondary text-center">
            定制打谱
          </Link>
        </div>
      </div>

      <button
        onClick={() => {
          logout();
          router.push("/");
        }}
        className="text-red-500 hover:text-red-600 text-sm"
      >
        退出登录
      </button>
    </div>
  );
}
