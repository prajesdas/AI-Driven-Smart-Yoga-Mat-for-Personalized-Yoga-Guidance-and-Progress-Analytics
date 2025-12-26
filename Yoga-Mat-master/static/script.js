const aura = document.getElementById("aura")
const statusText = document.getElementById("status")
const socket = io()

let mediaRecorder
let audioStream
let isRecording = false

aura.addEventListener("click", async () => {
  if (!isRecording) await startMic()
})

async function startMic() {
  try {
    audioStream = await navigator.mediaDevices.getUserMedia({ audio:true })
    mediaRecorder = new MediaRecorder(audioStream, { mimeType:"audio/webm" })

    mediaRecorder.ondataavailable = async (event) => {
      if (event.data.size>0) {
        const buffer = await event.data.arrayBuffer()
        socket.emit("audio_chunk", buffer)
      }
    }

    mediaRecorder.start(1000)
    aura.className = "listening"
    statusText.innerText = "Listening..."
    isRecording = true
  } catch(err) {
    statusText.innerText = "Microphone access denied"
    console.error(err)
  }
}

// Receive model output from backend
socket.on("model_output", (data) => {
  aura.className = "speaking"
  statusText.innerText = data.text

  const utter = new SpeechSynthesisUtterance(data.text)
  utter.onend = () => {
    aura.className = "listening"
    statusText.innerText = "Listening..."
  }

  speechSynthesis.speak(utter)
})
