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
import datetime

router = APIRouter(
    prefix="/api/wav",
)

file_list = [0, 0, 0]

prob_list = [
    {'region': '경기', 'percentage': 0, 'color': '#ff6359'},
    {'region': '강원', 'percentage': 0, 'color': '#4682b4'},
    {'region': '전라', 'percentage': 0, 'color': '#3cb371'},
    {'region': '경상', 'percentage': 0, 'color': '#ffd700'},
    {'region': '충청', 'percentage': 0, 'color': '#800080'},
    {'region': '제주', 'percentage': 0, 'color': '#ffa500'}
]

UPLOAD_WEBM_DIR = "uploaded_webm_files"
os.makedirs(UPLOAD_WEBM_DIR, exist_ok=True)
UPLOAD_WAV_DIR = "uploaded_wav_files"
os.makedirs(UPLOAD_WAV_DIR, exist_ok=True)

'''
@router.options("/getwav")
async def preflight():
    response = JSONResponse()
    response.headers["Access-Control-Allow-Origin"] = "https://cola-mu.vercel.app"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
    response.headers["Access-Control-Allow-Credentials"] = "true"
    return response
'''


@router.post("/getwav/{index}")
async def upload_audio(index: int, audioFile: UploadFile = File(...)) -> JSONResponse:
    i = int(index)
    file_name = f"{i}_{datetime.datetime.now().strftime("%Y%m%d_%H%M%S")}.webm"
    file_path = os.path.join(UPLOAD_WEBM_DIR, file_name)

    with open(file_path, "wb") as file:
        contents = await audioFile.read()
        file.write(contents)

    file_size = os.path.getsize(file_path)
    token = str(uuid.uuid4())
    file_list[i - 1] = file_name

    return JSONResponse(content={
        "file_size": file_size,
        "token": token,
        "file_content_type": audioFile.content_type
    })


@router.get("/result/{index}")
async def wav_result(index: int):
    i = int(index)
    name = f"{file_list[i - 1][:-5]}.wav"
    path = os.path.join(UPLOAD_WAV_DIR, name)

    # if (audio => webm)
    sound = AudioSegment.from_file(f"./uploaded_webm_files/{file_list[i - 1]}", 'webm')
    sound.export(f"./uploaded_wav_files/{name}", format="wav")
    # elif (audio => mp4)
    # ...

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    checkpoint = 105
    checkpoint_dir = f"./inference/checkpoint-{checkpoint}"
    d = checkpoint_dir

    model = Wav2Vec2ForSequenceClassification.from_pretrained(d)

    id2label = model.config.id2label
    label2id = model.config.label2id

    model.to(device)

    probs, idxs = inference.predict_top3(f"./uploaded_wav_files/{name}")
    for k in range(3):
        index = idxs[k].item()
        prob = probs[k].item() * 100
        label = id2label[index]

        for j in prob_list:
            if j['region'] == label:
                j['percentage'] += prob


@router.get("/result/complicated/{index}")
async def wav_result_complicated(index: int):
    i = int(index)
    name = f"{file_list[i - 1][:-5]}.wav"
    path = os.path.join(UPLOAD_WAV_DIR, name)

    # if (audio => webm)
    sound = AudioSegment.from_file(f"./uploaded_webm_files/{file_list[i - 1]}", 'webm')
    sound.export(f"./uploaded_wav_files/{name}", format="wav")
    # elif (audio => mp4)
    # ...

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    checkpoint = 105
    checkpoint_dir = f"./inference/checkpoint-{checkpoint}"
    d = checkpoint_dir

    model = Wav2Vec2ForSequenceClassification.from_pretrained(d)

    id2label = model.config.id2label
    label2id = model.config.label2id

    model.to(device)

    probs, idxs = inference.predict_top3(f"./uploaded_wav_files/{name}")
    for k in range(3):
        index = idxs[k].item()
        prob = probs[k].item() * 100
        label = id2label[index]

        for j in prob_list:
            if j['region'] == label:
                j['percentage'] += prob

    return {"result": prob_list}

