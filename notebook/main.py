from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# Initialize FastAPI app
app = FastAPI()

# Enable CORS for frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Update with your frontend URL in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request model for multiple URLs and question
class URLRequest(BaseModel):
    urls: list[str]
    question: str

# Initialize Gemini model via LangChain
llm = ChatGoogleGenerativeAI(
    model="gemini-1.5-flash",
    google_api_key=GOOGLE_API_KEY,
    temperature=0.7
)

# Define prompt template for processing URLs and question
prompt_template = PromptTemplate(
    input_variables=["urls", "question"],
    template="Given the following URLs: {urls}\nAnswer the question: {question}"
)

@app.post("/process-url")
async def process_url(request: URLRequest):
    try:
        # Create LangChain chain
        chain = prompt_template | llm
        # Format URLs as a comma-separated string
        urls_str = ", ".join(request.urls) if request.urls else "No URLs provided"
        # Invoke the chain with URLs and question
        result = chain.invoke({"urls": urls_str, "question": request.question})
        return {"urls": request.urls, "question": request.question, "result": result.content}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing input: {str(e)}")

@app.get("/")
def menar_root():
    return {"message": "Gen AI URL Processor API"}