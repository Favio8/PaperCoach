const $ = (selector, root = document) => root.querySelector(selector);
const $$ = (selector, root = document) => Array.from(root.querySelectorAll(selector));

const stageOrder = ["背景", "问题", "核心想法", "系统架构", "方法", "实验", "结果", "局限", "思考"];

const stageContent = {
  背景: {
    goal: "建立论文研究背景，判断这篇论文为什么值得精读。",
    read: "标题、摘要和 Introduction 前半部分",
    focus: "论文在做什么、为什么重要、属于哪个 Agent 子方向",
    questions: [
      "这篇论文在做什么？请用一句话回答。",
      "它为什么重要？请指出具体研究缺口。",
      "它和 Agent 哪个子方向最相关？证据在哪里？",
      "它相对已有工作的关键变化是什么？",
    ],
    facts: [
      "序列转导任务通常使用编码器-解码器结构。",
      "注意力机制已经被用于连接编码器和解码器。",
      "机器翻译是论文中最核心的验证场景之一。",
    ],
    understanding: ["这篇论文的出发点不是发明注意力，而是重新组织整个序列建模架构。"],
    questionsWorth: ["注意力机制为什么可以从辅助模块变成核心架构？"],
  },
  问题: {
    goal: "理解现有论文阅读工具没有解决的问题。",
    read: "引言第 2-4 段，以及图 1",
    focus: "现有摘要工具的局限",
    questions: [
      "现有工具没有解决的核心问题是什么？",
      "论文中哪些证据支持这个判断？",
      "PaperCoach 和普通 PDF 问答工具有什么不同？",
    ],
    facts: [
      "现有方法基于编码器-解码器框架并使用注意力机制。",
      "循环模型存在固有的顺序计算限制，影响长序列训练。",
      "Transformer 仅基于注意力，完全移除了循环和卷积。",
    ],
    understanding: [
      "核心问题是：RNN 的顺序计算限制导致训练效率低，特别是在长序列上。",
      "作者通过注意力机制的全局视角替代方案来解决该问题。",
    ],
    questionsWorth: [
      "仅用注意力机制如何建模序列的位置信息？",
      "在长序列任务上，训练效率提升的具体表现如何？",
      "该架构在其他任务上的泛化能力如何？",
    ],
  },
  核心想法: {
    goal: "抓住 Transformer 的核心创新：完全基于注意力的序列建模。",
    read: "引言最后 2 段，以及模型概览",
    focus: "用自注意力替代循环和卷积",
    questions: [
      "Transformer 的关键想法和传统 RNN 最大差异是什么？",
      "为什么作者认为 attention alone 是可行的？",
      "这个想法解决了 Problem 阶段里的哪个限制？",
    ],
    facts: [
      "Transformer 基于 self-attention 处理序列内部依赖。",
      "模型不再依赖 recurrence 或 convolution。",
      "并行化能力是作者强调的重要优势。",
    ],
    understanding: ["核心想法是把注意力从局部模块提升为整个架构的组织原则。"],
    questionsWorth: ["完全移除循环结构后，顺序信息如何被保留？"],
  },
  系统架构: {
    goal: "理解编码器、解码器、多头注意力和前馈网络之间如何协作。",
    read: "模型结构部分，以及图 1",
    focus: "Transformer 的模块关系和信息流",
    questions: [
      "图 1 中编码器和解码器分别包含哪些关键模块？",
      "Multi-Head Attention 出现在哪些位置？",
      "Add & Norm 在整体结构中起什么作用？",
    ],
    facts: [
      "模型由堆叠的编码器和解码器组成。",
      "每层包含注意力、前馈网络、残差连接和归一化。",
      "解码器额外使用 masked self-attention。",
    ],
    understanding: ["架构的重点是稳定地堆叠注意力模块，并保留可训练性。"],
    questionsWorth: ["残差连接和归一化对深层注意力模型有多关键？"],
  },
  方法: {
    goal: "理解 scaled dot-product attention 与 multi-head attention 的机制。",
    read: "方法第 3.2-3.3 节",
    focus: "注意力计算流程和多头机制",
    questions: [
      "Scaled dot-product attention 的输入和输出是什么？",
      "为什么需要除以 sqrt(d_k)？",
      "多头注意力相比单头注意力提供了什么能力？",
    ],
    facts: [
      "注意力由 Query、Key、Value 计算得到。",
      "缩放项用于缓解维度较大时 softmax 梯度变小的问题。",
      "多头机制允许模型从不同表示子空间关注信息。",
    ],
    understanding: ["方法的关键在于让模型同时学习多种关系，而不是只看单一相似度。"],
    questionsWorth: ["不同注意力头是否真的学习到了不同语言结构？"],
  },
  实验: {
    goal: "判断实验设置是否足以支撑 Transformer 的核心 claim。",
    read: "实验设置和训练细节",
    focus: "数据集、baseline、指标和训练成本",
    questions: [
      "论文用哪些任务验证模型效果？",
      "baseline 是否足以说明 Transformer 的优势？",
      "实验指标如何同时体现质量和效率？",
    ],
    facts: [
      "论文主要在机器翻译任务上实验。",
      "使用 BLEU 等指标衡量翻译质量。",
      "作者比较了训练成本和模型质量。",
    ],
    understanding: ["实验不仅证明效果，也在证明并行训练带来的效率收益。"],
    questionsWorth: ["如果换成非翻译任务，实验结论是否仍然成立？"],
  },
  结果: {
    goal: "理解结果如何支持论文贡献，以及哪些地方仍需谨慎。",
    read: "结果表格和分析段落",
    focus: "性能提升、训练效率和证据强度",
    questions: [
      "哪个结果最直接支持 Transformer 的核心贡献？",
      "结果是否同时展示了质量和效率提升？",
      "有哪些结果还不能完全说明泛化能力？",
    ],
    facts: [
      "Transformer 在机器翻译任务上取得强竞争结果。",
      "论文强调更少训练成本下的高质量表现。",
      "结果集中于特定任务和数据集。",
    ],
    understanding: ["最强证据来自质量和效率同时提升，而不是单一分数更高。"],
    questionsWorth: ["训练效率优势在更大模型规模下是否会继续保持？"],
  },
  局限: {
    goal: "识别论文没有覆盖的边界、失败场景和后续风险。",
    read: "讨论、结论和实验边界",
    focus: "任务范围、数据规模和未验证场景",
    questions: [
      "论文最明显的实验边界是什么？",
      "方法局限更来自任务设定还是模型机制？",
      "哪些结论需要后续工作继续验证？",
    ],
    facts: [
      "论文实验主要围绕机器翻译展开。",
      "对更广泛任务的泛化需要后续验证。",
      "位置编码设计仍可能影响长序列能力。",
    ],
    understanding: ["局限不是模型无效，而是证据主要集中在特定任务上。"],
    questionsWorth: ["长上下文建模是否需要新的位置机制？"],
  },
  思考: {
    goal: "沉淀自己的评价、延伸问题和可复现实验想法。",
    read: "全文关键标注和阶段笔记",
    focus: "研究地图、复现实验和后续阅读",
    questions: [
      "这篇论文对后续 LLM 架构产生了什么影响？",
      "如果写博客，最应该强调哪条主线？",
      "你会设计什么复现实验来加深理解？",
    ],
    facts: [
      "Transformer 后续成为大规模语言模型的重要基础。",
      "注意力机制、并行化和可扩展性构成论文主线。",
      "复现实验可以从小型翻译或序列任务开始。",
    ],
    understanding: ["这篇论文的长期价值在于提出了一种更适合扩展的序列建模范式。"],
    questionsWorth: ["从 Transformer 到现代 LLM，中间最关键的工程变化是什么？"],
  },
};

