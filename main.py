import re
import fire

from metagpt.actions import Action, UserRequirement
from metagpt.logs import logger
from metagpt.roles import Role
from metagpt.schema import Message
from metagpt.team import Team


# 函数用于从生成的文本中解析代码内容
def parse_text(rsp):
    pattern = r"```text(.*)```"
    match = re.search(pattern, rsp, re.DOTALL)
    text = match.group(1) if match else rsp
    text = text.replace("```text", "")
    text = text.replace("```", "")
    return text


# 总体情节的构建师角色
class StoryPlanner(Action):
    PROMPT_TEMPLATE: str = """
    根据以下主题或背景设定，创建一份中篇小说的总体情节架构:
    主题:{theme}:
    要求:
    - 精心构建主线情节，确保情节紧凑且引人入胜，明确每个情节点与主旨的关联
    - 精确设定主要人物，塑造复杂且深刻的人物关系，强调人物动机与性格转变
    - 详细定义主要人物的品格特征、情感与行为逻辑，使其更具立体感与可信度
    - 精心设计主要冲突，包括内心的挣扎与外部的对抗，明确冲突发展的方向与层次
    - 设计高潮迭起的转折点与决战时刻，增强情节的张力与悬念，确保情感与情节的引爆点
    - 提供完整且紧凑的情节架构，注重细节的连贯性，确保每一段情节都推动人物成长与故事发展
    - 设定符合故事背景的行文风格，精准把握情境氛围，运用语言展现人物内心及冲突的深度
    输出格式:```text yourtext```
    """

    name: str = "StoryPlanner"

    async def run(self, theme: str):
        prompt = self.PROMPT_TEMPLATE.format(theme=theme)
        rsp = await self._aask(prompt)
        text = parse_text(rsp)
        open('workspace/novelSet.txt', 'w').write(text)
        return text


class PlotArchitect(Role):
    name: str = "Plot Architect"
    profile: str = "负责总体情节构建"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._watch([UserRequirement])
        self.set_actions([StoryPlanner])


class ArchitectureEvaluation(Action):
    PROMPT_TEMPLATE: str = """
    根据以下总体情节架构，进行小说的评分，并给出评语：
    评估维度：
    1. **情节逻辑与连贯性**  
       评语：评估故事情节的合理性与流畅度，是否有合理的因果关系与情节发展。注意评估转折是否自然，人物行为决策是否符合其性格和情境。
    2. **人物设定与发展**  
       评语：考察主要人物是否有深刻的性格塑造和成长弧线。评估人物在故事中的变化，尤其是在冲突中的选择是否合乎其动机，并产生有效的情感共鸣。
    3. **世界观构建**  
       评语：评估世界观的原创性与完整性，设定是否独特且自洽。注意是否有足够的细节支撑背景故事，避免出现显得牵强或未展开的地方。
    4. **节奏与张力**  
       评语：评估故事的节奏是否紧凑且富有张力，是否能够保持读者的持续兴趣。特别注意高潮部分的设计，是否能够合理推动情节并增强情感波动。
    5. **主题与象征**  
       评语：评估小说的主题深度与表达方式，是否通过人物与情节传递了具有思考价值的核心思想。留意是否有不够深刻或表达过于直白的地方。
    6. **创新性**  
       评语：评估故事架构与情节设置的创新性。注意小说中是否使用了新的叙事技巧或独特的创意元素，而非依赖传统或常见的叙事手法。
    7. **情感共鸣**  
       评语：评估情感表现的真实度与感染力，特别是是否能够触动读者的情感。评估人物之间关系的描写是否自然，是否能够引起读者的共鸣与思考。
    评分标准：每个维度的评分范围为1-10，1表示非常差，10表示非常好。  
    反馈要求：每个维度的反馈应简明扼要，突出优缺点，并给出具体的建议。

    情节架构:{plot_architecture}

    输出格式:```text  评分xxxxx，评语xxxx```
    """

    name: str = "ArchitectureEvaluation"

    async def run(self, plot_architecture: str):
        prompt = self.PROMPT_TEMPLATE.format(plot_architecture=plot_architecture)
        rsp = await self._aask(prompt)
        text = parse_text(rsp)
        return text


class ArchitectureEvaluator(Role):
    name: str = "Architecture Evaluator"
    profile: str = "进行小说架构的评分"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.set_actions([ArchitectureEvaluation])
        self._watch([StoryPlanner])

    async def _act(self) -> Message:
        logger.info(f"{self._setting}: 准备执行 {self.rc.todo}({self.rc.todo.name})")
        todo = self.rc.todo

        context = self.get_memories()
        plot_architecture = await todo.run(context)
        msg = Message(plot_architecture=plot_architecture, role=self.profile, cause_by=type(todo))

        return msg


