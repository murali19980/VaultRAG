import axios from "axios";

const api = axios.create({
  baseURL: "http://localhost:8000",
  timeout: 120_000,
  headers: { "Content-Type": "application/json" },
});

api.interceptors.response.use(
  (res) => res,
  (error) => {
    if (error.response) {
      console.error(
        `API error ${error.response.status}:`,
        error.response.data
      );
    } else if (error.request) {
      console.error("API no response:", error.message);
    } else {
      console.error("API request setup error:", error.message);
    }
    return Promise.reject(error);
  }
);

export default api;
