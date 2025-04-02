#!/usr/bin/env python
# src/novel_generation_crew/main.py
import os
import asyncio
import json
from typing import List, Dict

from crewai.flow.flow import Flow, listen, start
from pydantic import BaseModel, Field
from .crews.novel_outline_crew.novel_outline_crew import NovelOutlineCrew
from .crews.chapter_writer_crew.chapter_writer_crew import ChapterWriterCrew
from .types import NovelOutline, ChapterOutline, Chapter, Novel
from .data.reference_novels import get_reference_novels

class NovelGenerationState(BaseModel):
    """小说生成状态"""
    # 小说类型
    novel_type: str = ""
    # 小说数量
    novel_count: int = 1
    # 当前小说索引
    current_novel: int = 0
    # 小说章节数
    chapter_count: int = 10
    # 每章字数
    chapter_words: int = 1000
    # 小说大纲
    novel_outlines: List[NovelOutline] = []
    # 已完成小说列表
    completed_novels: List[Novel] = []
    # 当前小说索引
    current_novel_index: int = 0
    # 当前章节索引
    current_chapter_index: int = 0
    # 当前章节列表
    current_chapters: List[Chapter] = []

class NovelGenerationFlow(Flow[NovelGenerationState]):
    """爽文小说生成流程"""
    
    @start()
    def initialize_parameters(self):
        """初始化小说生成参数"""
        print("\n===== 爽文小说生成系统 =====\n")
        
        # 获取用户输入
        self.state.novel_type = input("请输入小说类型 (如'穿越爽文', '都市重生'等): ")
        self.state.novel_count = int(input("请输入需要生成的小说数量: "))
        self.state.chapter_count = int(input("请输入每本小说的章节数: "))
        self.state.chapter_words = int(input("请输入每章节的字数: "))
        
        print(f"\n准备生成 {self.state.novel_count} 篇 {self.state.novel_type} 小说")
        print(f"每篇 {self.state.chapter_count} 章，每章约 {self.state.chapter_words} 字")
        
        # 创建输出目录
        os.makedirs("output", exist_ok=True)
        
        return self.state
    
    @listen(initialize_parameters)
    def start_novel_generation(self, _):
        """开始生成新小说"""
        self.state.current_novel += 1
        self.state.current_chapters = []
        self.state.current_chapter_index = 0
        
        print(f"\n===== 开始生成第 {self.state.current_novel}/{self.state.novel_count} 篇小说 =====\n")
        return "开始新小说生成"
    
    @listen(start_novel_generation)
    def generate_novel_outline(self, _):
        """生成小说大纲"""
        print("正在生成小说大纲...")
        
        # 获取参考小说
        reference_novels = get_reference_novels(self.state.novel_type)
        
        # 创建小说大纲
        result = NovelOutlineCrew().crew().kickoff(
            inputs={
                "novel_type": self.state.novel_type,
                "chapter_count": self.state.chapter_count,
                "chapter_words": self.state.chapter_words,
                "reference_novels": reference_novels,
            }
        )
        # 
        # 保存小说大纲
        novel_outline = result.pydantic
        self.state.novel_outlines.append(novel_outline)
        
        print(f"小说大纲生成完成: {novel_outline.title}")
        print(f"共 {len(novel_outline.chapters)} 章")
        
        # 保存大纲到文件
        outline_path = f"output/{self.state.novel_type}_小说_{self.state.current_novel}_大纲.json"
        with open(outline_path, "w", encoding="utf-8") as f:
            # novel_outline.model_dump()将Pydantic 模型对象转换为字典
            # json.dumps() - 将字典转换为 JSON 字符串
            # ensure_ascii=False - 确保中文字符不被转义为 Unicode 编码
            # indent=2 - 设置 JSON 缩进，使文件更易读
            f.write(json.dumps(novel_outline.model_dump(), ensure_ascii=False, indent=2))
        
        print(f"大纲已保存至: {outline_path}")
        
        return novel_outline
    
    @listen(generate_novel_outline)
    async def generate_chapters(self, novel_outline: NovelOutline):
        """生成小说章节"""
        print(f"开始生成《{novel_outline.title}》的章节...")

        # 当前小说索引，即第几本小说
        self.state.current_novel_index = len(self.state.novel_outlines) - 1
        self.state.current_chapters = []
        
        # 生成每个章节
        for i, chapter_outline in enumerate(novel_outline.chapters):

            chapter = await self.generate_single_chapter(
                    novel_outline=novel_outline,
                    chapter_index=i,
                    chapter_outline=chapter_outline
                )
            self.state.current_chapters.append(chapter)
      
        # 创建完整小说
        novel = Novel(
            title=novel_outline.title,
            chapters=self.state.current_chapters
        )
        self.state.completed_novels.append(novel)
        
        # 保存小说内容
        self.save_novel(novel)
        
        # # 检查是否需要生成更多小说
        # if self.state.current_novel < self.state.novel_count:
        #     return self.start_novel_generation(None)
        # else:
        #     return self.generation_complete()
        return {
        "novel_title": novel.title,
        "chapter_count": len(novel.chapters),
        "completed": self.state.current_novel >= self.state.novel_count
    }

    @listen(generate_chapters)
    def check_completion(self, result):
        """检查是否完成所有小说生成"""
        if self.state.current_novel < self.state.novel_count:
            return self.start_novel_generation(None)
        else:
            return self.generation_complete()
        
    async def generate_single_chapter(self, novel_outline: NovelOutline, chapter_index: int, chapter_outline: ChapterOutline) -> Chapter:
        """生成单个章节"""
        print(f"正在生成第 {chapter_index+1} 章: {chapter_outline.title}")
        
        # 准备前文内容参考
        previous_chapters = ""
        if chapter_index > 0 and self.state.current_chapters:
            # 只使用最近的章节作为上下文，以避免上下文过长
            recent_chapters = self.state.current_chapters[:chapter_index]
            if recent_chapters:
                for recent_chapter in recent_chapters[-2:]:  # 只取最近的两章
                    previous_chapters += f"## {recent_chapter.title}\n\n"
                    previous_chapters += f"{recent_chapter.content}\n\n"
        
        # 执行章节创作任务
        result = ChapterWriterCrew().crew().kickoff(
            inputs={
                "novel_title": novel_outline.title,
                "chapter_title": chapter_outline.title,
                "chapter_description": chapter_outline.description,
                "chapter_words": self.state.chapter_words,
                "novel_outline": json.dumps(novel_outline.model_dump(), ensure_ascii=False),
                "previous_chapters": previous_chapters
            }
        )
        try:
            # 从结果中提取章节内容
            chapter = result.pydantic
        except Exception as e:
            print(f"自动转换失败，尝试手动解析: {e}")
            # 手动创建Chapter对象
            chapter = Chapter(
                title=chapter_outline.title,
                content=result.raw  # 直接使用原始文本
        )
        print(f"第 {chapter_index+1} 章《{chapter.title}》生成完成")
        
        return chapter
    
    def save_novel(self, novel: Novel):
        """保存小说到文件"""
        # 生成文件名
        filename = f"output/{self.state.novel_type}_小说_{self.state.current_novel}_{novel.title}.md"
        
        # 组合小说内容
        content = f"# {novel.title}\n\n"
        
        for i, chapter in enumerate(novel.chapters):
            content += f"## 第{i+1}章：{chapter.title}\n\n"
            content += f"{chapter.content}\n\n"
        
        # 保存到文件
        with open(filename, "w", encoding="utf-8") as f:
            f.write(content)
        
        print(f"小说《{novel.title}》已保存至: {filename}")
    
    def generation_complete(self):
        """生成完成，显示结果摘要"""
        print("\n===== 小说生成完成 =====\n")
        print(f"总共生成了 {len(self.state.completed_novels)} 篇 {self.state.novel_type} 小说：")
        
        for i, novel in enumerate(self.state.completed_novels, 1):
            print(f"{i}. 《{novel.title}》- {len(novel.chapters)} 章")
        
        print("\n所有小说已保存到 output/ 目录")
        return "小说生成完成"

def kickoff():
    """启动小说生成流程"""
    flow = NovelGenerationFlow()
    flow.kickoff()

def plot():
    """生成流程图"""
    flow = NovelGenerationFlow()
    flow.plot()

if __name__ == "__main__":
    kickoff()