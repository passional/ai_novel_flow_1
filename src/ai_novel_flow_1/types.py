# src/novel_generation_crew/types.py
from typing import List
from pydantic import BaseModel

class ChapterOutline(BaseModel):
    """章节大纲"""
    title: str  # 章节标题
    description: str  # 章节内容描述

class NovelOutline(BaseModel):
    """小说大纲"""
    title: str  # 小说标题
    chapters: List[ChapterOutline]  # 章节列表
    structure: str  # 小说架构
    role: str  # 角色设定

class Chapter(BaseModel):
    """小说章节"""
    title: str  # 章节标题
    content: str  # 章节内容

class Novel(BaseModel):
    """完整小说"""
    title: str  # 小说标题
    chapters: List[Chapter]  # 章节列表