const state = {
  stage: "背景",
  page: 1,
  totalPages: 15,
  zoom: 100,
  continuousMode: true,
  selectedQuestionIndex: 0,
  sideTab: "coach",
  paper: null,
  sessionId: null,
  sessionPaperId: null,
  apiQuestionsByStage: {},
  navigationRequests: {},
  dynamicStageContent: {},
};

const LAYOUT_STORAGE_KEY = "papercoach.layout.v5";
const NOTES_STORAGE_KEY_PREFIX = "papercoach.stageNotes.v1";
const DEFAULT_LAYOUT = {
  leftWidth: 250,
  rightWidth: 380,
  readerFocus: false,
  sideTab: "coach",
};

const layoutState = {
  ...DEFAULT_LAYOUT,
};

const stageSectionHints = {
  背景: ["Abstract", "Introduction"],
  问题: ["Introduction", "Problem", "Motivation"],
  核心想法: ["Method", "Introduction", "Abstract"],
  系统架构: ["Method", "Architecture", "System", "VOYAGER Algorithm"],
  方法: ["Automatic Curriculum", "Skill Library", "Iterative Prompting Mechanism", "Method"],
  实验: ["Experimental Setup", "Baselines", "Experiments"],
  结果: ["Evaluation Results", "Ablation Studies", "Results"],
  局限: ["Limitations and Future Work", "Limitations", "Discussion", "Conclusion"],
  思考: ["Conclusion", "Limitations and Future Work", "Related Work"],
};

const stageEvidenceHints = {
  核心想法: [{ type: "figure", terms: ["figure 2"] }],
  系统架构: [{ type: "figure", terms: ["figure 2"] }],
  方法: [
    { type: "figure", terms: ["figure 3"] },
    { type: "figure", terms: ["figure 4"] },
    { type: "figure", terms: ["figure 5"] },
    { type: "figure", terms: ["figure 6"] },
  ],
  实验: [
    { type: "table", terms: ["table 1"] },
    { type: "table", terms: ["table 2"] },
  ],
  结果: [
    { type: "table", terms: ["table 1"] },
    { type: "table", terms: ["table 2"] },
    { type: "figure", terms: ["figure 9"] },
  ],
};

const stageFocusByPaper = {
  背景: "论文研究场景、任务背景和作者的动机",
  问题: "作者指出的核心挑战与已有方法不足",
  核心想法: "论文提出的新机制和关键组件",
  系统架构: "系统模块、信息流和图表结构",
  方法: "方法细节、输入输出和执行流程",
  实验: "实验设置、评估指标和对照方法",
  结果: "结果证据、性能提升和结论强度",
  局限: "方法边界、失败场景和未验证部分",
  思考: "自己的评价、复现计划和后续阅读问题",
};

const stageApiNames = {
  背景: "Background",
  问题: "Problem",
  核心想法: "Key Idea",
  系统架构: "Architecture",
  方法: "Method",
  实验: "Experiments",
  结果: "Results",
  局限: "Limitations",
  思考: "Thoughts",
};

const apiStageLabels = Object.fromEntries(
  Object.entries(stageApiNames).map(([label, apiName]) => [apiName, label]),
);

function showToast(message) {
  const region = $(".toast-region");
  if (!region) return;
  region.replaceChildren();
  const toast = document.createElement("div");
  toast.className = "toast";
  toast.textContent = message;
  region.appendChild(toast);
  window.clearTimeout(region.toastTimer);
  region.toastTimer = window.setTimeout(() => {
    toast.remove();
  }, 2600);
}

function restoreLayout() {
  const saved = readSavedLayout();
  if (saved) {
    layoutState.leftWidth = saved.leftWidth ?? layoutState.leftWidth;
    layoutState.rightWidth = saved.rightWidth ?? layoutState.rightWidth;
    layoutState.readerFocus = saved.readerFocus ?? layoutState.readerFocus;
    layoutState.sideTab = saved.sideTab ?? layoutState.sideTab;
  }
  state.sideTab = layoutState.sideTab;
  clampLayoutToViewport();
  applyLayout();
}

function readSavedLayout() {
  try {
    const raw = window.localStorage.getItem(LAYOUT_STORAGE_KEY);
    return raw ? JSON.parse(raw) : null;
  } catch (_error) {
    return null;
  }
}

function saveLayout() {
  window.localStorage.setItem(LAYOUT_STORAGE_KEY, JSON.stringify(layoutState));
}

function applyLayout() {
  document.documentElement.style.setProperty("--left-pane-width", `${layoutState.leftWidth}px`);
  document.documentElement.style.setProperty("--right-pane-width", `${layoutState.rightWidth}px`);

  const workspace = $(".workspace");
  workspace?.classList.toggle("is-reading-focus", layoutState.readerFocus);

  $$(".coach-tab").forEach((button) => {
    const active = button.dataset.sideTab === state.sideTab;
    button.classList.toggle("is-active", active);
    button.setAttribute("aria-selected", String(active));
  });
  $$(".coach-tab-panel").forEach((panel) => {
    panel.classList.toggle("is-active", panel.dataset.tabPanel === state.sideTab);
  });

  const draftButton = $(".toggle-draft-button");
  if (draftButton) {
    draftButton.textContent = "笔记";
    draftButton.classList.toggle("is-active", state.sideTab === "notes");
  }

  const focusButton = $(".focus-reader-button");
  if (focusButton) {
    focusButton.textContent = layoutState.readerFocus ? "退出专注" : "专注阅读";
    focusButton.classList.toggle("is-active", layoutState.readerFocus);
  }
}

function setSideTab(tabName, options = {}) {
  state.sideTab = tabName === "notes" ? "notes" : "coach";
  layoutState.sideTab = state.sideTab;
  applyLayout();
  if (options.save !== false) saveLayout();
}

function clamp(value, min, max) {
  return Math.max(min, Math.min(max, value));
}

function centerMinWidth() {
  return window.matchMedia("(max-width: 1320px)").matches ? 650 : 760;
}

function workspaceTrackWidth(workspace) {
  const rect = workspace.getBoundingClientRect();
  const style = window.getComputedStyle(workspace);
  const padding = parseFloat(style.paddingLeft) + parseFloat(style.paddingRight);
  const columnGap = parseFloat(style.columnGap || style.gap) || 0;
  const resizers = 16;
  const gaps = columnGap * 4;
  const safetyBuffer = 24;
  return rect.width - padding - resizers - gaps - safetyBuffer;
}

function clampLayoutToViewport() {
  const workspace = $(".workspace");
  if (workspace) {
    const availableForPanes = workspaceTrackWidth(workspace) - centerMinWidth();
    layoutState.leftWidth = clamp(layoutState.leftWidth, 190, 460);
    layoutState.rightWidth = clamp(layoutState.rightWidth, 280, 560);

    if (availableForPanes > 0) {
      const minPaneSum = 190 + 280;
      const targetPaneSum = Math.max(minPaneSum, availableForPanes);
      if (layoutState.leftWidth + layoutState.rightWidth > targetPaneSum) {
        const overflow = layoutState.leftWidth + layoutState.rightWidth - targetPaneSum;
        const rightReduction = Math.min(overflow, Math.max(0, layoutState.rightWidth - 280));
        layoutState.rightWidth -= rightReduction;
        layoutState.leftWidth = clamp(layoutState.leftWidth - (overflow - rightReduction), 190, 460);
      }
    }
  }

  return;
}

function resetLayout() {
  Object.assign(layoutState, DEFAULT_LAYOUT);
  state.sideTab = layoutState.sideTab;
  clampLayoutToViewport();
  applyLayout();
  saveLayout();
}

