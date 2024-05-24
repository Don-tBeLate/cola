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
    const [allSentences, setAllSentences] = useState([]);
    const navigate = useNavigate();
    const location = useLocation();
    const { nickname, allResults, audioUrls } = location.state;

    useEffect(() => {
        window.scrollTo(0, 0);
    }, []);

    useEffect(() => {
        const fetchData = async () => {
            try {
                const response = await fetch('http://3.34.59.190/api/wav/result/graph');
                const data = await response.json();
                if (data.list1 && data.list2 && data.list3 && data.list4 && data.list5 && data.list6) {
                    setAllSentences([data.list1, data.list2, data.list3, data.list4, data.list5, data.list6]);
                } else {
                    console.error('Unexpected data format:', data);
                }
            } catch (error) {
                console.error('Error fetching data:', error);
            }
        };

        fetchData();
    }, []);

    const goToFinalPage = () => {
        navigate('/final', { state: { nickname, allResults, audioUrls } });
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

    const createChartData = (data1, data2, title) => ({
        title: title,
        labels: Array.from({ length: data1.length }, (_, i) => `Point ${i + 1}`),
        datasets: [
            {
                label: 'Data 1',
                data: data1,
                borderColor: '#f08080',
                tension: 0.1,
                pointRadius: 0
            },
            {
                label: 'Data 2',
                data: data2,
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
                {allSentences.length === 6 && (
                    <>
                        {Array.from({ length: 3 }).map((_, index) => (
                            <div key={`section-${index}`} className="graph-section">
                                <h3>{sentenceTitles[index]}</h3>
                                <div style={{ height: '200px', width: '100%' }}>
                                    <Line data={createChartData(allSentences[index * 2], allSentences[index * 2 + 1], sentenceTitles[index])} options={chartOptions} />
                                </div>
                                <div className="audio-buttons">
                                    <button onClick={() => playAudio(audioUrls[index])} className="audio-button-l">
                                        <FontAwesomeIcon icon={faPlay} />
                                    </button>
                                    <span>음성 {index + 1}</span>
                                </div>
                            </div>
                        ))}
                    </>
                )}
            </div>
            <button className="next-btn" onClick={goToFinalPage}>다음 페이지로</button>
        </div>
    );
}

export default NextAnalysisPage;
