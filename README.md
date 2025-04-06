# AI-Powered Product Recommendation Engine - Backend

This is the backend component of the AI-Powered Product Recommendation Engine take-home assignment. It provides a FastAPI API that interfaces with an LLM to generate personalized product recommendations based on user preferences and browsing history.

## Project Structure

```
backend/
│
├── app.py               # Main FastAPI application
├── requirements.txt     # Python dependencies
├── config.py            # Configuration (add your API keys here)
├── data/
│   └── products.json    # Sample product catalog
│
├── services/
│   ├── __init__.py
│   ├── llm_service.py   # Service for LLM interactions (implement this)
│   └── product_service.py  # Service for product data operations
│
└── README.md            # This file
```

## Setup Instructions

1. Create a virtual environment:
   ```
   python -m venv venv
   ```

2. Activate the virtual environment:
   - Windows: `venv\Scripts\activate`
   - macOS/Linux: `source venv/bin/activate`

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Create a `.env` file in the backend directory with your OpenAI API key:
   ```
   OPENAI_API_KEY=your_openai_api_key_here
   MODEL_NAME=gpt-3.5-turbo
   MAX_TOKENS=1000
   TEMPERATURE=0.7
   DATA_PATH=data/products.json
   ```

5. Run the application:
   ```
   uvicorn app:app --host 0.0.0.0 --port 5000 --reload
   ```

The server will start on `http://localhost:5000`. You can access the automatic API documentation at `http://localhost:5000/docs`.

## API Endpoints

### GET /api/products
Returns the full product catalog.

#### Response
```json
[
  {
    "id": "prod001",
    "name": "Ultra-Comfort Running Shoes",
    "category": "Footwear",
    "subcategory": "Running",
    "price": 89.99,
    "brand": "SportsFlex",
    "description": "...",
    "features": ["..."],
    "rating": 4.7,
    "inventory": 45,
    "tags": ["..."]
  },
  ...
]
```

### POST /api/recommendations
Generates personalized product recommendations based on user preferences and browsing history.

#### Request Body
```json
{
  "preferences": {
    "priceRange": "all", // Options: "0-50", "50-100", "100+", "all"
    "categories": ["Electronics", "Home"], // Array of category names
    "brands": ["SoundWave", "FitTech"] // Array of brand names
  },
  "browsing_history": ["prod002", "prod007"] // Array of product IDs
}
```

#### Response
```json
{
  "recommendations": [
    {
      "product": {
        "id": "prod009",
        "name": "Bluetooth Portable Speaker",
        "category": "Electronics",
        "subcategory": "Audio",
        "price": 69.99,
        "brand": "SoundWave",
        "description": "...",
        "features": ["..."],
        "rating": 4.4,
        "inventory": 50,
        "tags": ["..."]
      },
      "explanation": "Based on your interest in audio devices and the SoundWave brand...",
      "confidence_score": 8
    },
    ...
  ],
  "count": 5
}
```

## Implementation Tasks

As part of this assignment, you need to implement the following components:

### 1. LLM Service (services/llm_service.py)

The LLM service is responsible for generating personalized product recommendations. You need to implement:

- **`_create_recommendation_prompt`**: Design an effective prompt for the LLM that:
  - Incorporates user preferences (categories, price range, brands)
  - Leverages browsing history to understand user interests
  - Provides context about the available products
  - Specifies the expected response format

- **`_parse_recommendation_response`**: Parse the LLM's response to extract:
  - Product recommendations
  - Explanations for each recommendation
  - Confidence scores (if applicable)

Focus on prompt engineering to get relevant, accurate recommendations with meaningful explanations.

### 2. Error Handling

Implement robust error handling throughout the API, including:
- Invalid input validation
- LLM API error handling
- Graceful error responses

## Testing Your Implementation

A test script (`candidate_test.py`) is provided in the root directory to help you test your implementation. Run it after starting your Flask server:

```
python candidate_test.py
```

## Evaluation Criteria

Your backend implementation will be evaluated based on:

1. **Prompt Engineering Quality (50%)**
   - Effectiveness of prompts in generating relevant recommendations
   - Context handling and optimization
   - Clarity and usefulness of recommendation explanations

2. **API Design and Implementation (30%)**
   - RESTful API design and implementation
   - Error handling and edge cases
   - Response time and efficiency

3. **Code Quality (20%)**
   - Code readability and organization
   - Documentation and comments
   - Error handling approaches

## Tips for Success

- **Focus on prompt engineering**: This is the most critical part of the assignment. Consider how to structure your prompts to get the best recommendations.
- **Test with various scenarios**: Try different combinations of preferences and browsing history to ensure your implementation adapts well.
- **Consider token limitations**: Be mindful of the LLM's context window limitations when designing your prompts.
- **Document your approach**: In addition to code comments, consider adding a section in your project README explaining your prompt engineering strategy.