function setupResizablePanes() {
  const workspace = $(".workspace");
  const leftResizer = $(".left-pane-resizer");
  const rightResizer = $(".right-pane-resizer");

  if (leftResizer && workspace) {
    makePointerDrag(leftResizer, {
      cursor: "col-resize",
      onMove: (event) => {
        const rect = workspace.getBoundingClientRect();
        const style = window.getComputedStyle(workspace);
        const paddingLeft = parseFloat(style.paddingLeft);
        const available = workspaceTrackWidth(workspace) - layoutState.rightWidth - centerMinWidth();
        const maxWidth = Math.max(190, Math.min(460, available));
        layoutState.leftWidth = clamp(event.clientX - rect.left - paddingLeft, 190, maxWidth);
        applyLayout();
      },
      onEnd: saveLayout,
      onReset: () => {
        layoutState.leftWidth = DEFAULT_LAYOUT.leftWidth;
        clampLayoutToViewport();
        applyLayout();
        saveLayout();
      },
    });
  }

  if (rightResizer && workspace) {
    makePointerDrag(rightResizer, {
      cursor: "col-resize",
      onMove: (event) => {
        const rect = workspace.getBoundingClientRect();
        const style = window.getComputedStyle(workspace);
        const paddingRight = parseFloat(style.paddingRight);
        const available = workspaceTrackWidth(workspace) - layoutState.leftWidth - centerMinWidth();
        const maxWidth = Math.max(280, Math.min(560, available));
        layoutState.rightWidth = clamp(rect.right - paddingRight - event.clientX, 280, maxWidth);
        applyLayout();
      },
      onEnd: saveLayout,
      onReset: () => {
        layoutState.rightWidth = DEFAULT_LAYOUT.rightWidth;
        clampLayoutToViewport();
        applyLayout();
        saveLayout();
      },
    });
  }

}

function makePointerDrag(handle, options) {
  handle.addEventListener("pointerdown", (event) => {
    event.preventDefault();
    const previousCursor = document.body.style.cursor;
    document.body.style.cursor = options.cursor || "";
    document.body.classList.add("is-resizing");
    const onMove = (moveEvent) => options.onMove(moveEvent);
    const onUp = () => {
      document.removeEventListener("pointermove", onMove);
      document.removeEventListener("pointerup", onUp);
      document.removeEventListener("pointercancel", onUp);
      document.body.classList.remove("is-resizing");
      document.body.style.cursor = previousCursor;
      options.onEnd?.();
    };
    document.addEventListener("pointermove", onMove);
    document.addEventListener("pointerup", onUp, { once: true });
    document.addEventListener("pointercancel", onUp, { once: true });
  });

  handle.addEventListener("dblclick", () => {
    options.onReset?.();
  });
}

function setBusy(button, label, callback) {
  if (!button) return;
  const original = button.innerHTML;
  button.disabled = true;
  button.textContent = label;
  Promise.resolve(callback())
    .catch((error) => showToast(error.message || "操作失败"))
    .finally(() => {
      button.disabled = false;
      button.innerHTML = original;
    });
}

function getStageContent(stageLabel) {
  return state.dynamicStageContent[stageLabel] || stageContent[stageLabel] || stageContent["问题"];
}

function stageApiName(stageLabel) {
  return stageApiNames[stageLabel] || stageLabel;
}

function stageLabelFromApi(apiStage) {
  return apiStageLabels[apiStage] || apiStage;
}

function notesStorageKey(paper = state.paper) {
  return `${NOTES_STORAGE_KEY_PREFIX}:${paper?.paper_id || "demo"}`;
}

function readSavedStageNotes(paper = state.paper) {
  try {
    const raw = window.localStorage.getItem(notesStorageKey(paper));
    if (!raw) return {};
    const parsed = JSON.parse(raw);
    return parsed && typeof parsed === "object" ? parsed : {};
  } catch (_error) {
    return {};
  }
}

function mergeStageNotes(generatedContent, savedNotes) {
  return Object.fromEntries(
    stageOrder.map((stageLabel) => {
      const generated = generatedContent[stageLabel] || stageContent[stageLabel] || {};
      const saved = savedNotes?.[stageLabel] || {};
      return [
        stageLabel,
        {
          ...generated,
          facts: normalizeNoteList(saved.facts, generated.facts),
          understanding: normalizeNoteList(saved.understanding, generated.understanding),
          questionsWorth: normalizeNoteList(saved.questionsWorth, generated.questionsWorth),
        },
      ];
    }),
  );
}

function normalizeNoteList(value, fallback = []) {
  if (Array.isArray(value)) {
    return value.map((item) => String(item).trim()).filter(Boolean);
  }
  if (typeof value === "string") {
    return value
      .split(/\n+/)
      .map((item) => item.trim())
      .filter(Boolean);
  }
  return fallback || [];
}

function saveStageNotes(statusText = "已自动保存") {
  try {
    window.localStorage.setItem(notesStorageKey(), JSON.stringify(state.dynamicStageContent));
    updateDraftStatus(`${state.stage} · ${statusText}`);
  } catch (_error) {
    updateDraftStatus(`${state.stage} · 本地保存失败`);
  }
}

function updateDraftStatus(text) {
  const status = $(".draft-status");
  if (status) status.textContent = text;
}

async function loadInitialPaper() {
  try {
    const response = await fetch("/api/papers");
    if (!response.ok) return;
    const papers = await response.json();
    if (!Array.isArray(papers) || papers.length === 0) return;
    const paper = papers.find((item) => item.paper_id === "paper_voyager") || papers[papers.length - 1];
    hydratePaper(paper);
    showToast(`已加载论文：${paper.title}`);
  } catch (_error) {
    // Keep the static demo data if the API is unavailable.
  }
}

async function createReadingSession(paperId) {
  if (!paperId) return null;
  if (state.sessionId && state.sessionPaperId === paperId) return state.sessionId;

  state.sessionId = null;
  state.sessionPaperId = paperId;
  state.apiQuestionsByStage = {};
  state.navigationRequests = {};

  try {
    const response = await fetch("/api/sessions", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ paper_id: paperId }),
    });
    if (!response.ok) throw new Error("AI 会话创建失败");
    const payload = await response.json();
    state.sessionId = payload.session_id;
    requestStageNavigation(state.stage, { silent: true, force: true });
    return state.sessionId;
  } catch (error) {
    showToast(error.message || "AI 会话创建失败，暂时使用本地阅读导航");
    return null;
  }
}

async function ensureReadingSession() {
  if (!state.paper?.paper_id) return null;
  return createReadingSession(state.paper.paper_id);
}

function hydratePaper(paper) {
  state.paper = paper;
  state.totalPages = inferTotalPages(paper);
  state.page = Math.min(Math.max(firstReadablePage(paper), 1), state.totalPages);
  state.dynamicStageContent = mergeStageNotes(buildPaperStageContent(paper), readSavedStageNotes(paper));
  state.sessionId = null;
  state.sessionPaperId = null;
  state.apiQuestionsByStage = {};
  state.navigationRequests = {};

  $(".paper-title").textContent = paper.title || "未命名论文";
  $(".meta-card h3").textContent = paper.title || "未命名论文";

  const authorNode = $(".paper-authors");
  if (authorNode) {
    authorNode.textContent =
      paper.authors && paper.authors.length > 0 ? paper.authors.join(", ") : "未识别作者";
  }

  const sectionCount = $(".parsed-sections");
  if (sectionCount) sectionCount.textContent = `${paper.sections?.length || 0} / ${paper.sections?.length || 0}`;

  const pageCount = $(".paper-pages");
  if (pageCount) pageCount.textContent = String(state.totalPages);

  renderStage(state.stage);
  updateReader();
  createReadingSession(paper.paper_id);
}

