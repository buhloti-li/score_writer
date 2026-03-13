"use client";

import { useQuery } from "@tanstack/react-query";
import SearchBar from "@/components/SearchBar";
import ScoreCard from "@/components/ScoreCard";
import { scoreApi } from "@/lib/api";
import Link from "next/link";

const INSTRUMENTS = [
  { name: "钢琴", icon: "🎹" },
  { name: "吉他", icon: "🎸" },
  { name: "小提琴", icon: "🎻" },
  { name: "声乐", icon: "🎤" },
  { name: "长笛", icon: "🪈" },
  { name: "大提琴", icon: "🎻" },
];

export default function HomePage() {
  const { data: latestScores } = useQuery({
    queryKey: ["scores", "latest"],
    queryFn: () => scoreApi.list({ page: 1, page_size: 8 }),
  });

  return (
    <div>
      {/* Hero */}
      <section className="bg-gradient-to-br from-primary-600 to-primary-800 text-white">
        <div className="max-w-7xl mx-auto px-4 py-20 sm:px-6 lg:px-8 text-center">
          <h1 className="text-4xl md:text-5xl font-bold mb-4">
            专业乐谱，触手可得
          </h1>
          <p className="text-lg text-primary-100 mb-8 max-w-2xl mx-auto">
            基于 AI 自动打谱与 LilyPond 出版级排版，提供高质量乐谱搜索、浏览与定制服务
          </p>
          <div className="flex justify-center">
            <SearchBar />
          </div>
          <p className="text-sm text-primary-200 mt-4">
            找不到想要的乐谱？试试
            <Link href="/custom" className="underline hover:text-white ml-1">
              定制打谱
            </Link>
          </p>
        </div>
      </section>

      {/* Instruments */}
      <section className="max-w-7xl mx-auto px-4 py-12 sm:px-6 lg:px-8">
        <h2 className="text-2xl font-bold text-gray-900 mb-6">按乐器浏览</h2>
        <div className="grid grid-cols-3 md:grid-cols-6 gap-4">
          {INSTRUMENTS.map((inst) => (
            <Link
              key={inst.name}
              href={`/scores?instrument=${encodeURIComponent(inst.name)}`}
              className="card p-4 text-center hover:shadow-md transition-shadow"
            >
              <span className="text-3xl">{inst.icon}</span>
              <p className="mt-2 text-sm font-medium text-gray-700">{inst.name}</p>
            </Link>
          ))}
        </div>
      </section>

      {/* Latest Scores */}
      <section className="max-w-7xl mx-auto px-4 py-12 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-2xl font-bold text-gray-900">最新乐谱</h2>
          <Link href="/scores" className="text-primary-600 hover:text-primary-700 text-sm font-medium">
            查看全部 →
          </Link>
        </div>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 md:gap-6">
          {latestScores?.items.map((score) => (
            <ScoreCard key={score.id} score={score} />
          ))}
          {!latestScores?.items.length && (
            <p className="col-span-4 text-center text-gray-400 py-12">
              暂无乐谱，敬请期待
            </p>
          )}
        </div>
      </section>

      {/* CTA */}
      <section className="bg-gray-900 text-white">
        <div className="max-w-7xl mx-auto px-4 py-16 sm:px-6 lg:px-8 text-center">
          <h2 className="text-3xl font-bold mb-4">找不到想要的乐谱？</h2>
          <p className="text-gray-300 mb-8 max-w-xl mx-auto">
            上传图片或描述需求，AI 自动打谱 + 专业审核，一天内交付出版级质量乐谱
          </p>
          <Link href="/custom" className="btn-primary text-lg px-8 py-3">
            立即定制
          </Link>
        </div>
      </section>
    </div>
  );
}