'''
@router.get("/result/graph")
async def wav_result_graph():
    path = "./uploaded_wav_files/"


    
    list1 = [198.24042577072393, 227.66866555638347, 287.05263598060753, 251.5409743840483, 216.20026535404142, 269.1545685635039, 292.33339655942547, 232.52419124696738, 235.07266946293973, 243.61524255864722, 254.06847079796955, 264.09609536824814, 218.8762659881506, 211.6231854469776, 246.1924231491936, 176.623358734001, 234.92997172728442, 188.95141126999948, 199.937948781763]
    list2 = [196.04581164200852, 213.93951412092557, 290.79467012549605, 293.363802859836, 283.227390688327, 280.2137596527201, 185.64535185445072, 176.80082563645692, 347.57794301852795, 328.499670886395, 214.545813485799, 215.74289268978507, 161.26799237037636, 229.10254722866654, 252.3500927394386]
    list3 = [310.92891031313513, 303.73629697240597, 302.8975116902129, 302.9897183004958, 306.886092071517, 341.2111533810065, 333.7385127094762, 299.0522160207035, 244.53726364921874, 209.15791388417531, 231.2965389213649, 286.17497583356845, 247.659159651274, 181.0060537397047, 178.16690417869023]

    #print("1")
    audio_path1 = path + f'{file_list[0][:-5]}.wav'
    audio_path2 = path + f'{file_list[1][:-5]}.wav'
    audio_path3 = path + f'{file_list[2][:-5]}.wav'

    #print("2")
    # 두 음성 파일 로드
    sound1 = parselmouth.Sound(audio_path1)
    sound2 = parselmouth.Sound(audio_path2)
    sound3 = parselmouth.Sound(audio_path3)

    #print("3")
    # 각 음성 파일의 피치 추출
    pitch1 = sound1.to_pitch()
    pitch2 = sound2.to_pitch()
    pitch3 = sound3.to_pitch()

    #print("4")
    # 피치 값 가져오기 (주파수)
    pitch_values1 = pitch1.selected_array['frequency']
    pitch_values2 = pitch2.selected_array['frequency']
    pitch_values3 = pitch3.selected_array['frequency']

    #print("5")
    # 시간 배열 계산
    times1 = pitch1.xs()
    times2 = pitch2.xs()
    times3 = pitch3.xs()

    #print("6")
    # 피치가 0이 아닌 값만 필터링
    valid_times1 = times1[pitch_values1 > 0]
    valid_pitch_values1 = pitch_values1[pitch_values1 > 0]
    valid_times2 = times2[pitch_values2 > 0]
    valid_pitch_values2 = pitch_values2[pitch_values2 > 0]
    valid_times3 = times3[pitch_values3 > 0]
    valid_pitch_values3 = pitch_values3[pitch_values3 > 0]

    #print("7")
    len1 = int(len(valid_times1) / 9.5)
    len2 = int(len(valid_times2) / 9.5)
    len3 = int(len(valid_times3) / 9.5)
    # /'/샘플 추출
    #print("8")
    sampled_pitch_values1 = valid_pitch_values1[::len1]
    sampled_pitch_values2 = valid_pitch_values2[::len2]
    sampled_pitch_values3 = valid_pitch_values3[::len3]

    #print("9")
    # 데이터를 리스트로 저장
    voice1_data = list(sampled_pitch_values1)
    voice2_data = list(sampled_pitch_values2)
    voice3_data = list(sampled_pitch_values3)
    
    audio_path1 = path + '오늘+나는+블루베리스무디를+먹었어_.wav'
    audio_path2 = path + '일요일엔+뭐+타고+오셨어요_.wav'

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

    # 샘플 추출
    sampled_pitch_values1 = valid_pitch_values1[::10]
    sampled_pitch_values2 = valid_pitch_values2[::10]

    voice1_data = list(sampled_pitch_values1)
    voice2_data = list(sampled_pitch_values2)

    return {'list1': voice1_data, 'list2': voice2_data,
            'list3': voice1_data, 'list4': voice2_data,
            'list5': voice1_data, 'list6': voice2_data}
'''


@router.get("/result/graph")
async def wav_result_graph():
    path = "./uploaded_wav_files/"
    audio_path1 = path + '오늘+나는+블루베리스무디를+먹었어_.wav'
    audio_path2 = path + '일요일엔+뭐+타고+오셨어요_.wav'
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
