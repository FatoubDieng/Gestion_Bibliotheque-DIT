import React, { useState, useEffect } from "react";
import { empruntsService } from "../services/api";

import book1 from "../assets/books/book1.jpg";
import book2 from "../assets/books/book2.jpg";
import book3 from "../assets/books/book3.jpg";

const BOOKS = [book1, book2, book3];

const STATUS = {
  en_cours: {
    label: "Borrowed",
    color: "#00BCD4",
  },

  retourne: {
    label: "Returned",
    color: "#4CAF50",
  },

  en_retard: {
    label: "Late",
    color: "#F44336",
  },
};

export default function Emprunts() {

  const [emprunts, setEmprunts] = useState([]);

  const [stats, setStats] = useState(null);

  const [loading, setLoading] = useState(true);

  const [filtre, setFiltre] = useState("tous");

  const [retourModal, setRetourModal] =
    useState(null);

  const [note, setNote] = useState("");

  const [saving, setSaving] = useState(false);

  const fetchData = async () => {

    setLoading(true);

    try {

      const [histRes, statsRes] =
        await Promise.all([
          empruntsService.historique(),
          empruntsService.statistiques(),
        ]);

      setEmprunts(histRes.data.results || []);

      setStats(statsRes.data);

    } catch (e) {
      console.log(e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  const empruntsFiltres =
    emprunts.filter((e) => {

      if (filtre === "tous") return true;

      if (filtre === "en_retard")
        return e.est_en_retard;

      return e.statut === filtre;
    });

  const handleRetour = async () => {

    if (!retourModal) return;

    setSaving(true);

    try {

      await empruntsService.retourner(
        retourModal.id,
        note ? parseInt(note) : null,
        ""
      );

      setRetourModal(null);

      setNote("");

      fetchData();

    } catch (e) {
      console.log(e);
    } finally {
      setSaving(false);
    }
  };

  return (

    <div className="loans-page">

      {/* HEADER */}

      <div className="loans-header">

        <div>

          <h1>Loans Management</h1>

          <p>
            Surveiller tous les livres empruntés 
            et les retours
            
          </p>

        </div>

        <button
          className="refresh-btn"
          onClick={fetchData}
        >
          Rafraichir
        </button>
      </div>

      {/* STATS */}

      {stats && (

        <div className="loan-stats">

          <div className="loan-stat-card blue">

            <h2>{stats.total_emprunts}</h2>

            <p>Total des emprunts</p>

          </div>

          <div className="loan-stat-card green">

            <h2>{stats.retournes}</h2>

            <p>Retourné</p>

          </div>

          <div className="loan-stat-card orange">

            <h2>{stats.en_cours}</h2>

            <p>Emprunté</p>

          </div>

          <div className="loan-stat-card red">

            <h2>{stats.en_retard}</h2>

            <p>retard</p>

          </div>

        </div>
      )}

      {/* FILTERS */}

      <div className="loan-filters">

        {[
          {
            key: "tous",
            label: "All",
          },

          {
            key: "en_cours",
            label: "Emprunts",
          },

          {
            key: "retourne",
            label: "Retourné",
          },

          {
            key: "en_retard",
            label: "retard",
          },
        ].map((f) => (

          <button
            key={f.key}
            className={
              filtre === f.key
                ? "active"
                : ""
            }
            onClick={() =>
              setFiltre(f.key)
            }
          >
            {f.label}
          </button>
        ))}
      </div>

      {/* LOADING */}

      {loading ? (

        <div className="loan-loader">

          <div className="loader"></div>

        </div>

      ) : (

        <div className="loans-grid">

          {empruntsFiltres.map(
            (e, index) => {

              const cfg =
                STATUS[e.statut] ||
                STATUS.en_cours;

              return (

                <div
                  className="loan-card"
                  key={e.id}
                >

                  {/* IMAGE */}

                  <div className="loan-image">

                    <img
                      src={
                        BOOKS[
                          index %
                            BOOKS.length
                        ]
                      }
                      alt="book"
                    />

                    <span
                      className="loan-status"
                      style={{
                        background:
                          cfg.color,
                      }}
                    >
                      {cfg.label}
                    </span>
                  </div>

                  {/* CONTENT */}

                  <div className="loan-content">

                    <h3>
                      Book #{e.livre_id}
                    </h3>

                    <p>
                      User #
                      {e.utilisateur_id}
                    </p>

                    <div className="loan-dates">

                      <div>
                        <span>
                          Borrow Date
                        </span>

                        <strong>
                          {
                            e.date_emprunt
                          }
                        </strong>
                      </div>

                      <div>
                        <span>
                          Return Date
                        </span>

                        <strong>
                          {
                            e.date_retour_prevue
                          }
                        </strong>
                      </div>
                    </div>

                    {e.jours_retard >
                      0 && (

                      <div className="late-box">

                        +{
                          e.jours_retard
                        }{" "}
                        days late

                      </div>
                    )}

                    {e.statut !==
                      "retourne" && (

                      <button
                        className="return-btn"
                        onClick={() =>
                          setRetourModal(
                            e
                          )
                        }
                      >
                        Return Book
                      </button>
                    )}
                  </div>
                </div>
              );
            }
          )}
        </div>
      )}

      {/* MODAL */}

      {retourModal && (

        <div className="modal-overlay">

          <div className="return-modal">

            <div className="modal-top">

              <h2>
                Return Book #
                {retourModal.livre_id}
              </h2>

              <button
                onClick={() =>
                  setRetourModal(null)
                }
              >
                ✕
              </button>

            </div>

            <div className="modal-body">

              <p>
                Loan #
                {retourModal.id}
              </p>

              <label>
                Rating
              </label>

              <select
                value={note}
                onChange={(e) =>
                  setNote(
                    e.target.value
                  )
                }
              >
                <option value="">
                  No Rating
                </option>

                {[1, 2, 3, 4, 5].map(
                  (n) => (
                    <option
                      key={n}
                      value={n}
                    >
                      {n} Stars
                    </option>
                  )
                )}
              </select>

              <button
                className="confirm-btn"
                onClick={handleRetour}
                disabled={saving}
              >
                {saving
                  ? "Saving..."
                  : "Confirm Return"}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}