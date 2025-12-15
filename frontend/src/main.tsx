import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import { API_URL } from "./constants/constants";
import App from "./App.tsx";
import "./index.css";

const queryClient = new QueryClient();

queryClient.prefetchQuery({
  queryKey: ["warmup"],
  queryFn: async () => {
    const res = await fetch(`${API_URL}api/warmup`);
    return res.json();
  },
});
createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <QueryClientProvider client={queryClient}>
      <App />
    </QueryClientProvider>
  </StrictMode>,
);
