// Configuração da API
// Detecta automaticamente se está usando Docker ou desenvolvimento local
const API_BASE_URL =
  window.location.hostname === "localhost" && window.location.port === "8080"
    ? "/api" // Docker com nginx proxy
    : "http://localhost:5000/api"; // Desenvolvimento local

// Estado da aplicação
let currentVideoData = null;

// Elementos do DOM
const urlInput = document.getElementById("urlInput");
const validateBtn = document.getElementById("validateBtn");
const downloadBtn = document.getElementById("downloadBtn");
const downloadBtnText = document.getElementById("downloadBtnText");
const qualitySelect = document.getElementById("qualitySelect");
const errorMessage = document.getElementById("errorMessage");
const errorText = document.getElementById("errorText");
const loader = document.getElementById("loader");
const videoPreview = document.getElementById("videoPreview");
const downloadStatus = document.getElementById("downloadStatus");
const downloadText = document.getElementById("downloadText");
const successMessage = document.getElementById("successMessage");
const successText = document.getElementById("successText");

// Elementos do preview
const videoThumbnail = document.getElementById("videoThumbnail");
const videoTitle = document.getElementById("videoTitle");
const videoDuration = document.getElementById("videoDuration");
const videoUploader = document.getElementById("videoUploader");

// Event Listeners
document.addEventListener("DOMContentLoaded", () => {
  validateBtn.addEventListener("click", handleValidate);
  downloadBtn.addEventListener("click", handleDownload);

  // Mudar texto do botão quando tipo de download mudar
  const downloadTypeRadios = document.querySelectorAll('input[name="downloadType"]');
  downloadTypeRadios.forEach((radio) => {
    radio.addEventListener("change", (e) => {
      if (e.target.value === "audio") {
        downloadBtnText.textContent = "Baixar Áudio (MP3)";
        // Ocultar seletor de qualidade para áudio
        document.querySelector(".quality-section").style.display = "none";
      } else {
        downloadBtnText.textContent = "Baixar Vídeo";
        document.querySelector(".quality-section").style.display = "block";
      }
    });
  });

  // Permitir validar com Enter
  urlInput.addEventListener("keypress", (e) => {
    if (e.key === "Enter") {
      handleValidate();
    }
  });

  // Limpar mensagens ao digitar
  urlInput.addEventListener("input", () => {
    hideAllMessages();
  });
});

// Função para validar URL
async function handleValidate() {
  const url = urlInput.value.trim();

  if (!url) {
    showError("Por favor, cole uma URL do YouTube");
    return;
  }

  // Validação básica client-side
  if (!isValidYouTubeUrl(url)) {
    showError("URL inválida. Certifique-se de que é um link do YouTube");
    return;
  }

  hideAllMessages();
  showLoader(true);
  disableButtons(true);

  try {
    const response = await fetch(`${API_BASE_URL}/validate`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ url }),
    });

    const data = await response.json();

    if (!response.ok) {
      throw new Error(data.error || "Erro ao validar URL");
    }

    if (data.success) {
      currentVideoData = data.data;
      displayVideoPreview(data.data);
    } else {
      throw new Error(data.error || "Erro desconhecido");
    }
  } catch (error) {
    console.error("Erro na validação:", error);
    showError(error.message || "Erro ao processar o vídeo. Tente novamente.");
  } finally {
    showLoader(false);
    disableButtons(false);
  }
}

