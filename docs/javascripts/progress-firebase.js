// Study path on the home page: per-step "completed" toggles, a progress bar and
// a rail that fills up to the last completed step.
//
// Progress lives in Firestore (project infra-handbook-progress):
//   progress/{uid}    the owner's own document, read and written only by them
//   progress/public   a read-only mirror that every visitor sees
// Both have the shape { steps: { <stepId>: { done, updatedAt } } }. Only the
// owner can write (enforced by firestore.rules); everyone else reads the mirror.
//
// The last state seen is cached in localStorage, so the path still shows
// progress offline or when the SDK can't load. Without JS the path renders as
// a plain list.

import { firebaseConfig, OWNER_EMAIL } from "./firebase-config.js";

const SDK = "https://www.gstatic.com/firebasejs/12.19.0/";
const CACHE_KEY = "hb-study-path-cache";

let firebase = null; // { auth, db, fns } once the SDK has loaded
let loading = null;
let user = null;
let unsubscribe = null;
let view = null; // the study path currently on the page, if any

function loadCache() {
  try {
    return JSON.parse(localStorage.getItem(CACHE_KEY)) || {};
  } catch (e) {
    return {};
  }
}

function saveCache(steps) {
  try {
    localStorage.setItem(CACHE_KEY, JSON.stringify(steps));
  } catch (e) {
    /* private mode or storage blocked: the cache is only a fallback */
  }
}

// { stepId: { done } } from a Firestore document's data.
function stepsFrom(data) {
  const steps = {};
  Object.entries((data && data.steps) || {}).forEach(([id, value]) => {
    steps[id] = { done: !!(value && value.done) };
  });
  return steps;
}

function isOwner(u) {
  return !!u && u.emailVerified && u.email === OWNER_EMAIL;
}

function loadFirebase() {
  if (!loading) {
    loading = Promise.all([
      import(SDK + "firebase-app.js"),
      import(SDK + "firebase-auth.js"),
      import(SDK + "firebase-firestore.js"),
    ]).then(([app, auth, fs]) => {
      const instance = app.initializeApp(firebaseConfig);
      let db;
      try {
        // Keeps a local copy, so reads work offline and writes sync later.
        db = fs.initializeFirestore(instance, {
          localCache: fs.persistentLocalCache({ tabManager: fs.persistentMultipleTabManager() }),
        });
      } catch (e) {
        db = fs.getFirestore(instance);
      }
      firebase = { auth: auth.getAuth(instance), db, authApi: auth, fs };
      auth.onAuthStateChanged(firebase.auth, (u) => {
        user = u;
        subscribe();
        if (view) view.render();
      });
      return firebase;
    });
  }
  return loading;
}

// Listen to the owner's document when they are signed in, else to the mirror.
function subscribe() {
  if (unsubscribe) unsubscribe();
  unsubscribe = null;
  const { fs, db } = firebase;
  const ref = isOwner(user) ? fs.doc(db, "progress", user.uid) : fs.doc(db, "progress", "public");
  unsubscribe = fs.onSnapshot(
    ref,
    { includeMetadataChanges: true },
    (snap) => {
      if (!view) return;
      view.steps = stepsFrom(snap.data());
      view.offline = snap.metadata.fromCache;
      view.pending = snap.metadata.hasPendingWrites;
      view.error = "";
      if (!snap.metadata.fromCache) saveCache(view.steps);
      view.render();
    },
    () => {
      if (!view) return;
      view.error = "No se pudo leer el progreso. Se muestra el último estado conocido.";
      view.render();
    }
  );
}

// Writes the given steps to the owner's document and to the public mirror.
function write(changes) {
  const { fs, db } = firebase;
  const steps = {};
  Object.entries(changes).forEach(([id, done]) => {
    steps[id] = { done, updatedAt: fs.serverTimestamp() };
  });
  const batch = fs.writeBatch(db);
  batch.set(fs.doc(db, "progress", user.uid), { steps }, { merge: true });
  batch.set(fs.doc(db, "progress", "public"), { steps }, { merge: true });
  return batch.commit();
}