function buildPaperStageContent(paper) {
  return Object.fromEntries(
    stageOrder.map((stageLabel) => {
      const readingPlan = buildStageReadingPlan(paper, stageLabel);
      const section = readingPlan.primarySection;
      const sectionLabel = readingPlan.label;
      const evidenceText = section?.content || paper.abstract || "";
      const facts = splitEvidenceSentences(evidenceText).slice(0, 3);
      const fallbackFacts = splitEvidenceSentences(paper.abstract || "").slice(0, 3);
      return [
        stageLabel,
        {
          goal: paperStageGoal(stageLabel, paper.title),
          read: sectionLabel,
          focus: stageFocusByPaper[stageLabel],
          questions: paperStageQuestions(stageLabel, paper.title, sectionLabel),
          facts: facts.length > 0 ? facts : fallbackFacts,
          understanding: [`这里等待你基于 ${sectionLabel} 写下自己的理解。`],
          questionsWorth: paperStageFollowups(stageLabel, paper.title),
        },
      ];
    }),
  );
}

function paperStageGoal(stageLabel, title) {
  const goals = {
    背景: "阅读本论文的研究背景，判断它为什么值得精读。",
    问题: "阅读本论文的核心问题，理解作者要解决什么。",
    核心想法: "阅读本论文的核心想法，抓住关键贡献。",
    系统架构: "阅读本论文的系统架构，理解模块关系。",
    方法: "阅读本论文的方法部分，拆解关键机制。",
    实验: "阅读本论文的实验设置，判断验证是否充分。",
    结果: "阅读本论文的结果证据，判断结论强弱。",
    局限: "阅读本论文的局限讨论，识别适用边界。",
    思考: "整理本论文的个人思考，形成后续问题。",
  };
  return goals[stageLabel] || goals["问题"];
}

function paperStageQuestions(stageLabel, title, sectionLabel) {
  const name = title || "这篇论文";
  const questions = {
    背景: [
      `从 ${sectionLabel} 看，${name} 面向什么研究场景？`,
      "作者为什么认为这个问题值得研究？",
      "你能找出一句最能概括研究背景的原文证据吗？",
    ],
    问题: [
      `从 ${sectionLabel} 看，作者认为现有方法的核心不足是什么？`,
      "这个不足为什么会影响 agent 的长期学习或任务完成？",
      "哪一句原文最能支撑你对问题的判断？",
    ],
    核心想法: [
      `根据 ${sectionLabel}，论文提出了哪些关键组件？`,
      "这些组件之间如何相互支撑，而不是孤立工作？",
      "这个想法和普通 LLM agent 的差异在哪里？",
    ],
    系统架构: [
      `从 ${sectionLabel} 看，系统由哪些模块组成？`,
      "信息或控制流在这些模块之间如何流动？",
      "哪张图或哪段描述最能说明整体架构？",
    ],
    方法: [
      `回到 ${sectionLabel}，方法执行流程的关键步骤是什么？`,
      "其中哪一步最容易失败，作者如何处理反馈或错误？",
      "这个方法如何把短期行为沉淀为长期能力？",
    ],
    实验: [
      `从 ${sectionLabel} 看，实验主要验证哪些 claim？`,
      "baseline 和指标是否足以说明论文方法有效？",
      "你认为最强的实验证据是哪一个？",
    ],
    结果: [
      `根据 ${sectionLabel}，哪个结果最支持论文贡献？`,
      "结果中是否存在需要谨慎解释的地方？",
      "这些结果能否证明方法具备泛化能力？",
    ],
    局限: [
      `从 ${sectionLabel} 看，论文最明显的边界是什么？`,
      "局限主要来自环境、模型能力，还是实验设计？",
      "如果继续做，你会优先补哪个实验？",
    ],
    思考: [
      `读完 ${name} 后，你会把它归入 Agent 研究的哪个方向？`,
      "这篇论文对你自己的项目有什么可迁移的设计？",
      "你会如何设计一篇博客来讲清楚它的贡献？",
    ],
  };
  return questions[stageLabel] || questions["问题"];
}

function paperStageFollowups(stageLabel, title) {
  const name = title || "这篇论文";
  return [
    `如果要复现《${name}》，最小可行实验是什么？`,
    "论文中的证据是否足以支撑作者最强的 claim？",
    "这个方法迁移到非论文任务时可能会遇到什么限制？",
  ];
}

function pickSectionForStage(paper, stageLabel) {
  return buildStageReadingPlan(paper, stageLabel).primarySection;
}

function buildStageReadingPlan(paper, stageLabel) {
  const sections = pickSectionsForStage(paper, stageLabel);
  const evidence = pickEvidenceForStage(paper, stageLabel);
  const primarySection = sections[0] || firstReadableSection(paper);
  const primaryPage =
    evidenceFirstStages().has(stageLabel) && evidence?.page
      ? evidence.page
      : primarySection?.page_start || evidence?.page || 1;

  return {
    sections,
    evidence,
    primarySection,
    primaryPage,
    label: formatReadingPlanLabel(sections, evidence),
  };
}

function pickSectionsForStage(paper, stageLabel) {
  const sections = (paper.sections || []).filter(isReaderSection);
  const hints = stageSectionHints[stageLabel] || [];
  const selected = [];

  for (const hint of hints) {
    const found = findSectionByHint(sections, hint, selected);
    if (found) selected.push(found);
    if (selected.length >= maxSectionsForStage(stageLabel)) break;
  }

  if (selected.length > 0) return selected;
  const fallback = firstReadableSection(paper);
  return fallback ? [fallback] : [];
}

function findSectionByHint(sections, hint, selected) {
  const normalizedHint = normalizeSectionTitle(hint);
  const isSelected = (section) => selected.some((item) => item.id === section.id);
  const exact = sections.find(
    (section) => !isSelected(section) && normalizeSectionTitle(section.title) === normalizedHint,
  );
  if (exact) return exact;
  return sections.find(
    (section) =>
      !isSelected(section) && normalizeSectionTitle(section.title).includes(normalizedHint),
  );
}

function normalizeSectionTitle(value = "") {
  return value
    .toLowerCase()
    .replace(/[^a-z0-9\u4e00-\u9fff]+/g, " ")
    .trim();
}

function isReaderSection(section) {
  const title = normalizeSectionTitle(section.title);
  return !["references", "acknowledgements", "broader impacts"].includes(title);
}

function firstReadableSection(paper) {
  return (paper.sections || []).find(isReaderSection) || null;
}

function maxSectionsForStage(stageLabel) {
  if (stageLabel === "方法") return 3;
  if (stageLabel === "实验") return 2;
  return 1;
}

function pickEvidenceForStage(paper, stageLabel) {
  const hints = stageEvidenceHints[stageLabel] || [];
  for (const hint of hints) {
    const pool = hint.type === "table" ? paper.tables || [] : paper.figures || [];
    const found = pool.find((item) => {
      const caption = (item.caption || "").toLowerCase();
      return hint.terms.every((term) => caption.includes(term.toLowerCase()));
    });
    if (found) return { ...found, type: hint.type };
  }
  return null;
}

function evidenceFirstStages() {
  return new Set(["核心想法", "系统架构"]);
}

function formatReadingPlanLabel(sections, evidence) {
  const sectionLabel = formatSectionGroupLocation(sections);
  const evidenceLabel = formatEvidenceLocation(evidence);
  if (sectionLabel && evidenceLabel) return `${sectionLabel}；重点看 ${evidenceLabel}`;
  return sectionLabel || evidenceLabel || "论文相关章节";
}