// Função para fazer download
async function handleDownload() {
  if (!currentVideoData) {
    showError("Nenhum vídeo selecionado");
    return;
  }

  const quality = qualitySelect.value;
  const url = currentVideoData.url;
  const downloadType = document.querySelector('input[name="downloadType"]:checked').value;

  hideAllMessages();
  showDownloadStatus(true, downloadType === "audio" ? "Baixando áudio..." : "Preparando download...");
  disableButtons(true);

  try {
    const response = await fetch(`${API_BASE_URL}/download`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ url, quality, download_type: downloadType }),
    });

    if (!response.ok) {
      const data = await response.json();
      throw new Error(data.error || "Erro ao fazer download");
    }

    // Obter o blob do vídeo/áudio
    const blob = await response.blob();

    // Criar URL temporária e fazer download
    const downloadUrl = window.URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = downloadUrl;
    const extension = downloadType === "audio" ? ".mp3" : ".mp4";
    a.download = `${sanitizeFilename(currentVideoData.title)}${extension}`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    window.URL.revokeObjectURL(downloadUrl);

    const successMsg =
      downloadType === "audio"
        ? "Áudio baixado com sucesso! Verifique seus downloads."
        : "Download iniciado com sucesso! Verifique seus downloads.";
    showSuccess(successMsg);
  } catch (error) {
    console.error("Erro no download:", error);
    showError(error.message || "Erro ao fazer download. Tente novamente.");
  } finally {
    showDownloadStatus(false);
    disableButtons(false);
  }
}

// Função para exibir preview do vídeo
function displayVideoPreview(data) {
  // Preencher informações
  videoThumbnail.src = data.thumbnail;
  videoThumbnail.alt = data.title;
  videoTitle.textContent = data.title;
  videoDuration.querySelector(".text").textContent = data.duration_string;
  videoUploader.querySelector(".text").textContent = data.uploader;

  // Preencher qualidades
  qualitySelect.innerHTML = "";
  data.qualities.forEach((quality) => {
    const option = document.createElement("option");
    option.value = quality.value;
    option.textContent = `${quality.label} ${quality.note ? "- " + quality.note : ""}`;
    qualitySelect.appendChild(option);
  });

  // Mostrar preview
  videoPreview.style.display = "block";
  videoPreview.scrollIntoView({ behavior: "smooth", block: "nearest" });
}

// Validação de URL do YouTube (client-side)
function isValidYouTubeUrl(url) {
  const patterns = [
    /^(https?:\/\/)?(www\.)?(youtube\.com\/watch\?v=|youtu\.be\/)[a-zA-Z0-9_-]{11}/,
    /^(https?:\/\/)?(www\.)?youtube\.com\/embed\/[a-zA-Z0-9_-]{11}/,
    /^(https?:\/\/)?(www\.)?youtube\.com\/v\/[a-zA-Z0-9_-]{11}/,
  ];

  return patterns.some((pattern) => pattern.test(url));
}

// Sanitizar nome de arquivo
function sanitizeFilename(filename) {
  return filename
    .replace(/[<>:"/\\|?*]/g, "")
    .replace(/\s+/g, "_")
    .substring(0, 200);
}

// Funções de UI
function showError(message) {
  errorText.textContent = message;
  errorMessage.style.display = "flex";
}

function showSuccess(message) {
  successText.textContent = message;
  successMessage.style.display = "flex";

  // Auto-hide após 5 segundos
  setTimeout(() => {
    successMessage.style.display = "none";
  }, 5000);
}

function showLoader(show) {
  loader.style.display = show ? "block" : "none";
}

function showDownloadStatus(show, message = "") {
  if (show) {
    downloadText.textContent = message;
    downloadStatus.style.display = "flex";
  } else {
    downloadStatus.style.display = "none";
  }
}

function hideAllMessages() {
  errorMessage.style.display = "none";
  successMessage.style.display = "none";
  downloadStatus.style.display = "none";
}

function disableButtons(disabled) {
  validateBtn.disabled = disabled;
  downloadBtn.disabled = disabled;
  urlInput.disabled = disabled;
  qualitySelect.disabled = disabled;
}

// Função para resetar a aplicação
function resetApp() {
  urlInput.value = "";
  currentVideoData = null;
  videoPreview.style.display = "none";
  hideAllMessages();
}

// Log de inicialização
console.log("YouTube Downloader inicializado");
console.log("API URL:", API_BASE_URL);
