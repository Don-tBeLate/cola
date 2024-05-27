from fastapi import APIRouter, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from pydub import AudioSegment
import uuid
import os

import parselmouth

from transformers import Wav2Vec2ForSequenceClassification, Wav2Vec2FeatureExtractor
import torch

from inference import inference

router = APIRouter(
    prefix="/api/wav",
)

class Result(BaseModel):
    result: list


prob_list = [
    {'region': '경기', 'percentage': 30, 'color': '#ff6359'},
    {'region': '강원', 'percentage': 20, 'color': '#4682b4'},
    {'region': '전라', 'percentage': 10, 'color': '#3cb371'},
    {'region': '경상', 'percentage': 0, 'color': '#ffd700'},
    {'region': '충청', 'percentage': 0, 'color': '#800080'},
    {'region': '제주', 'percentage': 0, 'color': '#ffa500'}
]

UPLOAD_WEBM_DIR = "uploaded_webm_files"
os.makedirs(UPLOAD_WEBM_DIR, exist_ok=True)
UPLOAD_WAV_DIR = "uploaded_wav_files"
os.makedirs(UPLOAD_WAV_DIR, exist_ok=True)

file_list = []


@router.options("/getwav")
async def preflight():
    response = JSONResponse()
    response.headers["Access-Control-Allow-Origin"] = "https://cola-mu.vercel.app"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
    response.headers["Access-Control-Allow-Credentials"] = "true"
    return response


@router.post("/getwav")
async def upload_audio(audioFile: UploadFile = File(...)) -> JSONResponse:
    file_name = f"{uuid.uuid4()}.webm"
    file_path = os.path.join(UPLOAD_WEBM_DIR, file_name)

    with open(file_path, "wb") as file:
        contents = await audioFile.read()
        file.write(contents)

    file_size = os.path.getsize(file_path)
    token = str(uuid.uuid4())
    file_list.append(file_name)

    return JSONResponse(content={
        "file_size": file_size,
        "token": token,
        "file_content_type": audioFile.content_type
    })


@router.get("/result/complicated")
async def wav_result_complicated():
    for f in file_list:
        name = f"{f[:-5]}.wav"
        print("1")
        path = os.path.join(UPLOAD_WAV_DIR, name)
        print("2")

        sound = AudioSegment.from_file(f"./uploaded_webm_files/{f}", 'webm')
        print("3")
        sound.export(f"./uploaded_wav_files/{name}", format="wav")
        print("4")

        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        print("5")
        checkpoint = 105
        checkpoint_dir = f"./inference/checkpoint-{checkpoint}"
        print("6")
        d = checkpoint_dir

        model = Wav2Vec2ForSequenceClassification.from_pretrained(d)
        print("7")

        id2label = model.config.id2label
        label2id = model.config.label2id
        print("8")

        model.to(device)
        print("9")

        probs, idxs = inference.predict_top3(f"./uploaded_wav_files/{name}")
        for i in range(3):
            index = idxs[i].item()
            prob = probs[i].item() * 100
            label = id2label[index]
            print(label + ' ' + prob)

            for j in prob_list:
                if j['region'] == label:
                    j['percentage'] += prob
            print("10")

    return {"result": prob_list}


@router.get("/result/graph")
async def wav_result_graph():
    path = "./uploaded_wav_files/"
    audio_path1 = path + f'{file_list[0][:-5]}.wav'
    audio_path2 = path + f'{file_list[1][:-5]}.wav'

    # 두 음성 파일 로드
    sound1 = parselmouth.Sound(audio_path1)
    sound2 = parselmouth.Sound(audio_path2)

    # 각 음성 파일의 피치 추출
    pitch1 = sound1.to_pitch()
    pitch2 = sound2.to_pitch()

    # 피치 값 가져오기 (주파수)
    pitch_values1 = pitch1.selected_array['frequency']
    pitch_values2 = pitch2.selected_array['frequency']

    # 시간 배열 계산
    times1 = pitch1.xs()
    times2 = pitch2.xs()

    # 피치가 0이 아닌 값만 필터링
    valid_times1 = times1[pitch_values1 > 0]
    valid_pitch_values1 = pitch_values1[pitch_values1 > 0]
    valid_times2 = times2[pitch_values2 > 0]
    valid_pitch_values2 = pitch_values2[pitch_values2 > 0]

    len1 = int(len(valid_times1) / 9.5)
    len2 = int(len(valid_times2) / 9.5)
    # /'/샘플 추출
    sampled_times1 = valid_times1[::len1]
    sampled_pitch_values1 = valid_pitch_values1[::len1]
    sampled_times2 = valid_times2[::len2]
    sampled_pitch_values2 = valid_pitch_values2[::len2]
    '''
    # 그래프 출력
    plt.figure(figsize=(10, 4))  # 그래프 크기 설정
    plt.plot(sampled_times1, sampled_pitch_values1, '-', linewidth=2, color='rosybrown',
             label='Voice 1')  # 음성 1 피치 데이터 플롯
    plt.plot(sampled_times2, sampled_pitch_values2, '-', linewidth=2, color='indianred',
             label='Voice 2')  # 음성 2 피치 데이터 플롯
    plt.fill_between(sampled_times1, sampled_pitch_values1, color='rosybrown', alpha=0.1)  # 음성 1 피치 아래 영역 채우기
    plt.fill_between(sampled_times2, sampled_pitch_values2, color='indianred', alpha=0.1)  # 음성 2 피치 아래 영역 채우기
    plt.grid(True)  # 그리드 표시
    plt.title('Pitch Contours of Two Voices (Sampled)')  # 그래프 제목
    plt.xlabel('Time (s)')  # x축 레이블
    plt.ylabel('Pitch (Hz)')  # y축 레이블
    plt.legend()  # 범례 표시
    plt.show()  # 그래프 표시
    '''
    # 데이터를 리스트로 저장
    voice1_data = list(sampled_pitch_values1)
    voice2_data = list(sampled_pitch_values2)

    return {'list1': voice1_data, 'list2': voice2_data,
            'list3': voice1_data, 'list4': voice2_data,
            'list5': voice1_data, 'list6': voice2_data}
