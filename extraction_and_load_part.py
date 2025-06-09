import os
import fitz  # PyMuPDF
import easyocr
from PIL import Image
import uuid
import io
import numpy as np
from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient
from qdrant_client.http.models import VectorParams, Distance, PointStruct

# --- CONFIG ---
PDF_DIR = "/home/espark/Documents/AI_chatbot_for_hydrogen/pdfs"
CHUNK_SIZE = 1000
OVERLAP = 100
COLLECTION_NAME = "pdf_chunks"
CHECKPOINT_FILE = "processed_files.txt"

# --- SETUP ---
embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
reader = easyocr.Reader(['en'])

# Qdrant client (remote version via HTTP)
qdrant = QdrantClient(host="localhost", port=6333)  # use actual IP if on remote server

# Create collection if it doesn't exist
embedding_dim = 384  # for 'all-MiniLM-L6-v2'
existing_collections = [col.name for col in qdrant.get_collections().collections]
if COLLECTION_NAME not in existing_collections:
    qdrant.recreate_collection(
        collection_name=COLLECTION_NAME,
        vectors_config=VectorParams(size=embedding_dim, distance=Distance.COSINE),
    )


def extract_text_from_pdf(pdf_path):
    doc = fitz.open(pdf_path)
    extracted_text = []

    for page_number, page in enumerate(doc):
        text = page.get_text()
        extracted_text.append(f"\n--- Page {page_number + 1} ---\n{text}")

        for img_index, img in enumerate(page.get_images(full=True)):
            xref = img[0]
            base_image = doc.extract_image(xref)
            image_bytes = base_image["image"]
            image = Image.open(io.BytesIO(image_bytes))
            image_np = np.array(image)
            ocr_results = reader.readtext(image_np)
            diagram_text = " ".join([res[1] for res in ocr_results])
            extracted_text.append(f"\n[Diagram on Page {page_number + 1}, Image {img_index + 1}]\n{diagram_text.strip()}\n")

    return "\n".join(extracted_text)


def chunk_text(text, chunk_size=CHUNK_SIZE, overlap=OVERLAP):
    chunks, start = [], 0
    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])
        start += chunk_size - overlap
    return chunks


def process_single_pdf(pdf_path):
    print(f"Processing {pdf_path} ...")
    text = extract_text_from_pdf(pdf_path)
    chunks = chunk_text(text)
    embeddings = embedding_model.encode(chunks, show_progress_bar=False)

    points = []
    for i, (chunk, vector) in enumerate(zip(chunks, embeddings)):
        point_id = str(uuid.uuid4())

        metadata = {
            "pdf_name": os.path.basename(pdf_path),
            "chunk_id": point_id,
            "text": chunk
        }
        points.append(PointStruct(id=point_id, vector=vector.tolist(), payload=metadata))

    qdrant.upsert(collection_name=COLLECTION_NAME, points=points)
    print(f"Stored {len(chunks)} chunks for {pdf_path} in Qdrant.")


def load_processed_files():
    if not os.path.exists(CHECKPOINT_FILE):
        return set()
    with open(CHECKPOINT_FILE, "r") as f:
        return set(line.strip() for line in f.readlines())


def save_processed_file(filename):
    with open(CHECKPOINT_FILE, "a") as f:
        f.write(filename + "\n")


if __name__ == "__main__":
    processed_files = load_processed_files()
    print(len(os.listdir(PDF_DIR)))
    for index, filename in enumerate(os.listdir(PDF_DIR), start=1):
        if filename.endswith(".pdf") and filename not in processed_files:
            print(f"Processing file #{index}: {filename}")
            pdf_file_path = os.path.join(PDF_DIR, filename)
            process_single_pdf(pdf_file_path)
            save_processed_file(filename)
        else:
            print(f"Skipping file #{index}: {filename} (already processed or not a PDF)")

    print("All PDFs processed and stored in Qdrant.")
