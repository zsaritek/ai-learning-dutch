# Dutch Language Learning Agent

A collaborative AI system that helps users learn Dutch through contextualized storytelling and multi-agent coordination.

## 🌟 Overview

This project demonstrates an advanced application of LLM agents working together to create educational content. The system helps Dutch language learners by generating simple, contextually relevant paragraphs tailored to their proficiency level, with vocabulary drawn from a searchable knowledge base.

The agent coordination approach showcases how multiple specialized AI agents can collaborate to produce high-quality educational content that's both engaging and appropriate for the learner's level.

## 🤖 Agent Architecture

The system employs three specialized agents working together:

### 1. Searcher Agent
- Receives topic and proficiency level from user input
- Searches a knowledge base of Dutch vocabulary
- Uses DuckDuckGo web search when needed for additional context
- Compiles relevant vocabulary words with English translations
- Adapts vocabulary complexity to user's proficiency level

### 2. Writer Agent
- Takes vocabulary from Searcher agent
- Creates a coherent short story incorporating key vocabulary
- Ensures grammar and complexity match the specified level
- Provides both Dutch text and English translations
- Maintains natural language flow while using provided vocabulary

### 3. Editor Team (Coordinator)
- Manages workflow between Searcher and Writer agents
- Orchestrates the full response generation process
- Ensures output meets the 5-sentence requirement
- Formats content according to specified structure
- Provides final quality control

## ⚙️ Technical Implementation

### Built With
- **FastAPI**: Web framework for the API endpoints
- **Agno AI Framework**: For agent creation and coordination
- **OpenAI Models**: Powers the language understanding and generation
- **PostgreSQL with pgvector**: Vector database for knowledge storage
- **DuckDuckGo Tools**: Web search capabilities for vocabulary lookup

### Knowledge Base
The system uses a searchable knowledge base created from Dutch language learning materials:
- PDF-based Dutch vocabulary (1000 common Dutch words)
- Vector embeddings for semantic search
- Persistent storage in PostgreSQL

## 📝 API Usage

### Running the Server
```
uvicorn main:app --reload
```

### Endpoints

#### GET /ask
Generate Dutch language content based on a user query.

**Parameters:**
- `query`: Your request including topic and proficiency level
- `format`: Response format (`text` or `json`, default is `text`)

**Examples:**
```
# For readable text output:
http://localhost:8000/ask?query="Tell me a simple story about a football match in Dutch. I am a beginner learner."

# For structured JSON output:
http://localhost:8000/ask?query="Tell me a simple story about a football match in Dutch. I am a beginner learner."&format=json
```

## 🔍 Sample Output

### Text Format
```
**Dutch Paragraph (5 sentences):**
Jan gaat naar een voetbalwedstrijd met zijn vriend. Hij ziet de spelers op het veld rennen. De keeper stopt de bal met zijn handen. Het team scoort een doelpunt en iedereen juicht. Na de wedstrijd gaan ze naar huis.

**English Translation:**
Jan goes to a football match with his friend. He sees the players running on the field. The goalkeeper stops the ball with his hands. The team scores a goal and everyone cheers. After the match, they go home.

**Key Vocabulary:**
- voetbalwedstrijd: football match
- spelers: players
- veld: field
- keeper: goalkeeper
- bal: ball
- doelpunt: goal
- juicht: cheers
```

### JSON Format
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
  "level": "beginner",
  "vocabulary": [
    {"dutch": "voetbalwedstrijd", "english": "football match"},
    {"dutch": "spelers", "english": "players"},
    {"dutch": "veld", "english": "field"},
    {"dutch": "keeper", "english": "goalkeeper"},
    {"dutch": "bal", "english": "ball"},
    {"dutch": "doelpunt", "english": "goal"},
    {"dutch": "juicht", "english": "cheers"}
  ]
}
```

## 🚀 Future Enhancements

- Expand knowledge base to include more Dutch learning resources
- Add pronunciation guidance for vocabulary words
- Implement user profiles to track learning progress
- Develop interactive exercises based on generated content
- Add support for themed vocabulary sets (travel, food, etc.)

## 🧩 How It Works Under the Hood

This project demonstrates several advanced concepts in LLM agent design:

1. **Agent Specialization**: Each agent has a focused role with specific instructions
2. **Collaborative Workflow**: Team coordination enables sequential processing
3. **Structured Outputs**: Pydantic models ensure consistent, well-formatted responses
4. **Knowledge Integration**: Combining embedded knowledge with web search capabilities
5. **Adaptive Content**: Content difficulty adjusts based on user's proficiency level

## 📋 Requirements

- Python 3.9+
- PostgreSQL with pgvector extension
- OpenAI API key
- Docker (optional, for database)

## 🔧 Setup

1. Clone the repository
2. Install dependencies: `pip install -r requirements.txt`
3. Set environment variables:
   - `OPENAI_API_KEY`: Your OpenAI API key
   - `OPENAI_MODEL`: Model to use (default: "gpt-4o")
4. Start the PostgreSQL database (Docker recommended)
5. Run the server: `uvicorn main:app --reload`

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.