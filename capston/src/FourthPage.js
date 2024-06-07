import React, { useState, useEffect, useRef } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import './NextPage.css';
import { FaMicrophone } from "react-icons/fa6";
import { FaHeadphones } from "react-icons/fa6";


function FourthPage() {
  const navigate = useNavigate();
  const location = useLocation();
  const nickname = location.state?.nickname;
  const previousAudioUrls = location.state?.audioUrls || [];
  const [isLoading, setLoading] = useState(false);
  const [recording, setRecording] = useState(false);
  const [audioUrl, setAudioUrl] = useState('');
  const [showModal, setShowModal] = useState(false);
  const [timer, setTimer] = useState(0);
  const [intervalId, setIntervalId] = useState(null);
  const mediaRecorderRef = useRef(null);
  const audioChunksRef = useRef([]);
  const [fileSize, setFileSize] = useState(null);
  const [token, setToken] = useState(null);
  const [fileContentType, setFileContentType] = useState(null);
  const [allResults, setAllResults] = useState([]);

  useEffect(() => {
    window.scrollTo(0, 0);
  }, []);


  const goToFifthPage = () => {
    if (!audioUrl) {
      alert('녹음이 완료되지 않았습니다. 녹음을 완료해 주세요.');
      return;
    }
    navigate('/fifthPage', { state: { nickname, audioUrls: [...previousAudioUrls, audioUrl] } });
  };

  useEffect(() => {
    const link = document.createElement('link');
    link.rel = 'stylesheet';
    link.href = 'https://fonts.googleapis.com/css2?family=Poor+Story&display=swap';
    document.head.appendChild(link);

    return () => {  // Cleanup to stop any ongoing recordings when the component unmounts
      mediaRecorderRef.current?.stream.getTracks().forEach(track => track.stop());
    };
  }, []);

  const handleRecording = async () => {
    if (!recording) {
      try {
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        mediaRecorderRef.current = new MediaRecorder(stream);
        audioChunksRef.current = [];

        mediaRecorderRef.current.ondataavailable = (event) => {
          audioChunksRef.current.push(event.data);
        };

        mediaRecorderRef.current.onstop = async () => {
          const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/mp4' });
          const url = URL.createObjectURL(audioBlob);
          setAudioUrl(url);
          setShowModal(false);

          const index = "3";
          const formData = new FormData();
          formData.append('audioFile', audioBlob, 'recording.mp4'); // Specify the filename to ensure correct handling

          try {
            const response = await fetch("https://kakacola.com/api/wav/getwav/" + index, {
              method: 'POST',
              body: formData
            });

            if (!response.ok) {
              throw new Error('Network response was not ok');
            }

            const data = await response.json();
            setFileSize(data.file_size);
            setToken(data.token);
            setFileContentType(data.file_content_type);
            console.log(data);

          } catch (error) {
            console.error('파일 업로드 실패:', error);
          }
        };

        mediaRecorderRef.current.start();
        setShowModal(true);
        setRecording(true);
        startTimer();
      } catch (error) {
        console.error('Error starting recording:', error);
        alert('Failed to start recording. Please ensure the microphone is not in use or blocked.');
      }
    } else {
      mediaRecorderRef.current.stop();
      setRecording(false);
      stopTimer();
    }
  };

  const startTimer = () => {
    const id = setInterval(() => {
      setTimer(prev => prev + 1);
    }, 1000);
    setIntervalId(id);
  };

  const stopTimer = () => {
    clearInterval(intervalId);
    setIntervalId(null);
    setTimer(0);
  };

  const playRecording = () => {
    if (audioUrl) {
      const audio = new Audio(audioUrl);
      audio.play();
    }
  };

  return (
    <div className="SecondPage">
      <div className="header">
        <div className="progress-container">
          <div className="progress-bar" style={{ width: '75%' }}></div>
        </div>
      </div>
      <div className={`content ${showModal ? 'dim' : ''}`}>
        {showModal && <div className="modal">{recording ? `Recording... ${timer}s` : 'Press record to start'}</div>}
        <h1 className="greeting">{nickname ? `${nickname}님, ` : ''}<br />아래 문장을 녹음해 주세요.</h1>
        <img src={process.env.PUBLIC_URL + '/profile2.jpg'} alt="profile" className="profile-image2" />
        <div className="buttons">
          <button className="record-btn" onClick={handleRecording} title={recording ? "Stop Recording" : "Start Recording"}>
            {recording ? <FaMicrophone size={30} className="recording" /> : <FaMicrophone size={30} />}
          </button>
          <button className="listen-btn" onClick={playRecording} disabled={!audioUrl} title="Play Recording">
            <FaHeadphones size={45} />
          </button>
        </div>
        <div className="sentence-box">
          <p className="sentence-title">SENTENCE 3.</p>
          <p className="sentence-content">오늘 나는 블루베리스무디를 먹었어.</p>
        </div>
        <button className="next-btn" onClick={goToFifthPage}>결과 확인하기</button>
      </div>
    </div>
  );
}

export default FourthPage;