import streamlit as st
import difflib
import requests
import base64


# Your Hugging Face API key (replace with your actual API key)
API_KEY = "replace with your actual API key"
API_URL = "https://api-inference.huggingface.co/models/google/flan-t5-base"

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

# Prompt Generation Function
def generate_prompt(user_input: str) -> str:
    prompt = f"Generate a video prompt based on this idea: {user_input}"
    data = {
        "inputs": prompt,
        "parameters": {
            "temperature": 0.7,
            "max_new_tokens": 100
        }
    }

    response = requests.post(API_URL, headers=headers, json=data)

    if response.status_code == 200:
        try:
            result = response.json()
            return result[0]['generated_text'].strip()
        except Exception:
            return "Error: Unexpected response format."
    else:
        return f"API Error {response.status_code}: {response.text}"

# Diff Function
def compute_diff_json(before: str, after: str):
    diff_output = []
    s = difflib.SequenceMatcher(None, before.split(), after.split())
    for tag, i1, i2, j1, j2 in s.get_opcodes():
        if tag == 'replace':
            diff_output.append({"op": "replace", "from": " ".join(before.split()[i1:i2]), "to": " ".join(after.split()[j1:j2])})
        elif tag == 'delete':
            diff_output.append({"op": "delete", "text": " ".join(before.split()[i1:i2])})
        elif tag == 'insert':
            diff_output.append({"op": "insert", "text": " ".join(after.split()[j1:j2])})
    return diff_output

# Streamlit App
st.set_page_config(page_title="AI Video Prompt Generator", page_icon="🎥")
st.title("AI Video Prompt Generator")

# Step 1: User Input
st.header("1. Describe Your Video Idea")
user_input = st.text_input("Enter your concept (e.g., 'a bright video of a cute puppy running around')")

if user_input:
    # Step 2: Generate Prompt
    with st.spinner("Generating prompt..."):
        original_prompt = generate_prompt(user_input)

    # Step 3: Let User Edit Prompt
    st.header("2. Edit the AI-Generated Prompt")
    edited_prompt = st.text_area("You can edit the prompt below:", value=original_prompt, height=150)

    # Step 4: Show Differences
    if edited_prompt and edited_prompt != original_prompt:
        st.header("3. See the Differences")
        diff_result = compute_diff_json(original_prompt, edited_prompt)
        for change in diff_result:
            if change["op"] == "replace":
                st.markdown(f"🔁 **Replaced:** `{change['from']}` ➡️ `{change['to']}`")
            elif change["op"] == "delete":
                st.markdown(f"❌ **Deleted:** `{change['text']}`")
            elif change["op"] == "insert":
                st.markdown(f"➕ **Inserted:** `{change['text']}`")
    else:
        st.info("No changes made to the original prompt.")

    # Step 5: Generate Video (Mock)
    st.header("5. Video Generation (Mock)")

    if st.button("Generate Video"):
        st.info("Generating a mock video...")

        # Use a sample video file as a mock response
        video_path = "mock.mp4" 

        with open(video_path, "rb") as video_file:
            video_bytes = video_file.read()
            encoded = base64.b64encode(video_bytes).decode()

        st.video(video_bytes)
        st.success("Mock video generated using your final prompt!")

    # Step 6: Show Final Prompt
    st.header("4. Final Prompt")
    st.text_area("This is your final prompt:", value=edited_prompt, height=150, disabled=True)
