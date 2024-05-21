import React, { useState, useEffect } from 'react';
import { Line } from 'react-chartjs-2';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faPlay } from '@fortawesome/free-solid-svg-icons';
import { Chart, CategoryScale, LinearScale, PointElement, LineElement } from 'chart.js';
import { useLocation } from 'react-router-dom';
import { useNavigate } from 'react-router-dom';
import './nextAnalysisPage.css';

Chart.register(CategoryScale, LinearScale, PointElement, LineElement);

const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    scales: {
        x: {
            display: false
        }
    }
};

const sentenceTitles = [
    "\"코카콜라 맛있다 맛있으면 더먹지\"",
    "Sentence 2",
    "Sentence 3"
];

function NextAnalysisPage() {
    const [audioPlaying, setAudioPlaying] = useState(null);
    const [standardSentences, setStandardSentences] = useState([]);
    const [userSentences, setUserSentences] = useState([]);
    const navigate = useNavigate();
    const location = useLocation();
    const { nickname, audioUrls } = location.state;

    useEffect(() => {
        window.scrollTo(0, 0);
    }, []);

    useEffect(() => {
        const fetchData = async () => {
            try {
                const response = await fetch('http://127.0.0.1:8000/api/wav/result/graph'); // 여기
                const data = await response.json();
                // 여기
                setStandardSentences(data.standardSentences);
                setUserSentences(data.userSentences);
            } catch (error) {
                console.error('Error fetching data:', error);
            }
        };

        fetchData();
    }, []);

    const goToFinalPage = () => {
        navigate('/final', { state: { nickname } });
    };

    const playAudio = (src) => {
        if (audioPlaying) {
            audioPlaying.pause();
            audioPlaying.currentTime = 0;
        }
        const audio = new Audio(src);
        audio.play();
        setAudioPlaying(audio);
    };

    useEffect(() => {
        const link = document.createElement('link');
        link.rel = 'stylesheet';
        link.href = 'https://fonts.googleapis.com/css2?family=Poor+Story&display=swap';
        document.head.appendChild(link);
    }, []);

    const createChartData = (standardData, userData, title) => ({
        title: title,
        labels: Array.from({ length: standardData.length }, (_, i) => `Point ${i + 1}`),
        datasets: [
            {
                label: '표준어 수치',
                data: standardData,
                borderColor: '#f08080',
                tension: 0.1,
                pointRadius: 0
            },
            {
                label: '나의 문장 수치',
                data: userData,
                borderColor: '#99b5db',
                tension: 0.1,
                pointRadius: 0
            }
        ]
    });

    return (
        <div className="next-analysis-page">
            <header>
                <h1>{nickname}님의<br />피치 비교 결과는?</h1>
                <img src={process.env.PUBLIC_URL + '/profile.jpg'} alt="profile" className="profile-image" />
            </header>
            <div className="analysis-container">
                {standardSentences.length > 0 && userSentences.length > 0 && standardSentences.map((standardData, index) => (
                    <div key={`section-${index}`} className="graph-section">
                        <h3>{sentenceTitles[index]}</h3>
                        <div style={{ height: '200px', width: '100%' }}>
                            <Line data={createChartData(standardData, userSentences[index], sentenceTitles[index])} options={chartOptions} />
                        </div>
                        <div className="audio-buttons">
                            <button onClick={() => playAudio(`audio${index + 1}standard.mp3`)} className="audio-button-l">
                                <FontAwesomeIcon icon={faPlay} />
                            </button>
                            <span>표준음</span>
                            <span className="vs-text">vs</span>
                            <button onClick={() => playAudio(`audio${index + 1}mine.mp3`)} className="audio-button-f">
                                <FontAwesomeIcon icon={faPlay} />
                            </button>
                            <span>내 음성</span>
                        </div>
                    </div>
                ))}
            </div>
            <button className="next-btn" onClick={goToFinalPage}>다음 페이지로</button>
        </div>
    );
}

export default NextAnalysisPage;