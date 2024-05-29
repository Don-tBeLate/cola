import React from 'react';
import ReactDOM from 'react-dom';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import App from './App';
import NextPage from './NextPage';
import ThirdPage from './ThirdPage';
import FourthPage from './FourthPage';
import FifthPage from './FifthPage';
import NextAnalysisPage from './nextAnalysisPage';
import Final from './final';

ReactDOM.render(
  <React.StrictMode>
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<App />} />
        <Route path="/nextPage" element={<NextPage />} />
        <Route path="/thirdPage" element={<ThirdPage />} />
        <Route path="/fourthPage" element={<FourthPage />} />
        <Route path="/fifthPage" element={<FifthPage />} />
        <Route path="/nextAnalysisPage" element={<NextAnalysisPage />} />
        <Route path="/final" element={<Final />} />

      </Routes>
    </BrowserRouter>
  </React.StrictMode>,
  document.getElementById('root')
);