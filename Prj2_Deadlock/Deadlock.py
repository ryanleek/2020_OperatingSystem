#2016104142 이광원 OSHW-2: Deadlock
import copy
#a,b 두 개의 리스트 비교(b가 a보다 같거나 큰지, n = 리소스 수)
def Larger(n, a, b):
    count = 0
    for i in range(n):
        if a[i] <= b[i]: count += 1
    
    if count == n: return True  #모든 원소가 성립하면 참
    else: return False          #하나라도 아니면 거짓

#프로세스가 종료 되었는지 확인(n = 리소스 수)
def Done(n, Need):
    count = 0
    for i in range(n):
        if Need[i] == 0: count += 1

    if count == n: return True  #Need의 모든 원소가 0이면 참
    else: return False          #하나라도 아니면 거짓

#프로세스 실행에 Deadlock이 발생하는지 확인하는 알고리즘(n = 프로세스 수, m = 리소스 수)
def Safety(n, m, Available, Allocation, Need):
    Work = Available[:] #사용 가능한 인스턴스 수 저장
    Finish = [False]*n  #종료한 프로세스 확인

    while 1:
        count, done = 0, True   #조건 확인 변수
        for i in range(n):
            #프로세스가 종료하지 않았고, 잔여 리소스가 필요 인스턴스보다 큰 프로세스가 있다면
            if Finish[i] == False and Larger(m, Need[i], Work):
                for j in range(m):
                    Work[j] += Allocation[i][j] #사용 완료한 인스턴스를 반환
                Finish[i] = True    #프로세스 종료
                break   #다음 시퀀스로 이동
            else: 
                count += 1
                done = done and Finish[i]   #모든 Finish 값이 True면 done이 True

        if count == n:  #조건에 만족하는 프로세스가 없는 경우
            if done: return True    #모든 프로세스가 종료한 상태(Deadlock이 발생하지 않음)
            else: return False      #종료되지 않은 프로세스가 있다(Deadlock 발생)

#프로세스가 리소스에 인스턴스를 요청하는 알고리즘(n = 프로세스 수, m = 인스턴스 수)
def R_Request(n, m, Available, Allocation, Need):
    Request, Quit = [0]*m, [[0]*m]*n    #프로세스가 요청할 인스턴스 내용, 프로그램 종료를 발생시키는 리스트 
    #Safety 알고리즘 테스트용 리스트 deep copy
    Avl = Available[:]
    Alc = copy.deepcopy(Allocation)
    Nd = copy.deepcopy(Need)

    print("-" * 50, "\n잔여 리소스:", Available)    #잔여 리소스 출력
    print("-" * 50)
    index = int(input("리소스를 요청할 프로세스(1 ~ %d, 0 >> 종료): " % n))-1
    if index == -1: return Available, Allocation, Quit  #프로그램 종료 시퀀스

    print("-" * 50, "\n프로세스%d의 필요 리소스:" % (index+1), Need[index]) #필요 리소스 출력
    print("-" * 50)
    for i in range(m): 
        Request[i] = int(input("프로세스%d가 요청할 리소스%d의 인스턴스 수: " % (index+1, i+1)))
        if Request[i] > Need[index][i]: #요청 리소스가 필요 리소스 보다 큰 경우
            print("필요한 인스턴스보다 큰 값을 입력했습니다.")
            return Available, Allocation, Need  #변경되지 않은 리스트 반환
        if Request[i] > Available[i]:   #요청 리소스가 잔여 리소스 보다 큰 경우
            print("인스턴스가 부족합니다.")
            return Available, Allocation, Need  #변경되지 않은 리스트 반환
        #요청 가능한 리소스 값 입력 >> 테스트용 리스트에 요청 값 반영
        Avl[i] -= Request[i]
        Alc[index][i] += Request[i]
        Nd[index][i] -= Request[i]
    
    if Safety(n, m, Avl, Alc, Nd):  #Safety 테스트 실행
        Available, Allocation, Need = Avl, Alc, Nd
        print("리소스가 할당 되었습니다.")  #Deadlock이 발생하지 않으므로 리소스 할당

        if Done(m, Need[index]): #리소스 할당으로 프로세스가 종료 되는지 확인
            for i in range(m):  #프로세스 종료 시퀀스
                Available[i] += Allocation[index][i]    #잔여 리소스 증가
                Allocation[index][i] = 0    #사용 리소스 초기화(0)
            print("프로세스%d 완료" % (index+1))

        return Available, Allocation, Need  #변경된 리스트 반환
    else:   #Deadlock이 발생
        print("요청이 Deadlock을 발생시킵니다.")
        return Available, Allocation, Need  #변경되지 않은 리스트 반환

#메인 프로그램
print("-" * 50)
n = int(input("프로세스의 수: "))   #프로세스의 수 n
m = int(input("리소스의 수: "))     #리소스의 수 m

Available = [0]*m   #리소스의 사용 가능한 인스턴스 수 저장
Instance = [0]*m    #리소스 별 최대 인스턴스 수 저장
Max = [[0 for j in range(m)] for i in range(n)] #프로세스가 사용할 최대 인스턴스 수 저장
Allocation = [[0 for j in range(m)] for i in range(n)]  #프로세스가 사용 중인 인스턴스 수 저장
Need = [[0 for j in range(m)] for i in range(n)]    #프로세스가 현재 필요한 인스턴스 수 저장

#초기 프로세스 및 리소스 설정 시퀀스
for i in range(m):
    print("-" * 50)
    x = int(input("리소스%d의 인스턴스 수: " % (i+1)))
    Instance[i] = x
    Available[i] = Instance[i]  #Available = Instance - Allocation(현재: 0)
    for j in range(n):
        Max[j][i] = int(input("프로세스%d이 요청할 리소스%d의 최대 인스턴스 수: " % (j+1, i+1)))
        Need[j][i] = Max[j][i]  #Need = Max - Allocation(현재: 0)
#모든 프로세스가 끝날 때 까지 인스턴스 요청(사용자가 종료 가능)
while 1:
    sum = 0
    Available, Allocation, Need = R_Request(n, m, Available, Allocation, Need)  #프로세스 요청, 변경사항 반영
    #모든 프로세스가 종료 되었는지 확인
    for i in range(n):
        for j in range (m):
            sum += Need[i][j]
    if sum == 0:    #필요 리소스 = 0 이면 종료
        break

print("-" * 50, "\n프로그램 종료\n", "-" * 50)
input() #프로그램 종료 대기