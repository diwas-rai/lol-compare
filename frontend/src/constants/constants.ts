declare global {
  interface Window {
    VITE_APP_API_URL?: string;
  }
}

export const API_URL =
  window.VITE_APP_API_URL ?? import.meta.env.VITE_APP_API_URL;