function formatSectionGroupLocation(sections) {
  if (!sections || sections.length === 0) return "";
  if (sections.length === 1) return formatSectionLocation(sections[0]);

  const titles = sections.map((section) => section.title).join(" / ");
  const pages = sections
    .flatMap((section) => [section.page_start, section.page_end])
    .filter(Boolean);
  const start = Math.min(...pages);
  const end = Math.max(...pages);
  if (Number.isFinite(start) && Number.isFinite(end) && start !== end) {
    return `${titles} 第 ${start}-${end} 页`;
  }
  if (Number.isFinite(start)) return `${titles} 第 ${start} 页`;
  return titles;
}

function formatEvidenceLocation(evidence) {
  if (!evidence) return "";
  const label = extractEvidenceLabel(evidence.caption, evidence.type);
  return evidence.page ? `${label} 第 ${evidence.page} 页` : label;
}

function extractEvidenceLabel(caption = "", type = "figure") {
  const match = caption.match(/(figure|fig\.?|table)\s*[a-z]?\d+/i);
  if (match) {
    return match[0].replace(/^fig\.?/i, "Figure").replace(/\s+/g, " ");
  }
  return type === "table" ? "Table" : "Figure";
}

function formatSectionLocation(section) {
  if (!section) return "论文相关章节";
  if (normalizeSectionTitle(section.title) === "abstract" && section.page_start) {
    return `${section.title} 第 ${section.page_start} 页`;
  }
  if (section.page_start && section.page_end && section.page_start !== section.page_end) {
    return `${section.title} 第 ${section.page_start}-${section.page_end} 页`;
  }
  if (section.page_start) return `${section.title} 第 ${section.page_start} 页`;
  return section.title;
}

function inferTotalPages(paper) {
  const pages = (paper.sections || [])
    .flatMap((section) => [section.page_start, section.page_end])
    .filter(Boolean);
  return Math.max(1, ...pages, state.totalPages);
}

function firstReadablePage(paper) {
  return buildStageReadingPlan(paper, state.stage).primaryPage || 1;
}

function renderStage(stageLabel, options = {}) {
  const content = getStageContent(stageLabel);
  state.stage = stageLabel;
  const activeIndex = stageOrder.indexOf(stageLabel);
  const progressLabel = `${stageLabel} · ${activeIndex + 1} / ${stageOrder.length}`;

  $$(".reader-stage-badge").forEach((badge) => {
    badge.textContent = progressLabel;
  });
  const readerGoal = $(".reader-goal");
  if (readerGoal) readerGoal.textContent = content.goal;
  const coachGoal = $(".coach-current-goal");
  if (coachGoal) coachGoal.textContent = content.goal;

  $$(".stage-item").forEach((button) => {
    const label = button.querySelectorAll("span")[1]?.textContent.trim();
    const index = stageOrder.indexOf(label);
    const stateIcon = $(".stage-state", button);
    button.classList.toggle("is-active", label === stageLabel);
    button.classList.toggle("is-done", index >= 0 && index < activeIndex);
    if (stateIcon) {
      stateIcon.className =
        label === stageLabel
          ? "stage-state chevron"
          : index >= 0 && index < activeIndex
            ? "stage-state check-mark"
            : "stage-state circle";
    }
  });

  const guidanceBlocks = $$(".guidance-block strong");
  if (guidanceBlocks[0]) guidanceBlocks[0].textContent = content.read;
  if (guidanceBlocks[1]) guidanceBlocks[1].textContent = content.focus;

  renderQuestionList(content.questions || []);

  renderDraft(content);
  renderPaperForStage(stageLabel);
  const feedback = $(".feedback-panel");
  if (feedback) feedback.hidden = true;
  if (options.requestNavigation !== false) {
    requestStageNavigation(stageLabel, { silent: true });
  }
}

function renderQuestionList(questions) {
  const list = $(".questions ol");
  if (!list) return;
  const safeQuestions = questions.length > 0 ? questions : ["请先完成本阶段阅读导航。"];
  state.selectedQuestionIndex = Math.min(state.selectedQuestionIndex, safeQuestions.length - 1);
  list.innerHTML = safeQuestions
    .map(
      (question, index) => `
        <li class="${index === state.selectedQuestionIndex ? "is-selected" : ""}" data-question-index="${index}">
          <span>${index + 1}</span>
          <p>${escapeHtml(question)}</p>
        </li>
      `,
    )
    .join("");
}

async function requestStageNavigation(stageLabel, options = {}) {
  if (!state.paper?.paper_id) return null;
  if (!state.sessionId) {
    if (options.force) await ensureReadingSession();
    if (!state.sessionId) return null;
  }
  if (state.navigationRequests[stageLabel] && !options.force) {
    return state.navigationRequests[stageLabel];
  }

  const requestPromise = fetch(`/api/sessions/${encodeURIComponent(state.sessionId)}/navigation`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ stage: stageApiName(stageLabel) }),
  })
    .then(async (response) => {
      if (!response.ok) {
        const error = await response.json().catch(() => ({}));
        throw new Error(error.detail || "AI 阅读导航生成失败");
      }
      return response.json();
    })
    .then((navigation) => {
      applyNavigationResponse(stageLabel, navigation);
      return navigation;
    })
    .catch((error) => {
      if (!options.silent) showToast(error.message || "AI 阅读导航生成失败");
      return null;
    })
    .finally(() => {
      delete state.navigationRequests[stageLabel];
    });

  state.navigationRequests[stageLabel] = requestPromise;
  return requestPromise;
}

function applyNavigationResponse(stageLabel, navigation) {
  if (!navigation) return;
  const label = stageLabelFromApi(navigation.stage);
  const content = getStageContent(label);
  const readingLabel = formatApiReadingTargets(navigation.reading_targets);
  const focusLabel = (navigation.focus_points || []).slice(0, 2).join("；");
  const apiQuestions = navigation.questions || [];

  content.goal = navigation.goal || content.goal;
  if (readingLabel) content.read = readingLabel;
  if (focusLabel) content.focus = focusLabel;
  if (apiQuestions.length > 0) {
    content.questions = apiQuestions.map((question) => question.question);
    state.apiQuestionsByStage[label] = apiQuestions;
  }
  state.dynamicStageContent[label] = content;

  if (state.stage === label) {
    renderStage(label, { requestNavigation: false });
  }
}

function formatApiReadingTargets(targets = []) {
  if (!Array.isArray(targets) || targets.length === 0) return "";
  return targets.map((target) => target.label || formatApiTarget(target)).join("；");
}

function formatApiTarget(target) {
  const title = target.title || "论文相关章节";
  if (target.page_start && target.page_end && target.page_start !== target.page_end) {
    return `${title} 第 ${target.page_start}-${target.page_end} 页`;
  }
  if (target.page_start) return `${title} 第 ${target.page_start} 页`;
  return title;
}

function currentApiQuestion() {
  const questions = state.apiQuestionsByStage[state.stage] || [];
  return questions[state.selectedQuestionIndex] || questions[0] || null;
}

function renderDraft(content) {
  const cards = $$(".draft-card");
  const groups = {
    facts: content.facts || [],
    understanding: content.understanding || [],
    questionsWorth: content.questionsWorth || [],
  };
  const labels = {
    facts: "证据",
    understanding: "理解",
    questionsWorth: "追问",
  };
  cards.forEach((card, index) => {
    const editor = $(".draft-editor", card);
    const footer = $(".card-footer", card);
    const key = editor?.dataset.draftKey || Object.keys(groups)[index];
    const items = groups[key] || [];
    if (editor && document.activeElement !== editor) {
      editor.value = items.join("\n");
    }
    if (footer) footer.textContent = `已保存 ${items.length} 条${labels[key]}`;
  });
  updateDraftStatus(`${state.stage} · 当前阶段已加载`);
}

