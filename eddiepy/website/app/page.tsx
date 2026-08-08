"use client";

import { useEffect, useMemo, useState } from "react";

type Lesson = {
  id: string;
  number: string;
  title: string;
  subtitle: string;
  description: string;
  code: string;
  tip: string;
};

const lessons: Lesson[] = [
  {
    id: "start",
    number: "01",
    title: "第一個程式",
    subtitle: "先讓電腦開口說話",
    description: "EddieLang 用中文關鍵字，把程式的第一步變得很直覺。",
    code: `說 "嗨，我是 EddieLang！"\n說 "今天開始學寫程式"`,
    tip: "說 後面可以放字串、變數或運算式。",
  },
  {
    id: "variables",
    number: "02",
    title: "變數與型別",
    subtitle: "替資料取一個名字",
    description: "用 設定 建立資料。int、float、str、bool 會告訴語言資料的型別。",
    code: `設定 str 名字 = "Eddie"\n設定 int 分數 = 100\n設定 bool 通過 = true\n說 名字`,
    tip: "變數建立後，可以用單一 = 更新內容。",
  },
  {
    id: "conditions",
    number: "03",
    title: "條件判斷",
    subtitle: "讓程式做出選擇",
    description: "如果、否則如果、否則會依照條件，選擇要執行的區塊。",
    code: `如果 分數 >= 60 {\n    說 "及格！"\n} 否則 {\n    說 "再試一次"\n}`,
    tip: "比較文字時記得加上引號，例如 難度 == \"簡單\"。",
  },
  {
    id: "loops",
    number: "04",
    title: "重複與迴圈",
    subtitle: "讓重複的事自動完成",
    description: "重複執行會一直執行到條件變成 false；重複則適合數固定次數。",
    code: `設定 int 次數 = 1\n重複 次數 從 1 到 3 {\n    說 次數\n}\n\n重複執行 次數 <= 5 {\n    次數 = 次數 + 1\n}`,
    tip: "在迴圈裡使用 停止 離開，使用 跳過 進入下一輪。",
  },
  {
    id: "functions",
    number: "05",
    title: "函數",
    subtitle: "把能力包裝起來重複使用",
    description: "函數可以接收參數，也可以用 回傳 把結果交回呼叫處。",
    code: `函數 相加(a, b) {\n    回傳 a + b\n}\n\n設定 int 結果 = 呼叫 相加(2, 3)\n說 結果`,
    tip: "函數參數用逗號分隔；區域變數只在函數裡使用。",
  },
  {
    id: "input",
    number: "06",
    title: "輸入與隨機",
    subtitle: "讓程式和使用者互動",
    description: "輸入 會讀取使用者內容，隨機(最小值, 最大值) 會產生包含上下限的整數。",
    code: `設定 int 最大值 = 100\n設定 int 猜測 = 輸入(\">>>\")\n設定 int 答案 = 隨機(0, 最大值)\n說 猜測`,
    tip: "輸入會依照變數型別自動轉成 int、float 或 bool。",
  },
];

function CodeBlock({ code }: { code: string }) {
  const [copied, setCopied] = useState(false);

  async function copyCode() {
    await navigator.clipboard?.writeText(code);
    setCopied(true);
    window.setTimeout(() => setCopied(false), 1500);
  }

  return (
    <div className="code-card">
      <div className="code-bar">
        <span className="traffic-lights"><i /><i /><i /></span>
        <span>main.eddie</span>
        <button onClick={copyCode} className="copy-button" aria-label="複製程式碼">
          {copied ? "已複製" : "複製"}
        </button>
      </div>
      <pre><code>{code}</code></pre>
    </div>
  );
}