function init() {
  const path = document.querySelector(".hb-path");
  if (!path) {
    view = null;
    return;
  }
  if (path.dataset.ready) return;
  path.dataset.ready = "1";

  const list = path.querySelector(".hb-path__steps");
  const steps = Array.from(path.querySelectorAll(".hb-step"));

  const progress = document.createElement("div");
  progress.className = "hb-progress";
  progress.innerHTML =
    '<div class="hb-progress__text"><strong></strong>' +
    '<span class="hb-progress__actions">' +
    '<button type="button" class="hb-progress__reset">Reiniciar</button>' +
    '<button type="button" class="hb-progress__auth"></button>' +
    "</span></div>" +
    '<div class="hb-progress__bar" aria-hidden="true"><span></span></div>' +
    '<p class="hb-progress__status" role="status" aria-live="polite"></p>';
  path.parentNode.insertBefore(progress, path);
  const label = progress.querySelector("strong");
  const bar = progress.querySelector(".hb-progress__bar span");
  const reset = progress.querySelector(".hb-progress__reset");
  const authButton = progress.querySelector(".hb-progress__auth");
  const status = progress.querySelector(".hb-progress__status");

  const state = { steps: loadCache(), offline: true, pending: false, error: "", busy: false };

  function setDone(changes) {
    const before = {};
    Object.keys(changes).forEach((id) => {
      before[id] = !!(state.steps[id] && state.steps[id].done);
      state.steps[id] = { done: changes[id] };
    });
    state.error = "";
    render();
    write(changes).catch(() => {
      // Rejected by the rules or the server: put the previous state back.
      Object.entries(before).forEach(([id, done]) => (state.steps[id] = { done }));
      state.error = "No se pudo guardar el cambio. Intenta de nuevo.";
      render();
    });
  }

  steps.forEach((step) => {
    const button = document.createElement("button");
    button.type = "button";
    button.className = "hb-step__toggle";
    button.addEventListener("click", () => {
      if (!isOwner(user)) return;
      const id = step.dataset.step;
      setDone({ [id]: !(state.steps[id] && state.steps[id].done) });
    });
    step.appendChild(button);
  });

  reset.addEventListener("click", () => {
    if (!isOwner(user)) return;
    const changes = {};
    steps.forEach((step) => (changes[step.dataset.step] = false));
    setDone(changes);
  });

  authButton.addEventListener("click", () => {
    if (!firebase || state.busy) return;
    const { auth, authApi } = firebase;
    state.busy = true;
    state.error = "";
    render();
    const action = user
      ? authApi.signOut(auth)
      : authApi.signInWithPopup(auth, new authApi.GoogleAuthProvider());
    action
      .catch((e) => {
        if (e && (e.code === "auth/popup-closed-by-user" || e.code === "auth/cancelled-popup-request")) return;
        state.error = "No se pudo iniciar sesión. Revisa tu conexión e intenta de nuevo.";
      })
      .finally(() => {
        state.busy = false;
        render();
      });
  });

  function message() {
    if (state.error) return state.error;
    if (!firebase) return "";
    if (user && !isOwner(user)) return "Sesión iniciada como " + user.email + ". Solo el dueño del manual puede marcar etapas.";
    if (state.pending) return "Sin conexión: el cambio se guardará al reconectar.";
    if (state.offline) return "Sin conexión: se muestra el último estado conocido.";
    return "";
  }

  function render() {
    const owner = isOwner(user);
    let done = 0;
    let last = null;
    let next = null;
    steps.forEach((step) => {
      const isDone = !!(state.steps[step.dataset.step] && state.steps[step.dataset.step].done);
      const button = step.querySelector(".hb-step__toggle");
      step.classList.toggle("is-done", isDone);
      step.classList.remove("is-next");
      button.disabled = !owner;
      button.classList.toggle("is-done", isDone);
      if (owner) {
        button.setAttribute("aria-pressed", String(isDone));
        button.textContent = isDone ? "Completada" : "Marcar como completada";
      } else {
        // Read-only: a status label, not a control.
        button.removeAttribute("aria-pressed");
        button.textContent = isDone ? "Completada" : "Pendiente";
      }
      if (isDone) {
        done++;
        last = step;
      } else if (!next) {
        next = step;
      }
    });
    if (next) next.classList.add("is-next");

    const pct = Math.round((done / steps.length) * 100);
    label.textContent =
      done === steps.length
        ? "Ruta completa: " + done + " de " + steps.length + " etapas"
        : done + " de " + steps.length + " etapas completadas";
    bar.style.width = pct + "%";
    reset.hidden = !owner || done === 0;

    authButton.hidden = !firebase;
    authButton.disabled = state.busy;
    authButton.textContent = user ? "Cerrar sesión" : "Iniciar sesión";

    const text = message();
    status.textContent = text;
    status.hidden = !text;

    // Rail fill ends at the marker of the last completed step.
    const fill = last ? last.offsetTop + 28 : 0;
    list.style.setProperty("--hb-fill", fill + "px");
  }

  view = state;
  state.render = render;
  render();
  window.addEventListener("resize", () => view === state && render());

  loadFirebase()
    .then(() => {
      // Already loaded on an earlier page: listen again for this page's view.
      if (unsubscribe) subscribe();
      render();
    })
    .catch(() => {
      state.error = "No se pudo cargar Firebase. Se muestra el último estado conocido.";
      render();
    });

  // Reveal steps as they scroll into view (skipped when motion is reduced).
  const reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  if (!reduce && "IntersectionObserver" in window) {
    path.classList.add("hb-path--animate");
    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            entry.target.classList.add("is-visible");
            observer.unobserve(entry.target);
          }
        });
      },
      { rootMargin: "0px 0px -10% 0px" }
    );
    steps.forEach((step) => observer.observe(step));
  }
}

// Material's instant navigation swaps pages without a full reload.
if (window.document$) window.document$.subscribe(init);
else if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", init);
else init();
