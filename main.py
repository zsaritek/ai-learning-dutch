"""
# Dutch Language Learning Agent

A collaborative AI system that helps users learn Dutch through contextualized storytelling.

## How It Works

This application uses a team of specialized agents to generate Dutch language content:

1. **Searcher Agent**: Finds relevant Dutch vocabulary based on a topic and proficiency level
   - First searches a knowledge base of Dutch words
   - Uses DuckDuckGo to find additional vocabulary if needed

2. **Writer Agent**: Creates a short story using vocabulary from the Searcher
   - Incorporates vocabulary into a coherent narrative
   - Adjusts complexity based on user's proficiency level

3. **Editor Team**: Coordinates the process and formats the final output
   - Manages the workflow between agents
   - Edits the final story into exactly 5 Dutch sentences with English translations

## Usage

Run the server:
```
uvicorn main:app --reload
```

Access the API with a query:
```
# For text output (default):
http://localhost:8000/ask?query="Tell me a simple story about a football match in Dutch. I am a beginner learner."

# For JSON output:
http://localhost:8000/ask?query="Tell me a simple story about a football match in Dutch. I am a beginner learner."&format=json
```

## Example Output

### Text Format:
```
**Dutch Paragraph (5 sentences):**
Jan gaat naar een voetbalwedstrijd met zijn vriend. Hij ziet de spelers op het veld rennen. De keeper stopt de bal met zijn handen. Het team scoort een doelpunt en iedereen juicht. Na de wedstrijd gaan ze naar huis.

**English Translation:**
Jan goes to a football match with his friend. He sees the players running on the field. The goalkeeper stops the ball with his hands. The team scores a goal and everyone cheers. After the match, they go home.
```

### JSON Format:
```json
{
  "dutch_sentences": [
    "Jan gaat naar een voetbalwedstrijd met zijn vriend",
    "Hij ziet de spelers op het veld rennen",
    "De keeper stopt de bal met zijn handen",
    "Het team scoort een doelpunt en iedereen juicht",
    "Na de wedstrijd gaan ze naar huis"
  ],
  "english_translations": [
    "Jan goes to a football match with his friend",
    "He sees the players running on the field",
    "The goalkeeper stops the ball with his hands",
    "The team scores a goal and everyone cheers",
    "After the match, they go home"
  ],
  "topic": "football match",
  "level": "beginner"
}
```

## Database
- PostgreSQL with pgvector extension (runs in Docker)
- Connection: postgresql://ai:ai@localhost:5532/ai
"""

from fastapi import FastAPI, Query
from fastapi.responses import PlainTextResponse, JSONResponse
from textwrap import dedent
from typing import List, Optional

from agno.agent import Agent, RunResponse
from agno.models.openai import OpenAIChat
from agno.knowledge.pdf_url import PDFUrlKnowledgeBase
from agno.vectordb.pgvector import PgVector
from agno.tools.duckduckgo import DuckDuckGoTools
from agno.embedder.openai import OpenAIEmbedder
from agno.team.team import Team
from pydantic import BaseModel, Field

import os

app = FastAPI(
    title="Dutch Language Learning API",
    description="An API that generates Dutch language learning content through contextualized storytelling",
    version="1.0.0"
)


class DutchVocabulary(BaseModel):
    """Represents a Dutch vocabulary word with its English translation."""
    dutch: str = Field(..., description="Dutch word")
    english: str = Field(..., description="English translation")


class DutchParagraph(BaseModel):
    """Structured output model for Dutch language learning content."""
    dutch_sentences: List[str] = Field(
        ...,
        description="Exactly 5 Dutch sentences forming a coherent paragraph about the requested topic."
    )
    english_translations: List[str] = Field(
        ...,
        description="English translations of the 5 Dutch sentences, in the same order."
    )
    topic: str = Field(
        ...,
        description="The topic of the Dutch paragraph."
    )
    level: str = Field(
        ..., 
        description="The Dutch proficiency level for which this content is intended."
    )
    vocabulary: List[DutchVocabulary] = Field(
        ...,
        description="List of key vocabulary words used in the Dutch sentences with their English translations."
    )


# Configure database and knowledge base
db_url = "postgresql+psycopg://ai:ai@localhost:5532/ai"

knowledge_base = PDFUrlKnowledgeBase(
    urls=["https://www.learndutch.org/wp-content/uploads/2014/06/e-book-lesson-1-20-1000DutchWords.pdf"],
    vector_db=PgVector(
        table_name="1000-dutch-words", 
        db_url=db_url,
        embedder=OpenAIEmbedder(id="text-embedding-3-small")),
)

# Check if knowledge base needs to be loaded
if os.getenv("IS_KNOWLEDGE_BASE_LOADED") != "true":
    # Load the knowledge base: IF NOT LOADED, RECREATE AND UPSERT
    knowledge_base.load(recreate=True, upsert=True)
    os.environ["IS_KNOWLEDGE_BASE_LOADED"] = "true"


