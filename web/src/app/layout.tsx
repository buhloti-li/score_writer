import type { Metadata } from "next";
import Providers from "@/components/Providers";
import Header from "@/components/Header";
import Footer from "@/components/Footer";
import "@/styles/globals.css";

export const metadata: Metadata = {
  title: "Score Writer - 乐谱搜索与定制平台",
  description: "自动化乐谱转录与销售平台，提供出版级质量的 LilyPond 排版乐谱。搜索、浏览、购买或定制您需要的乐谱。",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="zh-CN">
      <body className="min-h-screen flex flex-col">
        <Providers>
          <Header />
          <main className="flex-1">{children}</main>
          <Footer />
        </Providers>
      </body>
    </html>
  );
}
