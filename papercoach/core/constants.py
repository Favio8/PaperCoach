READING_STAGES: tuple[str, ...] = (
    "Background",
    "Problem",
    "Key Idea",
    "Architecture",
    "Method",
    "Experiments",
    "Results",
    "Limitations",
    "Thoughts",
)

STAGE_QUERIES: dict[str, str] = {
    "Background": "abstract introduction background motivation context",
    "Problem": "problem challenge limitation gap existing method motivation",
    "Key Idea": "key idea contribution proposal overview insight",
    "Architecture": "architecture framework system pipeline component figure",
    "Method": "method approach algorithm implementation procedure",
    "Experiments": "experiment setup dataset baseline metric evaluation",
    "Results": "result performance table comparison analysis",
    "Limitations": "limitation discussion failure future work threat",
    "Thoughts": "discussion conclusion implication future work insight",
}

STAGE_GOALS: dict[str, str] = {
    "Background": "建立论文研究背景，判断这篇论文为什么值得读。",
    "Problem": "识别作者试图解决的核心问题，以及现有方法的不足。",
    "Key Idea": "抓住论文提出的新想法和它相对已有工作的差异。",
    "Architecture": "理解系统或方法的整体结构，以及模块之间如何连接。",
    "Method": "理解方法细节、关键机制和执行流程。",
    "Experiments": "理解实验设置是否足以验证论文主张。",
    "Results": "判断结果支持了哪些结论，以及证据强弱。",
    "Limitations": "识别方法边界、失败场景和实验局限。",
    "Thoughts": "沉淀自己的评价、延伸问题和后续研究方向。",
}

STAGE_MODULES: dict[str, tuple[str, ...]] = {
    "Background": ("论文信息（Paper Info）", "研究背景（Background）"),
    "Problem": ("论文要解决的问题（Problem）",),
    "Key Idea": ("核心思想（Key Idea）",),
    "Architecture": ("整体架构（Architecture）",),
    "Method": ("方法细节（Method）",),
    "Experiments": ("实验设计（Experiments）",),
    "Results": ("实验结果（Results）",),
    "Limitations": ("优点（Strengths）", "局限性（Limitations）"),
    "Thoughts": (
        "我的理解（My Thoughts）",
        "可以改进的方向（Future Work）",
        "参考资料（References）",
    ),
}