# Searcher Agent
searcher = Agent(
    name="Searcher",
    role="Vocabulary Finder",
    model=OpenAIChat(id=os.getenv("OPENAI_MODEL", "gpt-4o")),
    instructions=dedent("""\
        You are an expert vocabulary finder for Dutch language learners.
        Your task is to identify relevant Dutch vocabulary based on a given topic and proficiency level.
        
        1. Receive the user's request which includes the topic (e.g., 'football match') and proficiency level.
        2. First, search the available knowledge base for relevant vocabulary words related to the topic.
        3. If the knowledge base yields insufficient results, use the DuckDuckGo search tool to find appropriate
           vocabulary words online.
        4. Compile a list of 10-15 key vocabulary words (Dutch word, English meaning) relevant to the topic and level.
        5. For beginners: focus on basic, everyday words
           For intermediate: include some more specific terminology
           For advanced: include idiomatic expressions and specialized vocabulary
           
        Format each vocabulary word clearly as: "Dutch word: English translation"
        
        Focus ONLY on finding and listing vocabulary. Do not write stories or explanations.
    """),      
    description="Searches for relevant Dutch vocabulary based on topic and proficiency level.",
    tools=[DuckDuckGoTools()],
    markdown=True,
    debug_mode=True,
    knowledge=knowledge_base,
)


# Writer Agent
writer = Agent(
    name="Writer",
    role="Dutch Story Writer",
    model=OpenAIChat(id=os.getenv("OPENAI_MODEL", "gpt-4o")),
    instructions=dedent("""\
        You are a creative writer specializing in crafting simple Dutch stories for language learners.
        Your task is to write a short, engaging story using provided vocabulary words.
        
        1. Receive a list of Dutch vocabulary words, the original topic, and the user's proficiency level.
        2. Write a very simple short story in Dutch related to the topic.
        3. The story must be EXACTLY 5 sentences long - no more, no less.
        4. Incorporate at least 5-7 of the provided vocabulary words naturally into the story.
        5. Ensure the story's complexity matches the specified proficiency level:
           - Beginner: Simple present tense, basic sentence structure
           - Intermediate: Some past tense, compound sentences
           - Advanced: More complex grammar, idiomatic expressions
        6. Provide English translations for each sentence.
        7. List the key vocabulary words used in the story with their translations.
        
        Do not include periods at the end of sentences in your structured output - they will be added during formatting.
        Do not define words within the story or add explanations.
    """),
    description="Writes a short, simple Dutch story based on provided vocabulary.",
    markdown=True,
    debug_mode=True,
)


# Editor Team
editor = Team(
    name="Editor",
    mode="coordinate",
    model=OpenAIChat(id=os.getenv("OPENAI_MODEL", "gpt-4o")),
    members=[searcher, writer],
    instructions=dedent("""\
        You are the coordinator for a Dutch language learning system.
        Your job is to orchestrate the Searcher and Writer agents to create a 5-sentence Dutch paragraph.
        
        Workflow:
        1. Extract the topic and proficiency level from the user's query
        2. Direct the Searcher to find relevant Dutch vocabulary for the topic and level
        3. Direct the Writer to create a story using those words
        4. Compile the final output in the structured format
        
        Final output requirements:
        - Exactly 5 Dutch sentences (no more, no less)
        - Each sentence must be grammatically correct and appropriate for the user's level
        - Each sentence must have an accurate English translation
        - Include a list of vocabulary words used in the story
        
        Output structure:
        - dutch_sentences: List of 5 Dutch sentences (without periods - they will be added in formatting)
        - english_translations: List of 5 corresponding English translations (without periods)
        - topic: The identified topic from the query
        - level: The identified proficiency level (beginner, intermediate, or advanced)
        - vocabulary: List of vocabulary objects with "dutch" and "english" fields
    """),
    description="Coordinates Searcher and Writer agents to create Dutch learning content.",
    response_model=DutchParagraph,
    use_json_mode=True,
    markdown=True,
    debug_mode=True,
)


@app.get("/", response_class=PlainTextResponse)
async def root():
    return """
    Dutch Language Learning API
    --------------------------
    Access the API at /ask with a 'query' parameter.
    Example: /ask?query="Tell me a story about a cat in Dutch. I am a beginner."
    
    Options:
    - format: Set to "json" for JSON output (default is "text")
    
    Documentation available at /docs
    """


@app.get("/ask")
async def ask(
    query: str = Query(..., description="Your request including topic and proficiency level"),
    format: str = Query("text", description="Response format: 'text' or 'json'")
):
    """Generate Dutch language learning content based on the query."""
    
    # Run the editor team to generate content
    response: RunResponse = editor.run(query)
    
    # Get structured content
    content = response.content
    
    if format.lower() == "json":
        # Return JSON response
        return content
    else:
        # Format as plain text for human readability
        dutch_sentences = content.dutch_sentences
        english_translations = content.english_translations
        vocabulary = content.vocabulary
        
        # Format text response
        formatted_text = "**Dutch Paragraph (5 sentences):**\n"
        formatted_text += ". ".join(dutch_sentences) + ".\n\n"
        
        formatted_text += "**English Translation:**\n"
        formatted_text += ". ".join(english_translations) + ".\n\n"
        
        formatted_text += "**Key Vocabulary:**\n"
        for word in vocabulary:
            formatted_text += f"- {word.dutch}: {word.english}\n"
        
        return PlainTextResponse(formatted_text)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)