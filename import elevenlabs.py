import elevenlabs

audio - elevenlabs.generate(
    text = "How may I assist you today, sir?",
    voice = "George"
)
elevenlabs.play(audio)