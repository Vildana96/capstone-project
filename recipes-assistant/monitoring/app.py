import streamlit as st
from assistant import create_assistant
from db_save import save_llm_call
from db_feedback import save_feedback
from judge import evaluate_relevance

def relevance_to_score(relevance):
    mapping = {"NON_RELEVANT": -1, 
               "PARTLY_RELEVANT":0, 
               "RELEVANT":1
               }
    return mapping[relevance]

assistant = create_assistant()
print("Assistant created successfully")

st.title("Quick Recipes Assistant")

user_input = st.text_input("Hi, I'm your assistant, how can I help you today?")

if "answer" not in st.session_state:
    st.session_state.answer = None

if "llm_call_id" not in st.session_state:
    st.session_state.llm_call_id = None

if st.button("Ask"):
    st.session_state.feedback_given = False
    with st.spinner("Processing..."):
        answer = assistant.rag(user_input)
        print(f"Answer: {answer}")
        # st.success("Completed!")
        # st.write(answer)
        st.session_state.answer = answer

        
        # st.subheader("Metrics")
        # st.write(f"Response time: {record.response_time:.2f}s")
        # st.write(f"Prompt tokens: {record.prompt_tokens}")
        # st.write(f"Completion tokens: {record.completion_tokens}")
        # st.write(f"Cost: ${record.cost:.4f}")

        record = assistant.last_call
        llm_call_id = save_llm_call(record, user_input)
        st.session_state.llm_call_id = llm_call_id
        # st.write(f"{llm_call_id}th LLM call added")

        relevance, explanation, tokens = evaluate_relevance(user_input, answer)
        save_feedback(llm_call_id, "judge",
                        relevance=relevance, explanation=explanation,
                        score=relevance_to_score(relevance))

if st.session_state.answer:

    st.success("Completed!")

    st.write(st.session_state.answer)

if "feedback_given" not in st.session_state:
    st.session_state.feedback_given = False

if not st.session_state.feedback_given:
    col1, col2 = st.columns(2)

    with col1:
        if st.button("👍 Helpful"):
            save_feedback(
                st.session_state.llm_call_id,
                "user",
                score=1
            )
            st.session_state.feedback_given = True
            st.success("Thanks for your feedback!")

    with col2:
        if st.button("👎 Not Helpful"):
            save_feedback(
                st.session_state.llm_call_id,
                "user",
                score=-1
            )
            st.session_state.feedback_given = True
            st.success("Thanks for your feedback!")