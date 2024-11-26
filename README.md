# 小说创作自动化生成 - 角色与动作介绍

该项目通过定义不同的`agent`实现定义的`action`以完成小说的撰写

## 相关文件地址
生成小说路径：[novel.txt](workspace/novel.txt)

主函数路径[main.py](main.py)

## 角色与动作的协作

### 角色与动作的分工

### 流程简述

1. **情节构建与规划**：`PlotArchitect` 通过 `StoryPlanner` 生成整体情节架构。
1. **情节架构的评分**： `ArchitectureEvaluator`通过`ArchitectureEvaluation`进行架构的评分
1. **情节架构修订**： `PlotReviser`通过`PlotRevisions`根据`ArchitectureEvaluator`的反馈进行评分的修订
2. **章节划分**：`ChapterPlanner` 使用 `ChapterDivider` 将情节架构拆分成具体章节。
3. **章节审查与指导**：`ChapterReviewer` 使用 `ContentReader` 审查前一章节并为下一章节提供写作建议。
4. **小说撰写**：`NovelWriter` 通过 `NovelWrite` 完成章节内容的创作，推动故事发展。

## 角色与动作概览

| 角色名称           | 角色描述                                                         | 动作名称      | 动作描述                                                     |
|--------------------|------------------------------------------------------------------|-----------------|------------------------------------------------------------|
| **PlotReviser** | 负责情节整体架构的构建与规划                                       | **StoryPlanner** | 根据主题生成小说的整体情节架构，包括人物、冲突和转折点等   |
| **ArchitectureEvaluator** | 进行情节结构的评分与评价 | **ArchitectureEvaluation** | 根据情节架构进行多个点的评分并给出评语  |
| **PlotReviser** | 根据情节架构的评分与评语进行架构的重写 | **PlotRevisions** | 根据情节架构的评分与评语进行架构的重写 |
| **ChapterPlanner**  | 负责将情节架构拆分成具体的章节，并确保章节之间的衔接合理         | **ChapterDivider** | 根据情节架构划分小说的章节，设置每章的情节目标               |
| **ChapterReviewer** | 审查已完成的章节，并为下一章提供创作指导                         | **ContentReader** | 提供章节写作指导，分析情节进展与人物变化                    |
| **NovelWriter**     | 根据指导完成每个章节的详细写作                                    | **NovelWrite**   | 根据指导和章节目标创作详细的章节文本                        |


---
