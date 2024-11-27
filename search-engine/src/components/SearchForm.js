import React from "react";

function SearchForm({
  query,
  setQuery,
  method,
  setMethod,
  loading,
  setHasSearched
}) {
  const handleSubmit = (e) => {
    e.preventDefault();
    if (query) {
      setHasSearched(true);
    }
  };

  return (
    <form className="search-form" onSubmit={handleSubmit}>
      <input
        type="text"
        placeholder="Enter your query"
        value={query}
        onChange={(e) => setQuery(e.target.value)}
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
  );
}

export default SearchForm;
