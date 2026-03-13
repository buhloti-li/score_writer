"use client";

import Link from "next/link";
import { useAuth } from "@/lib/auth";
import { useEffect } from "react";

export default function Header() {
  const { user, isLoading, loadUser, logout } = useAuth();

  useEffect(() => {
    loadUser();
  }, [loadUser]);

  return (
    <header className="bg-white border-b border-gray-200 sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          <div className="flex items-center gap-8">
            <Link href="/" className="text-xl font-bold text-primary-700">
              Score Writer
            </Link>
            <nav className="hidden md:flex items-center gap-6">
              <Link href="/scores" className="text-gray-600 hover:text-gray-900 text-sm font-medium">
                乐谱库
              </Link>
              <Link href="/custom" className="text-gray-600 hover:text-gray-900 text-sm font-medium">
                定制打谱
              </Link>
            </nav>
          </div>
          <div className="flex items-center gap-4">
            {isLoading ? (
              <div className="w-20 h-8 bg-gray-100 rounded animate-pulse" />
            ) : user ? (
              <div className="flex items-center gap-3">
                <Link href="/order" className="text-sm text-gray-600 hover:text-gray-900">
                  我的订单
                </Link>
                <Link href="/user/profile" className="text-sm text-gray-600 hover:text-gray-900">
                  {user.nickname || user.phone || "用户"}
                </Link>
                <button onClick={logout} className="text-sm text-gray-400 hover:text-gray-600">
                  退出
                </button>
              </div>
            ) : (
              <div className="flex items-center gap-2">
                <Link href="/user/login" className="btn-secondary text-sm py-1.5">
                  登录
                </Link>
                <Link href="/user/register" className="btn-primary text-sm py-1.5">
                  注册
                </Link>
              </div>
            )}
          </div>
        </div>
      </div>
    </header>
  );
}
