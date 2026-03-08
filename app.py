from contextlib import asynccontextmanager
from fastapi import FastAPI, UploadFile, File
from pydantic import BaseModel
from starlette.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
import uvicorn
import pandas as pd
import numpy as np
from PIL import Image
import io
import torch
import os
import torchvision.models as models
from torchvision import transforms
from transformers import AutoTokenizer, AutoModel
import faiss


df = None
image_index = None
text_index = None
images_path = r"C:\Users\chirag\OneDrive\Desktop\fashion\data\images"
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

# Image embedding model
model = models.resnet50(pretrained=True)
model = torch.nn.Sequential(*list(model.children())[:-1])
model.eval().to(device)

# Image preprocessing
transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
])

# Text embedding model
tokenizer = AutoTokenizer.from_pretrained('sentence-transformers/all-MiniLM-L6-v2')
text_model = AutoModel.from_pretrained('sentence-transformers/all-MiniLM-L6-v2').to(device)

def get_image_embedding(image_bytes):
    img = Image.open(io.BytesIO(image_bytes)).convert('RGB')
    img = transform(img).unsqueeze(0).to(device)
    with torch.no_grad():
        emb = model(img).squeeze().cpu().numpy().flatten()
    return emb

def get_text_embedding(text_query):
    inputs = tokenizer(text_query, return_tensors='pt', truncation=True, padding=True).to(device)
    with torch.no_grad():
        outputs = text_model(**inputs)
    emb = outputs.last_hidden_state.mean(dim=1).squeeze().cpu().numpy()
    return emb

#Lifespan Event Handler 
@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Application is starting up...")
    global df, image_index, text_index
    try:
        csv_path = r"C:\Users\chirag\OneDrive\Desktop\fashion\data\styles.csv"
        df = pd.read_csv(csv_path, on_bad_lines='skip')
        df['image'] = df['id'].astype(str) + '.jpg'
        available_files = set(os.listdir(images_path))
        df = df[df['image'].isin(available_files)].reset_index(drop=True)
        image_embeddings = np.load(r"C:\Users\chirag\OneDrive\Desktop\fashion\data\image_embeddings.npy")
        text_embeddings = np.load(r"C:\Users\chirag\OneDrive\Desktop\fashion\data\text_embeddings.npy")
        image_index = faiss.IndexFlatL2(2048)
        image_index.add(image_embeddings.astype('float32'))
        text_index = faiss.IndexFlatL2(384)
        text_index.add(text_embeddings.astype('float32'))
        print("Data and models loaded successfully!")
    except Exception as e:
        print(f"ERROR during startup: {e}")
        raise e
    
    yield

    print("Application is shutting down.")

app = FastAPI(lifespan=lifespan)

if os.path.exists(images_path):
    app.mount("/images", StaticFiles(directory=images_path), name="images")
else:
    print(f"Warning: The images directory '{images_path}' was not found. Images will not be served.")

