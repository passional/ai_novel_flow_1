# src/novel_generation_crew/crews/chapter_writer_crew/chapter_writer_crew.py
from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task

from ...types import Chapter

@CrewBase
class ChapterWriterCrew:
    """爽文小说章节创作Crew"""
    
    agents_config = "config/agents.yaml"
    tasks_config = "config/tasks.yaml"
    
    @agent
    def chapter_writer(self) -> Agent:
        return Agent(
            config=self.agents_config["chapter_writer"],
            verbose=True
        )
    
    @agent
    def chapter_editor(self) -> Agent:
        return Agent(
            config=self.agents_config["chapter_editor"],
            verbose=True
        )
    
    @task
    def write_chapter(self) -> Task:
        return Task(
            config=self.tasks_config["write_chapter"]
        )
    
    @task
    def review_and_polish(self) -> Task:
        return Task(
            config=self.tasks_config["review_and_polish"],
            output_pydantic=Chapter
        )
    
    @crew
    def crew(self) -> Crew:
        """创建爽文小说章节创作团队"""
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True
        )