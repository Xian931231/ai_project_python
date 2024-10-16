# newfrom_ai_python

## .env 파일 생성 
위키 참조

## poerty(의존성 관리 패키지) 사용법

- 설치
    - pip install poetry

- 패키지 설치
    - poetry add "패키지 이름"

- 패키지 삭제
    - poetry add "패키지 이름" 

- 프로젝트 의존성 패키지 설치
    - poetry install

- 가상 환경 설정 보기
    - poetry env info

- Poetry 에서는 가상환경을 기본적으로 로컬 캐쉬 경로로 잡기때문에 아래와같이 설정 필요.
    ```shell
    # config 설정 확인 
    poetry config --list
    
    # virtualenvs.in-project 확인 
    virtualenvs.in-project=true 로 변경 
    
    # virtualenvs.path 확인 / 로컬 가상 환경 env 경로로 설정 
    virtualenvs.path = ".venv" 
    
    # poetry shell 실행 후 프로젝트 루트 경로에 virtualenvs.path 에서 설정한 경로가 생성되는지 확인 
    ```

## 프로젝트 실행 

~~poetry run uvicorn main:app --reload~~
python start.py
