import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import CreatorView from './views/CreatorView';
import DisplayView from './views/DisplayView';
import AdminView from './views/AdminView';
import './App.css';

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<CreatorView />} />
        <Route path="/create" element={<CreatorView />} />
        <Route path="/display" element={<DisplayView />} />
        <Route path="/admin" element={<AdminView />} />
      </Routes>
    </Router>
  );
}

export default App;
