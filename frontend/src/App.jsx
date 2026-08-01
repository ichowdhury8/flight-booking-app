import { Route, Routes } from "react-router-dom";

import Footer from "./components/Footer";
import Header from "./components/Header";
import ConfirmationPage from "./pages/ConfirmationPage";
import NotFoundPage from "./pages/NotFoundPage";
import PassengerPage from "./pages/PassengerPage";
import SearchPage from "./pages/SearchPage";

export default function App() {
  return (
    <div className="page">
      <Header />

      <main className="main">
        <div className="container">
          <Routes>
            <Route path="/" element={<SearchPage />} />
            <Route path="/book/:flightId" element={<PassengerPage />} />
            <Route path="/booking/:reference" element={<ConfirmationPage />} />
            <Route path="*" element={<NotFoundPage />} />
          </Routes>
        </div>
      </main>

      <Footer />
    </div>
  );
}
