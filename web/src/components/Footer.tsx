export default function Footer() {
  return (
    <footer className="bg-white border-t border-gray-200 mt-auto">
      <div className="max-w-7xl mx-auto px-4 py-8 sm:px-6 lg:px-8">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          <div>
            <h3 className="font-semibold text-gray-900 mb-3">Score Writer</h3>
            <p className="text-sm text-gray-500">
              自动化乐谱转录与销售平台，提供出版级质量的 LilyPond 排版乐谱。
            </p>
          </div>
          <div>
            <h3 className="font-semibold text-gray-900 mb-3">乐器分类</h3>
            <div className="flex flex-wrap gap-2 text-sm text-gray-500">
              <span>钢琴</span>
              <span>吉他</span>
              <span>小提琴</span>
              <span>声乐</span>
              <span>长笛</span>
              <span>大提琴</span>
            </div>
          </div>
          <div>
            <h3 className="font-semibold text-gray-900 mb-3">联系我们</h3>
            <p className="text-sm text-gray-500">如需帮助请联系客服</p>
          </div>
        </div>
        <div className="mt-8 pt-4 border-t border-gray-100 text-center text-xs text-gray-400">
          &copy; {new Date().getFullYear()} Score Writer. All rights reserved.
        </div>
      </div>
    </footer>
  );
}
