"use client";

import { useSearchParams, useRouter } from "next/navigation";
import { useQuery } from "@tanstack/react-query";
import { Suspense } from "react";
import SearchBar from "@/components/SearchBar";
import ScoreCard from "@/components/ScoreCard";
import Pagination from "@/components/Pagination";
import { scoreApi } from "@/lib/api";
import Link from "next/link";

const INSTRUMENTS = ["钢琴", "吉他", "小提琴", "声乐", "长笛", "大提琴", "萨克斯", "单簧管"];

function ScoresContent() {
  const searchParams = useSearchParams();
  const router = useRouter();

  const q = searchParams.get("q") || "";
  const instrument = searchParams.get("instrument") || "";
  const page = parseInt(searchParams.get("page") || "1");
  const pageSize = 20;

  const { data, isLoading } = useQuery({
    queryKey: ["scores", q, instrument, page],
    queryFn: () =>
      q
        ? scoreApi.search({ q, instrument: instrument || undefined, page, page_size: pageSize })
        : scoreApi.list({ page, page_size: pageSize, instrument: instrument || undefined }),
  });

  const totalPages = data ? Math.ceil(data.total / pageSize) : 0;

  const setPage = (p: number) => {
    const params = new URLSearchParams(searchParams.toString());
    params.set("page", String(p));
    router.push(`/scores?${params.toString()}`);
  };

  return (
    <div className="max-w-7xl mx-auto px-4 py-8 sm:px-6 lg:px-8">
      <div className="mb-8">
        <SearchBar defaultValue={q} />
      </div>

      {/* Instrument filter */}
      <div className="flex flex-wrap gap-2 mb-6">
        <Link
          href="/scores"
          className={`px-3 py-1.5 rounded-full text-sm font-medium transition-colors ${
            !instrument ? "bg-primary-600 text-white" : "bg-gray-100 text-gray-600 hover:bg-gray-200"
          }`}
        >
          全部
        </Link>
        {INSTRUMENTS.map((inst) => (
          <Link
            key={inst}
            href={`/scores?instrument=${encodeURIComponent(inst)}${q ? `&q=${encodeURIComponent(q)}` : ""}`}
            className={`px-3 py-1.5 rounded-full text-sm font-medium transition-colors ${
              instrument === inst
                ? "bg-primary-600 text-white"
                : "bg-gray-100 text-gray-600 hover:bg-gray-200"
            }`}
          >
            {inst}
          </Link>
        ))}
      </div>

      {/* Results */}
      {isLoading ? (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 md:gap-6">
          {Array.from({ length: 8 }).map((_, i) => (
            <div key={i} className="card animate-pulse">
              <div className="aspect-[3/4] bg-gray-200" />
              <div className="p-4 space-y-2">
                <div className="h-4 bg-gray-200 rounded w-3/4" />
                <div className="h-3 bg-gray-200 rounded w-1/2" />
              </div>
            </div>
          ))}
        </div>
      ) : data?.items.length ? (
        <>
          <p className="text-sm text-gray-500 mb-4">
            共 {data.total} 个结果
          </p>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 md:gap-6">
            {data.items.map((score) => (
              <ScoreCard key={score.id} score={score} />
            ))}
          </div>
          <Pagination page={page} totalPages={totalPages} onPageChange={setPage} />
        </>
      ) : (
        <div className="text-center py-20">
          <p className="text-gray-500 text-lg mb-4">
            {q ? `没有找到"${q}"相关的乐谱` : "暂无乐谱"}
          </p>
          <Link href="/custom" className="btn-primary">
            帮我找谱 / 定制打谱
          </Link>
        </div>
      )}
    </div>
  );
}

export default function ScoresPage() {
  return (
    <Suspense fallback={<div className="text-center py-20 text-gray-400">加载中...</div>}>
      <ScoresContent />
    </Suspense>
  );
}