function syncDraftEditor(editor) {
  const key = editor.dataset.draftKey;
  if (!key) return;
  const content = getStageContent(state.stage);
  content[key] = editor.value
    .split(/\n+/)
    .map((item) => item.trim())
    .filter(Boolean);
  state.dynamicStageContent[state.stage] = content;
  const card = editor.closest(".draft-card");
  const footer = card ? $(".card-footer", card) : null;
  const label = key === "facts" ? "证据" : key === "understanding" ? "理解" : "追问";
  if (footer) footer.textContent = `已保存 ${content[key].length} 条${label}`;
  saveStageNotes();
}

function renderPaperForStage(stageLabel) {
  if (!state.paper) return;
  const readingPlan = buildStageReadingPlan(state.paper, stageLabel);
  const section = readingPlan.primarySection;
  const contentRoot = $(".paper-content");
  if (!section || !contentRoot) return;

  state.page = Math.min(Math.max(readingPlan.primaryPage || section.page_start || state.page, 1), state.totalPages);
  const sectionIndex = Math.max(1, (state.paper.sections || []).indexOf(section) + 1);
  const paragraphs = sectionParagraphs(section).slice(0, 6);
  contentRoot.innerHTML = `
    <h2><span>${sectionIndex}</span> ${escapeHtml(section.title)}</h2>
    ${paragraphs.map((paragraph, index) => `<p>${formatParagraph(paragraph, index)}</p>`).join("")}
  `;
  renderFigureEvidence(state.paper, stageLabel);
  updateReader({ scrollToPage: true, behavior: "auto" });
}

function renderFigureEvidence(paper, stageLabel) {
  const figure = $(".architecture-figure");
  if (!figure) return;
  const figureItem = pickFigureForStage(paper, stageLabel);
  if (!figureItem) {
    figure.hidden = true;
    return;
  }
  figure.hidden = false;
  const label = figureItem.id?.replace("_", " ") || "figure";
  figure.innerHTML = `
    <div class="figure-card">
      <strong>${escapeHtml(label.toUpperCase())}</strong>
      <span>论文证据</span>
    </div>
    <figcaption>${escapeHtml(figureItem.caption || "图表说明暂未识别")}</figcaption>
  `;
}

function pickFigureForStage(paper, stageLabel) {
  const figures = paper.figures || [];
  const tables = paper.tables || [];
  if (["实验", "结果"].includes(stageLabel)) return tables[0] || figures[0] || null;
  return figures[0] || tables[0] || null;
}

function sectionParagraphs(section) {
  if (section.paragraphs && section.paragraphs.length > 0) {
    return section.paragraphs.map((paragraph) => paragraph.text).filter(Boolean);
  }
  return splitEvidenceSentences(section.content || "").reduce((groups, sentence, index) => {
    const groupIndex = Math.floor(index / 2);
    groups[groupIndex] = groups[groupIndex] ? `${groups[groupIndex]} ${sentence}` : sentence;
    return groups;
  }, []);
}

function formatParagraph(paragraph, index) {
  const escaped = escapeHtml(paragraph);
  if (index === 0 || index === 2) return `<mark>${escaped}</mark>`;
  return escaped;
}

function splitEvidenceSentences(text) {
  return (text || "")
    .replace(/\s+/g, " ")
    .split(/(?<=[.!?。！？])\s+/)
    .map((item) => item.trim())
    .filter((item) => item.length >= 30)
    .slice(0, 12);
}

let pageScrollFrame = 0;

function updateReader(options = {}) {
  updatePageDisplay();
  updateZoomDisplay();
  updateReaderModeButton();

  const paperPage = $(".paper-page");
  if (!paperPage) return;
  paperPage.style.transform = "";

  if (state.continuousMode) {
    renderContinuousPdfPages();
    applyPdfZoom();
    if (options.scrollToPage) {
      scrollContinuousPageIntoView(state.page, options.behavior || "smooth");
    }
    return;
  }

  renderPdfPageImage();
  applyPdfZoom();
}

function updatePageDisplay() {
  $$(".page-input").forEach((input) => {
    const number = $("span", input);
    const total = $("em", input);
    if (number) number.textContent = String(state.page);
    if (total) total.textContent = `/ ${state.totalPages}`;
  });
  $$(".pdf-continuous-page").forEach((page) => {
    page.classList.toggle("is-current", Number(page.dataset.page) === state.page);
  });
}

function updateZoomDisplay() {
  const zoomPill = $(".zoom-pill");
  if (zoomPill) zoomPill.textContent = `${state.zoom}%`;
}

function updateReaderModeButton() {
  const button = $(".continuous-mode-button");
  if (!button) return;
  button.textContent = state.continuousMode ? "连续" : "单页";
  button.classList.toggle("is-active", state.continuousMode);
  button.setAttribute("aria-pressed", String(state.continuousMode));
}

function applyPdfZoom() {
  const width = state.zoom === 100 ? "min(100%, 1040px)" : `${state.zoom}%`;
  $$(".pdf-page-image, .pdf-continuous-image").forEach((image) => {
    image.style.width = width;
  });
}

function changePage(nextPage) {
  state.page = Math.max(1, Math.min(state.totalPages, nextPage));
  updateReader({ scrollToPage: true });
  showToast(`已切换到第 ${state.page} 页`);
}

function setupReaderScrollTracking() {
  const paperPage = $(".paper-page");
  if (!paperPage) return;
  paperPage.addEventListener("scroll", () => {
    if (!state.continuousMode) return;
    window.cancelAnimationFrame(pageScrollFrame);
    pageScrollFrame = window.requestAnimationFrame(syncPageFromContinuousScroll);
  });
}

function syncPageFromContinuousScroll() {
  const paperPage = $(".paper-page");
  if (!paperPage) return;

  const containerRect = paperPage.getBoundingClientRect();
  let nextPage = state.page;
  let bestDistance = Number.POSITIVE_INFINITY;

  $$(".pdf-continuous-page").forEach((page) => {
    const rect = page.getBoundingClientRect();
    if (rect.bottom < containerRect.top + 60 || rect.top > containerRect.bottom - 80) return;
    const distance = Math.abs(rect.top - containerRect.top - 12);
    if (distance < bestDistance) {
      bestDistance = distance;
      nextPage = Number(page.dataset.page) || nextPage;
    }
  });

  if (nextPage !== state.page) {
    state.page = nextPage;
    updatePageDisplay();
  }
}

function scrollContinuousPageIntoView(pageNumber, behavior = "smooth") {
  const target = $(`.pdf-continuous-page[data-page="${pageNumber}"]`);
  if (!target) return;
  target.scrollIntoView({ block: "start", behavior });
  updatePageDisplay();
}

function renderPdfPageImage() {
  const paperPage = $(".paper-page");
  const viewer = $(".pdf-page-viewer");
  const continuousViewer = $(".pdf-continuous-viewer");
  const image = $(".pdf-page-image");
  if (!paperPage || !viewer || !image || !state.paper?.paper_id) {
    paperPage?.classList.remove("has-page-image");
    return;
  }

  const pageUrl = `/api/papers/${encodeURIComponent(state.paper.paper_id)}/pages/${state.page}/image?scale=1.5`;
  if (continuousViewer) continuousViewer.hidden = true;
  viewer.hidden = false;
  paperPage.classList.add("has-page-image");
  paperPage.classList.remove("is-continuous");

  image.onerror = () => {
    image.classList.remove("is-loaded");
    paperPage.classList.remove("has-page-image");
    viewer.hidden = true;
    showToast("PDF 页面图片加载失败，已切换到文本视图");
  };
  image.onload = () => {
    image.classList.add("is-loaded");
    viewer.hidden = false;
    paperPage.classList.add("has-page-image");
    applyPdfZoom();
  };
  if (image.dataset.src !== pageUrl) {
    image.dataset.src = pageUrl;
    image.alt = `${state.paper.title || "论文"} 第 ${state.page} 页`;
    image.classList.remove("is-loaded");
    image.src = pageUrl;
  }
}

