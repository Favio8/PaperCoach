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
