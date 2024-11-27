import json
import os
import logging
from process_query import preprocess_text  # Pastikan ini sesuai dengan proyek Anda

# Konfigurasi logging
logging.basicConfig(
    level=logging.INFO,  # Atur level log ke INFO
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),  # Output ke console
        logging.FileHandler("preprocessing.log", mode="w")  # Simpan log ke file
    ]
)

def preprocess_and_save(input_file, output_file):
    try:
        # Muat file article_metadata.json
        logging.info(f"Membaca file input dari: {input_file}")
        with open(input_file, mode="r", encoding="utf-8") as file:
            articles = json.load(file)
        logging.info(f"Berhasil memuat {len(articles)} artikel.")

        # Proses setiap artikel
        for article_id, article in articles.items():
            logging.info(f"Memproses artikel ID: {article_id}")
            content = article.pop("content", "")  # Hapus content dari data asli
            if content:
                article["tokenized_content"] = preprocess_text(content)  # Tambahkan tokenized content
                logging.info(f"Artikel ID {article_id} berhasil di-tokenize.")
            else:
                logging.warning(f"Artikel ID {article_id} tidak memiliki konten.")

        # Simpan hasil ke file baru
        logging.info(f"Menyimpan hasil preprocessing ke: {output_file}")
        with open(output_file, mode="w", encoding="utf-8") as file:
            json.dump(articles, file, ensure_ascii=False, indent=4)
        logging.info(f"File tokenized berhasil disimpan ke {output_file}.")
    except FileNotFoundError:
        logging.error(f"File {input_file} tidak ditemukan.")
    except Exception as e:
        logging.exception(f"Terjadi kesalahan: {e}")

# File input dan output
current_dir = os.path.dirname(__file__)
input_filename = os.path.join(current_dir, "../data/article_metadata.json")
output_filename = os.path.join(current_dir, "../data/article_metadata_tokenized.json")

# Panggil fungsi untuk preprocess dan simpan
preprocess_and_save(input_filename, output_filename)
