"use client";

import { useParams } from "next/navigation";
import { useQuery } from "@tanstack/react-query";
import { orderApi, scoreApi } from "@/lib/api";
import Link from "next/link";

export default function OrderDetailPage() {
  const { id } = useParams<{ id: string }>();

  const { data: order, isLoading } = useQuery({
    queryKey: ["order", id],
    queryFn: () => orderApi.get(id),
    enabled: !!id,
  });

  const { data: score } = useQuery({
    queryKey: ["score", order?.score_id],
    queryFn: () => scoreApi.get(order!.score_id!),
    enabled: !!order?.score_id,
  });

  if (isLoading) {
    return <div className="text-center py-20 text-gray-400">加载中...</div>;
  }

  if (!order) {
    return <div className="text-center py-20 text-gray-500">订单不存在</div>;
  }

  return (
    <div className="max-w-2xl mx-auto px-4 py-8">
      <h1 className="text-2xl font-bold mb-6">订单详情</h1>

      <div className="card p-6 space-y-4">
        <InfoRow label="订单号" value={order.id} />
        <InfoRow label="金额" value={`¥${order.amount}`} />
        <InfoRow label="支付状态" value={
          order.payment_status === "paid" ? "已支付" :
          order.payment_status === "refunded" ? "已退款" : "待支付"
        } />
        <InfoRow label="发货状态" value={
          order.delivery_status === "delivered" ? "已发货" : "待发货"
        } />
        <InfoRow label="来源" value={order.source === "taobao" ? "淘宝" : "网站"} />
        <InfoRow label="下单时间" value={new Date(order.created_at).toLocaleString("zh-CN")} />
        {order.delivered_at && (
          <InfoRow label="发货时间" value={new Date(order.delivered_at).toLocaleString("zh-CN")} />
        )}
      </div>

      {score && (
        <div className="card p-6 mt-4">
          <h2 className="font-semibold mb-3">乐谱信息</h2>
          <Link href={`/scores/${score.id}`} className="text-primary-600 hover:underline">
            {score.title}
          </Link>
          {score.composer && <p className="text-sm text-gray-500 mt-1">{score.composer}</p>}
        </div>
      )}

      <div className="mt-6">
        <Link href="/order" className="text-primary-600 hover:underline text-sm">
          ← 返回订单列表
        </Link>
      </div>
    </div>
  );
}

function InfoRow({ label, value }: { label: string; value: string }) {
  return (
    <div className="flex justify-between">
      <span className="text-gray-500">{label}</span>
      <span className="text-gray-900 text-right">{value}</span>
    </div>
  );
}