#API Endpoints
@app.get("/", response_class=HTMLResponse)
async def serve_app():
    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Fashion Search</title>
        <script src="https://cdn.tailwindcss.com"></script>
        <style>
            body {
                font-family: 'Inter', sans-serif;
                background-color: #f4f4f4;
            }
            .container {
                max-width: 960px;
                margin: 0 auto;
            }
            .image-card {
                background-color: white;
                border-radius: 12px;
                box-shadow: 0 4px 6px rgba(0,0,0,0.1);
                overflow: hidden;
                transition: transform 0.2s;
            }
            .image-card:hover {
                transform: scale(1.03);
            }
        </style>
    </head>
    <body class="bg-gray-100 min-h-screen p-8">
        <div class="container mx-auto">
            <h1 class="text-4xl font-bold text-center text-gray-800 mb-2">Fashion Search</h1>
            <p class="text-center text-gray-600 mb-8">Search for similar fashion items using text or an image.</p>
            <div class="bg-white p-8 rounded-xl shadow-lg mb-8">
                <h2 class="text-2xl font-semibold mb-4 text-gray-700">Search by Text</h2>
                <div class="flex items-center space-x-4">
                    <input type="text" id="text-query" placeholder="e.g., 'pink floral dress'" class="flex-grow p-3 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500">
                    <button id="text-search-btn" class="bg-blue-600 hover:bg-blue-700 text-white font-bold py-3 px-6 rounded-lg shadow-md transition-colors">Search</button>
                </div>
            </div>
            <div class="bg-white p-8 rounded-xl shadow-lg mb-8">
                <h2 class="text-2xl font-semibold mb-4 text-gray-700">Search by Image</h2>
                <div class="flex flex-col space-y-4">
                    <input type="file" id="image-upload" accept="image/*" class="p-3 border rounded-lg file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100">
                    <button id="image-search-btn" class="bg-blue-600 hover:bg-blue-700 text-white font-bold py-3 px-6 rounded-lg shadow-md transition-colors">Search</button>
                </div>
            </div>
            <div id="results" class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6">
                <!-- Search results will be displayed here -->
            </div>
        </div>
        <script>
            const textQueryInput = document.getElementById('text-query');
            const textSearchBtn = document.getElementById('text-search-btn');
            const imageUploadInput = document.getElementById('image-upload');
            const imageSearchBtn = document.getElementById('image-search-btn');
            const resultsContainer = document.getElementById('results');
            const BASE_URL = 'http://127.0.0.1:8000';
            async function searchText() {
                const query = textQueryInput.value;
                if (!query) return;
                resultsContainer.innerHTML = '<p class="text-center text-gray-500">Searching...</p>';
                try {
                    const response = await fetch(`${BASE_URL}/search_by_text`, {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ query: query, top_k: 5 })
                    });
                    if (!response.ok) {
                        throw new Error('Network response was not ok');
                    }
                    const data = await response.json();
                    displayResults(data.results);
                } catch (error) {
                    resultsContainer.innerHTML = `<p class="text-red-500 text-center">Error: ${error.message}</p>`;
                    console.error('Error:', error);
                }
            }
            async function searchImage() {
                const file = imageUploadInput.files[0];
                if (!file) return;
                resultsContainer.innerHTML = '<p class="text-center text-gray-500">Uploading and searching...</p>';
                const formData = new FormData();
                formData.append('file', file);
                formData.append('top_k', 5);
                try {
                    const response = await fetch(`${BASE_URL}/search_by_image`, {
                        method: 'POST',
                        body: formData
                    });
                    if (!response.ok) {
                        throw new Error('Network response was not ok');
                    }
                    const data = await response.json();
                    displayResults(data.results);
                } catch (error) {
                    resultsContainer.innerHTML = `<p class="text-red-500 text-center">Error: ${error.message}</p>`;
                    console.error('Error:', error);
                }
            }
            function displayResults(results) {
                resultsContainer.innerHTML = '';
                if (results.length === 0) {
                    resultsContainer.innerHTML = '<p class="text-center text-gray-500">No results found.</p>';
                    return;
                }
                results.forEach(item => {
                    const imageUrl = `${BASE_URL}${item['image_url']}`;
                    const cardHtml = `
                        <div class="image-card p-4 flex flex-col items-center text-center">
                            <img src="${imageUrl}" alt="${item['name']}" class="rounded-lg mb-4 w-full h-48 object-cover">
                            <h3 class="font-bold text-gray-800">${item['name']}</h3>
                            <p class="text-sm text-gray-500">${item['category']} - ${item['gender']}</p>
                        </div>
                    `;
                    resultsContainer.innerHTML += cardHtml;
                });
            }
            textSearchBtn.addEventListener('click', searchText);
            imageSearchBtn.addEventListener('click', searchImage);
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)

class TextQuery(BaseModel):
    query: str
    top_k: int = 5

@app.post("/search_by_text")
async def search_by_text(query: TextQuery):
    query_emb = get_text_embedding(query.query)
    D, I = text_index.search(np.expand_dims(query_emb, axis=0).astype('float32'), k=query.top_k)
    
    results = []
    for idx in I[0]:
        row = df.iloc[idx]
        results.append({
            "id": int(row['id']),
            "name": row['productDisplayName'],
            "category": row['masterCategory'],
            "gender": row['gender'],
            # This is the corrected line
            "image_url": f"/images/{row['image']}" 
        })
    return {"results": results}

@app.post("/search_by_image")
async def search_by_image(file: UploadFile = File(...), top_k: int = 5):
    image_bytes = await file.read()
    query_emb = get_image_embedding(image_bytes)
    D, I = image_index.search(np.expand_dims(query_emb, axis=0).astype('float32'), k=top_k)

    results = []
    for idx in I[0]:
        row = df.iloc[idx]
        results.append({
            "id": int(row['id']),
            "name": row['productDisplayName'],
            "category": row['masterCategory'],
            "gender": row['gender'],
            # This is the corrected line
            "image_url": f"/images/{row['image']}"
        })
    return {"results": results}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
