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
from dataclasses import dataclass

router = APIRouter(
    prefix="/api/wav",
)


class Result(BaseModel):
    result: list


@dataclass
class Audiofile:
    file_list: list = None
    cnt: int = 0
    flag: int = 0


af = Audiofile()

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
    af.file_list.append(file_name)

    return JSONResponse(content={
        "file_size": file_size,
        "token": token,
        "file_content_type": audioFile.content_type
    })


@router.get("/result")
async def wav_result():
    name = f"{af.file_list[af.cnt][:-5]}.wav"
    path = os.path.join(UPLOAD_WAV_DIR, name)

    #if (audio => webm)
    sound = AudioSegment.from_file(f"./uploaded_webm_files/{af.file_list[af.cnt]}", 'webm')
    sound.export(f"./uploaded_wav_files/{name}", format="wav")
    # elif (audio => mp4)
    #...

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    checkpoint = 105
    checkpoint_dir = f"./inference/checkpoint-{checkpoint}"
    d = checkpoint_dir

    model = Wav2Vec2ForSequenceClassification.from_pretrained(d)

    id2label = model.config.id2label
    label2id = model.config.label2id

    model.to(device)

    probs, idxs = inference.predict_top3(f"./uploaded_wav_files/{name}")
    for i in range(3):
        index = idxs[i].item()
        prob = probs[i].item() * 100
        label = id2label[index]

        for j in prob_list:
            if j['region'] == label:
                j['percentage'] += prob

    af.cnt += 1


@router.get("/result/complicated")
async def wav_result_complicated():
    return {"result": prob_list}


@router.get("/result/graph")
async def wav_result_graph():
    path = "./uploaded_wav_files/"
    audio_path1 = path + f'{af.file_list[0][:-5]}.wav'
    audio_path2 = path + f'{af.file_list[1][:-5]}.wav'
    audio_path3 = path + f'{af.file_list[2][:-5]}.wav'
    sen1_path = path + '한이는+서강대학교+학생이야_.wav'
    sen2_path = path + '일요일엔+뭐+타고+오셨어요_.wav'
    sen3_path = path + '오늘+나는+블루베리스무디를+먹었어_.wav'

    # 두 음성 파일 로드
    sound1 = parselmouth.Sound(audio_path1)
    sound2 = parselmouth.Sound(audio_path2)
    sound3 = parselmouth.Sound(audio_path3)
    sen1 = parselmouth.Sound(sen1_path)
    sen2 = parselmouth.Sound(sen2_path)
    sen3 = parselmouth.Sound(sen3_path)

    # 각 음성 파일의 피치 추출
    pitch1 = sound1.to_pitch()
    pitch2 = sound2.to_pitch()
    pitch3 = sound3.to_pitch()
    pitch4 = sen1.to_pitch()
    pitch5 = sen2.to_pitch()
    pitch6 = sen3.to_pitch()

    # 피치 값 가져오기 (주파수)
    pitch_values1 = pitch1.selected_array['frequency']
    pitch_values2 = pitch2.selected_array['frequency']
    pitch_values3 = pitch3.selected_array['frequency']
    pitch_values4 = pitch4.selected_array['frequency']
    pitch_values5 = pitch5.selected_array['frequency']
    pitch_values6 = pitch6.selected_array['frequency']

    # 시간 배열 계산
    times1 = pitch1.xs()
    times2 = pitch2.xs()
    times3 = pitch3.xs()
    times4 = pitch4.xs()
    times5 = pitch5.xs()
    times6 = pitch6.xs()

    # 피치가 0이 아닌 값만 필터링
    valid_times1 = times1[pitch_values1 > 0]
    valid_pitch_values1 = pitch_values1[pitch_values1 > 0]
    valid_times2 = times2[pitch_values2 > 0]
    valid_pitch_values2 = pitch_values2[pitch_values2 > 0]
    valid_times3 = times3[pitch_values3 > 0]
    valid_pitch_values3 = pitch_values3[pitch_values3 > 0]
    valid_times4 = times4[pitch_values4 > 0]
    valid_pitch_values4 = pitch_values4[pitch_values4 > 0]
    valid_times5 = times5[pitch_values5 > 0]
    valid_pitch_values5 = pitch_values5[pitch_values5 > 0]
    valid_times6 = times6[pitch_values6 > 0]
    valid_pitch_values6 = pitch_values6[pitch_values6 > 0]

    len1 = int(len(valid_times1) / 9.5)
    len2 = int(len(valid_times2) / 9.5)
    len3 = int(len(valid_times3) / 9.5)
    len4 = int(len(valid_times4) / 9.5)
    len5 = int(len(valid_times5) / 9.5)
    len6 = int(len(valid_times6) / 9.5)
    # /'/샘플 추출
    sampled_pitch_values1 = valid_pitch_values1[::len1]
    sampled_pitch_values2 = valid_pitch_values2[::len2]
    sampled_pitch_values3 = valid_pitch_values3[::len3]
    sampled_pitch_values4 = valid_pitch_values4[::len4]
    sampled_pitch_values5 = valid_pitch_values5[::len5]
    sampled_pitch_values6 = valid_pitch_values6[::len6]

    # 데이터를 리스트로 저장
    voice1_data = list(sampled_pitch_values1)
    voice2_data = list(sampled_pitch_values2)
    voice3_data = list(sampled_pitch_values3)
    voice4_data = list(sampled_pitch_values4)
    voice5_data = list(sampled_pitch_values5)
    voice6_data = list(sampled_pitch_values6)

    return {'list1': voice1_data, 'list2': voice4_data,
            'list3': voice2_data, 'list4': voice5_data,
            'list5': voice3_data, 'list6': voice6_data}
