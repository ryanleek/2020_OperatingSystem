import time
import random
#알고리즘 및 세부 기능들 
#블록이 버퍼에 존재하는지 확인
def exist(Bn, i):
    if Bn in HQ_Header[i]: return True
    else: return False

#버퍼가 이용 중 인지 확인
def not_free(Bn):
    if Bn in FreeList: return False
    else: return True

#프로세스를 sleep 상태로 전환(1초 정지, 3회차에 wake)
def sleep(Bn):
    global slp_iter
    slp_iter += 1   #sleep 카운터 1증가
    time.sleep(1)   #1초 대기

    #sleep 카운터가 3 이라면
    if slp_iter == 3:   
        slp_iter = 0    #카운터 초기화
        FreeList.append(Bn) #버퍼는 free로 전환(자유리스트에 추가)
        print("- slp3: process awake, buffer('%s') available" % Bn)
    
    #sleep 카운터가 3 이하라면
    else:               #휴면 상태
        print("- slp%d: sleeping..." % slp_iter)

#자유 리스트에 버퍼가 없을 때 사용 중인 임의 버퍼 반환(다른 프로세스 종료를 시뮬레이션)
def randombfr(N):
    while 1:
        i = random.randrange(0,N)
        if HQ_Header[i]:
            j = random.randrange(0,len(HQ_Header[i]))
            Bn = HQ_Header[i][j]
            return Bn
            
#메모리 write 대기 중 인지 확인, 출력
def delayed():
    if FreeList[0] in Delayed:  #자유 리스트에서 출력 지연 버퍼 확인
        n = FreeList.pop(0)     #자유 리스트에서 제거
        Delayed.remove(n)       #지연출력 리스트에서 제거(메모리로 출력)
        print("- buffer('%s') freed, written to memory" % n)
        return True
    else: return False

#버퍼의 공간을 새로운 버퍼 공간으로 수정
def replacebfr(bfr, Bn, i):
    j = int(bfr) % N    #기존 버퍼의 Hash 상태
    HQ_Header[j].remove(bfr)    #기존 버퍼 삭제
    FreeList.pop(0)     #자유 리스트에서 제거
    print("- buffer('%s') removed for new block" % bfr)

    HQ_Header[i].append(Bn)     #새 버퍼 추가
    FreeList.append(Bn) #자유 리스트에서 새 버퍼 추가
    print("- buffer('%s') added" % Bn)

#버퍼 할당 알고리즘
def getblk(Bn, N):
    i = int(Bn) % N #Hash 함수
    lock = False    #버퍼를 찾지 못한 상태

    print('-'*50)
    while not lock: #적합한 버퍼를 찾지 못함
        if exist(Bn, i):    #블록이 해쉬대기열에 있다
            #버퍼가 사용중 이라면
            if not_free(Bn):
                sleep(Bn)   #프로세스 휴면 상태로 전환(반환까지 대기)
                continue    #while loop 복귀
            
            FreeList.remove(Bn) #자유 리스트에서 버퍼 제거
            print("- buffer('%s') allocated" % Bn)    #버퍼가 사용중 임을 표시
            return
        
        else:               #블록이 해쉬대기열에 없다
            #자유 리스트에 버퍼가 없다면(size: 0)
            if not FreeList:
                if slp_iter == 0: bfr = randombfr(N)
                sleep(bfr)   #프로세스 휴면 상태로 전환(버퍼 전환 대기)
                continue    #while loop 복귀
            
            #자유 리스트의 버퍼가 delayed write 상태라면
            if delayed():
                continue    #while loop 복귀, 자유리스트에서 버퍼 삭제, 메모리 출력

            replacebfr(FreeList[0], Bn, i)  #자유 리스트의 선두 버퍼를 삭제하고 새 버퍼를 추가한다
            FreeList.remove(Bn) #자유 리스트에서 새 버퍼 제거
            print("- buffer('%s') allocated" % Bn)    #버퍼가 사용중 임을 표시
            return

#메인 프로그램
slp_iter = 0    #sleep 시뮬레이션을 위한 sleep 카운터
HQ_Header, FreeList, Delayed = [], [], []   #해쉬행렬 공간, 자유 리스트, 지연출력 리스트

f = open('cache.txt', mode='r', encoding='utf-8')   #파일 정보 입력

N = int(f.readline())   #Hash Queue Header 크기
for line in range(N):
    n = int(f.readline())   #Queue별 블록 수
    queue = list(f.readline().split())  #Queue의 블록 번호
    HQ_Header.append(queue) #Queue를 Hash Queue에 추가
m = int(f.readline())   #자유 리스트의 블록 수
FreeList = list(f.readline().split())   #자유 리스트의 블록 번호

while 1:
    #인터페이스 출력
    print('-'*50)
    for i in range(N):  #현재 상태 출력
        print("blk no", i, "mod", N, HQ_Header[i])
    print("free list", FreeList)
    if Delayed: print("delayed write", Delayed)
    print('-'*50)
    index = int(input("1. change block status to delayed write \n2. getblk \n3. exit \ninput: "))
    
    #블록 상태를 delayed write로 전환
    if index == 1:
        Bn = input("block: ")   #전환할 블록 입력
        i = int(Bn) % N         #Hash 함수
        if Bn in HQ_Header[i]: Delayed.append(Bn)
    #블록을 버퍼에 할당
    elif index == 2:
        Bn = input("getblk: ")  #할당할 블록 입력
        getblk(Bn, N)
    #프로그램 종료
    else:
        break

input() #프로그램 종료 대기