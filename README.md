# 👗 AI Fashion Search Engine

An AI-powered fashion search engine that retrieves similar fashion products using **text queries** or **image inputs**.
The system uses **deep learning embeddings** and **FAISS similarity search** to find visually or semantically similar fashion items.

---

## 🚀 Features

* 🔍 **Text-based search**
  Search fashion products using natural language queries like *"red floral dress"*.

* 🖼 **Image-based search**
  Upload an image to find visually similar fashion items.

* ⚡ **Fast similarity search**
  Uses **FAISS (Facebook AI Similarity Search)** for efficient nearest neighbor retrieval.

* 🧠 **Deep learning embeddings**

  * ResNet50 for image embeddings
  * Sentence Transformers for text embeddings

* 🌐 **Interactive interface**

  * FastAPI backend
  * Streamlit frontend

---

## 🏗️ Project Architecture

User Query (Text / Image)
↓
Embedding Model
↓
Vector Embedding
↓
FAISS Similarity Search
↓
Top-K Similar Fashion Items

---

## 🛠 Tech Stack

* Python
* PyTorch
* FastAPI
* Streamlit
* FAISS
* Transformers (Sentence Transformers)
* ResNet50 (Image Embeddings)

---

## 📂 Project Structure

fashion-search-engine
│
├── app.py                 # FastAPI backend
├── streamlit.py           # Streamlit UI
├── Fashion_search.ipynb   # Notebook for generating embeddings
├── .gitignore
└── README.md

---

## ⚙️ Installation

Clone the repository:

git clone https://github.com/chiragsadhwani-ai/fashion-search-engine.git
cd fashion-search-engine

Install dependencies:

pip install -r requirements.txt

---

## ▶️ Running the Project

### Start the FastAPI server

python app.py

---

### Start the Streamlit interface

streamlit run streamlit.py

This will open a web interface where you can:

* search using text
* upload images for similarity search

---

## 📊 Dataset

This project uses the **Fashion Product Images Dataset**.

Dataset source:

https://www.kaggle.com/datasets/paramaggarwal/fashion-product-images-dataset

Note:
The dataset is **not included in this repository due to GitHub size limits**.

---

## 🔮 Future Improvements

* Deploy the application using Docker
* Use CLIP embeddings for better multimodal search
* Add a recommendation system
* Build a React frontend

---

## 👨‍💻 Author

**Chirag Sadhwani**

MSc Data Analytics
International Institute for Population Sciences (IIPS), Mumbai

GitHub:
https://github.com/chiragsadhwani-ai

---

## ⭐ Support

If you like this project, give it a **star ⭐** on GitHub.
