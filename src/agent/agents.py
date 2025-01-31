from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task, after_kickoff

from src.agent.tools import search_tool
from crewai_tools import SerperDevTool

from langchain_openai import ChatOpenAI

from typing import List

from pydantic import BaseModel

class PredictionResponse(BaseModel):
    answer: int
    reasoning: str
    sources: List[str]


@CrewBase
class ITMOCrew:
    agents_config = 'config/agents.yaml'
    tasks_config = 'config/tasks.yaml'

    def __init__(self):
        self.model: ChatOpenAI | None = None
        self.serper_dev_tool = SerperDevTool(
            country="ru",
            locale="ru",
            location="Russia",
            n_results=5,
        )

    def init_model(self, model: ChatOpenAI):
        self.model = model

    @agent
    def researcher(self) -> Agent:
        return Agent(
            config=self.agents_config['researcher'],
            tools=[search_tool, self.serper_dev_tool],
            verbose=False,
            memory=True,
            llm=self.model
        )

    @task
    def research_task(self) -> Task:
        return Task(
            config=self.tasks_config['research_task'],
            agent=self.researcher(),
            output_json=PredictionResponse,
            async_execution=True,
        )

    @crew
    def crew(self) -> Crew:
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=False,
            async_execution=True,
            cache=True,
        )
