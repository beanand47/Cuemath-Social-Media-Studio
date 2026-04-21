const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

async function request(path, options = {}) {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    headers: {
      "Content-Type": "application/json",
      ...(options.headers || {}),
    },
    ...options,
  });

  if (!response.ok) {
    const errorText = await response.text();
    try {
      const parsed = JSON.parse(errorText);
      throw new Error(parsed.detail || "Request failed");
    } catch {
      throw new Error(errorText || "Request failed");
    }
  }

  return response.json();
}

export function generateCarousel(payload) {
  return request("/generate", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}
