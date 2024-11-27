import string
from Sastrawi.Stemmer.StemmerFactory import StemmerFactory # type: ignore
import nltk  # type: ignore

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
    except Exception as e:
        print(f"Terjadi kesalahan saat membaca stopwords dari {file_path}: {e}")
    return stopwords

# Inisialisasi stemmer untuk bahasa Indonesia menggunakan Sastrawi
factory = StemmerFactory()
stemmer = factory.create_stemmer()
# Load custom stopwords dari file
custom_stopwords = load_stopwords("./stopwords.txt")

def preprocess_text(text):
    """Melakukan preprocessing teks: tokenisasi, menghapus stopwords, stemming."""
    text = text.lower()
    text = ''.join([char for char in text if char not in string.punctuation])
    words = nltk.word_tokenize(text)
    processed_words = [stemmer.stem(word) for word in words if word not in custom_stopwords]
    return processed_words
