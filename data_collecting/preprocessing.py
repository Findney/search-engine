import json
import nltk
import string
import logging
from collections import defaultdict, Counter
import math
from Sastrawi.Stemmer.StemmerFactory import StemmerFactory

# Inisialisasi logging
logging.basicConfig(filename='log-preprocessing.txt', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Fungsi untuk membaca stopwords dari file txt
def load_stopwords(file_path):
    """Membaca stopwords dari file txt dan mengembalikannya sebagai set."""
    stopwords = set()
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            for line in file:
                word = line.strip().lower()  # Menghapus spasi dan membuat huruf kecil
                if word:  # Pastikan tidak menambahkan kata kosong
                    stopwords.add(word)
        logging.info(f"Berhasil memuat {len(stopwords)} stopwords dari {file_path}.")
    except Exception as e:
        logging.error(f"Terjadi kesalahan saat membaca stopwords dari {file_path}: {e}")
    return stopwords

# Inisialisasi stemmer untuk bahasa Indonesia menggunakan Sastrawi
factory = StemmerFactory()
stemmer = factory.create_stemmer()

# Load custom stopwords dari file
custom_stopwords = load_stopwords("./stopwords.txt")

def preprocess_text(text):
    """Melakukan preprocessing teks: tokenisasi, menghapus stopwords, stemming."""
    logging.info("Mulai preprocessing teks.")
    text = text.lower()
    text = ''.join([char for char in text if char not in string.punctuation])
    words = nltk.word_tokenize(text)
    processed_words = [stemmer.stem(word) for word in words if word not in custom_stopwords]
    logging.info(f"Preprocessing selesai. Teks diproses menjadi {len(processed_words)} kata.")
    return processed_words

def build_inverted_index_and_tfidf(input_filename="../data/extracted_articles.json"):
    inverted_index = defaultdict(list)
    article_metadata = {}
    tf = defaultdict(lambda: defaultdict(int))
    df = defaultdict(int)
    total_documents = 0

    logging.info(f"Membaca artikel dari file {input_filename}.")
    try:
        with open(input_filename, mode='r', encoding='utf-8') as file:
            articles_data = json.load(file)
        logging.info(f"Berhasil membaca {len(articles_data)} artikel dari {input_filename}.")

        for article_id, article in enumerate(articles_data, start=1):
            url = article['url']
            title = article['title']
            date = article['date']
            image_url = article['image_url']
            content = article['content']
            summary = article['summary']

            article_metadata[article_id] = {
                'url': url,
                'title': title,
                'date': date,
                'image_url': image_url,
                'content': content,
                'summary': summary
            }

            words = preprocess_text(content)
            total_documents += 1

            word_counts = Counter(words)
            for word, count in word_counts.items():
                tf[word][article_id] = count
                df[word] += 1
                inverted_index[word].append(article_id)

        inverted_index = dict(sorted(inverted_index.items()))
        logging.info(f"Inverted index dibangun dengan {len(inverted_index)} kata unik.")

        tfidf = defaultdict(lambda: defaultdict(float))
        for word, doc_ids in tf.items():
            for doc_id, count in doc_ids.items():
                term_frequency = count
                inverse_document_frequency = math.log10(total_documents / (1 + df[word]))
                tfidf[word][doc_id] = term_frequency * inverse_document_frequency

        return inverted_index, article_metadata, tfidf

    except FileNotFoundError:
        logging.error(f"File {input_filename} tidak ditemukan.")
        return {}, {}, {}
    except Exception as e:
        logging.error(f"Terjadi kesalahan saat membaca file {input_filename}: {e}")
        return {}, {}, {}

def save_to_file(data, filename):
    try:
        with open(filename, 'w', encoding='utf-8') as file:
            json.dump(data, file, ensure_ascii=False, indent=4)
        logging.info(f"Data disimpan ke file {filename}.")
    except Exception as e:
        logging.error(f"Terjadi kesalahan saat menyimpan file {filename}: {e}")

def main():
    inverted_index, article_metadata, tfidf = build_inverted_index_and_tfidf()
    save_to_file(inverted_index, "../data/inverted_index.json")
    save_to_file(article_metadata, "../data/article_metadata.json")
    save_to_file(tfidf, "../data/tfidf_scores.json")

if __name__ == "__main__":
    main()
