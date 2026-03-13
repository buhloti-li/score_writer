"use client";

import { useParams, useRouter } from "next/navigation";
import { useQuery } from "@tanstack/react-query";
import { scoreApi, orderApi } from "@/lib/api";
import { useAuth } from "@/lib/auth";
import { useState } from "react";

export default function ScoreDetailPage() {
  const { id } = useParams<{ id: string }>();
  const router = useRouter();
  const { user } = useAuth();
  const [purchasing, setPurchasing] = useState(false);

  const { data: score, isLoading } = useQuery({
    queryKey: ["score", id],
    queryFn: () => scoreApi.get(id),
    enabled: !!id,
  });

  const handlePurchase = async () => {
    if (!user) {
      router.push("/user/login");
      return;
    }
    if (!score) return;

    setPurchasing(true);
    try {
      const order = await orderApi.create({
        score_id: score.id,
        amount: parseFloat(score.price),
        source: "website",
      });
      router.push(`/order/${order.id}`);
    } catch (err: any) {
      alert(err.message || "下单失败");
    } finally {
      setPurchasing(false);
    }
  };

  if (isLoading) {
    return (
      <div className="max-w-5xl mx-auto px-4 py-8 animate-pulse">
        <div className="grid md:grid-cols-2 gap-8">
          <div className="aspect-[3/4] bg-gray-200 rounded-xl" />
          <div className="space-y-4">
            <div className="h-8 bg-gray-200 rounded w-3/4" />
            <div className="h-4 bg-gray-200 rounded w-1/2" />
            <div className="h-4 bg-gray-200 rounded w-1/3" />
          </div>
        </div>
      </div>
    );
  }

  if (!score) {
    return (
      <div className="text-center py-20 text-gray-500">
        乐谱不存在
      </div>
    );
  }

  const difficultyLabel = score.difficulty
    ? ["", "入门", "初级", "中级", "高级", "专业"][score.difficulty]
    : null;

  return (
    <div className="max-w-5xl mx-auto px-4 py-8 sm:px-6 lg:px-8">
      <div className="grid md:grid-cols-2 gap-8">
        {/* Preview */}
        <div className="card">
          <div className="aspect-[3/4] bg-gray-100 flex items-center justify-center">
            {score.preview_image_url ? (
              <img
                src={score.preview_image_url}
                alt={score.title}
                className="w-full h-full object-contain"
              />
            ) : score.pdf_watermarked_url ? (
              <iframe
                src={score.pdf_watermarked_url}
                className="w-full h-full"
                title="Score preview"
              />
            ) : (
              <div className="text-gray-400 text-center">
                <svg className="w-16 h-16 mx-auto mb-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 19V6l12-3v13M9 19c0 1.105-1.343 2-3 2s-3-.895-3-2 1.343-2 3-2 3 .895 3 2zm12-3c0 1.105-1.343 2-3 2s-3-.895-3-2 1.343-2 3-2 3 .895 3 2zM9 10l12-3" />
                </svg>
                <p>暂无预览</p>
              </div>
            )}
          </div>
        </div>

        {/* Info */}
        <div>
          <h1 className="text-3xl font-bold text-gray-900 mb-2">{score.title}</h1>
          {score.title_en && (
            <p className="text-lg text-gray-500 mb-4">{score.title_en}</p>
          )}

          <div className="space-y-3 mb-6">
            {score.composer && (
              <InfoRow label="作曲" value={score.composer} />
            )}
            {score.arranger && (
              <InfoRow label="编曲" value={score.arranger} />
            )}
            {score.lyricist && (
              <InfoRow label="作词" value={score.lyricist} />
            )}
            {score.instrument && (
              <InfoRow label="乐器" value={score.instrument} />
            )}
            {score.key_signature && (
              <InfoRow label="调号" value={score.key_signature} />
            )}
            {score.time_signature && (
              <InfoRow label="拍号" value={score.time_signature} />
            )}
            {difficultyLabel && (
              <InfoRow label="难度" value={difficultyLabel} />
            )}
            {score.genre && (
              <InfoRow label="风格" value={score.genre} />
            )}
            {score.page_count && (
              <InfoRow label="页数" value={`${score.page_count} 页`} />
            )}
          </div>

          {score.tags && score.tags.length > 0 && (
            <div className="flex flex-wrap gap-2 mb-6">
              {score.tags.map((tag) => (
                <span key={tag} className="bg-gray-100 text-gray-600 px-3 py-1 rounded-full text-sm">
                  {tag}
                </span>
              ))}
            </div>
          )}

          {score.description && (
            <p className="text-gray-600 mb-6">{score.description}</p>
          )}

          <div className="border-t border-gray-200 pt-6">
            <div className="flex items-end gap-4 mb-4">
              <span className="text-4xl font-bold text-primary-600">¥{score.price}</span>
              <span className="text-sm text-gray-400 mb-1">
                已售 {score.download_count} 份
              </span>
            </div>
            <button
              onClick={handlePurchase}
              disabled={purchasing || score.status !== "available"}
              className="btn-primary w-full text-lg py-3"
            >
              {purchasing
                ? "处理中..."
                : score.status === "available"
                  ? "立即购买"
                  : "暂不可购买"}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

function InfoRow({ label, value }: { label: string; value: string }) {
  return (
    <div className="flex">
      <span className="text-gray-500 w-16 flex-shrink-0">{label}</span>
      <span className="text-gray-900">{value}</span>
    </div>
  );
}
