#2016104142 이광원 운영체제 과제#1

#Background APS 구현(우선도: 주기적 > 비주기적)
def Background_APS(p_tasks, ap_tasks):  #주기적 태스크 리스트, 비주기적 태스크 리스트 입력
    clock, average = 0, 0   #clock: 1초 = 1 progress

    while clock < hPeriod:   #Hyper Period 내의 값 계산
        busy = False    #해당 clock에 compute를 했는지 확인
        
        #주기적 태스크 확인
        for task in p_tasks:
            task.periodic(clock)    #태스크의 주기가 돌아왔는지 확인
            if task.compute(clock, busy): busy = True   #완료된 태스크가 아니라면, 이번 clock에 compute를 하지 않았다면
       
        #비주기적 태스크 확인(우선도가 낮으므로 주기적 태스크 다음으로 확인)
        for task in ap_tasks:
            if task.arrival(clock): #비주기적 태스크의 요청이 왔는지 확인
                if task.compute(clock, busy): busy = True   #완료된 태스크가 아니라면, 이번 clock에 compute를 하지 않았다면, 태스크 수행(busy=>True)
        clock += 1  #clock 이동
    
    #비주기적 Task의 평균 지연 시간 계산
    for task in ap_tasks:
        average += task.calc_delay()    #지연 시간의 합
    print("Background APS의 평균 지연 시간:", average/len(ap_tasks))

#Polling Server APS 구현(우선도: Polling > 주기적)
def Polling_APS(p_tasks, ap_tasks, p_server):  #주기적 태스크 리스트, 비주기적 태스크 리스트, psTask 객체 입력
    clock, average = 0, 0   #clock: 1초 = 1 progress

    while clock < hPeriod:   #Hyper Period 내의 값 계산
        busy = False    #해당 clock에 compute를 했는지 확인

        if p_server.periodic(clock):    #Polling Period 인지 확인
            for _ in range(p_server.capacity):  #psTask는 Capacity 만큼 우선권 가짐
                for task in ap_tasks:
                    if task.arrival(clock): #비주기적 태스크의 요청이 왔는지 확인
                        if task.compute(clock, False): 
                            clock += 1 #완료된 태스크가 아니라면, (우선권 만큼)태스크 수행, clock 이동
                            break 
        
        #주기적 태스크 확인(우선도가 낮으므로 Polling 태스크 다음으로 확인)
        for task in p_tasks:
            task.periodic(clock)    #태스크의 Period가 돌아왔는지 확인
            if task.compute(clock, busy): busy = True   #완료된 태스크가 아니라면, 이번 clock에 compute를 하지 않았다면, 태스크 수행(busy=>True)
        clock += 1  #clock 이동
    
    #비주기적 Task의 평균 지연 시간 계산
    for task in ap_tasks:
        average += task.calc_delay()    #지연 시간의 합
    print("Polling Server APS의 평균 지연 시간:", average/len(ap_tasks))

#태스크의 부모 클래스
class Task:
    #기본 생성자
    def __init__(self, name, c_time):
        self.name = name        #태스크의 이름
        self.cmpt_Time = c_time #태스크의 처리시간
        self.strt_Time = -1     #태스크 시작시간
        self.end_Time = -1      #태스크 종료시간
        self.progress = 0       #태스크 진행도(0~처리시간)
    #완료된 태스크인지 반환
    def check_done(self):
        return self.cmpt_Time == self.progress
    #태스크 1progrss 만큼 수행, 수행 여부 반환
    def compute(self, clock, busy):
        if self.check_done() or busy: return False  #완료된 태스크 거나 다른 태스크 수행중 >> 수행하지 않음

        if self.progress == 0: self.strt_Time = clock   #수행된적 없는 태스크라면 clock 기록(시작시간)
        self.progress += 1  #태스크 수행
        if self.check_done(): self.end_Time = clock + 1 #완료된 태스크라면 clock 기록(종료시간)
        return True #태스크를 수행 했음

#주기적 태스크 클래스, 태스크 상속 받음
class pTask(Task):
    #기본 생성자
    def __init__(self, name, c_time, period):
        super().__init__(name, c_time)  #기본 태스크 field 설정
        self.period = period            #태스크의 주기
    #태스크의 주기를 반복
    def periodic(self, clock):
        if clock % self.period == 0: self.progress = 0 #진행도 초기화

#비주기적 태스크 클래스, 태스크 상속 받음
class apTask(Task):
    #기본 생성자
    def __init__(self, name, c_time, a_time):
        super().__init__(name, c_time)  #기본 태스크 field 설정
        self.arv_Time = a_time          #태스크 요청시간
    #태스크가 요청되었는지 반환
    def arrival(self, clock):
        if self.arv_Time > clock: return False  #요청시간 > clock >> 요청되지 않음
        else: return True                       #태스크가 요청됨
    #태스크의 대기시간 반환
    def calc_delay(self):
        return self.strt_Time - self.arv_Time   #대기시간 = 시작시간 - 요청시간

#Polling 서버 클래스(태스크의 field가 필요하지 않으므로 상속 받지 않음)
class psTask():
    #기본 생성자
    def __init__(self, name, cap, period):
        self.name = name        #Server 이름    
        self.capacity = cap     #Server 용량
        self.period = period    #Polling 주기
    #Polling의 주기를 반복
    def periodic(self, clock):
        if clock % self.period == 0: return True
        else: return False

#메인 프로그램
Periodic, Aperiodic = [], []    #주기적, 비주기적 태스크 리스트 - 순차 검색에 용이(우선도가 높은 태스크 순으로 입력, queue와 달리 get()해도 없어지지 않는다.)
hPeriod = 0                     #Hyper Period 설정

menu = input("[1. Background APS  2. Polling Server APS]:") #사용자가 태스크의 APS 결정 

p_num = int(input("주기적 테스트 개수:"))
for i in range(p_num):
    name, c_time, period = input("[주기적 테스트의 이름/처리시간/주기]:").split()
    Periodic.append(pTask(name, int(c_time), int(period)))      #주기적 태스크 설정

    if int(period) > hPeriod: hPeriod = int(period) #Hyper Period 탐색

a_num = int(input("비주기적 테스트 개수:"))
for i in range(a_num):
    name, c_time, a_time = input("[비주기적 테스트의 이름/처리시간/요청시간]:").split()
    Aperiodic.append(apTask(name, int(c_time), int(a_time)))    #비주기적 태스크 설정

if menu == "1":   #Background_APS의 지연시간 계산
    Background_APS(Periodic, Aperiodic)
else:           #Polling_APS의 지연시간 계산
    name, cap, period = input("[Polling Server의 이름/용량/주기]:").split()
    Polling_Server = psTask(name, int(cap), int(period))    #Polling 서버 설정
    Polling_APS(Periodic, Aperiodic, Polling_Server)