import React, { useState, useEffect } from "react";

import {
  livresService,
  usersService,
  empruntsService,
  recoService,
} from "../services/api";

import libraryImage from "../assets/books/library.jpg";

export default function Dashboard() {

  const [stats, setStats] = useState(null);

  const [loading, setLoading] = useState(true);

  useEffect(() => {

    Promise.allSettled([
      livresService.lister(),
      usersService.statistiques(),
      empruntsService.statistiques(),
      recoService.health(),
    ]).then(([livres, users, emprunts, model]) => {

      setStats({
        livres:
          livres.status === "fulfilled"
            ? livres.value.data
            : null,

        users:
          users.status === "fulfilled"
            ? users.value.data
            : null,

        emprunts:
          emprunts.status === "fulfilled"
            ? emprunts.value.data
            : null,

        modele:
          model.status === "fulfilled"
            ? model.value.data
            : null,
      });

      setLoading(false);
    });

  }, []);

  if (loading) {

    return (

      <div className="loading">

        <div className="spinner"></div>

      </div>
    );
  }

  const services = [

    {
      name: "Books Service",
      port: 8001,
      ok: !!stats?.livres,
    },

    {
      name: "Users Service",
      port: 8002,
      ok: !!stats?.users,
    },

    {
      name: "Loans Service",
      port: 8003,
      ok: !!stats?.emprunts,
    },

    {
      name: "AI Recommendation",
      port: 8004,
      ok: !!stats?.modele,
    },
  ];

  const distributions = [

    {
      label: "Étudiants",
      count:
        stats?.users?.par_type
          ?.etudiants || 0,
      icon: "🎓",
    },

    {
      label: "Professeurs",
      count:
        stats?.users?.par_type
          ?.professeurs || 0,
      icon: "👨‍🏫",
    },

    {
      label: "Personnel",
      count:
        stats?.users?.par_type
          ?.personnel || 0,
      icon: "🏢",
    },
  ];

  return (

    <div className="fade-in">

      {/* HERO */}

      <div
        className="hero"
        style={{
          backgroundImage: `
            linear-gradient(
              rgba(13,74,42,0.88),
              rgba(26,107,60,0.88)
            ),
            url(${libraryImage})
          `,
          backgroundSize: "cover",
          backgroundPosition: "center",
        }}
      >

        <div>

          <span className="hero-tag">
            DIT SMART LIBRARY
          </span>

          <h1>
            Bibliothèque
            <br />
            Universitaire Intelligente
          </h1>

          <p>
            Gérez les livres, les emprunts,
            les utilisateurs et les
            recommandations IA depuis une
            plateforme moderne.
          </p>
        </div>

        <div className="hero-icon">
          📚
        </div>
      </div>

      {/* HEADER */}

      <div className="page-header">

        <div>

          <h1 className="page-title">
            Tableau de bord{" "}
            <span>Administrateur</span>
          </h1>

          <p className="page-subtitle">
            Vue globale de la bibliothèque
            universitaire
          </p>
        </div>
      </div>

      {/* STATS */}

      <div className="stats-grid">

        <div className="stat-card">

          <span className="stat-icon">
            📚
          </span>

          <span className="stat-value">
            {stats?.livres?.count || 0}
          </span>

          <span className="stat-label">
            Livres
          </span>
        </div>

        <div className="stat-card">

          <span className="stat-icon">
            👥
          </span>

          <span className="stat-value">
            {stats?.users?.total || 0}
          </span>

          <span className="stat-label">
            Utilisateurs
          </span>
        </div>

        <div className="stat-card">

          <span className="stat-icon">
            📖
          </span>

          <span className="stat-value">
            {stats?.emprunts
              ?.total_emprunts || 0}
          </span>

          <span className="stat-label">
            Emprunts
          </span>
        </div>

        <div className="stat-card">

          <span className="stat-icon">
            ⚠️
          </span>

          <span
            className="stat-value"
            style={{
              color:
                stats?.emprunts
                  ?.en_retard > 0
                  ? "var(--danger)"
                  : undefined,
            }}
          >
            {stats?.emprunts
              ?.en_retard || 0}
          </span>

          <span className="stat-label">
            Retards
          </span>
        </div>
      </div>

      {/* MAIN GRID */}

      <div
        style={{
          display: "grid",
          gridTemplateColumns:
            "repeat(auto-fit,minmax(320px,1fr))",
          gap: "1.5rem",
        }}
      >

        {/* USERS */}

        <div className="card">

          <div className="card-header">

            <h3 className="card-title">
              Répartition des utilisateurs
            </h3>

            <span className="badge badge-info">
              Temps réel
            </span>
          </div>

          <div
            style={{
              display: "flex",
              flexDirection: "column",
              gap: "1.2rem",
            }}
          >

            {distributions.map(
              (item, index) => {

                const total =
                  stats?.users?.total || 1;

                const percentage =
                  Math.round(
                    (item.count / total) *
                      100
                  );

                return (

                  <div key={index}>

                    <div
                      style={{
                        display: "flex",
                        justifyContent:
                          "space-between",
                        marginBottom:
                          "0.4rem",
                      }}
                    >

                      <span
                        style={{
                          fontWeight: 600,
                        }}
                      >
                        {item.icon}{" "}
                        {item.label}
                      </span>

                      <strong>
                        {item.count}
                      </strong>
                    </div>

                    <div
                      style={{
                        width: "100%",
                        height: "10px",
                        background:
                          "var(--grey-200)",
                        borderRadius:
                          "20px",
                        overflow: "hidden",
                      }}
                    >

                      <div
                        style={{
                          width: `${percentage}%`,
                          height: "100%",
                          background:
                            "linear-gradient(90deg,var(--green-main),var(--green-mid))",
                          borderRadius:
                            "20px",
                        }}
                      ></div>
                    </div>

                    <div
                      style={{
                        fontSize: "0.75rem",
                        color:
                          "var(--grey-500)",
                        marginTop: "4px",
                      }}
                    >
                      {percentage}% du total
                    </div>
                  </div>
                );
              }
            )}
          </div>
        </div>

        {/* SERVICES */}

        <div className="card">

          <div className="card-header">

            <h3 className="card-title">
              État des microservices
            </h3>

            <span className="badge badge-success">
              Infrastructure
            </span>
          </div>

          <div
            style={{
              display: "flex",
              flexDirection: "column",
              gap: "1rem",
            }}
          >

            {services.map(
              (service, index) => (

                <div
                  key={index}
                  style={{
                    display: "flex",
                    justifyContent:
                      "space-between",
                    alignItems:
                      "center",
                    padding: "1rem",
                    border:
                      "1px solid var(--grey-200)",
                    borderRadius:
                      "var(--radius)",
                    background:
                      "var(--grey-50)",
                  }}
                >

                  <div
                    style={{
                      display: "flex",
                      alignItems:
                        "center",
                      gap: "12px",
                    }}
                  >

                    <div
                      style={{
                        width: "12px",
                        height: "12px",
                        borderRadius:
                          "50%",
                        background:
                          service.ok
                            ? "var(--success)"
                            : "var(--danger)",
                        boxShadow:
                          service.ok
                            ? "0 0 12px rgba(39,174,96,0.5)"
                            : "0 0 12px rgba(192,57,43,0.5)",
                      }}
                    ></div>

                    <div>

                      <div
                        style={{
                          fontWeight: 700,
                          color:
                            "var(--grey-900)",
                        }}
                      >
                        {service.name}
                      </div>

                      <div
                        style={{
                          fontSize:
                            "0.8rem",
                          color:
                            "var(--grey-500)",
                        }}
                      >
                        localhost:
                        {service.port}
                      </div>
                    </div>
                  </div>

                  <span
                    className={`badge ${
                      service.ok
                        ? "badge-success"
                        : "badge-danger"
                    }`}
                  >
                    {service.ok
                      ? "Online"
                      : "Offline"}
                  </span>
                </div>
              )
            )}
          </div>
        </div>
      </div>

      {/* QUICK INFO */}

      <div
        style={{
          marginTop: "2rem",
        }}
      >

        <div className="card">

          <div className="card-header">

            <h3 className="card-title">
              Informations système
            </h3>
          </div>

          <div
            style={{
              display: "grid",
              gridTemplateColumns:
                "repeat(auto-fit,minmax(200px,1fr))",
              gap: "1rem",
            }}
          >

            <div>

              <div
                style={{
                  fontSize: "0.8rem",
                  color:
                    "var(--grey-500)",
                  marginBottom: "4px",
                }}
              >
                Institution
              </div>

              <strong>
                Dakar Institute of Technology
              </strong>
            </div>

            <div>

              <div
                style={{
                  fontSize: "0.8rem",
                  color:
                    "var(--grey-500)",
                  marginBottom: "4px",
                }}
              >
                Système
              </div>

              <strong>
                Smart Library Platform
              </strong>
            </div>

            <div>

              <div
                style={{
                  fontSize: "0.8rem",
                  color:
                    "var(--grey-500)",
                  marginBottom: "4px",
                }}
              >
                Intelligence artificielle
              </div>

              <strong>
                {stats?.modele
                  ? "Active"
                  : "Indisponible"}
              </strong>
            </div>

            <div>

              <div
                style={{
                  fontSize: "0.8rem",
                  color:
                    "var(--grey-500)",
                  marginBottom: "4px",
                }}
              >
                Statut global
              </div>

              <strong
                style={{
                  color:
                    "var(--success)",
                }}
              >
                Opérationnel
              </strong>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}