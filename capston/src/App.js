import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { CSSTransition } from 'react-transition-group';
import './App.css';

const profileImg = process.env.PUBLIC_URL + '/profile.jpg';
const logoImg = process.env.PUBLIC_URL + '/logo.jpg';

function App() {
  const [nickname, setNickname] = useState('');
  const [inProp, setInProp] = useState(true);  // 애니메이션 상태
  const navigate = useNavigate();

  const handleStart = () => {
    if (nickname.trim() === '') {
      alert('닉네임을 입력해주세요.');
      return;
    }
    console.log('시작하기!');
    setInProp(false);  // 애니메이션 트리거
    setTimeout(() => {
      navigate('/nextPage', { state: { nickname } });
    }, 1000); // 애니메이션 지속시간 후 페이지 이동
  };

  useEffect(() => {
    window.scrollTo(0, 0);
}, []);

  return (
    <CSSTransition in={inProp} timeout={1000} classNames="slide" unmountOnExit>
      <div className="App">
        <header className="App-header">
          <img src={logoImg} alt="logo" className="App-logo" />
          <p className="description">
            소리로보는 지역, <br />우리의 다양성을 음성으로 담다
          </p>
        </header>
        <main className="App-main">
          <div className="circle-box">
            <p>나의 사투리는 어떨까?<br />닉네임을 설정하고 시작해보자!</p>
            <div className="profile-container">
              <img src={profileImg} alt="profile" className="profile-image" />
              <input
                type="text"
                placeholder="닉네임을 입력해주세요"
                className="nickname-input"
                value={nickname}
                onChange={(e) => setNickname(e.target.value)}
              />
              <button className="start-btn" onClick={handleStart}>시작하기</button>
            </div>
          </div>
        </main>
        <footer className="App-footer">
          <p>&copy; 2024 Dialect Classification Service</p>
        </footer>
      </div>
    </CSSTransition>
  );
}

export default App;