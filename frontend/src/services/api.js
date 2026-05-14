/**
 * — Couche API
 * Centralise tous les appels HTTP vers les microservices backend.
 *
 * Architecture :
 *   livresAPI    → http://localhost:8001
 *   usersAPI     → http://localhost:8002
 *   empruntsAPI  → http://localhost:8003
 *   recoAPI      → http://localhost:8004
 */

import axios from 'axios';

const LIVRES_URL   = process.env.REACT_APP_LIVRES_URL   || 'http://localhost:8001';
const USERS_URL    = process.env.REACT_APP_USERS_URL    || 'http://localhost:8002';
const EMPRUNTS_URL = process.env.REACT_APP_EMPRUNTS_URL || 'http://localhost:8003';
const RECO_URL     = process.env.REACT_APP_RECO_URL     || 'http://localhost:8004';

//  Instances Axios par service 
const livresAPI   = axios.create({ baseURL: `${LIVRES_URL}/api` });
const usersAPI    = axios.create({ baseURL: `${USERS_URL}/api` });
const empruntsAPI = axios.create({ baseURL: `${EMPRUNTS_URL}/api` });
const recoAPI     = axios.create({ baseURL: RECO_URL });


// SERVICE LIVRES

export const livresService = {
  /** Lister tous les livres */
  lister: (params = {}) => livresAPI.get('/livres/', { params }),

  /** Détail d'un livre */
  detail: (id) => livresAPI.get(`/livres/${id}/`),

  /** Recherche */
  rechercher: (q) => livresAPI.get('/livres/search/', { params: { q } }),

  /** Livres disponibles */
  disponibles: () => livresAPI.get('/livres/disponibles/'),

  /** Catégories */
  categories: () => livresAPI.get('/livres/categories/'),

  /** Ajouter un livre */
  ajouter: (data) => livresAPI.post('/livres/', data),

  /** Modifier un livre */
  modifier: (id, data) => livresAPI.put(`/livres/${id}/`, data),

  /** Supprimer un livre */
  supprimer: (id) => livresAPI.delete(`/livres/${id}/`),
};


// SERVICE UTILISATEURS

export const usersService = {
  /** Lister tous les utilisateurs */
  lister: () => usersAPI.get('/users/'),

  /** Profil d'un utilisateur */
  profil: (id) => usersAPI.get(`/users/${id}/profil/`),

  /** Créer un utilisateur */
  creer: (data) => usersAPI.post('/users/', data),

  /** Modifier un utilisateur */
  modifier: (id, data) => usersAPI.put(`/users/${id}/`, data),

  /** Rechercher */
  rechercher: (q) => usersAPI.get('/users/search/', { params: { q } }),

  /** Filtrer par type */
  parType: (type) => usersAPI.get('/users/par-type/', { params: { type } }),

  /** Statistiques */
  statistiques: () => usersAPI.get('/users/statistiques/'),
};


// SERVICE EMPRUNTS

export const empruntsService = {
  /** Emprunter un livre */
  emprunter: (utilisateur_id, livre_id) =>
    empruntsAPI.post('/emprunts/emprunter/', { utilisateur_id, livre_id }),

  /** Retourner un livre */
  retourner: (id, note, commentaire) =>
    empruntsAPI.post(`/emprunts/${id}/retourner/`, { note_utilisateur: note, commentaire }),

  /** Historique (filtrable) */
  historique: (params = {}) => empruntsAPI.get('/emprunts/historique/', { params }),

  /** Emprunts en retard */
  retards: () => empruntsAPI.get('/emprunts/retards/'),

  /** Statistiques */
  statistiques: () => empruntsAPI.get('/emprunts/statistiques/'),
};


// #SERVICE RECOMMANDATION

export const recoService = {
  /** Recommandations pour un utilisateur */
  recommandations: (userId, n = 5) =>
    recoAPI.get(`/recommendations/${userId}`, { params: { n } }),

  /** Entraîner le modèle */
  entrainer: (params = {}) => recoAPI.post('/train', params),

  /** Infos du modèle */
  modelInfo: () => recoAPI.get('/model/info'),

  /** Health check */
  health: () => recoAPI.get('/health'),
};