function renderContinuousPdfPages() {
  const paperPage = $(".paper-page");
  const singleViewer = $(".pdf-page-viewer");
  const continuousViewer = $(".pdf-continuous-viewer");
  if (!paperPage || !continuousViewer || !state.paper?.paper_id) {
    paperPage?.classList.remove("has-page-image", "is-continuous");
    return;
  }

  const renderKey = `${state.paper.paper_id}:${state.totalPages}`;
  if (continuousViewer.dataset.renderKey !== renderKey) {
    continuousViewer.innerHTML = Array.from({ length: state.totalPages }, (_, index) => {
      const page = index + 1;
      const pageUrl = `/api/papers/${encodeURIComponent(state.paper.paper_id)}/pages/${page}/image?scale=1.5`;
      return `
        <section class="pdf-continuous-page" data-page="${page}" aria-label="第 ${page} 页">
          <div class="pdf-continuous-page-label">第 ${page} / ${state.totalPages} 页</div>
          <img class="pdf-continuous-image" loading="lazy" alt="${escapeHtml(
            state.paper.title || "论文",
          )} 第 ${page} 页" src="${pageUrl}" />
        </section>
      `;
    }).join("");
    continuousViewer.dataset.renderKey = renderKey;
  }

  singleViewer.hidden = true;
  continuousViewer.hidden = false;
  paperPage.classList.add("has-page-image", "is-continuous");
  updatePageDisplay();
}

function exportNotes() {
  const title = $(".paper-title")?.textContent.trim() || "PaperCoach 笔记";
  const sections = $$(".draft-card").map((card) => {
    const heading = $("h3", card)?.textContent.trim() || "片段";
    const editor = $(".draft-editor", card);
    const items = (editor?.value || "")
      .split(/\n+/)
      .map((item) => item.trim())
      .filter(Boolean)
      .map((item) => `- ${item}`);
    return `## ${heading}\n${items.join("\n")}`;
  });
  const answer = $(".answer-box textarea")?.value.trim();
  const content = [`# ${title}`, `当前阶段：${state.stage}`, ...sections];
  if (answer) content.push(`## 当前回答\n${answer}`);
  downloadText("papercoach-notes.md", content.join("\n\n"));
  showToast("已导出 Markdown 笔记");
}

function downloadText(filename, content) {
  const blob = new Blob([content], { type: "text/markdown;charset=utf-8" });
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  link.remove();
  URL.revokeObjectURL(url);
}

function showFeedback(kind) {
  const panel = $(".feedback-panel");
  if (!panel) return;
  const current = getStageContent(state.stage);
  if (kind === "hint") {
    panel.innerHTML = `
      <h3>提示</h3>
      <p>先不要直接总结整篇论文。请回到“${current.read}”，找到一句能支撑你判断的原文证据。</p>
      <ul>
        <li>先说作者指出的问题。</li>
        <li>再说这个问题为什么影响方法或实验。</li>
        <li>最后补上 section、figure 或页码。</li>
      </ul>
    `;
  } else {
    panel.innerHTML = `
      <h3>回答反馈</h3>
      <p>你的回答已经进入“${state.stage}”阶段记录。下一步建议补充一个更具体的论文证据位置。</p>
      <ul>
        <li>准确性：4 / 5</li>
        <li>完整性：3 / 5</li>
        <li>证据引用：建议明确写出第几节或图表编号。</li>
      </ul>
    `;
  }
  panel.hidden = false;
}

function renderAnswerFeedback(response) {
  const panel = $(".feedback-panel");
  if (!panel) return;
  const scores = response?.scores || {};
  const provider = response?.feedback_provider || response?.feedback_source || "local";
  const sourceLabel = response?.feedback_source === "llm" ? `远程模型：${provider}` : "本地评分反馈";
  const scoreItems = [
    ["准确性", scores.accuracy],
    ["完整性", scores.completeness],
    ["深度", scores.depth],
    ["证据", scores.evidence],
    ["表达", scores.expression],
  ].filter(([, value]) => value !== undefined);
  const suggestions = response?.reread_suggestions || [];
  panel.innerHTML = `
    <h3>AI 回答反馈</h3>
    <div class="feedback-source">${escapeHtml(sourceLabel)}</div>
    ${
      scoreItems.length
        ? `<div class="score-grid">${scoreItems
            .map(([label, value]) => `<span>${label}<strong>${value} / 5</strong></span>`)
            .join("")}</div>`
        : ""
    }
    ${
      suggestions.length
        ? `<div class="feedback-suggestions"><strong>建议回读</strong><ul>${suggestions
            .map((item) => `<li>${escapeHtml(item)}</li>`)
            .join("")}</ul></div>`
        : ""
    }
    <pre class="feedback-text">${escapeHtml(response?.feedback || "暂未返回反馈。")}</pre>
  `;
  panel.hidden = false;
}

function renderHintFeedback(question) {
  const panel = $(".feedback-panel");
  if (!panel) return;
  const current = getStageContent(state.stage);
  const evidence = question?.evidence_location || current.read;
  const prompt = question?.question || current.questions?.[state.selectedQuestionIndex] || current.questions?.[0];
  panel.innerHTML = `
    <h3>阅读提示</h3>
    <p>先回到 <strong>${escapeHtml(evidence)}</strong>，不要急着总结整篇论文。</p>
    <ul>
      <li>先找一句能直接回答当前问题的原文。</li>
      <li>再写出它说明了什么，以及为什么能支持你的判断。</li>
      <li>最后补上 section、figure、table 或页码。</li>
    </ul>
    <p class="hint-question">当前问题：${escapeHtml(prompt || "请基于当前阶段问题作答。")}</p>
  `;
  panel.hidden = false;
}

async function submitAnswer() {
  const textarea = $(".answer-box textarea");
  const answer = textarea?.value.trim() || "";
  if (!answer) {
    showToast("请先写下你的回答");
    textarea?.focus();
    return;
  }

  await ensureReadingSession();
  if (!currentApiQuestion()) {
    await requestStageNavigation(state.stage, { force: true });
  }
  const question = currentApiQuestion();

  if (!state.sessionId || !question?.id) {
    const content = getStageContent(state.stage);
    content.understanding = [answer, ...content.understanding.filter((item) => item !== answer)].slice(0, 4);
    state.dynamicStageContent[state.stage] = content;
    renderDraft(content);
    saveStageNotes("回答已保存");
    showFeedback("answer");
    showToast("AI 会话暂不可用，已使用本地反馈");
    return;
  }

  const content = getStageContent(state.stage);
  try {
    const response = await fetch(`/api/sessions/${encodeURIComponent(state.sessionId)}/answers`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        question_id: question.id,
        answer,
      }),
    });
    if (!response.ok) {
      const error = await response.json().catch(() => ({}));
      throw new Error(error.detail || "AI 反馈生成失败");
    }
    const feedback = await response.json();
    content.understanding = [answer, ...content.understanding.filter((item) => item !== answer)].slice(0, 4);
    state.dynamicStageContent[state.stage] = content;
    renderDraft(content);
    saveStageNotes("回答已保存");
    renderAnswerFeedback(feedback);
    showToast(feedback.understood ? "回答已提交，AI 认为本阶段可以推进" : "回答已提交，AI 已给出修改建议");
  } catch (error) {
    showToast(error.message || "AI 反馈生成失败，已保留你的回答");
    content.understanding = [answer, ...content.understanding.filter((item) => item !== answer)].slice(0, 4);
    state.dynamicStageContent[state.stage] = content;
    renderDraft(content);
    saveStageNotes("回答已保存");
    showFeedback("answer");
  }
}

