import matplotlib.pylab as plt

#Best Fit Case로 메모리 관리
def Best_Fit(r_id, size):
    #다른 Request가 없는 경우
    if len(Requests) == 0:  
        for i in range(size):
            Memory[i] = r_id    #메모리를 Request에게 0K에 할당
        
        print_Alloc(r_id, 0, size)  #메모리 할당 결과 출력

        Locations.append(0) #Request 주소 저장
        Sizes.append(size)  #Request 크기 저장

    #다른 Request가 이미 있는 경우
    else: 
        #메모리를 Best Fit Case에 따라 할당
        if not Allocate(r_id, size):  return    #메모리가 할당 되지 않음

    Requests.append(R_id)   #Request 저장

#메모리를 Best Fit Case에 따라 할당하는 알고리즘
def Allocate(r_id, size):
    start, holes = Check_Hole() #메모리의 Hole 확인
    M_hole, loc, free = M_size, -1, 0   #최소 Hole 크기, Request 주소, 빈 메모리 크기 초기화
    
    #Request가 요구하는 메모리 보다 크고, 그 중 제일 작은 Hole 탐색
    for i in range(len(holes)):
        if holes[i] >= size and holes[i] < M_hole: 
            M_hole, loc = holes[i], start[i]    #최소 Hole 크기, Request 주소 설정

        free += holes[i]    #빈 메모리 크기 계산

    #조건에 맞는 Hole이 없는 경우
    if loc == -1:
        #빈 메모리가 부족한 경우
        if free < size:
            print("\nUnable to allocate due to lack of Memory\n")
            return False #메모리 할당 실패

        #Compaction으로 적합한 Hole 확보
        else:           
            Compaction(free)
            loc = M_size-free
            

    for i in range(size): Memory[loc+i] = r_id  #메모리를 Request에게 할당

    print_Alloc(r_id, loc, size)    #메모리 할당 결과 출력
    
    Locations.append(loc)   #Request 주소 저장
    Sizes.append(size)      #Request 크기 저장

    return True #메모리 할당 성공

#메모리의 Hole 확인, Hole의 시작점, 크기 반환
def Check_Hole():
    count, P_id= 0, -1      #홀의 크기, 이전 메모리 할당 값 초기화 
    start, holes = [], []   #Hole의 시작점, 크기 리스트 초기화
    #Hole 탐색
    for i in range(M_size):
        #메모리가 할당 되어있지 않은 경우
        if Memory[i] == 0:
            count += 1  #메모리 크기 1 증가

            #이전 메모리 할당 값이 0이 아니면
            if P_id != 0: start.append(i)   #새로운 Hole 발견

        #Memory가 할당 되어있는 경우    
        else:               
            #이전 메모리 할당 값이 0이면
            if P_id == 0: 
                holes.append(count) #Hole의 크기 저장
                count = 0   #Hole의 크기 초기화

        P_id = Memory[i]    #이전(현재) 메모리 할당 값 저장

        #마지막 Hole의 크기 저장
        if count != 0 and i == M_size-1: holes.append(count)

    return start, holes #Hole의 시작점, 크기 반환

#메모리를 압축하여 빈 메모리를 Block(Hole)으로 변환
def Compaction(free):
    for _ in range(free):   #빈 메모리를 뒤로 이동
        Memory.remove(0)
        Memory.append(0)
    print("\n-Compaction complete, memory relocated")   #압축 완료

    move = 0    #이동 변수
    for i in range(len(Locations)): #압축 결과에 따라 메모리 위치 정보 수정
        Locations[i] = move #위치 정보 수정
        move += Sizes[i]

#메모리 할당 위치, 잔여 메모리, Block(Hole) 정보 출력 
def print_Alloc(r_id, loc, size):
    _, holes = Check_Hole() #빈 메모리 크기 확인
    free = 0    #빈 메모리 크기 초기화

    for i in range(len(holes)): free += holes[i]    #전체 빈 메모리 크기 계산

    print("\nREQUEST %d: %dK" % (r_id, size))
    print("-Request %d allocated at address %dK" % (r_id, loc))
    print("-%dK free, %d block(s), average size = %fK\n" % (free, len(holes), free/ len(holes)))

#할당 중인 메모리를 초기화
def Free(r_id):
    #종료 시킬 Request 내용 검색, 삭제
    for i in range(len(Requests)):
        if Requests[i] == r_id:
            loc = Locations.pop(i)
            size = Sizes.pop(i)

    Requests.remove(r_id)   #Request 삭제
    start, sizes = Check_Hole() #빈 메모리 정보 확인
    s_coal = -1 #할당 되었던 메모리 앞 Hole의 시작 주소 초기화

    #바로 앞 Hole의 시작 주소 탐색
    for i in range(len(start)):
        if start[i]+sizes[i] == loc:
            s_coal = start[i]   #앞 Hole의 시작 주소 설정

    #Request에 할당 된 메모리 검색
    for i in range(M_size):
        if Memory[i] == r_id: Memory[i] = 0 #Request에 할당 된 메모리 초기화

    _, holes = Check_Hole() #변경된 빈 메모리 정보 확인
    free = 0    #빈 메모리 크기 초기화
    for i in range(len(holes)): free += holes[i]    #전체 빈 메모리 크기 계산

    print("\nFREE REQUEST", r_id, "(%dK)" % size)
    print("-Request %d freed at address %dK" % (r_id, loc))

    #할당 되었던 메모리 바로 뒤의 Hole과 병합
    if loc+size != len(Memory)-1 and Memory[loc+size] == 0:
        print("-Coalescing blocks at addresses %dK and %dK" % (loc, loc+size))

    #할당 되었던 메모리 바로 앞의 Hole과 병합
    if s_coal != -1:
        print("-Coalescing blocks at addresses %dK and %dK" % (s_coal, loc))

    print("-%dK free, %d block(s), average size = %fK\n" % (free, len(holes), free/len(holes)))

#메인 프로그램
M_size = int(input("Memory Size(K): ")) #메모리의 크기 입력
Memory = [0]*M_size #메모리를 리스트로 구현
Requests, Locations, Sizes = [], [], [] #Request의 id, 메모리 위치, 크기 저장 리스트

while 1:
    R_id = int(input("Request ID(0 to exit): "))    #조작할 Request의 ID 입력
    if R_id == 0: break                             #프로그램 종료
    R_size = int(input("Request Memory Size(K): ")) #Request가 요청할 메모리 크기 입력
    #새로운 Request 발생 시
    if R_id not in Requests: 
        Best_Fit(R_id, R_size)  #Best Fit Case로 메모리 할당
    else:
        #Request가 가진 메모리 초기화
        if R_size == 0: Free(R_id)
        #중복된 Request 요청 발생 시
        else: 
            print("\nThere is already a Request allocated with the same id\n")

#(BONUS)최종 메모리 할당 결과를 이미지로 출력
barh = []   #할당 된 메모리 정보 리스트
for i in range(len(Requests)):
    barh.append((Locations[i], Sizes[i]))   #할당 된 메모리 정보 입력

fig, ax = plt.subplots()
ax.broken_barh(barh, (5, 9), facecolors=('red', 'yellow', 'green', 'blue', 'purple', 'white'), hatch='//')
ax.set_ylim(0, 20)
ax.set_xlim(0, M_size)
ax.set_xlabel('address')
ax.set_yticks([10])
ax.set_yticklabels(['Memory'])

plt.show()  #이미지 출력