STAGE_READING_GUIDES: dict[str, dict[str, tuple[str, ...] | str]] = {
    "Background": {
        "read": (
            "标题、摘要和首页信息",
            "Introduction 前半部分",
            "项目页或代码仓库 README（如果论文提供）",
        ),
        "goal": "确认论文元信息、研究动机，并初步判断它在 Agent 谱系中的位置。",
        "focus": (
            "标题中的关键词和任务场景",
            "摘要中 claim 的主语、宾语和证据指向",
            "引言中作者如何描述现有方法缺口",
            "这篇论文属于能力缺口、系统缺口还是评测缺口",
        ),
        "answer": (
            "用 4 个短句回答：论文在做什么、为什么重要、属于哪个 Agent 子方向、"
            "相对已有工作的关键变化是什么。"
        ),
    },
    "Problem": {
        "read": (
            "Introduction 后半部分",
            "Method 开头的问题定义或任务设定段",
            "Task Setup / Preliminaries / Problem Formulation（如果有）",
        ),
        "goal": "明确任务定义、输入输出、约束条件，以及作者真正要解决的核心问题。",
        "focus": (
            "论文在哪个具体场景下定义 Agent 任务",
            "原方法在哪里失败",
            "作者要提升的是认知能力、执行能力，还是长程任务成功率",
        ),
        "answer": "请说明核心问题是什么、为什么现有方法不足、这个问题会影响 Agent 的哪类能力。",
    },
    "Key Idea": {
        "read": (
            "Abstract",
            "Introduction 最后 1 到 3 段",
            "Method 总览和 contribution list",
            "方法总图或 pipeline 图",
        ),
        "goal": "把论文创新压缩成一两句话，并看清它和 baseline 的关键差异。",
        "focus": (
            "we propose / our key idea / unlike prior work",
            "contribution list 中每个贡献是否有方法或实验支撑",
            "总图里新增模块如何插入原流程",
        ),
        "answer": "请写出核心想法、它和已有工作的差异、以及它为什么可能解决前一阶段的问题。",
    },
    "Architecture": {
        "read": (
            "方法总览部分",
            "系统架构图或 pipeline 图",
            "Algorithm / pseudo code（如果有）",
        ),
        "goal": "搞清模块划分、信息流、控制流、状态更新和模块调用关系。",
        "focus": (
            "模块边界",
            "每个模块输入输出",
            "状态如何更新",
            "哪些模块是本文新设计的",
        ),
        "answer": "请用自己的话描述系统由哪些模块组成，以及数据或控制信号如何流动。",
    },
    "Method": {
        "read": (
            "Method 全文",
            "关键公式、算法、伪代码",
            "附录中的 prompt template / implementation details（如果正文较简略）",
        ),
        "goal": "真正理解方法如何工作，并定位最可能产生贡献的关键步骤。",
        "focus": (
            "方法分几步",
            "每一步输入输出是什么",
            "为什么这么设计",
            "哪一步最不可替代，失败模式可能在哪里",
        ),
        "answer": "请选择一个关键机制，说明它的输入、输出、作用和可能失败的位置。",
    },
    "Experiments": {
        "read": (
            "Experimental Setup",
            "Benchmark / Dataset / Environment",
            "Baselines 和 Metrics 定义",
            "Ablation 设置",
        ),
        "goal": "理解实验在证明什么，并判断证据链是否完整。",
        "focus": (
            "benchmark 是否合理",
            "baseline 是否公平",
            "指标是否匹配论文 claim",
            "是否有消融、泛化、效率或案例分析",
        ),
        "answer": "请说明实验主要验证哪个 claim，baseline 和指标是否足以支撑这个 claim。",
    },
    "Results": {
        "read": (
            "Results 主表",
            "Ablation table",
            "Case study / Error analysis",
            "结果讨论部分",
        ),
        "goal": "判断哪些结果真正支持论文主张，哪些结果可能被过度解读。",
        "focus": (
            "最关键主表",
            "最能解释机制的消融",
            "是否有反常结果",
            "提升是否稳定，以及代价是什么",
        ),
        "answer": (
            "请选择一个最能支持核心贡献的结果，说明相比谁、提升什么指标、"
            "为什么能支持 claim。"
        ),
    },
    "Limitations": {
        "read": (
            "Limitations / Discussion",
            "Failure cases",
            "Appendix 中实验覆盖不到的部分",
            "Conclusion",
        ),
        "goal": "找到作者承认的局限，以及作者没有充分展开但值得追问的边界。",
        "focus": (
            "是否依赖强模型或强工具",
            "成本、复杂度、鲁棒性、泛化和安全性",
            "是否存在理想化假设",
            "结论是否超出实验证据",
        ),
        "answer": "请区分作者承认的局限和你推导出的局限，并给出证据位置。",
    },
    "Thoughts": {
        "read": (
            "自己前面完成的所有模块",
            "Introduction",
            "Method overview",
            "Results",
            "Conclusion / Future Work",
            "References 中最关键的 2 到 5 篇前置工作",
        ),
        "goal": "形成自己的观点和后续研究问题，而不是重复论文摘要。",
        "focus": (
            "这篇论文改变了你对什么问题的认识",
            "它更像研究突破还是工程整合",
            "在 Agent 脉络中的真实价值",
            "哪些模块可替换，哪些实验可补强，哪些场景尚未验证",
        ),
        "answer": "请写出你的评价、一个可改进方向，以及 2 到 5 个适合博客读者继续阅读的参考资料。",
    },
}
