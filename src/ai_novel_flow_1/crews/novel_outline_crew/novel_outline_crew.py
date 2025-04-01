# from crewai import Agent, Crew, Process, Task
# from crewai.project import CrewBase, agent, crew, task

# # If you want to run a snippet of code before or after the crew starts,
# # you can use the @before_kickoff and @after_kickoff decorators
# # https://docs.crewai.com/concepts/crews#example-crew-class-with-decorators

# @CrewBase
# class NovelOutlineCrew():
#     """NovelOutlineCrew crew"""

#     # Learn more about YAML configuration files here:
#     # Agents: https://docs.crewai.com/concepts/agents#yaml-configuration-recommended
#     # Tasks: https://docs.crewai.com/concepts/tasks#yaml-configuration-recommended
#     agents_config = 'config/agents.yaml'
#     tasks_config = 'config/tasks.yaml'

#     # If you would like to add tools to your agents, you can learn more about it here:
#     # https://docs.crewai.com/concepts/agents#agent-tools
#     @agent
#     def researcher(self) -> Agent:
#         return Agent(
#             config=self.agents_config['researcher'],
#             verbose=True
#         )

#     @agent
#     def reporting_analyst(self) -> Agent:
#         return Agent(
#             config=self.agents_config['reporting_analyst'],
#             verbose=True
#         )

#     # To learn more about structured task outputs,
#     # task dependencies, and task callbacks, check out the documentation:
#     # https://docs.crewai.com/concepts/tasks#overview-of-a-task
#     @task
#     def research_task(self) -> Task:
#         return Task(
#             config=self.tasks_config['research_task'],
#         )

#     @task
#     def reporting_task(self) -> Task:
#         return Task(
#             config=self.tasks_config['reporting_task'],
#             output_file='report.md'
#         )

#     @crew
#     def crew(self) -> Crew:
#         """Creates the NovelOutlineCrew crew"""
#         # To learn how to add knowledge sources to your crew, check out the documentation:
#         # https://docs.crewai.com/concepts/knowledge#what-is-knowledge

#         return Crew(
#             agents=self.agents, # Automatically created by the @agent decorator
#             tasks=self.tasks, # Automatically created by the @task decorator
#             process=Process.sequential,
#             verbose=True,
#             # process=Process.hierarchical, # In case you wanna use that instead https://docs.crewai.com/how-to/Hierarchical/
#         )
# src/novel_generation_crew/crews/novel_outline_crew/novel_outline_crew.py
from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai_tools import SerperDevTool
from ...types import NovelOutline
#from novel_generation_crew.types import NovelOutline

@CrewBase
class NovelOutlineCrew:
    """爽文小说大纲生成Crew"""
    
    agents_config = "config/agents.yaml"
    tasks_config = "config/tasks.yaml"
    
    @agent
    def plot_designer(self) -> Agent:
        return Agent(
            config=self.agents_config["plot_designer"],
            verbose=True
        )
    
    @agent
    def character_designer(self) -> Agent:
        return Agent(
            config=self.agents_config["character_designer"],
            verbose=True
        )
    
    @agent
    def outline_creator(self) -> Agent:
        return Agent(
            config=self.agents_config["outline_creator"],
            verbose=True
        )
    
    @task
    def design_story(self) -> Task:
        return Task(
            config=self.tasks_config["design_story"]
        )
    
    @task
    def design_characters(self) -> Task:
        return Task(
            config=self.tasks_config["design_characters"]
        )
    
    @task
    def create_novel_outline(self) -> Task:
        return Task(
            config=self.tasks_config["create_novel_outline"],
            output_pydantic=NovelOutline
        )
    
    @crew
    def crew(self) -> Crew:
        """创建爽文小说大纲生成团队"""
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True
        )