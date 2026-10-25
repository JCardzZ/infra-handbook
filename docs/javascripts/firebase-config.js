// Firebase web app config for project infra-handbook-progress (app
// infra-handbook-web), from `firebase apps:sdkconfig WEB <appId>`.
// These values identify the project; they are not secrets. Access is
// controlled by firestore.rules. See README.md.

export const firebaseConfig = {
  apiKey: "AIzaSyCBqTrOIxqzBNClb-zrFn8iiFA3aSGpDEc",
  authDomain: "infra-handbook-progress.firebaseapp.com",
  projectId: "infra-handbook-progress",
  storageBucket: "infra-handbook-progress.firebasestorage.app",
  messagingSenderId: "14893446693",
  appId: "1:14893446693:web:794fe7ee4dbeb4866871cc",
};

// The only account allowed to mark steps. firestore.rules checks the same email.
export const OWNER_EMAIL = "cardozamanuel96@gmail.com";
