import React, { useState } from "react";
import { Link, useNavigate } from "react-router-dom";

function HomePage() {
  const [query, setQuery] = useState("");
  const [method, setMethod] = useState("cosine");
  const navigate = useNavigate();

  const handleSearch = (e) => {
    e.preventDefault();
    if (query) {
      navigate("/search", { state: { query, method } });
    }
  };

  return (
    <div className="home-page">
      <header>
        <Link to="/">
          <h1>NgulikTek</h1>
        </Link>
      </header>
      <form className="" onSubmit={handleSearch}>
        <div className="search-form">
          <input
            type="text"
            placeholder="Enter your query"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            required
          />
          <div className="method-select">
            <label>
              <select
                value={method}
                onChange={(e) => setMethod(e.target.value)}
              >
                <option value="cosine">Cosine Similarity</option>
                <option value="jaccard">Jaccard Similarity</option>
              </select>
            </label>
          </div>
        </div>
        <div className="search-button">
          <button type="submit">Search</button>
        </div>
      </form>
    </div>
  );
}

export default HomePage;
