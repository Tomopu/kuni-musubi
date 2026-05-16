export const PREFERENCES_STORAGE_KEY = "kuni-musubi.preferences";

function resolveApiBaseUrl(): string {
  if (process.env.NEXT_PUBLIC_API_BASE_URL) {
    return process.env.NEXT_PUBLIC_API_BASE_URL;
  }

  if (typeof window !== "undefined") {
    return `http://${window.location.hostname}:8000`;
  }

  return "http://localhost:8000";
}

export const API_BASE_URL = resolveApiBaseUrl();
