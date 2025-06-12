"""Agentic workflow module for Excel Query Bot.

Classes:
    AppReact: Main ReAct agent class for SQL query generation and execution.
"""

from src.agents.tools import SqlQueryTool
from langchain.agents import AgentType, initialize_agent


class AppReact():
    """ReAct agent for natural language to SQL query conversion and execution.
    
    Attributes:
        generator: The language model instance (e.g., AzureChatOpenAI) used for reasoning.
        text_db: Database interface with SQLAlchemy engine for query execution.
        tools (list): List of LangChain-compatible tools (currently only SqlQueryTool).
        agent_chain: Initialized LangChain agent configured with ReAct pattern.
        
    """
    def __init__(
        self,
        generator,
        text_db,
        **kwargs,
    ):
        """Initialize the ReAct agent with language model and database components.
        
        Args:
            generator: Language model instance for query interpretation and reasoning.
            text_db: Database interface object with a SQLAlchemy engine attribute.
            **kwargs: Additional keyword arguments for future extensibility.

        """
        self.generator = generator
        self.text_db = text_db
        self.tools = [
            SqlQueryTool(generator=self.generator, text_db=self.text_db),
        ]
        self.agent_chain = initialize_agent(
            self.tools,
            self.generator,
            handle_parsing_errors=True,
            agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
            return_intermediate_steps=True,
            max_iterations=2,
            verbose=True,
        )

    def execute(self, prompt):
        """Execute a natural language query and return raw database results.
        
        Args:
            prompt (str): Natural language query about the Excel data.
                         
        Returns:
            dict: Response dictionary with the following structure:
                - 'output': Raw query results as returned by SqlQueryTool
                - 'intermediate_steps': List of agent reasoning steps for debugging
                
        """
        response = self.agent_chain(prompt)
        
        if 'intermediate_steps' in response and response['intermediate_steps']:
            for step in response['intermediate_steps']:
                # Each step is a tuple of (AgentAction, observation)
                if len(step) >= 2:
                    action, observation = step
                    # Check if this step used the sql_query tool
                    if hasattr(action, 'tool') and action.tool == 'sql_query':
                        # Return the raw query results directly
                        return {
                            'output': observation,
                            'intermediate_steps': response.get('intermediate_steps', [])
                        }
        
        # Fallback to original response if no sql_query tool was used
        return response
