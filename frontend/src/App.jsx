import React from "react";
import { BrowserRouter, Routes, Route, NavLink } from "react-router-dom";

import Catalogue from "./pages/Catalogue";
import Emprunts from "./pages/Emprunts";
import Utilisateurs from "./pages/Utilisateurs";
import Recommandations from "./pages/Recommandations";
import Dashboard from "./pages/Dashboard";

import "./App.css";

function TopBanner() {
  return (
    <div className="top-banner">
      <div className="top-banner-left">
        <span>📍 Dakar Institute of Technology</span>
        <span>📚 Bibliothèque Universitaire</span>
      </div>

      <div className="top-banner-right">
        <span>📞 +221 33 000 00 00</span>
        <span>✉️ bibliotheque@dit.sn</span>
      </div>
    </div>
  );
}

function Navbar() {
  return (
    <header className="navbar-wrapper">
      <nav className="navbar">

        {/* LOGO */}

        <NavLink to="/" className="navbar-brand">

          <div className="brand-logo">
            <img
              src="https://images.unsplash.com/photo-1521587760476-6c12a4b040da?q=80&w=1200&auto=format&fit=crop"
              alt="library"
            />
          </div>

          <div className="brand-text-block">
            <h2>DIT Library</h2>
            <p>Dakar Institute of Technology</p>
          </div>
        </NavLink>

        {/* LINKS */}

        <div className="navbar-links">

          <NavLink
            to="/"
            className={({ isActive }) =>
              isActive ? "nav-link active" : "nav-link"
            }
          >
            Dashboard
          </NavLink>

          <NavLink
            to="/catalogue"
            className={({ isActive }) =>
              isActive ? "nav-link active" : "nav-link"
            }
          >
            Catalogue
          </NavLink>

          <NavLink
            to="/emprunts"
            className={({ isActive }) =>
              isActive ? "nav-link active" : "nav-link"
            }
          >
            Emprunts
          </NavLink>

          <NavLink
            to="/utilisateurs"
            className={({ isActive }) =>
              isActive ? "nav-link active" : "nav-link"
            }
          >
            Membres
          </NavLink>

          <NavLink
            to="/recommandations"
            className={({ isActive }) =>
              isActive ? "nav-link active ia-link" : "nav-link ia-link"
            }
          >
            <span className="ia-dot"></span>
            Recommandations IA
          </NavLink>
        </div>
      </nav>
    </header>
  );
}

function Footer() {
  return (
    <footer className="footer">

      <div className="footer-content">

        <div>
          <h3>DIT Library</h3>

          <p>
            Plateforme moderne de gestion de bibliothèque universitaire.
          </p>
        </div>

        <div className="footer-links">
          <span>Catalogue</span>
          <span>Utilisateurs</span>
          <span>Emprunts</span>
          <span>IA Recommandation</span>
        </div>
      </div>

      <div className="footer-bottom">
        © 2024 Dakar Institute of Technology — Tous droits réservés.
      </div>
    </footer>
  );
}

export default function App() {
  return (
    <BrowserRouter>

      <div className="app-layout">

        <TopBanner />

        <Navbar />

        <main className="main-content">

          <Routes>

            <Route
              path="/"
              element={<Dashboard />}
            />

            <Route
              path="/catalogue"
              element={<Catalogue />}
            />

            <Route
              path="/emprunts"
              element={<Emprunts />}
            />

            <Route
              path="/utilisateurs"
              element={<Utilisateurs />}
            />

            <Route
              path="/recommandations"
              element={<Recommandations />}
            />

          </Routes>

        </main>

        <Footer />

      </div>

    </BrowserRouter>
  );
}