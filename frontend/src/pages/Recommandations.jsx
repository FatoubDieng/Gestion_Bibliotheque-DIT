import React, { useState, useEffect } from "react";
import { recoService } from "../services/api";

import book1 from "../assets/books/book1.jpg";
import book2 from "../assets/books/book2.jpg";
import book3 from "../assets/books/book3.jpg";
import book4 from "../assets/books/book4.jpg";
import book5 from "../assets/books/book5.jpg";

const BOOK_IMAGES = [
  book1,
  book2,
  book3,
  book4,
  book5,
];

export default function Recommandations() {
  const [userId, setUserId] = useState("");
  const [recos, setRecos] = useState(null);
  const [modelInfo, setModelInfo] = useState(null);
  const [loading, setLoading] = useState(false);
  const [training, setTraining] = useState(false);

  const [trainParams, setTrainParams] = useState({
    algorithme: "SVD",
    n_components: 10,
  });

  useEffect(() => {
    recoService
      .modelInfo()
      .then((r) => setModelInfo(r.data))
      .catch(() => setModelInfo(null));
  }, []);

  const handleSearch = async () => {
    if (!userId) return;

    setLoading(true);

    try {
      const res = await recoService.recommandations(
        parseInt(userId),
        8
      );

      setRecos(res.data);
    } catch (error) {
      console.log(error);
    } finally {
      setLoading(false);
    }
  };

  const handleTrain = async () => {
    setTraining(true);

    try {
      await recoService.entrainer(trainParams);

      const info = await recoService.modelInfo();

      setModelInfo(info.data);
    } catch (error) {
      console.log(error);
    } finally {
      setTraining(false);
    }
  };

  return (
    <div className="recommandation-container">

      {/* TOPBAR */}

      <div className="topbar">
        <div>
          <h1>Recommendation Panel</h1>
          <p>AI Book Recommendation System</p>
        </div>

        <div className="admin-profile">
          <div className="admin-avatar">A</div>
          <span>Admin</span>
        </div>
      </div>

      {/* STATS */}

      <div className="stats-grid">

        <div className="stat-card cyan">
          <h2>{modelInfo?.n_users || 0}</h2>
          <p>Users</p>
        </div>

        <div className="stat-card green">
          <h2>{modelInfo?.n_items || 0}</h2>
          <p>Books</p>
        </div>

        <div className="stat-card orange">
          <h2>{modelInfo?.type || "SVD"}</h2>
          <p>Algorithm</p>
        </div>

        <div className="stat-card red">
          <h2>{modelInfo?.metrics?.rmse || "--"}</h2>
          <p>RMSE</p>
        </div>
      </div>

      {/* MAIN */}

      <div className="main-grid">

        {/* LEFT */}

        <div className="left-section">

          {/* SEARCH */}

          <div className="panel">
            <div className="panel-header">
              <h3>Search Recommendations</h3>
            </div>

            <div className="search-box">
              <input
                type="number"
                placeholder="Enter user ID..."
                value={userId}
                onChange={(e) => setUserId(e.target.value)}
              />

              <button onClick={handleSearch}>
                {loading ? "Loading..." : "Recommend"}
              </button>
            </div>
          </div>

          {/* RECOMMENDATIONS */}

          <div className="panel">
            <div className="panel-header">
              <h3>Recommended Books</h3>
            </div>

            {!recos && (
              <div className="empty-box">
                No recommendations yet
              </div>
            )}

            {recos && (
              <div className="recommendation-grid">

                {recos.recommandations.map((book, index) => (

                  <div className="book-card" key={index}>

                    {/* IMAGE */}

                    <img
                      src={
                        BOOK_IMAGES[
                          index % BOOK_IMAGES.length
                        ]
                      }
                      alt="book"
                      className="book-image"
                    />

                    {/* INFOS */}

                    <div className="book-content">

                      <h4>
                        {book.titre ||
                          `Book #${book.book_id}`}
                      </h4>

                      <p>{book.auteur}</p>

                      <span className="score">
                        Score : {book.score}
                      </span>

                      {book.categorie && (
                        <div className="category">
                          {book.categorie}
                        </div>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>

        {/* RIGHT */}

        <div className="right-section">

          {/* MODEL INFO */}

          <div className="panel">

            <div className="panel-header">
              <h3>Model Status</h3>
            </div>

            <div className="info-row">
              <span>Status</span>
              <strong>
                {modelInfo?.chargé
                  ? "Loaded"
                  : "Offline"}
              </strong>
            </div>

            <div className="info-row">
              <span>Algorithm</span>
              <strong>{modelInfo?.type || "--"}</strong>
            </div>

            <div className="info-row">
              <span>Users</span>
              <strong>{modelInfo?.n_users || 0}</strong>
            </div>

            <div className="info-row">
              <span>Books</span>
              <strong>{modelInfo?.n_items || 0}</strong>
            </div>

            <div className="info-row">
              <span>MAE</span>
              <strong>
                {modelInfo?.metrics?.mae || "--"}
              </strong>
            </div>
          </div>

          {/* TRAIN */}

          <div className="panel">

            <div className="panel-header">
              <h3>Train Model</h3>
            </div>

            <div className="form-group">

              <label>Algorithm</label>

              <select
                value={trainParams.algorithme}
                onChange={(e) =>
                  setTrainParams({
                    ...trainParams,
                    algorithme: e.target.value,
                  })
                }
              >
                <option value="SVD">SVD</option>
                <option value="KNN">KNN</option>
              </select>
            </div>

            {trainParams.algorithme === "SVD" && (

              <div className="form-group">

                <label>
                  Components (
                  {trainParams.n_components})
                </label>

                <input
                  type="range"
                  min="5"
                  max="30"
                  value={trainParams.n_components}
                  onChange={(e) =>
                    setTrainParams({
                      ...trainParams,
                      n_components: +e.target.value,
                    })
                  }
                />
              </div>
            )}

            <button
              className="train-btn"
              onClick={handleTrain}
              disabled={training}
            >
              {training
                ? "Training..."
                : "Launch Training"}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}