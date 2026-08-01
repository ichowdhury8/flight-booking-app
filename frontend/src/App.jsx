import { Route, Routes } from "react-router-dom";

import Footer from "./components/Footer";
import Header from "./components/Header";
import NotFoundPage from "./pages/NotFoundPage";
import PlaceholderPage from "./pages/PlaceholderPage";
import SearchPage from "./pages/SearchPage";

export default function App() {
  return (
    <div className="page">
      <Header />

      <main className="main">
        <div className="container">
          <Routes>
            <Route path="/" element={<SearchPage />} />
            <Route
              path="/book/:flightId"
              element={<PlaceholderPage title="Passenger details" task={11} />}
            />
            <Route
              path="/booking/:reference"
              element={<PlaceholderPage title="Booking confirmed" task={12} />}
            />
            <Route path="*" element={<NotFoundPage />} />
          </Routes>
        </div>
      </main>

      <Footer />
    </div>
  );
}
