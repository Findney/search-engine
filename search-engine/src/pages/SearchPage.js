import React, { useState, useEffect } from "react";
import { Link, useLocation, useNavigate } from "react-router-dom";
import axios from "axios";

function SearchPage() {
  const location = useLocation();
  const navigate = useNavigate();
  const [query, setQuery] = useState("");
  const [method, setMethod] = useState("cosine");
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [hasSearched, setHasSearched] = useState(false);
  const [page, setPage] = useState(1); 
  const [perPage] = useState(10); 
  const [totalPages, setTotalPages] = useState(0); 

  useEffect(() => {
    if (!location.state) {
      navigate("/");
      return;
    }

    setQuery(location.state.query);
    setMethod(location.state.method);
    setHasSearched(true);
    fetchResults(location.state.query, location.state.method, 1);
  }, [location.state, navigate]);

  const fetchResults = async (searchQuery, searchMethod, page) => {
    setLoading(true);
    try {
      const response = await axios.post("http://127.0.0.1:5000/api/search", {
        query: searchQuery,
        method: searchMethod,
        page: page,
        per_page: perPage,
      });

      const { results, total_pages } = response.data;
      setResults(results);
      setTotalPages(total_pages);
    } catch (error) {
      console.error("Error fetching search results:", error);
    }
    setLoading(false);
  };

  useEffect(() => {
    if (query && hasSearched) {
      fetchResults(query, method, page);
    }
  }, [method, page]);

  const handleSearch = async (e) => {
    e.preventDefault();
    if (query) {
      setHasSearched(true);
      fetchResults(query, method, 1); // Always start from page 1 on new search
      // Update URL state
      navigate("/search", { state: { query, method }, replace: true });
    }
  };

  const handleInputChange = (e) => {
    setQuery(e.target.value);
    if (hasSearched) {
      setHasSearched(false);
    }
  };

  const handlePageChange = (newPage) => {
    setPage(newPage);
    fetchResults(query, method, newPage);
  };

  return (
    <div className="search-page">
      <header>
        <Link to="/">
          <h1>NgulikTek</h1>
        </Link>
      </header>
      <form className="search-form" onSubmit={handleSearch}>
        <input
          type="text"
          placeholder="Enter your query"
          value={query}
          onChange={handleInputChange}
          required
        />
        <div className="method-select">
          <label>
            <select value={method} onChange={(e) => setMethod(e.target.value)}>
              <option value="cosine">Cosine Similarity</option>
              <option value="jaccard">Jaccard Similarity</option>
            </select>
          </label>
        </div>
        <button type="submit" disabled={loading}>
          {loading ? "Searching..." : "Search"}
        </button>
      </form>

      {loading && (
        <div className="loading-spinner">
          <div className="spinner"></div>
        </div>
      )}

      {results.length === 0 && !loading && hasSearched && (
        <p className="no-results-message">
          No results found. Try a different query.
        </p>
      )}

      <div className="results">
        {results.map((result, index) => {
          const similarityScore =
            method === "cosine"
              ? result.cosine_similarity
              : result.jaccard_similarity;

          return (
            <a
              key={index}
              href={result.article.url}
              className="result-item"
              target="_blank"
              rel="noopener noreferrer"
            >
              <img
                src={result.article.image_url}
                alt={result.article.title}
                className="result-image"
              />
              <div className="result-details">
                <h2>{result.article.title}</h2>
                <p>{result.article.date}</p>
                <p>{result.article.summary}</p>
                <p>
                  <strong>
                    {method === "cosine"
                      ? "Cosine Similarity"
                      : "Jaccard Similarity"}
                    :{" "}
                  </strong>
                  {similarityScore ? similarityScore.toFixed(4) : "N/A"}
                </p>
              </div>
            </a>
          );
        })}
      </div>

      {/* Show pagination only if results are available and the search is complete */}
      {results.length > 0 && !loading && hasSearched && (
        <div className="pagination">
          <button
            onClick={() => handlePageChange(page - 1)}
            disabled={page === 1 || loading}
          >
            Previous
          </button>
          <span>Page {page} / {totalPages}</span>
          <button
            onClick={() => handlePageChange(page + 1)}
            disabled={loading || page === totalPages}
          >
            Next
          </button>
        </div>
      )}
    </div>
  );
}

export default SearchPage;
  