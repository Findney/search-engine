// App.js
import React from "react"; // Mengimpor React untuk mendukung sintaks JSX.
import { Routes, Route } from "react-router-dom"; // Mengimpor komponen Routes dan Route dari react-router-dom untuk mendefinisikan navigasi aplikasi.
import HomePage from "./pages/HomePage"; // Mengimpor komponen HomePage untuk ditampilkan pada rute tertentu.
import SearchPage from "./pages/SearchPage"; // Mengimpor komponen SearchPage untuk ditampilkan pada rute tertentu.
import "./App.css"; // Mengimpor file CSS untuk memberikan gaya pada aplikasi.

function App() {
  return (
    <div className="App"> {/* Elemen pembungkus utama aplikasi dengan kelas CSS "App". */}
      <Routes>
        {/* Komponen Routes digunakan untuk mendefinisikan kumpulan rute dalam aplikasi. */}
        <Route path="/" element={<HomePage />} /> 
        {/* Rute ini merender komponen HomePage ketika URL adalah "/" (halaman utama). */}
        <Route path="/search" element={<SearchPage />} /> 
        {/* Rute ini merender komponen SearchPage ketika URL adalah "/search". */}
      </Routes>
    </div>
  );
}

export default App; // Mengekspor komponen App sehingga dapat digunakan di file lain.
