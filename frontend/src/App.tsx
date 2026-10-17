import ObservatoryDashboard from "./dashboard/ObservatoryDashboard";
import "./App.css";

export default function App() {
  return (
    <main className="app">
      <header className="app-header">
        <h1 className="app-title">Nexus Observatory</h1>
        <p className="app-subtitle">Cloud-disk share URL parser • classifier • catalog</p>
      </header>
      <ObservatoryDashboard />
    </main>
  );
}