# SLM_UI_Streamlit

간단 소개
- Streamlit 기반의 간단한 채팅형 UI 프로젝트입니다.
- `main.py`에서 메시지 입력/전송, 응답 수신 및 화면 렌더링을 처리합니다.
- `upload.py`는 파일 업로드 관련 유틸/엔드포인트 처리를 담당합니다.

필수 사항
- macOS 환경에서 개발/실행을 가정합니다.
- Python 3.9+ 권장
- 필요한 패키지: `streamlit`, `requests`

빠른 시작
1. 가상환경 생성 및 활성화
   - python3 -m venv .venv
   - source .venv/bin/activate
2. 의존성 설치
   - pip install streamlit requests
   (프로젝트에 `requirements.txt`가 있다면 `pip install -r requirements.txt`를 사용)
3. 앱 실행
   - streamlit run main.py

구성 파일
- `main.py`
  - Streamlit 앱 진입점
  - 메시지 상태는 `st.session_state`에 저장 (`messages`, `input_text`, `auto_send` 등)
  - 사용자 입력 폼은 하나의 `st.form`을 사용하도록 구성 (중복된 `st.form` key 오류 주의)
  - `submit_question()` 함수에서 외부 API 호출(`requests.post`)로 답변을 받아 `messages`에 추가
  - HTML 렌더링 시 `html.escape()` 기반의 `safe_html()`을 사용하여 XSS/렌더링 문제 방지
- `upload.py`
  - 파일 업로드 관련 헬퍼 또는 엔드포인트 처리용 스크립트 (프로젝트에 따라 내용 상이)

주요 구현/주의사항
- 중복 폼 오류: `StreamlitAPIException: There are multiple identical forms with key='...'` 발생 시 동일한 `st.form` key를 가진 블록이 여러 개 있는지 확인하고 하나로 통합하세요.
- `st.experimental_rerun` 사용 중단: 최신 Streamlit에서는 해당 속성이 없을 수 있으므로 호출을 제거하고 `st.session_state` 변경과 `st.stop()` 등으로 흐름을 조절하세요.
- `st.utils` 참조 에러: `module 'streamlit' has no attribute 'utils'`가 발생하면 해당 참조를 제거하고 `html.escape()`로 안전하게 텍스트를 처리하세요.
- 자동 전송 처리: `auto_send` 플래그는 `st.session_state.pop("auto_send", False)`로 한 번만 소비하도록 처리하면 중복 호출을 방지할 수 있습니다.
- 입력 초기화: `st.form(..., clear_on_submit=True)`를 사용하면 제출 후 입력 필드를 자동으로 비웁니다.

예시 코드 스니펫 (주요 요지)
- 안전한 HTML 변환:
```python
import html

def safe_html(text: str) -> str:
    return html.escape(text).replace("\n", "<br/>")# SLM_UI_Streamlit
