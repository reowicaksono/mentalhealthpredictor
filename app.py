import streamlit as st
import numpy as np
import pickle
import matplotlib.pyplot as plt
from skfuzzy import control as ctrl

def load_fuzzy_model():
    with open('fuzzy_model.pkl', 'rb') as f:
        return pickle.load(f)
def plot_fuzzy_output(risk_level):
    fig, ax = plt.subplots()
    ax.plot([0, 3, 5, 8, 10], [0, 0.33, 0.5, 0.67, 1], label="Low Risk")
    ax.plot([3, 5, 7, 9, 10], [0, 0.5, 0.75, 0.9, 1], label="Medium Risk")
    ax.plot([6, 7, 8, 9, 10], [0, 0.67, 0.8, 1, 1], label="High Risk")
    ax.axvline(risk_level, color='red', linestyle='--', label=f"Prediksi Risiko: {risk_level:.2f}")
    ax.set_title("Visualisasi Risiko Kesehatan Mental")
    ax.set_xlabel("Tingkat Risiko")
    ax.set_ylabel("Derajat Keanggotaan")
    ax.legend()
    st.pyplot(fig)

mental_health_ctrl_comprehensive = load_fuzzy_model()
mental_health_simulation_comprehensive = ctrl.ControlSystemSimulation(mental_health_ctrl_comprehensive)

def reset_state():
    st.session_state.page = 0
    st.session_state.answers = {
        "depression": [],
        "schizophrenia": [],
        "anxiety": [],
        "bipolar": [],
        "eating_disorder": []
    }
    st.session_state.temp_answers = []


st.title("Prediksi Risiko Kesehatan Mental Berbasis Logika Fuzzy")
st.write("Aplikasi ini menggunakan logika fuzzy untuk memprediksi risiko kesehatan mental berdasarkan beberapa variabel.")
st.write("Catatan :")
st.write("Low : 0 - 0.33")
st.write("Medium : 0.33 - 0.65")
st.write("High : 0.66 - 1")

if "page" not in st.session_state:
    st.session_state.page = 0

if "answers" not in st.session_state:
    st.session_state.answers = {
        "depression": [],
        "schizophrenia": [],
        "anxiety": [],
        "bipolar": [],
        "eating_disorder": []
    }

if "temp_answers" not in st.session_state:
    st.session_state.temp_answers = [] 


questions = {
    "depression": ["Apakah Anda merasa sedih secara terus-menerus?", 
                   "Apakah Anda kehilangan minat pada aktivitas sehari-hari?", 
                   "Apakah Anda merasa lelah hampir setiap hari?"],
    "schizophrenia": ["Apakah Anda merasa halusinasi atau mendengar suara yang tidak nyata?", 
                      "Apakah Anda merasa sulit membedakan antara kenyataan dan ilusi?", 
                      "Apakah Anda merasa memiliki pikiran aneh atau tidak masuk akal?"],
    "anxiety": ["Apakah Anda sering merasa cemas atau gelisah?", 
                "Apakah Anda kesulitan mengendalikan rasa khawatir?", 
                "Apakah Anda sering merasa takut akan situasi tertentu?"],
    "bipolar": ["Apakah Anda pernah merasa sangat bahagia atau sangat sedih tanpa alasan jelas?", 
                "Apakah suasana hati Anda sering berubah-ubah secara drastis?", 
                "Apakah Anda pernah merasa memiliki energi berlebihan kemudian tiba-tiba merasa sangat lelah?"],
    "eating_disorder": ["Apakah Anda khawatir secara berlebihan tentang berat badan atau bentuk tubuh?", 
                        "Apakah Anda sering makan dalam jumlah banyak secara tiba-tiba?", 
                        "Apakah Anda sering merasa bersalah setelah makan?"]
}

variables = list(questions.keys())

def validate_input(input_value):
    try:
        value = float(input_value)
        if 0.0 <= value <= 1.0:
            return value
        else:
            st.warning("Masukkan nilai antara 0 dan 1.")
            return None
    except ValueError:
        st.warning("Masukkan angka yang valid.")
        return None


if st.session_state.page == 0:
    if st.button("Mulai"):
        st.session_state.page = 1

if st.session_state.page > 0 and st.session_state.page <= len(variables):
    variable = variables[st.session_state.page - 1]
    st.header(f"Pertanyaan untuk {variable.capitalize()}")
    
    st.session_state.temp_answers = []  
    all_valid = True  
    
    for i, question in enumerate(questions[variable]):
        user_input = st.text_input(f"{question} (Masukkan nilai antara 0 - 1)", key=f"{variable}_{i}")
        validated_value = validate_input(user_input)
        
        if validated_value is not None:
            st.session_state.temp_answers.append(validated_value)
        else:
            all_valid = False
    
 
    if all_valid and len(st.session_state.temp_answers) == len(questions[variable]) and st.button("Lanjut"):
        st.session_state.answers[variable] = st.session_state.temp_answers 
        st.session_state.page += 1

if st.session_state.page == len(variables) + 1:

    depression = np.mean(st.session_state.answers["depression"])
    schizophrenia = np.mean(st.session_state.answers["schizophrenia"])
    anxiety = np.mean(st.session_state.answers["anxiety"])
    bipolar = np.mean(st.session_state.answers["bipolar"])
    eating_disorder = np.mean(st.session_state.answers["eating_disorder"])


    mental_health_simulation_comprehensive.input['schizophrenia'] = schizophrenia
    mental_health_simulation_comprehensive.input['depression'] = depression
    mental_health_simulation_comprehensive.input['anxiety'] = anxiety
    mental_health_simulation_comprehensive.input['bipolar'] = bipolar
    mental_health_simulation_comprehensive.input['eating_disorder'] = eating_disorder

    mental_health_simulation_comprehensive.compute()


    risk_level = mental_health_simulation_comprehensive.output['mental_health_risk']

    st.success(f"Hasil prediksi risiko kesehatan mental Anda: {risk_level:.2f}")

    plot_fuzzy_output(risk_level)

    if st.button("Mulai Lagi"):
        reset_state()
