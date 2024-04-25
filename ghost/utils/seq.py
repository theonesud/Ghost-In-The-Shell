import streamlit as st


def execute_tasks(funcs_with_args):
    # Check the current task index and retrieve the function and its arguments
    current_task, args = funcs_with_args[st.session_state.conv_index]

    # Call the function with its respective arguments
    result = current_task(**args) if callable(current_task) else current_task

    # Increment the task index
    st.session_state.conv_index += 1

    # If we've reached the end of the list, stop incrementing
    if st.session_state.conv_index >= len(funcs_with_args):
        st.session_state.conv_index = len(funcs_with_args)

    return result