export default function Home() {
  const [activeId, setActiveId] = useState("start");
  const [query, setQuery] = useState("");
  const [completed, setCompleted] = useState<string[]>([]);

  useEffect(() => {
    const saved = window.localStorage.getItem("eddielang-progress");
    if (saved) setCompleted(JSON.parse(saved));
  }, []);

  const visibleLessons = useMemo(() => {
    const keyword = query.trim().toLowerCase();
    if (!keyword) return lessons;
    return lessons.filter((lesson) =>
      `${lesson.title} ${lesson.subtitle} ${lesson.description}`.toLowerCase().includes(keyword),
    );
  }, [query]);

  const activeLesson = lessons.find((lesson) => lesson.id === activeId) ?? lessons[0];
  const progress = Math.round((completed.length / lessons.length) * 100);

  function toggleComplete(id: string) {
    const next = completed.includes(id)
      ? completed.filter((item) => item !== id)
      : [...completed, id];
    setCompleted(next);
    window.localStorage.setItem("eddielang-progress", JSON.stringify(next));
  }

  return (
    <main className="site-shell">
      <aside className="sidebar">
        <a className="brand" href="#top" aria-label="EddieLang 教學首頁">
          <span className="brand-mark">E</span>
          <span><strong>EddieLang</strong><small>中文程式語言</small></span>
        </a>
        <div className="sidebar-label">學習路線</div>
        <nav className="lesson-nav" aria-label="課程章節">
          {lessons.map((lesson) => (
            <button
              key={lesson.id}
              className={activeId === lesson.id ? "lesson-link active" : "lesson-link"}
              onClick={() => { setActiveId(lesson.id); document.getElementById(lesson.id)?.scrollIntoView({ behavior: "smooth" }); }}
            >
              <span className="lesson-number">{lesson.number}</span>
              <span>{lesson.title}</span>
              {completed.includes(lesson.id) && <b aria-label="已完成">✓</b>}
            </button>
          ))}
        </nav>
        <div className="progress-card">
          <div className="progress-heading"><span>學習進度</span><strong>{progress}%</strong></div>
          <div className="progress-track"><span style={{ width: `${progress}%` }} /></div>
          <p>{completed.length === lessons.length ? "太棒了，全部完成！" : "每天學一點，寫出自己的程式。"}</p>
        </div>
        <a className="github-link" href="https://github.com" target="_blank" rel="noreferrer">↗ 查看專案</a>
      </aside>

      <section className="content" id="top">
        <header className="topbar">
          <span className="eyebrow"><span className="status-dot" />互動式學習指南</span>
          <label className="search-box">
            <span>⌕</span>
            <input value={query} onChange={(event) => setQuery(event.target.value)} placeholder="搜尋章節或概念..." aria-label="搜尋章節" />
            <kbd>⌘ K</kbd>
          </label>
        </header>

        <div className="hero">
          <div className="hero-copy">
            <p className="hero-kicker">WELCOME TO THE LANGUAGE LAB</p>
            <h1>用中文，寫出<br /><em>你的第一個程式。</em></h1>
            <p className="hero-lede">EddieLang 是一門為初學者設計的中文程式語言。從「說」開始，逐步學會讓想法動起來。</p>
            <div className="hero-actions">
              <button className="primary-button" onClick={() => document.getElementById("start")?.scrollIntoView({ behavior: "smooth" })}>開始學習 <span>↓</span></button>
              <span className="lesson-count">{lessons.length} 個核心章節 <i>·</i> 約 20 分鐘</span>
            </div>
          </div>
          <div className="hero-terminal" aria-label="EddieLang 程式預覽">
            <div className="terminal-top"><span className="traffic-lights"><i /><i /><i /></span><span>hello.eddie</span><span className="terminal-live">● LIVE</span></div>
            <div className="terminal-code"><span className="line-no">01</span><span><b className="pink">說</b> <strong>"你好，世界！"</strong></span><span className="line-no">02</span><span><b className="pink">說</b> <strong>"準備好了嗎？"</strong></span><span className="line-no">03</span><span className="terminal-output">你好，世界！</span><span className="line-no">04</span><span className="terminal-output">準備好了嗎？</span><span className="cursor">▌</span></div>
          </div>
        </div>

        <div className="section-intro"><span className="section-label">THE BASICS</span><h2>從想法，到執行。</h2><p>每個章節都用一個小概念，帶你看懂程式如何一步步完成任務。</p></div>

        <div className="lesson-grid">
          {visibleLessons.map((lesson) => (
            <article className={`lesson-card ${activeId === lesson.id ? "selected" : ""}`} id={lesson.id} key={lesson.id} onClick={() => setActiveId(lesson.id)}>
              <div className="lesson-card-heading"><span className="chapter-tag">CHAPTER {lesson.number}</span><button className={completed.includes(lesson.id) ? "check checked" : "check"} onClick={(event) => { event.stopPropagation(); toggleComplete(lesson.id); }} aria-label="標記章節完成">{completed.includes(lesson.id) ? "✓" : "○"}</button></div>
              <h3>{lesson.title}<span>{lesson.subtitle}</span></h3>
              <p>{lesson.description}</p>
              <CodeBlock code={lesson.code} />
              <div className="lesson-tip"><span>✦</span>{lesson.tip}</div>
            </article>
          ))}
        </div>

        {visibleLessons.length === 0 && <div className="empty-state">找不到相關章節，試試「函數」或「迴圈」。</div>}

        <section className="final-cta">
          <div><span className="section-label">YOUR TURN</span><h2>把下一個想法，<em>寫成程式。</em></h2><p>下載 EddieLang，開啟你的第一個 `.eddie` 檔案。</p></div>
          <code>eddie your-file.eddie <span>↗</span></code>
        </section>
        <footer><span>EDDIELANG / 教學實驗室</span><span>Made for curious minds · 2026</span></footer>
      </section>
    </main>
  );
}
