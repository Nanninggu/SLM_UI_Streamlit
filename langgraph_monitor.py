import streamlit as st
import requests
import json
import time
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
import threading

# LangGraph API 설정
LANGGRAPH_API_BASE = "http://localhost:8080/api/langgraph"

# 타임아웃 설정 (5분)
TIMEOUT = 300

def check_api_health():
    """API 상태 확인"""
    try:
        response = requests.get(f"{LANGGRAPH_API_BASE}/health", timeout=5)
        return response.status_code == 200, response.json() if response.status_code == 200 else None
    except Exception as e:
        return False, {"error": str(e)}

def get_session_state(session_id):
    """세션 상태 조회"""
    try:
        response = requests.get(f"{LANGGRAPH_API_BASE}/state/{session_id}", timeout=5)
        return response.status_code == 200, response.json() if response.status_code == 200 else None
    except Exception as e:
        return False, {"error": str(e)}

def init_session(session_id, config=None):
    """세션 초기화"""
    try:
        payload = {
            "session_id": session_id,
            "config": config or {"max_messages": 20}
        }
        response = requests.post(f"{LANGGRAPH_API_BASE}/session/init", json=payload, timeout=5)
        return response.status_code == 200, response.json() if response.status_code == 200 else None
    except Exception as e:
        return False, {"error": str(e)}

def delete_session(session_id):
    """세션 삭제"""
    try:
        response = requests.delete(f"{LANGGRAPH_API_BASE}/session/{session_id}", timeout=5)
        return response.status_code == 200, response.json() if response.status_code == 200 else None
    except Exception as e:
        return False, {"error": str(e)}

def get_available_workflows():
    """사용 가능한 워크플로우 목록 조회"""
    try:
        response = requests.get(f"{LANGGRAPH_API_BASE}/workflows", timeout=5)
        return response.status_code == 200, response.json() if response.status_code == 200 else None
    except Exception as e:
        return False, {"error": str(e)}

def chat_with_langgraph(message, session_id="default", model="exaone3.5:2.4b", temperature=0.7):
    """LangGraph 채팅 API 호출"""
    try:
        payload = {
            "message": message,
            "session_id": session_id,
            "model": model,
            "temperature": temperature
        }
        response = requests.post(f"{LANGGRAPH_API_BASE}/chat", json=payload, timeout=TIMEOUT)
        return response.status_code == 200, response.json() if response.status_code == 200 else None
    except Exception as e:
        return False, {"error": str(e)}

def chat_with_langgraph_async(message, session_id="default", model="exaone3.5:2.4b", temperature=0.7):
    """비동기 채팅 API 호출"""
    try:
        url = f"{LANGGRAPH_API_BASE}/chat/async"
        payload = {
            "message": message,
            "session_id": session_id,
            "model": model,
            "temperature": temperature
        }
        
        # 비동기 요청을 위한 스레드 풀 사용
        with ThreadPoolExecutor() as executor:
            future = executor.submit(requests.post, url, json=payload, timeout=TIMEOUT)
            response = future.result(timeout=TIMEOUT)
        
        return response.status_code == 200, response.json() if response.status_code == 200 else None
    except requests.exceptions.Timeout:
        return False, {"error": "요청 시간이 초과되었습니다. 다시 시도해주세요."}
    except Exception as e:
        return False, {"error": f"API 호출 실패: {str(e)}"}

def chat_with_langgraph_stream(message, session_id="default", model="exaone3.5:2.4b", temperature=0.7):
    """스트리밍 채팅 API 호출"""
    try:
        url = f"{LANGGRAPH_API_BASE}/chat/stream"
        payload = {
            "message": message,
            "session_id": session_id,
            "model": model,
            "temperature": temperature
        }
        
        response = requests.post(url, json=payload, stream=True, timeout=TIMEOUT)
        
        if response.status_code == 200:
            for line in response.iter_lines():
                if line:
                    line_str = line.decode('utf-8')
                    if line_str.startswith('data: '):
                        data_str = line_str[6:]  # 'data: ' 제거
                        try:
                            data = json.loads(data_str)
                            yield data
                        except json.JSONDecodeError:
                            continue
        else:
            yield {"success": False, "error": f"HTTP 오류: {response.status_code}"}
            
    except requests.exceptions.Timeout:
        yield {"success": False, "error": "스트리밍 요청 시간이 초과되었습니다."}
    except Exception as e:
        yield {"success": False, "error": f"스트리밍 API 호출 실패: {str(e)}"}

def execute_workflow(workflow_type, parameters, session_id="default"):
    """워크플로우 실행"""
    try:
        payload = {
            "workflow_type": workflow_type,
            "parameters": parameters,
            "session_id": session_id
        }
        response = requests.post(f"{LANGGRAPH_API_BASE}/workflow", json=payload, timeout=TIMEOUT)
        return response.status_code == 200, response.json() if response.status_code == 200 else None
    except Exception as e:
        return False, {"error": str(e)}

