import React, { useState, useEffect } from "react";
import { usersService } from "../services/api";


const TYPE_CONFIG = {
  etudiant: {
    label: "Étudiant",
    color: "#3B82F6",
    image:
      "https://images.unsplash.com/photo-1522202176988-66273c2fd55f?q=80&w=1200&auto=format&fit=crop",
  },

  professeur: {
    label: "Professeur",
    color: "#F59E0B",
    image:
      "https://images.unsplash.com/photo-1500648767791-00dcc994a43e?q=80&w=1200&auto=format&fit=crop",
  },

  personnel: {
    label: "Personnel",
    color: "#10B981",
    image:
      "https://images.unsplash.com/photo-1494790108377-be9c29b29330?q=80&w=1200&auto=format&fit=crop",
  },
};

export default function Utilisateurs() {

  const [users, setUsers] = useState([]);

  const [loading, setLoading] =
    useState(true);

  const [filtre, setFiltre] =
    useState("tous");

  const [search, setSearch] =
    useState("");

  const [showForm, setShowForm] =
    useState(false);

  const [saving, setSaving] =
    useState(false);

  const [newUser, setNewUser] =
    useState({
      nom: "",
      prenom: "",
      email: "",
      type_user: "etudiant",
      matricule: "",
      telephone: "",
    });

  const fetchUsers = async () => {

    setLoading(true);

    try {

      const res =
        await usersService.lister();

      const data =
        res.data.results ||
        res.data;

      setUsers(
        Array.isArray(data)
          ? data
          : []
      );

    } catch (e) {
      console.log(e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchUsers();
  }, []);

  const usersFiltres =
    users.filter((u) => {

      const matchType =
        filtre === "tous" ||
        u.type_user === filtre;

      const matchSearch =
        !search ||
        `${u.nom} ${u.prenom} ${u.email}`
          .toLowerCase()
          .includes(
            search.toLowerCase()
          );

      return (
        matchType && matchSearch
      );
    });

  const handleSave = async () => {

    setSaving(true);

    try {

      await usersService.creer(
        newUser
      );

      setShowForm(false);

      setNewUser({
        nom: "",
        prenom: "",
        email: "",
        type_user: "etudiant",
        matricule: "",
        telephone: "",
      });

      fetchUsers();

    } catch (e) {
      console.log(e);
    } finally {
      setSaving(false);
    }
  };

  return (

    <div className="users-page">

      {/* HERO */}

      <div className="users-hero">

        <div className="hero-overlay"></div>

        <div className="hero-content">

          <div>

            <span className="hero-badge">
              DIT Library Platform
            </span>

            <h1>
              Gestion, Utilisateur
            </h1>

            <p>
              Gerer tous les etudiants, professors 
              et membres du professionel dans 
              le systeme bibliothèque numérique
            </p>
          </div>

          <button
            className="hero-btn"
            onClick={() =>
              setShowForm(true)
            }
          >
            + ajouter un utilisateur
          </button>
        </div>
      </div>

      {/* STATS */}

      <div className="users-stats">

        <div className="stat-box">
          <span>Total Utilisateurs</span>
          <strong>
            {users.length}
          </strong>
        </div>

        <div className="stat-box">
          <span>Etudiants</span>
          <strong>
            {
              users.filter(
                (u) =>
                  u.type_user ===
                  "etudiant"
              ).length
            }
          </strong>
        </div>

        <div className="stat-box">
          <span>Professeurs</span>
          <strong>
            {
              users.filter(
                (u) =>
                  u.type_user ===
                  "professeur"
              ).length
            }
          </strong>
        </div>

        <div className="stat-box">
          <span>Staff</span>
          <strong>
            {
              users.filter(
                (u) =>
                  u.type_user ===
                  "personnel"
              ).length
            }
          </strong>
        </div>
      </div>

      {/* FILTERS */}

      <div className="users-toolbar">

        <div className="search-input">

          <input
            type="text"
            placeholder="Search users..."
            value={search}
            onChange={(e) =>
              setSearch(
                e.target.value
              )
            }
          />
        </div>

        <div className="toolbar-filters">

          <button
            className={
              filtre === "tous"
                ? "active"
                : ""
            }
            onClick={() =>
              setFiltre("tous")
            }
          >
            All
          </button>

          <button
            className={
              filtre === "etudiant"
                ? "active"
                : ""
            }
            onClick={() =>
              setFiltre(
                "etudiant"
              )
            }
          >
            Etudiants
          </button>

          <button
            className={
              filtre ===
              "professeur"
                ? "active"
                : ""
            }
            onClick={() =>
              setFiltre(
                "professeur"
              )
            }
          >
            Professeurs
          </button>

          <button
            className={
              filtre ===
              "personnel"
                ? "active"
                : ""
            }
            onClick={() =>
              setFiltre(
                "personnel"
              )
            }
          >
            Staff
          </button>
        </div>
      </div>

      {/* LOADING */}

      {loading ? (

        <div className="users-loader">

          <div className="loader"></div>

        </div>

      ) : (

        <div className="users-grid">

          {usersFiltres.map((u) => {

            const cfg =
              TYPE_CONFIG[
                u.type_user
              ] ||
              TYPE_CONFIG.etudiant;

            return (

              <div
                className="user-card"
                key={u.id}
              >

                {/* IMAGE */}

                <div className="user-cover">

                  <img
                    src={cfg.image}
                    alt="user"
                  />

                  <div
                    className="role-badge"
                    style={{
                      background:
                        cfg.color,
                    }}
                  >
                    {cfg.label}
                  </div>
                </div>

                {/* CONTENT */}

                <div className="user-body">

                  <div className="user-name-section">

                    <h3>
                      {u.prenom}{" "}
                      {u.nom}
                    </h3>

                    <p>
                      {u.email}
                    </p>
                  </div>

                  <div className="user-details">

                    <div className="detail-item">
                      <span>
                        Matricule
                      </span>

                      <strong>
                        {u.matricule ||
                          "—"}
                      </strong>
                    </div>

                    <div className="detail-item">
                      <span>
                        Telephone
                      </span>

                      <strong>
                        {u.telephone ||
                          "—"}
                      </strong>
                    </div>

                    <div className="detail-item">
                      <span>
                        Status
                      </span>

                      <strong
                        style={{
                          color:
                            u.actif
                              ? "#10B981"
                              : "#EF4444",
                        }}
                      >
                        {u.actif
                          ? "Active"
                          : "Inactive"}
                      </strong>
                    </div>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      )}

      {/* MODAL */}

      {showForm && (

        <div className="modal-overlay">

          <div className="create-modal">

            <div className="modal-top">

              <h2>
                Create nouveau utilisateur
              </h2>

              <button
                onClick={() =>
                  setShowForm(false)
                }
              >
                ✕
              </button>
            </div>

            <div className="modal-grid">

              <input
                type="text"
                placeholder="First name"
                value={newUser.prenom}
                onChange={(e) =>
                  setNewUser({
                    ...newUser,
                    prenom:
                      e.target.value,
                  })
                }
              />

              <input
                type="text"
                placeholder="Last name"
                value={newUser.nom}
                onChange={(e) =>
                  setNewUser({
                    ...newUser,
                    nom:
                      e.target.value,
                  })
                }
              />

              <input
                type="email"
                placeholder="Email"
                value={newUser.email}
                onChange={(e) =>
                  setNewUser({
                    ...newUser,
                    email:
                      e.target.value,
                  })
                }
              />

              <input
                type="text"
                placeholder="Matricule"
                value={
                  newUser.matricule
                }
                onChange={(e) =>
                  setNewUser({
                    ...newUser,
                    matricule:
                      e.target.value,
                  })
                }
              />

              <input
                type="text"
                placeholder="Telephone"
                value={
                  newUser.telephone
                }
                onChange={(e) =>
                  setNewUser({
                    ...newUser,
                    telephone:
                      e.target.value,
                  })
                }
              />

              <select
                value={
                  newUser.type_user
                }
                onChange={(e) =>
                  setNewUser({
                    ...newUser,
                    type_user:
                      e.target.value,
                  })
                }
              >
                <option value="etudiant">
                  Etudiants
                </option>

                <option value="professeur">
                  Professeurs
                </option>

                <option value="personnel">
                  Staff
                </option>
              </select>
            </div>

            <button
              className="create-btn"
              onClick={handleSave}
              disabled={saving}
            >
              {saving
                ? "Saving..."
                : "Create User"}
            </button>
          </div>
        </div>
      )}
    </div>
  );
}