"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/lib/auth";

export default function CustomPage() {
  const { user } = useAuth();
  const router = useRouter();
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [files, setFiles] = useState<File[]>([]);
  const [submitting, setSubmitting] = useState(false);
  const [submitted, setSubmitted] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!user) {
      router.push("/user/login");
      return;
    }

    setSubmitting(true);
    try {
      // Upload images if any
      let uploadedUrls: string[] = [];
      if (files.length > 0) {
        const formData = new FormData();
        files.forEach((f) => formData.append("files", f));

        const token = localStorage.getItem("access_token");
        const res = await fetch("/api/v1/upload/images", {
          method: "POST",
          headers: token ? { Authorization: `Bearer ${token}` } : {},
          body: formData,
        });
        if (res.ok) {
          const data = await res.json();
          uploadedUrls = data.files.map((f: any) => f.url);
        }
      }

      // Create task
      const token = localStorage.getItem("access_token");
      const res = await fetch("/api/v1/tasks", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          ...(token ? { Authorization: `Bearer ${token}` } : {}),
        },
        body: JSON.stringify({
          type: "customer_transcribe",
          title: title,
          source: "website",
          customer_info: { description, user_id: user.id },
          original_images: uploadedUrls,
          image_source: uploadedUrls.length > 0 ? "user_upload" : null,
          priority: "high",
        }),
      });

      if (res.ok) {
        setSubmitted(true);
      } else {
        const err = await res.json();
        alert(err.detail || "提交失败");
      }
    } catch {
      alert("提交失败，请重试");
    } finally {
      setSubmitting(false);
    }
  };

  if (submitted) {
    return (
      <div className="max-w-2xl mx-auto px-4 py-20 text-center">
        <div className="text-5xl mb-4">✓</div>
        <h1 className="text-2xl font-bold mb-2">定制需求已提交</h1>
        <p className="text-gray-500 mb-6">
          我们会在1个工作日内完成打谱并通知您，请关注订单状态。
        </p>
        <button onClick={() => router.push("/order")} className="btn-primary">
          查看我的订单
        </button>
      </div>
    );
  }

  return (
    <div className="max-w-2xl mx-auto px-4 py-8">
      <h1 className="text-2xl font-bold mb-2">定制打谱</h1>
      <p className="text-gray-500 mb-8">
        上传乐谱图片或描述您需要的乐谱，AI 自动打谱 + 专业审核，一天内交付。
      </p>

      <form onSubmit={handleSubmit} className="space-y-6">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            曲名 <span className="text-red-500">*</span>
          </label>
          <input
            type="text"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            placeholder="请输入曲名，如：月光奏鸣曲"
            className="input-field"
            required
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            需求描述
          </label>
          <textarea
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            placeholder="描述您的需求，如：乐器类型、难度要求、特殊要求等"
            className="input-field min-h-[120px] resize-y"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            上传乐谱图片（可选）
          </label>
          <p className="text-xs text-gray-400 mb-2">
            支持 JPG、PNG、PDF 格式，单文件最大 20MB
          </p>
          <input
            type="file"
            multiple
            accept=".jpg,.jpeg,.png,.pdf"
            onChange={(e) => setFiles(Array.from(e.target.files || []))}
            className="block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:text-sm file:font-medium file:bg-primary-50 file:text-primary-700 hover:file:bg-primary-100"
          />
          {files.length > 0 && (
            <p className="text-sm text-gray-500 mt-2">
              已选 {files.length} 个文件
            </p>
          )}
        </div>

        <div className="card p-4 bg-blue-50 border-blue-200">
          <h3 className="font-medium text-blue-900 mb-1">定制说明</h3>
          <ul className="text-sm text-blue-700 space-y-1">
            <li>- 简单乐谱（单声部，1-2页）：¥15-30</li>
            <li>- 中等乐谱（钢琴谱，3-5页）：¥40-80</li>
            <li>- 复杂乐谱（多声部，5+页）：¥100-200</li>
            <li>- 交付时间：1个工作日内</li>
          </ul>
        </div>

        <button type="submit" disabled={submitting || !title} className="btn-primary w-full text-lg py-3">
          {submitting ? "提交中..." : "提交定制需求"}
        </button>
      </form>
    </div>
  );
}