async function requestHint() {
  await ensureReadingSession();
  if (!currentApiQuestion()) {
    await requestStageNavigation(state.stage, { force: true });
  }
  renderHintFeedback(currentApiQuestion());
  showToast("已根据当前阅读阶段生成提示");
}

async function uploadPaper(file) {
  if (!file) return;
  if (!file.name.toLowerCase().endsWith(".pdf")) {
    showToast("请上传 PDF 文件");
    return;
  }

  const formData = new FormData();
  formData.append("file", file);
  try {
    const response = await fetch("/api/papers", {
      method: "POST",
      body: formData,
    });
    if (!response.ok) throw new Error("上传失败，请确认后端服务已启动");
    const uploaded = await response.json();
    const paperResponse = await fetch(`/api/papers/${uploaded.paper_id}`);
    const paper = paperResponse.ok ? await paperResponse.json() : uploaded;
    hydratePaper(paper);
    showToast("PDF 已上传并解析");
  } catch (error) {
    showToast(error.message || "上传失败");
  }
}

async function importFromZoteroPath(path) {
  const trimmedPath = path.trim().replace(/^["']|["']$/g, "");
  if (!trimmedPath) return;
  try {
    const response = await fetch("/api/papers/import-zotero", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ path: trimmedPath }),
    });
    if (!response.ok) {
      const error = await response.json().catch(() => ({}));
      throw new Error(error.detail || "Zotero 导入失败");
    }
    const imported = await response.json();
    const paperResponse = await fetch(`/api/papers/${imported.paper_id}`);
    const paper = paperResponse.ok ? await paperResponse.json() : imported;
    hydratePaper(paper);
    showToast("已从 Zotero 导入论文");
  } catch (error) {
    showToast(error.message || "Zotero 导入失败");
  }
}

function openSettings() {
  const backdrop = $(".modal-backdrop");
  if (backdrop) backdrop.hidden = false;
}

function closeSettings() {
  const backdrop = $(".modal-backdrop");
  if (backdrop) backdrop.hidden = true;
}

function escapeHtml(value) {
  return value
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

const answerBox = $(".answer-box textarea");
const counter = $(".answer-box span");

if (answerBox && counter) {
  answerBox.addEventListener("input", () => {
    counter.textContent = `${answerBox.value.length} / ${answerBox.maxLength}`;
  });
}

$$(".stage-item").forEach((button) => {
  button.addEventListener("click", () => {
    const label = button.querySelectorAll("span")[1]?.textContent.trim();
    if (label) {
      state.selectedQuestionIndex = 0;
      renderStage(label);
      showToast(`已切换到「${label}」阶段`);
    }
  });
});

$(".questions ol")?.addEventListener("click", (event) => {
  const item = event.target.closest("li");
  if (!item) return;
  const index = Number(item.dataset.questionIndex || 0);
  state.selectedQuestionIndex = index;
  $$(".questions li").forEach((question, questionIndex) => {
    question.classList.toggle("is-selected", questionIndex === index);
  });
});

$$(".draft-editor").forEach((editor) => {
  editor.addEventListener("input", () => syncDraftEditor(editor));
});

$$(".coach-tab").forEach((button) => {
  button.addEventListener("click", () => {
    setSideTab(button.dataset.sideTab);
  });
});

$(".export-notes-button")?.addEventListener("click", exportNotes);
$(".settings-button")?.addEventListener("click", openSettings);
$$(".modal-close-button").forEach((button) => button.addEventListener("click", closeSettings));
$(".save-settings-button")?.addEventListener("click", () => {
  closeSettings();
  showToast("设置已保存");
});
$(".modal-backdrop")?.addEventListener("click", (event) => {
  if (event.target === event.currentTarget) closeSettings();
});

$(".upload-button")?.addEventListener("click", () => $(".upload-input")?.click());
$(".upload-input")?.addEventListener("change", (event) => uploadPaper(event.target.files?.[0]));
$(".zotero-import-button")?.addEventListener("click", () => {
  const path = window.prompt("粘贴 Zotero PDF 文件路径", "");
  if (path) importFromZoteroPath(path);
});

$(".prev-page-button")?.addEventListener("click", () => changePage(state.page - 1));
$(".next-page-button")?.addEventListener("click", () => changePage(state.page + 1));
$(".zoom-out-button")?.addEventListener("click", () => {
  state.zoom = Math.max(80, state.zoom - 10);
  updateReader({ scrollToPage: state.continuousMode, behavior: "auto" });
});
$(".zoom-in-button")?.addEventListener("click", () => {
  state.zoom = Math.min(160, state.zoom + 10);
  updateReader({ scrollToPage: state.continuousMode, behavior: "auto" });
});
$(".continuous-mode-button")?.addEventListener("click", () => {
  state.continuousMode = !state.continuousMode;
  updateReader({ scrollToPage: true, behavior: "auto" });
  showToast(state.continuousMode ? "已切换为连续阅读模式" : "已切换为单页阅读模式");
});
$(".fit-width-button")?.addEventListener("click", () => {
  state.zoom = 100;
  updateReader({ scrollToPage: state.continuousMode, behavior: "auto" });
  showToast("已恢复页宽视图");
});
$(".toggle-draft-button")?.addEventListener("click", () => {
  setSideTab("notes");
  showToast("已切换到阶段笔记");
});
$(".focus-reader-button")?.addEventListener("click", () => {
  layoutState.readerFocus = !layoutState.readerFocus;
  applyLayout();
  saveLayout();
  showToast(layoutState.readerFocus ? "已进入专注阅读布局" : "已退出专注阅读布局");
});
$(".reset-layout-button")?.addEventListener("click", () => {
  resetLayout();
  showToast("布局已重置");
});
$(".outline-button")?.addEventListener("click", () => {
  const sections = state.paper?.sections?.slice(0, 5).map((section) => section.title).join(" / ");
  showToast(`目录：${sections || "Introduction / Method / Experiments / Results"}`);
});
$(".search-button")?.addEventListener("click", () => {
  const keyword = window.prompt("搜索论文内容", "attention");
  if (keyword) showToast(`已定位关键词：${keyword}`);
});
$(".download-paper-button")?.addEventListener("click", () => {
  const source = state.paper?.source_file || "当前论文文件";
  downloadText(
    "papercoach-paper-source.txt",
    `PaperCoach 当前论文：${$(".paper-title")?.textContent.trim()}\n源文件：${source}`,
  );
});
$(".fullscreen-button")?.addEventListener("click", () => {
  const reader = $(".reader");
  if (reader?.requestFullscreen) {
    reader.requestFullscreen();
  } else {
    showToast("当前浏览器不支持全屏 API");
  }
});

$(".collapse-coach-button")?.addEventListener("click", () => {
  $(".coach-panel")?.classList.toggle("is-collapsed");
});
$(".more-button")?.addEventListener("click", () => showToast("更多操作：复制问题、清空回答、查看历史反馈"));
$(".submit-answer-button")?.addEventListener("click", () => {
  setBusy($(".submit-answer-button"), "提交中...", async () => {
    await new Promise((resolve) => window.setTimeout(resolve, 260));
    submitAnswer();
  });
});
$(".request-hint-button")?.addEventListener("click", () => {
  setBusy($(".request-hint-button"), "生成中...", requestHint);
});

document.addEventListener("keydown", (event) => {
  if (event.key === "Escape") closeSettings();
});

window.addEventListener("resize", () => {
  clampLayoutToViewport();
  applyLayout();
});

restoreLayout();
setupResizablePanes();
setupReaderScrollTracking();
state.dynamicStageContent = mergeStageNotes(stageContent, readSavedStageNotes());
renderStage(state.stage);
updateReader();
loadInitialPaper();
