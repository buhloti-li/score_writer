"use client";

import Link from "next/link";
import type { ScoreResponse } from "@/lib/api";

export default function ScoreCard({ score }: { score: ScoreResponse }) {
  return (
    <Link href={`/scores/${score.id}`} className="card group hover:shadow-md transition-shadow">
      <div className="aspect-[3/4] bg-gray-100 flex items-center justify-center">
        {score.preview_image_url ? (
          <img
            src={score.preview_image_url}
            alt={score.title}
            className="w-full h-full object-cover"
          />
        ) : (
          <div className="text-gray-400 text-center p-4">
            <svg className="w-12 h-12 mx-auto mb-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 19V6l12-3v13M9 19c0 1.105-1.343 2-3 2s-3-.895-3-2 1.343-2 3-2 3 .895 3 2zm12-3c0 1.105-1.343 2-3 2s-3-.895-3-2 1.343-2 3-2 3 .895 3 2zM9 10l12-3" />
            </svg>
            <span className="text-sm">暂无预览</span>
          </div>
        )}
      </div>
      <div className="p-4">
        <h3 className="font-semibold text-gray-900 group-hover:text-primary-600 transition-colors line-clamp-1">
          {score.title}
        </h3>
        {score.composer && (
          <p className="text-sm text-gray-500 mt-1">{score.composer}</p>
        )}
        <div className="flex items-center justify-between mt-3">
          <span className="text-primary-600 font-bold">¥{score.price}</span>
          <div className="flex items-center gap-2 text-xs text-gray-400">
            {score.instrument && (
              <span className="bg-gray-100 px-2 py-0.5 rounded">{score.instrument}</span>
            )}
            {score.difficulty && (
              <span className="bg-gray-100 px-2 py-0.5 rounded">
                难度 {score.difficulty}
              </span>
            )}
          </div>
        </div>
      </div>
    </Link>
  );
}
