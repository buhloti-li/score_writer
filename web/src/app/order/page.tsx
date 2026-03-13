"use client";

import { useQuery } from "@tanstack/react-query";
import { useAuth } from "@/lib/auth";
import { orderApi } from "@/lib/api";
import { useRouter } from "next/navigation";
import { useEffect } from "react";
import Link from "next/link";

const STATUS_MAP: Record<string, { label: string; color: string }> = {
  pending: { label: "待支付", color: "text-yellow-600 bg-yellow-50" },
  paid: { label: "已支付", color: "text-green-600 bg-green-50" },
  refunded: { label: "已退款", color: "text-gray-600 bg-gray-50" },
};

const DELIVERY_MAP: Record<string, { label: string; color: string }> = {
  pending: { label: "待发货", color: "text-orange-600 bg-orange-50" },
  delivered: { label: "已发货", color: "text-green-600 bg-green-50" },
};

export default function OrderListPage() {
  const { user, isLoading: authLoading } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (!authLoading && !user) router.push("/user/login");
  }, [user, authLoading, router]);

  const { data, isLoading } = useQuery({
    queryKey: ["orders"],
    queryFn: () => orderApi.list({ page: 1, page_size: 50 }),
    enabled: !!user,
  });

  if (authLoading || !user) return null;

  return (
    <div className="max-w-4xl mx-auto px-4 py-8">
      <h1 className="text-2xl font-bold mb-6">我的订单</h1>

      {isLoading ? (
        <div className="space-y-4">
          {[1, 2, 3].map((i) => (
            <div key={i} className="card p-6 animate-pulse">
              <div className="h-4 bg-gray-200 rounded w-1/3 mb-2" />
              <div className="h-3 bg-gray-200 rounded w-1/4" />
            </div>
          ))}
        </div>
      ) : data?.items.length ? (
        <div className="space-y-4">
          {data.items.map((order) => {
            const status = STATUS_MAP[order.payment_status] || STATUS_MAP.pending;
            const delivery = DELIVERY_MAP[order.delivery_status] || DELIVERY_MAP.pending;
            return (
              <Link key={order.id} href={`/order/${order.id}`} className="card p-6 block hover:shadow-md transition-shadow">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm text-gray-500">
                    订单号: {order.id.slice(0, 8)}...
                  </span>
                  <span className="text-sm text-gray-400">
                    {new Date(order.created_at).toLocaleString("zh-CN")}
                  </span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="font-semibold text-lg">¥{order.amount}</span>
                  <div className="flex gap-2">
                    <span className={`px-2 py-0.5 rounded text-xs font-medium ${status.color}`}>
                      {status.label}
                    </span>
                    {order.payment_status === "paid" && (
                      <span className={`px-2 py-0.5 rounded text-xs font-medium ${delivery.color}`}>
                        {delivery.label}
                      </span>
                    )}
                  </div>
                </div>
              </Link>
            );
          })}
        </div>
      ) : (
        <div className="text-center py-20">
          <p className="text-gray-500 mb-4">暂无订单</p>
          <Link href="/scores" className="btn-primary">
            去选购乐谱
          </Link>
        </div>
      )}
    </div>
  );
}
