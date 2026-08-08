import { a as require_react, o as __toESM, t as require_jsx_runtime } from "../index.js";
//#region app/page.tsx
var import_react = /* @__PURE__ */ __toESM(require_react(), 1);
var import_jsx_runtime = require_jsx_runtime();
var lessons = [
	{
		id: "start",
		number: "01",
		title: "第一個程式",
		subtitle: "先讓電腦開口說話",
		description: "EddieLang 用中文關鍵字，把程式的第一步變得很直覺。",
		code: `說 "嗨，我是 EddieLang！"\n說 "今天開始學寫程式"`,
		tip: "說 後面可以放字串、變數或運算式。"
	},
	{
		id: "variables",
		number: "02",
		title: "變數與型別",
		subtitle: "替資料取一個名字",
		description: "用 設定 建立資料。int、float、str、bool 會告訴語言資料的型別。",
		code: `設定 str 名字 = "Eddie"\n設定 int 分數 = 100\n設定 bool 通過 = true\n說 名字`,
		tip: "變數建立後，可以用單一 = 更新內容。"
	},
	{
		id: "conditions",
		number: "03",
		title: "條件判斷",
		subtitle: "讓程式做出選擇",
		description: "如果、否則如果、否則會依照條件，選擇要執行的區塊。",
		code: `如果 分數 >= 60 {\n    說 "及格！"\n} 否則 {\n    說 "再試一次"\n}`,
		tip: "比較文字時記得加上引號，例如 難度 == \"簡單\"。"
	},
	{
		id: "loops",
		number: "04",
		title: "重複與迴圈",
		subtitle: "讓重複的事自動完成",
		description: "重複執行會一直執行到條件變成 false；重複則適合數固定次數。",
		code: `設定 int 次數 = 1\n重複 次數 從 1 到 3 {\n    說 次數\n}\n\n重複執行 次數 <= 5 {\n    次數 = 次數 + 1\n}`,
		tip: "在迴圈裡使用 停止 離開，使用 跳過 進入下一輪。"
	},
	{
		id: "functions",
		number: "05",
		title: "函數",
		subtitle: "把能力包裝起來重複使用",
		description: "函數可以接收參數，也可以用 回傳 把結果交回呼叫處。",
		code: `函數 相加(a, b) {\n    回傳 a + b\n}\n\n設定 int 結果 = 呼叫 相加(2, 3)\n說 結果`,
		tip: "函數參數用逗號分隔；區域變數只在函數裡使用。"
	},
	{
		id: "input",
		number: "06",
		title: "輸入與隨機",
		subtitle: "讓程式和使用者互動",
		description: "輸入 會讀取使用者內容，隨機(最小值, 最大值) 會產生包含上下限的整數。",
		code: `設定 int 最大值 = 100\n設定 int 猜測 = 輸入(\">>>\")\n設定 int 答案 = 隨機(0, 最大值)\n說 猜測`,
		tip: "輸入會依照變數型別自動轉成 int、float 或 bool。"
	}
];
function CodeBlock({ code }) {
	const [copied, setCopied] = (0, import_react.useState)(false);
	async function copyCode() {
		await navigator.clipboard?.writeText(code);
		setCopied(true);
		window.setTimeout(() => setCopied(false), 1500);
	}
	return /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
		className: "code-card",
		children: [/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
			className: "code-bar",
			children: [
				/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("span", {
					className: "traffic-lights",
					children: [
						/* @__PURE__ */ (0, import_jsx_runtime.jsx)("i", {}),
						/* @__PURE__ */ (0, import_jsx_runtime.jsx)("i", {}),
						/* @__PURE__ */ (0, import_jsx_runtime.jsx)("i", {})
					]
				}),
				/* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", { children: "main.eddie" }),
				/* @__PURE__ */ (0, import_jsx_runtime.jsx)("button", {
					onClick: copyCode,
					className: "copy-button",
					"aria-label": "複製程式碼",
					children: copied ? "已複製" : "複製"
				})
			]
		}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("pre", { children: /* @__PURE__ */ (0, import_jsx_runtime.jsx)("code", { children: code }) })]
	});
}
function Home() {
	const [activeId, setActiveId] = (0, import_react.useState)("start");
	const [query, setQuery] = (0, import_react.useState)("");
	const [completed, setCompleted] = (0, import_react.useState)([]);
	(0, import_react.useEffect)(() => {
		const saved = window.localStorage.getItem("eddielang-progress");
		if (saved) setCompleted(JSON.parse(saved));
	}, []);
	const visibleLessons = (0, import_react.useMemo)(() => {
		const keyword = query.trim().toLowerCase();
		if (!keyword) return lessons;
		return lessons.filter((lesson) => `${lesson.title} ${lesson.subtitle} ${lesson.description}`.toLowerCase().includes(keyword));
	}, [query]);
	lessons.find((lesson) => lesson.id === activeId) ?? lessons[0];
	const progress = Math.round(completed.length / lessons.length * 100);
	function toggleComplete(id) {
		const next = completed.includes(id) ? completed.filter((item) => item !== id) : [...completed, id];
		setCompleted(next);
		window.localStorage.setItem("eddielang-progress", JSON.stringify(next));
	}
	return /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("main", {
		className: "site-shell",
		children: [/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("aside", {
			className: "sidebar",
			children: [
				/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("a", {
					className: "brand",
					href: "#top",
					"aria-label": "EddieLang 教學首頁",
					children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", {
						className: "brand-mark",
						children: "E"
					}), /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("span", { children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("strong", { children: "EddieLang" }), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("small", { children: "中文程式語言" })] })]
				}),
				/* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
					className: "sidebar-label",
					children: "學習路線"
				}),
				/* @__PURE__ */ (0, import_jsx_runtime.jsx)("nav", {
					className: "lesson-nav",
					"aria-label": "課程章節",
					children: lessons.map((lesson) => /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("button", {
						className: activeId === lesson.id ? "lesson-link active" : "lesson-link",
						onClick: () => {
							setActiveId(lesson.id);
							document.getElementById(lesson.id)?.scrollIntoView({ behavior: "smooth" });
						},
						children: [
							/* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", {
								className: "lesson-number",
								children: lesson.number
							}),
							/* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", { children: lesson.title }),
							completed.includes(lesson.id) && /* @__PURE__ */ (0, import_jsx_runtime.jsx)("b", {
								"aria-label": "已完成",
								children: "✓"
							})
						]
					}, lesson.id))
				}),
				/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
					className: "progress-card",
					children: [
						/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
							className: "progress-heading",
							children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", { children: "學習進度" }), /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("strong", { children: [progress, "%"] })]
						}),
						/* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
							className: "progress-track",
							children: /* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", { style: { width: `${progress}%` } })
						}),
						/* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", { children: completed.length === lessons.length ? "太棒了，全部完成！" : "每天學一點，寫出自己的程式。" })
					]
				}),
				/* @__PURE__ */ (0, import_jsx_runtime.jsx)("a", {
					className: "github-link",
					href: "https://github.com",
					target: "_blank",
					rel: "noreferrer",
					children: "↗ 查看專案"
				})
			]
		}), /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("section", {
			className: "content",
			id: "top",
			children: [
				/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("header", {
					className: "topbar",
					children: [/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("span", {
						className: "eyebrow",
						children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", { className: "status-dot" }), "互動式學習指南"]
					}), /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("label", {
						className: "search-box",
						children: [
							/* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", { children: "⌕" }),
							/* @__PURE__ */ (0, import_jsx_runtime.jsx)("input", {
								value: query,
								onChange: (event) => setQuery(event.target.value),
								placeholder: "搜尋章節或概念...",
								"aria-label": "搜尋章節"
							}),
							/* @__PURE__ */ (0, import_jsx_runtime.jsx)("kbd", { children: "⌘ K" })
						]
					})]
				}),
				/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
					className: "hero",
					children: [/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
						className: "hero-copy",
						children: [
							/* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
								className: "hero-kicker",
								children: "WELCOME TO THE LANGUAGE LAB"
							}),
							/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("h1", { children: [
								"用中文，寫出",
								/* @__PURE__ */ (0, import_jsx_runtime.jsx)("br", {}),
								/* @__PURE__ */ (0, import_jsx_runtime.jsx)("em", { children: "你的第一個程式。" })
							] }),
							/* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
								className: "hero-lede",
								children: "EddieLang 是一門為初學者設計的中文程式語言。從「說」開始，逐步學會讓想法動起來。"
							}),
							/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
								className: "hero-actions",
								children: [/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("button", {
									className: "primary-button",
									onClick: () => document.getElementById("start")?.scrollIntoView({ behavior: "smooth" }),
									children: ["開始學習 ", /* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", { children: "↓" })]
								}), /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("span", {
									className: "lesson-count",
									children: [
										lessons.length,
										" 個核心章節 ",
										/* @__PURE__ */ (0, import_jsx_runtime.jsx)("i", { children: "·" }),
										" 約 20 分鐘"
									]
								})]
							})
						]
					}), /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
						className: "hero-terminal",
						"aria-label": "EddieLang 程式預覽",
						children: [/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
							className: "terminal-top",
							children: [
								/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("span", {
									className: "traffic-lights",
									children: [
										/* @__PURE__ */ (0, import_jsx_runtime.jsx)("i", {}),
										/* @__PURE__ */ (0, import_jsx_runtime.jsx)("i", {}),
										/* @__PURE__ */ (0, import_jsx_runtime.jsx)("i", {})
									]
								}),
								/* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", { children: "hello.eddie" }),
								/* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", {
									className: "terminal-live",
									children: "● LIVE"
								})
							]
						}), /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
							className: "terminal-code",
							children: [
								/* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", {
									className: "line-no",
									children: "01"
								}),
								/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("span", { children: [
									/* @__PURE__ */ (0, import_jsx_runtime.jsx)("b", {
										className: "pink",
										children: "說"
									}),
									" ",
									/* @__PURE__ */ (0, import_jsx_runtime.jsx)("strong", { children: "\"你好，世界！\"" })
								] }),
								/* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", {
									className: "line-no",
									children: "02"
								}),
								/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("span", { children: [
									/* @__PURE__ */ (0, import_jsx_runtime.jsx)("b", {
										className: "pink",
										children: "說"
									}),
									" ",
									/* @__PURE__ */ (0, import_jsx_runtime.jsx)("strong", { children: "\"準備好了嗎？\"" })
								] }),
								/* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", {
									className: "line-no",
									children: "03"
								}),
								/* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", {
									className: "terminal-output",
									children: "你好，世界！"
								}),
								/* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", {
									className: "line-no",
									children: "04"
								}),
								/* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", {
									className: "terminal-output",
									children: "準備好了嗎？"
								}),
								/* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", {
									className: "cursor",
									children: "▌"
								})
							]
						})]
					})]
				}),
				/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
					className: "section-intro",
					children: [
						/* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", {
							className: "section-label",
							children: "THE BASICS"
						}),
						/* @__PURE__ */ (0, import_jsx_runtime.jsx)("h2", { children: "從想法，到執行。" }),
						/* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", { children: "每個章節都用一個小概念，帶你看懂程式如何一步步完成任務。" })
					]
				}),
				/* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
					className: "lesson-grid",
					children: visibleLessons.map((lesson) => /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("article", {
						className: `lesson-card ${activeId === lesson.id ? "selected" : ""}`,
						id: lesson.id,
						onClick: () => setActiveId(lesson.id),
						children: [
							/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
								className: "lesson-card-heading",
								children: [/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("span", {
									className: "chapter-tag",
									children: ["CHAPTER ", lesson.number]
								}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("button", {
									className: completed.includes(lesson.id) ? "check checked" : "check",
									onClick: (event) => {
										event.stopPropagation();
										toggleComplete(lesson.id);
									},
									"aria-label": "標記章節完成",
									children: completed.includes(lesson.id) ? "✓" : "○"
								})]
							}),
							/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("h3", { children: [lesson.title, /* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", { children: lesson.subtitle })] }),
							/* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", { children: lesson.description }),
							/* @__PURE__ */ (0, import_jsx_runtime.jsx)(CodeBlock, { code: lesson.code }),
							/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
								className: "lesson-tip",
								children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", { children: "✦" }), lesson.tip]
							})
						]
					}, lesson.id))
				}),
				visibleLessons.length === 0 && /* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
					className: "empty-state",
					children: "找不到相關章節，試試「函數」或「迴圈」。"
				}),
				/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("section", {
					className: "final-cta",
					children: [/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", { children: [
						/* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", {
							className: "section-label",
							children: "YOUR TURN"
						}),
						/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("h2", { children: ["把下一個想法，", /* @__PURE__ */ (0, import_jsx_runtime.jsx)("em", { children: "寫成程式。" })] }),
						/* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", { children: "下載 EddieLang，開啟你的第一個 `.eddie` 檔案。" })
					] }), /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("code", { children: ["eddie your-file.eddie ", /* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", { children: "↗" })] })]
				}),
				/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("footer", { children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", { children: "EDDIELANG / 教學實驗室" }), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", { children: "Made for curious minds · 2026" })] })
			]
		})]
	});
}
//#endregion
export { Home as default };
