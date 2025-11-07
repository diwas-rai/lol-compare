import { RouterProvider } from "react-router-dom";
import "./App.css";
import { router } from "./constants/router/router";

export default function App() {
  return (
    <div className="App">
      <RouterProvider router={router} />
    </div>
  );
}
