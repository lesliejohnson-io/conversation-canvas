
import { createRoot } from "react-dom/client";
import App from "./App.tsx";
import "./styles/index.css";

console.log("CSS loaded");

createRoot(document.getElementById("root")!).render(<App />);
  