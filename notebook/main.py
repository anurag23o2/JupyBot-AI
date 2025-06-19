from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
from dotenv import load_dotenv
from newspaper import Article
import os

# Load env
load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# FastAPI app
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class URLRequest(BaseModel):
    urls: list[str]
    question: str

# Gemini model
llm = ChatGoogleGenerativeAI(
    model="gemini-1.5-flash",
    google_api_key=GOOGLE_API_KEY,
    temperature=0.7
)

# Updated Prompt Template
prompt_template = PromptTemplate(
    input_variables=["content", "question"],
    template="""
You are a helpful assistant. Based on the following content extracted from news articles:
{content}

Answer the question: {question}
"""
)

# Fetch and extract article text from URLs
def extract_text_from_urls(urls: list[str]) -> str:
    all_text = []
    for url in urls:
        try:
            article = Article(url)
            article.download()
            article.parse()
            all_text.append(f"From {url}:\n{article.text}")
        except Exception as e:
            all_text.append(f"Failed to extract content from {url}: {str(e)}")
    return "\n\n".join(all_text)

@app.post("/process-url")
async def process_url(request: URLRequest):
    try:
        # Step 1: Extract text content from URLs
        content = extract_text_from_urls(request.urls)

        # Step 2: Create prompt with content and question
        chain = prompt_template | llm
        result = chain.invoke({"content": content, "question": request.question})

        return {"urls": request.urls, "question": request.question, "result": result.content}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing input: {str(e)}")

@app.get("/")
def root():
    return {"message": "Gen AI URL Processor API"}