class PlotRevisions(Action):
    PROMPT_TEMPLATE: str = """
    情节架构:{plot_architecture}
    该情节架构评价：:{plot_revisions}
    请根据该情节架构评价进行情节架构的修订，根据评分内容进行情节架构的优化

    输出格式:```text  yourtext```
    """

    name: str = "PlotRevisions"

    async def run(self, plot_revisions: str):
        with open('workspace/novelSet.txt', 'r') as f:
            plot_architecture = f.read()
        prompt = self.PROMPT_TEMPLATE.format(plot_architecture=plot_architecture, plot_revisions=plot_revisions)
        rsp = await self._aask(prompt)
        text = parse_text(rsp)
        open('workspace/novelSet.txt', 'w').write(text)
        return text


class PlotReviser(Role):
    name: str = "Plot Reviser"
    profile: str = "进行小说情节的修订"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.set_actions([PlotRevisions])
        self._watch([ArchitectureEvaluation])

    async def _act(self) -> Message:
        logger.info(f"{self._setting}: 准备执行 {self.rc.todo}({self.rc.todo.name})")
        todo = self.rc.todo

        context = self.get_memories()
        plot_revisions = await todo.run(context)
        msg = Message(plot_revisions=plot_revisions, role=self.profile, cause_by=type(todo))

        return msg


# 章节划分师角色
class ChapterDivider(Action):
    PROMPT_TEMPLATE: str = """
    根据以下总体情节架构，将小说划分为若干章节，并明确每个章节的重点情节目标:
    - 每章需要包含具体的情节目标，并且推动故事主线的发展
    - 保持故事节奏与情节推进合理，确保每章既有独立性又能衔接前后
    - 强调每个章节中的冲突、人物的心理活动和转变
    - 确保章节之间有足够的张力与情感起伏
    情节架构:{plot_architecture}
    将全部章节放到一个同一个列表中
    输出格式:```text  ['章节1:xxxxxx','章节2:xxxxxx','章节3:xxxxxx','章节x:xxxxxx']```
    """

    name: str = "ChapterDivider"

    async def run(self, plot_architecture: str):
        prompt = self.PROMPT_TEMPLATE.format(plot_architecture=plot_architecture)
        rsp = await self._aask(prompt)
        text = parse_text(rsp)
        open('workspace/novelChapter.txt', 'w').write(text)
        open("workspace/Recording.txt", "w", encoding='utf-8').write('0')
        return text


class ChapterPlanner(Role):
    name: str = "Chapter Planner"
    profile: str = "负责章节划分"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.set_actions([ChapterDivider])
        self._watch([PlotRevisions])

    async def _act(self) -> Message:
        logger.info(f"{self._setting}: 准备执行 {self.rc.todo}({self.rc.todo.name})")
        todo = self.rc.todo

        context = self.get_memories()
        plot_architecture = await todo.run(context)
        msg = Message(plot_architecture=plot_architecture, role=self.profile, cause_by=type(todo))

        return msg


# 章节总结与规划师角色
class ContentReader(Action):
    PROMPT_TEMPLATE: str = """
    阅读以下章节内容，并为下一章的写作提供指导:
    已完成章节内容:
    {previous_chapters}
    需要提供以下指导:
    - 当前情节的推进方向，如何顺利衔接上一章的情节
    - 主要角色的行为动机或心理变化，如何发展其冲突
    - 下一章的主要冲突或解决方向
    - 进行上一章的总结并指出问题，以优化下一章的写作内容
    下一章:{Chapter}
    输出格式:```text yourtext```
    """

    name: str = "ContentReader"

    async def run(self, chapter):
        try:
            with open('workspace/novel.txt', 'r', encoding='utf-8') as file:
                novel = file.read()
        except FileNotFoundError:
            open('workspace/novel.txt', 'w', encoding='utf-8').write('')
            return "这是第一章，无需参考指导。"

        prompt = self.PROMPT_TEMPLATE.format(previous_chapters=novel, Chapter=chapter)
        rsp = await self._aask(prompt)
        text = parse_text(rsp)
        return text


class ChapterReviewer(Role):
    name: str = "Content Reviewer"
    profile: str = "负责阅读前面章节并指导下一章的写作"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._watch([UserRequirement])
        self.set_actions([ContentReader])

    async def _act(self) -> Message:
        logger.info(f"{self._setting}: 准备执行 {self.rc.todo}({self.rc.todo.name})")
        todo = self.rc.todo
        msg = self.get_memories(k=1)[0]
        with open('workspace/novelChapter.txt', 'r', encoding='utf-8') as file:
            novelChapter = eval(file.read())
        try:
            with open('workspace/Recording.txt', 'r', encoding='utf-8') as file:
                Recording = int(file.read())
        except FileNotFoundError:
            open("workspace/Recording.txt", "w", encoding='utf-8').write('0')
            Recording = 0
        chapter = novelChapter[Recording]
        chapter = await todo.run(chapter)
        msg = Message(chapter=chapter, role=self.profile, cause_by=type(todo))
        return msg


