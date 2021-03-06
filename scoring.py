# (실행할 수 있는 모듈)
# 첫 번째 인수로 지정된 디렉토리의 소스코드를 채점한다.
# ex) python scoring.py something/ <- something 디렉토리의 소스코드를 채점

import os
import sys
import subprocess
import glob
from settings import *

if len(sys.argv) < 2:
    print('채점할 디렉토리를 첫 번째 인수로 지정해주세요.')
    sys.exit()

TARGET_PATH = sys.argv[1]


def wrong_answer(number, msg):
    print('%d번 문제 오답' % number)
    print('이유: ' + msg + '\n\n')


# number번 문제를 채점하고 점수를 반환함.
def check_problem(number):
    print('================================')
    code_path = '%s/%d.c' % (TARGET_PATH, number)

    # 찌꺼기 삭제
    if os.path.exists('a.exe'):
        os.remove('a.exe')

    # i번째 소스코드가 있나 확인
    if not os.path.exists(code_path):
        raise Exception('%d.c 소스코드가 없습니다.' % number)

    # i번째 소스코드 컴파일
    subprocess.run('gcc -std=%s %s' % (COMPILER, code_path))

    # 컴파일 실패했는지 확인
    if not os.path.exists('a.exe'):
        raise Exception('컴파일 실패')

    # 컴파일된 프로그램에 input 넣어보고 정답 output과 대조해보기
    inputs = glob.glob('answer/%d_input*.txt' % number)
    outputs = glob.glob('answer/%d_output*.txt' % number)

    score = 0.0
    test_count = len(inputs)

    for i in range(test_count):
        prob_input = open(inputs[i], 'r')
        prob_output = open(outputs[i], 'r')

        output, err = subprocess.Popen('a.exe', stdin=prob_input, stdout=subprocess.PIPE).communicate()
        program_output = output.decode().replace('\r\n', '\n').strip()
        prob_input.seek(0)
        input_str = prob_input.read()
        answer_str = prob_output.read()

        prob_input.close()
        prob_output.close()

        if program_output == answer_str:
            print('테스트 케이스 %d 통과' % (i + 1))
            score += PROBLEM_SCORE[number] * 1.0 / test_count
        else:
            print('테스트 케이스 %d 오답\n' % (i + 1) +
                  '[입력]\n%s\n\n[정답]\n%s\n\n[프로그램의 출력값]\n%s\n\n' % (input_str, answer_str, program_output))

    if score == 0:
        raise Exception('테스트 케이스 모두 틀림')

    return score


check_result = [None] * (PROBLEM_COUNT + 1)
total_score = 0.0

# 채점 시작
for i in range(1, PROBLEM_COUNT + 1):
    # i번째 문제 채점
    try:
        score = check_problem(i)
        if score == PROBLEM_SCORE[i]:  # 모든 테스트 케이스를 통과했으면
            print('%d번 문제 정답\n\n' % i)
            check_result[i] = 'O'
        else:  # 테스트 케이스를 하나라도 통과하지 못했으면
            print('%d번 문제 일부 오답\n\n' % i)
            check_result[i] = '?'
        total_score += score
    except Exception as e:
        wrong_answer(i, str(e))
        check_result[i] = 'X'

# 결과를 요약하여 출력
print("========== 요약 ==========")
print("O: 정답, X: 오답, ?: 일부만 정답")
for i in range(1, PROBLEM_COUNT + 1):
    print('%d. [%s]' % (i, check_result[i]), end='  /  ')
print("\n총점: " + str(total_score))
