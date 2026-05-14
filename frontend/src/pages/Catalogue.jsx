import React, { useState, useEffect } from "react";
import { livresService, empruntsService } from "../services/api";

import book1 from "../assets/books/book1.jpg";
import book2 from "../assets/books/book2.jpg";
import book3 from "../assets/books/book3.jpg";
import book4 from "../assets/books/book4.jpg";

const booksImages = [book1, book2, book3, book4];

function LivreModal({ livre, onClose, onEmprunter }) {
  const [userId, setUserId] = useState("");
  const [msg, setMsg] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleEmprunter = async () => {
    if (!userId) {
      return setMsg({
        type: "error",
        text: "Entrez un ID utilisateur.",
      });
    }

    setLoading(true);

    try {
      await empruntsService.emprunter(
        parseInt(userId),
        livre.id
      );

      setMsg({
        type: "success",
        text: "Emprunt enregistré avec succès !",
      });

      onEmprunter();

    } catch (e) {

      setMsg({
        type: "error",
        text:
          e.response?.data?.error ||
          "Erreur lors de l'emprunt.",
      });

    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="modal-overlay" onClick={onClose}>

      <div
        className="modal"
        onClick={(e) => e.stopPropagation()}
      >

        <div className="modal-header">

          <h3 className="modal-title">
            {livre.titre}
          </h3>

          <button
            className="modal-close"
            onClick={onClose}
          >
            ✕
          </button>

        </div>

        <div
          style={{
            display: "flex",
            flexDirection: "column",
            gap: "12px",
          }}
        >

          <div>
            <span
              style={{
                color: "var(--text-secondary)",
                fontSize: "0.8rem",
              }}
            >
              AUTEUR
            </span>

            <br />

            {livre.auteur}
          </div>

          <div>
            <span
              style={{
                color: "var(--text-secondary)",
                fontSize: "0.8rem",
              }}
            >
              ISBN
            </span>

            <br />

            <code
              style={{
                fontSize: "0.85rem",
                color: "var(--accent)",
              }}
            >
              {livre.isbn}
            </code>
          </div>

          <div
            style={{
              display: "flex",
              gap: "12px",
            }}
          >

            <div>
              <span
                style={{
                  color: "var(--text-secondary)",
                  fontSize: "0.8rem",
                }}
              >
                CATÉGORIE
              </span>

              <br />

              {livre.categorie || "—"}
            </div>

            <div>
              <span
                style={{
                  color: "var(--text-secondary)",
                  fontSize: "0.8rem",
                }}
              >
                STOCK
              </span>

              <br />

              <span
                className={
                  livre.stock_dispo > 0
                    ? "stock-ok"
                    : "stock-out"
                }
              >
                {livre.stock_dispo}/
                {livre.stock_total}
              </span>
            </div>
          </div>

          {livre.description && (
            <div
              style={{
                color: "var(--grey-500)",
                fontSize: "0.875rem",
                lineHeight: 1.6,
              }}
            >
              {livre.description}
            </div>
          )}

          {livre.stock_dispo > 0 && (

            <div
              style={{
                borderTop:
                  "1px solid var(--grey-200)",
                paddingTop: "1rem",
                marginTop: "0.5rem",
              }}
            >

              <div className="form-group">

                <label className="form-label">
                  ID Utilisateur
                </label>

                <input
                  className="form-input"
                  type="number"
                  placeholder="Ex: 1"
                  value={userId}
                  onChange={(e) =>
                    setUserId(e.target.value)
                  }
                />

              </div>

              {msg && (
                <div
                  className={`alert alert-${
                    msg.type === "error"
                      ? "error"
                      : "success"
                  }`}
                  style={{ marginTop: "8px" }}
                >
                  {msg.text}
                </div>
              )}
            </div>
          )}
        </div>

        <div className="modal-actions">

          <button
            className="btn btn-secondary"
            onClick={onClose}
          >
            Fermer
          </button>

          {livre.stock_dispo > 0 && (
            <button
              className="btn btn-primary"
              onClick={handleEmprunter}
              disabled={loading}
            >
              {loading
                ? "..."
                : "📖 Emprunter"}
            </button>
          )}

        </div>
      </div>
    </div>
  );
}

export default function Catalogue() {

  const [livres, setLivres] = useState([]);

  const [filtres, setFiltres] = useState([]);

  const [categorie, setCategorie] =
    useState("Tous");

  const [search, setSearch] =
    useState("");

  const [loading, setLoading] =
    useState(true);

  const [selected, setSelected] =
    useState(null);

  const [showModal, setShowModal] =
    useState(false);

  const [showForm, setShowForm] =
    useState(false);

  const [newLivre, setNewLivre] =
    useState({
      titre: "",
      auteur: "",
      isbn: "",
      categorie: "",
      stock_total: 1,
      stock_dispo: 1,
    });

  const [saving, setSaving] =
    useState(false);

  const [alert, setAlert] =
    useState(null);

  const fetchLivres = async () => {

    setLoading(true);

    try {

      const res =
        await livresService.lister();

      const data =
        res.data.results || res.data;

      setLivres(
        Array.isArray(data) ? data : []
      );

      const cats = [
        ...new Set(
          data
            .map((l) => l.categorie)
            .filter(Boolean)
        ),
      ];

      setFiltres(cats);

    } catch {

      setAlert({
        type: "error",
        text:
          "Impossible de charger les livres.",
      });

    } finally {

      setLoading(false);
    }
  };

  useEffect(() => {
    fetchLivres();
  }, []);

  const livresFiltres = livres.filter((l) => {

    const matchCat =
      categorie === "Tous" ||
      l.categorie === categorie;

    const matchSearch =
      !search ||
      l.titre
        ?.toLowerCase()
        .includes(search.toLowerCase()) ||
      l.auteur
        ?.toLowerCase()
        .includes(search.toLowerCase());

    return matchCat && matchSearch;
  });

  const handleSave = async () => {

    setSaving(true);

    try {

      await livresService.ajouter(
        newLivre
      );

      setAlert({
        type: "success",
        text:
          "Livre ajouté avec succès !",
      });

      setShowForm(false);

      setNewLivre({
        titre: "",
        auteur: "",
        isbn: "",
        categorie: "",
        stock_total: 1,
        stock_dispo: 1,
      });

      fetchLivres();

    } catch (e) {

      setAlert({
        type: "error",
        text:
          JSON.stringify(
            e.response?.data || "Erreur"
          ),
      });

    } finally {

      setSaving(false);
    }
  };

  return (
    <div className="fade-in">

      <div className="catalogue-top">

  <div className="catalogue-hero">

    <div className="catalogue-hero-content">

      <span className="catalogue-badge">
        📚 Bibliothèque numérique
      </span>

      <h1>
        Explorez notre collection de livres
      </h1>

      <p>
        Découvrez des ouvrages universitaires,
        scientifiques et littéraires disponibles
        à la bibliothèque.
      </p>

    </div>

    <div className="catalogue-stats">

      <div className="catalogue-stat-card">
        <strong>{livres.length}</strong>
        <span>Livres disponibles</span>
      </div>

      <div className="catalogue-stat-card">
        <strong>{filtres.length}</strong>
        <span>Catégories</span>
      </div>

    </div>

  </div>

  <div className="catalogue-toolbar">

    <div className="catalogue-search">

      <span>🔍</span>

      <input
        type="text"
        placeholder="Rechercher un titre ou un auteur..."
        value={search}
        onChange={(e) =>
          setSearch(e.target.value)
        }
      />

    </div>

    <button
      className="catalogue-add-btn"
      onClick={() => setShowForm(true)}
    >
      + Ajouter un livre
    </button>

  </div>

  <div className="catalogue-filters">

    {["Tous", ...filtres].map((cat) => (

      <button
        key={cat}
        className={`catalogue-filter ${
          categorie === cat
            ? "active"
            : ""
        }`}
        onClick={() =>
          setCategorie(cat)
        }
      >
        {cat}
      </button>

    ))}

  </div>

</div>

      {loading ? (

        <div className="loading">
          <div className="spinner"></div>
        </div>

      ) : livresFiltres.length === 0 ? (

        <div className="empty-state">

          <div className="empty-icon">
            📭
          </div>

          <p>Aucun livre trouvé.</p>

        </div>

      ) : (

        <div className="catalogue-section">

          <div className="catalogue-header">

            <h2>Popular Books</h2>

            <div className="line"></div>

          </div>

          <div className="books-grid">

            {livresFiltres.map(
              (livre, index) => (

                <div
                  key={livre.id}
                  className="book-card"
                  onClick={() => {
                    setSelected(livre);
                    setShowModal(true);
                  }}
                >

                  <div className="book-image">

                    <img
                      src={
                        booksImages[
                          index %
                            booksImages.length
                        ]
                      }
                      alt={livre.titre}
                    />

                  </div>

                  <div className="book-content">

                    <h3>
                      {livre.titre}
                    </h3>

                    <p className="book-author">
                      by {livre.auteur}
                    </p>

                    <div className="book-category">
                      {livre.categorie}
                    </div>

                    <button className="book-btn">
                      Voir détails
                    </button>

                  </div>
                </div>
              )
            )}

          </div>
        </div>
      )}

      {showModal && selected && (

        <LivreModal
          livre={selected}
          onClose={() =>
            setShowModal(false)
          }
          onEmprunter={() => {
            fetchLivres();
            setShowModal(false);
          }}
        />
      )}

      {showForm && (

        <div className="modal-overlay">

          <div className="modal">

            <div className="modal-header">

              <h3 className="modal-title">
                Ajouter un livre
              </h3>

              <button
                className="modal-close"
                onClick={() =>
                  setShowForm(false)
                }
              >
                ✕
              </button>

            </div>

            <div
              style={{
                display: "flex",
                flexDirection: "column",
                gap: "1rem",
              }}
            >

              <div className="form-grid">

                <div className="form-group">

                  <label className="form-label">
                    Titre
                  </label>

                  <input
                    className="form-input"
                    value={newLivre.titre}
                    onChange={(e) =>
                      setNewLivre({
                        ...newLivre,
                        titre:
                          e.target.value,
                      })
                    }
                  />

                </div>

                <div className="form-group">

                  <label className="form-label">
                    Auteur
                  </label>

                  <input
                    className="form-input"
                    value={newLivre.auteur}
                    onChange={(e) =>
                      setNewLivre({
                        ...newLivre,
                        auteur:
                          e.target.value,
                      })
                    }
                  />

                </div>
              </div>

              <div className="form-grid">

                <div className="form-group">

                  <label className="form-label">
                    ISBN
                  </label>

                  <input
                    className="form-input"
                    value={newLivre.isbn}
                    onChange={(e) =>
                      setNewLivre({
                        ...newLivre,
                        isbn:
                          e.target.value,
                      })
                    }
                  />

                </div>

                <div className="form-group">

                  <label className="form-label">
                    Catégorie
                  </label>

                  <input
                    className="form-input"
                    value={newLivre.categorie}
                    onChange={(e) =>
                      setNewLivre({
                        ...newLivre,
                        categorie:
                          e.target.value,
                      })
                    }
                  />

                </div>
              </div>

              <div className="form-group">

                <label className="form-label">
                  Stock total
                </label>

                <input
                  className="form-input"
                  type="number"
                  min="1"
                  value={newLivre.stock_total}
                  onChange={(e) =>
                    setNewLivre({
                      ...newLivre,
                      stock_total:
                        +e.target.value,
                      stock_dispo:
                        +e.target.value,
                    })
                  }
                />

              </div>
            </div>

            <div className="modal-actions">

              <button
                className="btn btn-secondary"
                onClick={() =>
                  setShowForm(false)
                }
              >
                Annuler
              </button>

              <button
                className="btn btn-primary"
                onClick={handleSave}
                disabled={
                  saving ||
                  !newLivre.titre ||
                  !newLivre.isbn
                }
              >
                {saving
                  ? "..."
                  : "Enregistrer"}
              </button>

            </div>
          </div>
        </div>
      )}
    </div>
  );
}