# 小说主笔角色
class NovelWrite(Action):
    PROMPT_TEMPLATE: str = """
    根据以下信息完成当前章节的写作:
    - 指导内容:{guidance}  
      说明:根据已有的指导内容，明确写作方向，并确保情节在人物发展和冲突推进方面得当。
    - 当前章节目标:{chapter_goal}  
      说明:本章节的目标是要完成的情节目标，请确保该目标与情节架构一致。
    - 总体情节架构:{plot_architecture}  
      说明:确保当前章节的情节与整个小说的整体架构相符，情节发展和角色行为应符合大方向。
    - 写作要求:
        - 章节要求篇幅{lens}字左右,可以根据具体情况进行调整，不必强行续写
        - 请详细描写人物的外貌、动作、心理活动及环境细节，创造生动的场景。
        - 强调角色的情感波动、内心冲突，以及行为动机，尤其是在情节冲突和转折点。
        - 适当加入对话，推动情节的同时体现人物的个性和矛盾。
        - 保持叙述的流畅性和节奏感，确保故事的节奏不拖沓，并引发读者的兴趣。
        - 你需要写的是小说章节，仅仅需要写出小说文本即可，不需要做其他内容，也不需要写出章节名称
    输出格式:```text yourneoval```
    """

    name: str = "NovelWrite"

    async def run(self, guidance: str):
        with open('workspace/novelSet.txt', 'r', encoding='utf-8') as file:
            plot_architecture = file.read()

        with open('workspace/novelChapter.txt', 'r', encoding='utf-8') as file:
            novelChapter = eval(file.read())

        with open('workspace/Recording.txt', 'r', encoding='utf-8') as file:
            Recording = int(file.read())

        chapter_goal = novelChapter[Recording]

        Recording += 1
        open("workspace/Recording.txt", "w", encoding='utf-8').write(str(Recording))
        prompt = self.PROMPT_TEMPLATE.format(
            lens=len(novelChapter),
            guidance=guidance,
            chapter_goal=chapter_goal,
            plot_architecture=plot_architecture
        )
        rsp = await self._aask(prompt)
        text = parse_text(rsp)
        open('workspace/novel.txt', 'a', encoding='utf-8').write(text)
        open('workspace/novel.txt', 'a', encoding='utf-8').write('\n')
        return text


class NovelWriter(Role):
    name: str = "Novel Writer"
    profile: str = "进行当前章节的撰写"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.set_actions([NovelWrite])
        self._watch([ContentReader])

    async def _act(self) -> Message:
        logger.info(f"{self._setting}: 准备执行 {self.rc.todo}({self.rc.todo.name})")
        todo = self.rc.todo
        msg = self.get_memories(k=1)[0]
        context = self.get_memories()
        guidance = await todo.run(context)
        msg = Message(plot_architecture=guidance, role=self.profile, cause_by=type(todo))

        return msg


async def main(

        idea: str = "请以游戏《英雄联盟》为背景，以游戏中的佛耶戈做主角，主线为：在《英雄联盟》的宇宙中，破败之王佛耶戈原是卡玛维亚王国一个古老王国的君主，他深爱着自己的王后伊苏尔德。然而，一场突如其来的灾难摧毁了他的王国，也夺走了他挚爱的王后的生命。佛耶戈无法接受这一现实，他的心灵因此陷入了深深的悲痛和愤怒之中。为了复活伊苏尔德，佛耶戈不惜一切代价，前往福光岛的生命之泉，在复活王后的过程中发生了意外，福光岛变成了暗影岛，佛耶戈也变成了破败之王。写一篇中长篇的小说",
        investment: float = 1000.0,
        n_round: int = 10
):
    logger.info(idea)

    team1 = Team()
    team1.hire(
        [
            PlotArchitect(),
            ArchitectureEvaluator(),
            PlotReviser(),
            ChapterPlanner(),
        ]
    )

    team1.invest(investment=investment)
    team1.run_project(idea)
    await team1.run(n_round=n_round)

    team2 = Team()
    team2.hire(
        [
            ChapterReviewer(),
            NovelWriter(),
        ]
    )
    with open('workspace/novelChapter.txt', 'r', encoding='utf-8') as file:
        novelChapter = eval(file.read())

    for i in range(len(novelChapter)):
        team2.invest(investment=investment)
        team2.run_project(idea)
        await team2.run(n_round=n_round)


if __name__ == "__main__":
    fire.Fire(main)