def execute_workflow_async(workflow_type, parameters, session_id="default"):
    """비동기 워크플로우 API 호출"""
    try:
        url = f"{LANGGRAPH_API_BASE}/workflow/async"
        payload = {
            "workflow_type": workflow_type,
            "parameters": parameters,
            "session_id": session_id
        }
        
        # 비동기 요청을 위한 스레드 풀 사용
        with ThreadPoolExecutor() as executor:
            future = executor.submit(requests.post, url, json=payload, timeout=TIMEOUT)
            response = future.result(timeout=TIMEOUT)
        
        return response.status_code == 200, response.json() if response.status_code == 200 else None
    except requests.exceptions.Timeout:
        return False, {"error": "워크플로우 실행 시간이 초과되었습니다. 다시 시도해주세요."}
    except Exception as e:
        return False, {"error": f"워크플로우 실행 실패: {str(e)}"}

def show_langgraph_monitor():
    """LangGraph 모니터링 화면 표시"""
    st.markdown("""
    <div class="gemini-card">
        <h3 style="color: #1a73e8; margin-bottom: 1rem; font-weight: 600;">🔗 LangGraph 모니터링</h3>
        <p style="color: #5f6368; margin-bottom: 1.5rem; font-size: 1rem;">LangGraph API 상태 및 세션 관리</p>
    </div>
    """, unsafe_allow_html=True)

    # API 상태 확인 섹션
    st.subheader("📊 API 상태")

    col1, col2, col3 = st.columns([1, 1, 1])

    with col1:
        if st.button("🔄 상태 새로고침", key="refresh_status"):
            st.rerun()

    with col2:
        if st.button("🏥 헬스 체크", key="health_check"):
            is_healthy, health_data = check_api_health()
            if is_healthy:
                st.success("✅ API가 정상 작동 중입니다!")
                st.json(health_data)
            else:
                st.error("❌ API 연결 실패")
                st.json(health_data)

    with col3:
        if st.button("📋 워크플로우 목록", key="workflows_list"):
            success, workflows = get_available_workflows()
            if success:
                st.success("✅ 워크플로우 목록을 가져왔습니다!")
                st.json(workflows)
            else:
                st.error("❌ 워크플로우 목록 조회 실패")
                st.json(workflows)

    # 세션 관리 섹션
    st.subheader("👥 세션 관리")

    # 세션 ID 입력
    session_id = st.text_input("세션 ID", value="streamlit_monitor", key="session_id_input")

    col1, col2, col3 = st.columns([1, 1, 1])

    with col1:
        if st.button("🆕 새 세션 시작", key="init_session"):
            success, result = init_session(session_id)
            if success:
                st.success("✅ 새 세션이 시작되었습니다!")
                st.json(result)
            else:
                st.error("❌ 세션 초기화 실패")
                st.json(result)

    with col2:
        if st.button("📊 세션 상태 조회", key="get_session_state"):
            success, state = get_session_state(session_id)
            if success:
                st.success("✅ 세션 상태를 가져왔습니다!")
                st.json(state)
            else:
                st.error("❌ 세션 상태 조회 실패")
                st.json(state)

    with col3:
        if st.button("🗑️ 세션 삭제", key="delete_session"):
            success, result = delete_session(session_id)
            if success:
                st.success("✅ 세션이 삭제되었습니다!")
                st.json(result)
            else:
                st.error("❌ 세션 삭제 실패")
                st.json(result)

    # 채팅 테스트 섹션
    st.subheader("💬 채팅 테스트")
    
    # 채팅 방식 선택
    chat_mode = st.radio(
        "채팅 방식 선택:",
        ["일반 채팅", "비동기 채팅", "스트리밍 채팅"],
        horizontal=True,
        key="chat_mode_select"
    )
    
    test_message = st.text_area("테스트 메시지", placeholder="LangGraph API를 테스트할 메시지를 입력하세요...", key="test_message")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        model = st.selectbox("모델 선택", ["exaone3.5:2.4b", "gpt-3.5-turbo", "gpt-4"], key="model_select")
    
    with col2:
        temperature = st.slider("Temperature", 0.0, 1.0, 0.7, 0.1, key="temperature_slider")
    
    if st.button("🚀 채팅 테스트 실행", key="chat_test"):
        if test_message.strip():
            if chat_mode == "일반 채팅":
                with st.spinner("LangGraph API 호출 중..."):
                    success, result = chat_with_langgraph(
                        test_message, 
                        session_id, 
                        model, 
                        temperature
                    )
                    
                    if success:
                        st.success("✅ 채팅 테스트 성공!")
                        st.write("**응답:**")
                        st.write(result.get("response", ""))
                        if result.get("context_used"):
                            st.info(f"📚 컨텍스트: {result['context_used']}")
                        st.json(result)
                    else:
                        st.error("❌ 채팅 테스트 실패")
                        st.json(result)
            
            elif chat_mode == "비동기 채팅":
                with st.spinner("LangGraph API 호출 중 (비동기 처리)..."):
                    success, result = chat_with_langgraph_async(
                        test_message, 
                        session_id, 
                        model, 
                        temperature
                    )
                    
                    if success:
                        st.success("✅ 비동기 채팅 테스트 성공!")
                        st.write("**응답:**")
                        st.write(result.get("response", ""))
                        if result.get("context_used"):
                            st.info(f"📚 컨텍스트: {result['context_used']}")
                        st.json(result)
                    else:
                        st.error("❌ 비동기 채팅 테스트 실패")
                        st.json(result)
            
            elif chat_mode == "스트리밍 채팅":
                st.info("스트리밍 채팅을 시작합니다...")
                
                # 스트리밍 응답을 위한 컨테이너
                response_container = st.empty()
                status_container = st.empty()
                
                try:
                    for data in chat_with_langgraph_stream(
                        test_message, 
                        session_id,
                        model,
                        temperature
                    ):
                        if data.get("status") == "processing":
                            status_container.info(f"🔄 {data.get('message', '처리 중...')}")
                        elif data.get("success"):
                            status_container.success("✅ 완료!")
                            response_container.write("**응답:**")
                            response_container.write(data["response"])
                            if data.get("context_used"):
                                st.info(f"📚 컨텍스트: {data['context_used']}")
                        elif data.get("error"):
                            status_container.error("❌ 오류 발생")
                            response_container.error(f"오류: {data['error']}")
                            break
                except Exception as e:
                    st.error(f"스트리밍 처리 중 오류: {str(e)}")
        else:
            st.warning("⚠️ 테스트 메시지를 입력해주세요.")

    # 워크플로우 테스트 섹션
    st.subheader("🔄 워크플로우 테스트")
    
    workflow_type = st.selectbox(
        "워크플로우 유형",
        ["research", "analysis", "summary", "qa"],
        key="workflow_type_select"
    )
    
    # 워크플로우 실행 방식 선택
    workflow_mode = st.radio(
        "실행 방식 선택:",
        ["일반 실행", "비동기 실행"],
        horizontal=True,
        key="workflow_mode_select"
    )

    if workflow_type == "research":
        topic = st.text_input("연구 주제", placeholder="연구할 주제를 입력하세요...", key="research_topic")
        if st.button("🔬 연구 실행", key="research_test"):
            if topic.strip():
                if workflow_mode == "일반 실행":
                    with st.spinner("연구 워크플로우 실행 중..."):
                        success, result = execute_workflow(
                            "research", 
                            {"topic": topic}, 
                            session_id
                        )
                        if success:
                            st.success("✅ 연구 완료!")
                            st.write("**연구 결과:**")
                            st.write(result.get("result", {}).get("research_result", ""))
                            st.json(result)
                        else:
                            st.error("❌ 연구 실행 실패")
                            st.json(result)
                else:  # 비동기 실행
                    with st.spinner("연구 워크플로우 실행 중 (비동기 처리)..."):
                        success, result = execute_workflow_async(
                            "research", 
                            {"topic": topic}, 
                            session_id
                        )
                        if success:
                            st.success("✅ 연구 완료!")
                            st.write("**연구 결과:**")
                            st.write(result.get("result", {}).get("research_result", ""))
                            st.json(result)
                        else:
                            st.error("❌ 연구 실행 실패")
                            st.json(result)
            else:
                st.warning("⚠️ 연구 주제를 입력해주세요.")

    elif workflow_type == "analysis":
        data = st.text_area("분석할 데이터", placeholder="분석할 데이터를 입력하세요...", key="analysis_data")
        analysis_type = st.selectbox("분석 유형", ["trend", "sentiment", "statistical", "general"], key="analysis_type_select")
        if st.button("📈 분석 실행", key="analysis_test"):
            if data.strip():
                if workflow_mode == "일반 실행":
                    with st.spinner("분석 워크플로우 실행 중..."):
                        success, result = execute_workflow(
                            "analysis",
                            {"data": data, "analysis_type": analysis_type},
                            session_id
                        )
                        if success:
                            st.success("✅ 분석 완료!")
                            st.write("**분석 결과:**")
                            st.write(result.get("result", {}).get("analysis_result", ""))
                            st.json(result)
                        else:
                            st.error("❌ 분석 실행 실패")
                            st.json(result)
                else:  # 비동기 실행
                    with st.spinner("분석 워크플로우 실행 중 (비동기 처리)..."):
                        success, result = execute_workflow_async(
                            "analysis",
                            {"data": data, "analysis_type": analysis_type},
                            session_id
                        )
                        if success:
                            st.success("✅ 분석 완료!")
                            st.write("**분석 결과:**")
                            st.write(result.get("result", {}).get("analysis_result", ""))
                            st.json(result)
                        else:
                            st.error("❌ 분석 실행 실패")
                            st.json(result)
            else:
                st.warning("⚠️ 분석할 데이터를 입력해주세요.")

    elif workflow_type == "summary":
        content = st.text_area("요약할 내용", placeholder="요약할 내용을 입력하세요...", key="summary_content")
        summary_type = st.selectbox("요약 유형", ["key_points", "brief", "detailed"], key="summary_type_select")
        if st.button("📝 요약 실행", key="summary_test"):
            if content.strip():
                if workflow_mode == "일반 실행":
                    with st.spinner("요약 워크플로우 실행 중..."):
                        success, result = execute_workflow(
                            "summary",
                            {"content": content, "summary_type": summary_type},
                            session_id
                        )
                        if success:
                            st.success("✅ 요약 완료!")
                            st.write("**요약 결과:**")
                            st.write(result.get("result", {}).get("summary_result", ""))
                            st.json(result)
                        else:
                            st.error("❌ 요약 실행 실패")
                            st.json(result)
                else:  # 비동기 실행
                    with st.spinner("요약 워크플로우 실행 중 (비동기 처리)..."):
                        success, result = execute_workflow_async(
                            "summary",
                            {"content": content, "summary_type": summary_type},
                            session_id
                        )
                        if success:
                            st.success("✅ 요약 완료!")
                            st.write("**요약 결과:**")
                            st.write(result.get("result", {}).get("summary_result", ""))
                            st.json(result)
                        else:
                            st.error("❌ 요약 실행 실패")
                            st.json(result)
            else:
                st.warning("⚠️ 요약할 내용을 입력해주세요.")

    elif workflow_type == "qa":
        question = st.text_input("질문", placeholder="질문을 입력하세요...", key="qa_question")
        if st.button("❓ Q&A 실행", key="qa_test"):
            if question.strip():
                if workflow_mode == "일반 실행":
                    with st.spinner("Q&A 워크플로우 실행 중..."):
                        success, result = execute_workflow(
                            "qa",
                            {"question": question},
                            session_id
                        )
                        if success:
                            st.success("✅ Q&A 완료!")
                            st.write("**답변:**")
                            st.write(result.get("result", {}).get("qa_result", ""))
                            st.json(result)
                        else:
                            st.error("❌ Q&A 실행 실패")
                            st.json(result)
                else:  # 비동기 실행
                    with st.spinner("Q&A 워크플로우 실행 중 (비동기 처리)..."):
                        success, result = execute_workflow_async(
                            "qa",
                            {"question": question},
                            session_id
                        )
                        if success:
                            st.success("✅ Q&A 완료!")
                            st.write("**답변:**")
                            st.write(result.get("result", {}).get("qa_result", ""))
                            st.json(result)
                        else:
                            st.error("❌ Q&A 실행 실패")
                            st.json(result)
            else:
                st.warning("⚠️ 질문을 입력해주세요.")

    # API 정보 섹션
    st.subheader("ℹ️ API 정보")

    st.markdown(f"""
    **API Base URL:** `{LANGGRAPH_API_BASE}`
    
    **사용 가능한 엔드포인트:**
    - `GET /health` - API 상태 확인
    - `GET /workflows` - 워크플로우 목록 조회
    - `POST /chat` - 일반 채팅 API
    - `POST /chat/async` - 비동기 채팅 API
    - `POST /chat/stream` - 스트리밍 채팅 API
    - `POST /workflow` - 일반 워크플로우 실행
    - `POST /workflow/async` - 비동기 워크플로우 실행
    - `POST /session/init` - 세션 초기화
    - `GET /state/{{sessionId}}` - 세션 상태 조회
    - `DELETE /session/{{sessionId}}` - 세션 삭제
    
    **타임아웃 설정:** {TIMEOUT}초 (5분)
    """)

    # 실시간 모니터링 (선택사항)
    st.subheader("📈 실시간 모니터링")

    if st.button("🔄 실시간 상태 업데이트", key="realtime_update"):
        # API 상태 확인
        is_healthy, health_data = check_api_health()

        # 세션 상태 확인
        success, state = get_session_state(session_id)

        # 결과 표시
        col1, col2 = st.columns(2)

        with col1:
            if is_healthy:
                st.success("✅ API 정상")
            else:
                st.error("❌ API 오류")

        with col2:
            if success:
                st.success("✅ 세션 정상")
            else:
                st.warning("⚠️ 세션 없음")

        # 상세 정보
        st.json({
            "api_health": health_data,
            "session_state": state,
            "timestamp": datetime.now().isoformat()
        })

