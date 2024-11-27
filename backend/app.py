import math
import json
from flask import Flask, request, jsonify # type: ignore
from data_collecting.process_query import preprocess_text
from flask_cors import CORS # type: ignore
import os

app = Flask(__name__)
CORS(app)

# Fungsi untuk memuat artikel metadata dengan ID sebagai string
def load_article_metadata(input_filename=None):
    current_dir = os.path.dirname(__file__)
    file_path = os.path.join(current_dir, "../data/article_metadata_tokenized.json") if input_filename is None else input_filename

    try:
        with open(file_path, mode='r', encoding='utf-8') as file:
            metadata = json.load(file)
            # Pastikan ID artikel sebagai string
            return {str(article_id): article for article_id, article in metadata.items()}
    except FileNotFoundError:
        print(f"File {file_path} tidak ditemukan.")
        return {}
    except Exception as e:
        print(f"Terjadi kesalahan saat memuat file {file_path}: {e}")
        return {}

# Fungsi untuk memuat inverted index dengan ID sebagai string
def load_inverted_index(input_filename=None):
    current_dir = os.path.dirname(__file__)
    file_path = os.path.join(current_dir, "../data/inverted_index.json") if input_filename is None else input_filename

    try:
        with open(file_path, mode='r', encoding='utf-8') as file:
            inverted_index = json.load(file)
            # Pastikan ID artikel sebagai string
            return {word: [str(article_id) for article_id in article_ids] for word, article_ids in inverted_index.items()}
    except FileNotFoundError:
        print(f"File {file_path} tidak ditemukan.")
        return {}
    except Exception as e:
        print(f"Terjadi kesalahan saat memuat file {file_path}: {e}")
        return {}

# Fungsi untuk memuat file TF-IDF
def load_tfidf(input_filename=None):
    current_dir = os.path.dirname(__file__)
    file_path = os.path.join(current_dir, "../data/tfidf_scores.json") if input_filename is None else input_filename

    try:
        with open(file_path, mode='r', encoding='utf-8') as file:
            tfidf = json.load(file)
            return tfidf
    except FileNotFoundError:
        print(f"File {file_path} tidak ditemukan.")
        return {}
    except Exception as e:
        print(f"Terjadi kesalahan saat memuat file {file_path}: {e}")
        return {}

# Fungsi Cosine Similarity menggunakan TF-IDF
def cosine_similarity(query_words, document_words):
    query_freq = {word: query_words.count(word) for word in set(query_words)}
    doc_freq = {word: document_words.count(word) for word in set(document_words)}
    intersection = set(query_freq.keys()).intersection(set(doc_freq.keys()))
    
    numerator = sum(query_freq[word] * doc_freq[word] for word in intersection)
    query_magnitude = math.sqrt(sum(val ** 2 for val in query_freq.values()))
    doc_magnitude = math.sqrt(sum(val ** 2 for val in doc_freq.values()))
    
    denominator = query_magnitude * doc_magnitude
    return numerator / denominator if denominator else 0

# Fungsi Jaccard Similarity
def jaccard_similarity(query_words, document_words):
    set_query = set(query_words)
    set_document = set(document_words)
    intersection = set_query.intersection(set_document)
    union = set_query.union(set_document)
    return len(intersection) / len(union) if union else 0

@app.route("/api/search", methods=["POST"])
def search():
    data = request.get_json()
    query = data.get("query", "")
    method = data.get("method", "cosine")  # Default ke cosine jika tidak ada metode
    page = data.get("page", 1)  # Default halaman ke 1 jika tidak ada
    per_page = data.get("per_page", 10)  # Default 10 hasil per halaman

    # Preprocess query
    query_words = preprocess_text(query)

    # Load inverted index dan metadata
    inverted_index = load_inverted_index()
    article_metadata = load_article_metadata()

    # Set untuk menyimpan artikel yang relevan
    result_articles = {}
    
    # Melakukan pencarian berdasarkan query
    for word in query_words:
        if word in inverted_index:
            for article_id in inverted_index[word]:
                if article_id in article_metadata:
                    # Mengambil metadata artikel menggunakan ID
                    article = article_metadata[article_id]
                    # Menambahkan artikel dengan URL sebagai kunci dan artikel sebagai nilai
                    result_articles.setdefault(article["url"], article)

    # Menghitung similarity
    similarity_scores = []
    for article in result_articles.values():
        # Ambil tokenized_content langsung
        tokenized_content = article.get("tokenized_content", [])
        
        if not tokenized_content:  # Jika tidak ada tokenized_content, abaikan artikel ini
            continue
        
        # Hitung skor similarity
        if method == "cosine":
            score = cosine_similarity(query_words, tokenized_content)
        else:
            score = jaccard_similarity(query_words, tokenized_content)
        
        # Tambahkan hasil ke daftar similarity_scores
        similarity_scores.append({
            "article": {
                "url": article["url"],
                "title": article["title"],
                "date": article["date"],
                "image_url": article["image_url"],
                "summary": article["summary"]
            },
            "cosine_similarity": score if method == "cosine" else None,
            "jaccard_similarity": score if method == "jaccard" else None
        })


    # Mengurutkan berdasarkan skor similarity
    similarity_scores.sort(key=lambda x: x["cosine_similarity"] if method == "cosine" else x["jaccard_similarity"], reverse=True)

    # Membatasi hasil ke 200 dokumen teratas
    top_results = similarity_scores[:200]
    num_documents = len(top_results)
    total_pages = math.ceil(num_documents / per_page)  # Menghitung total halaman

    # Menentukan indeks awal dan akhir untuk paginasi
    start = (page - 1) * per_page
    end = start + per_page

    # Mengambil hasil berdasarkan halaman dan per halaman
    paginated_results = top_results[start:end]

    # Mengembalikan hasil dengan informasi total halaman
    return jsonify({
        "results": paginated_results,
        "total_pages": total_pages,
        "current_page": page
    })

if __name__ == "__main__":
    app.run(debug=True)