# import the necessary packages
from scipy.spatial import distance as dist
from collections import OrderedDict
import numpy as np


class CentroidTracker:
    def __init__(self, maxDisappeared=50, maxDistance=50):
        # 순서가 지정된 두 개와 함께 다음 고유 개체 ID를 초기화
        # 주어진 객체 매핑을 추적하는 데 사용되는 사전
        # 중심에 대한 ID와 연속 프레임 수
        # 각각 "사라짐"으로 표시됨
        self.nextObjectID = 0
        self.objects = OrderedDict()
        self.disappeared = OrderedDict()
        self.bbox = OrderedDict()  # CHANGE

        # 주어진 최대 연속 프레임 수를 저장
        # 객체는 우리가 끝날 때까지 "사라진" 것으로 표시될 수 있음
        # 추적에서 개체를 등록 취소해야 함
        self.maxDisappeared = maxDisappeared

        # 연관시킬 중심 사이의 최대 거리를 저장.
        # 객체 -- 거리가 이 최대값보다 큰 경우
        # 객체를 "사라진" 것으로 표시하기 시작할 거리
        self.maxDistance = maxDistance

    def register(self, centroid, inputRect):
        # 객체를 등록할 때 사용 가능한 다음 객체를 사용
        # 중심을 저장할 ID
        self.objects[self.nextObjectID] = centroid
        self.bbox[self.nextObjectID] = inputRect  # CHANGE
        self.disappeared[self.nextObjectID] = 0
        self.nextObjectID += 1

    def deregister(self, objectID):
        # 객체 ID를 등록 취소하기 위해 객체 ID를 삭제
        # 각각의 사전 모두
        del self.objects[objectID]
        del self.disappeared[objectID]
        del self.bbox[objectID]  # CHANGE

    def update(self, rects):
        # 입력 경계 상자 직사각형 목록이 있는지 확인
        # 비었다
        if len(rects) == 0:
            # 기존의 추적된 개체를 반복하고 표시
            # 사라진 것처럼
            for objectID in list(self.disappeared.keys()):
                self.disappeared[objectID] += 1

                # 최대 연속 수에 도달한 경우
                # 주어진 객체가 다음과 같이 표시된 프레임
                # 누락, 등록 취소
                if self.disappeared[objectID] > self.maxDisappeared:
                    self.deregister(objectID)

            # 중심이나 추적 정보가 없으므로 일찍 반환
            # 업데이트
            # self.object를 반환
            return self.bbox

        # 현재 프레임의 입력 중심 배열을 초기화
        inputCentroids = np.zeros((len(rects), 2), dtype="int")
        inputRects = []
        # 경계 상자 사각형을 반복
        for (i, (startX, startY, endX, endY)) in enumerate(rects):
            # 경계 상자 좌표를 사용하여 중심을 유도
            cX = int((startX + endX) / 2.0)
            cY = int((startY + endY) / 2.0)
            inputCentroids[i] = (cX, cY)
            inputRects.append(rects[i])  # CHANGE

        # 현재 추적 중인 객체가 없으면 입력 받음
        # centroids 및 각각 등록
        if len(self.objects) == 0:
            for i in range(0, len(inputCentroids)):
                self.register(inputCentroids[i], inputRects[i])  # CHANGE

        # 그렇지 않으면 현재 추적 중인 개체이므로 다음을 수행해야 함
        # 입력 중심을 기존 객체와 일치시키려고 시도
        # centroids
        else:
            # 개체 ID 및 해당 중심 집합을 가져옴
            objectIDs = list(self.objects.keys())
            objectCentroids = list(self.objects.values())

            # 각 객체 쌍 사이의 거리를 계산
            # 중심 및 입력 중심, 각각 -- 우리의
            # 목표는 입력 중심을 기존의 중심과 일치시키는 것
            # object centroid
            D = dist.cdist(np.array(objectCentroids), inputCentroids)

            # 이 일치를 수행하려면 (1) 다음을 찾아야 함
            # 각 행에서 가장 작은 값 다음 (2) 행 정렬
            # 최소값을 기준으로 인덱스를 생성하여 행이
            # 인덱스의 *앞*에서 가장 작은 값
            # list
            rows = D.min(axis=1).argsort()

            # 다음으로 열에 대해 유사한 프로세스를 수행
            # 각 열에서 가장 작은 값을 찾은 다음
            # 이전에 계산된 행 인덱스 목록을 사용하여 정렬
            cols = D.argmin(axis=1)[rows]

            # 만일 우리가 업데이트, 등록을 결정하기 위하여
            # 또는 추적해야 하는 객체의 등록을 취소합니다.
            # 이미 조사한 행 및 열 인덱스 수
            usedRows = set()
            usedCols = set()

            # (행, 열) 인덱스 조합에 대한 루프
            # tuples
            for (row, col) in zip(rows, cols):
                # 만약 우리가 이미 그 줄이나 혹은 둘 중 하나를 조사했다면
                # 이전 열 값, 무시
                if row in usedRows or col in usedCols:
                    continue

                # 중심 사이의 거리가 다음보다 큰 경우
                # 최대 거리, 둘을 연결하지 않음
                # 같은 객체에 대한 중심
                if D[row, col] > self.maxDistance:
                    continue

                # 그렇지 않으면 현재 행의 개체 ID를 가져옴
                # 새로운 중심을 설정하고 사라진 것을 재설정
                # counter
                objectID = objectIDs[row]
                self.objects[objectID] = inputCentroids[col]
                self.bbox[objectID] = inputRects[col]  # CHANGE
                self.disappeared[objectID] = 0

                # 각 행을 검사했음을 나타내며
                # 열 인덱스, 각각
                usedRows.add(row)
                usedCols.add(col)

            # 아직 가지고 있지 않은 행과 열 인덱스를 모두 계산
            # examined
            unusedRows = set(range(0, D.shape[0])).difference(usedRows)
            unusedCols = set(range(0, D.shape[1])).difference(usedCols)

            # 객체 중심의 수가 다음과 같은 경우
            # 입력 중심의 수와 같거나 더 큼
            # 이러한 객체 중 일부가
            # 잠재적으로 사라짐
            if D.shape[0] >= D.shape[1]:
                # 사용하지 않는 행 인덱스에 대한 루프
                for row in unusedRows:
                    # 해당 행에 대한 개체 ID를 가져옴
                    # 사라진 카운터를 인덱싱하고 증가시킴
                    objectID = objectIDs[row]
                    self.disappeared[objectID] += 1

                    # 연속된 숫자가 있는지 확인
                    # 개체가 "사라짐"으로 표시된 프레임
                    # 객체 등록 취소 영장
                    if self.disappeared[objectID] > self.maxDisappeared:
                        self.deregister(objectID)

            # 그렇지 않으면 입력 중심의 수가 더 많은 경우
            # 우리가 필요로 하는 기존 객체 중심의 수보다
            # 각각의 새로운 입력 중심을 추적 가능한 객체로 등록
            else:
                for col in unusedCols:
                    self.register(inputCentroids[col], inputRects[col])

        # 추적 가능한 객체 세트를 반환
        # self.object를 반환
        return self.bbox

