const isLocalStaticFrontend =
  ["localhost", "127.0.0.1"].includes(window.location.hostname) && window.location.port === "8000";

const API_BASE_URL = isLocalStaticFrontend ? "http://localhost:5000/api" : "/api";

const PROJECT_NAME = "stream2downloader";

let currentVideoData = null;

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

const videoThumbnail = document.getElementById("videoThumbnail");
const videoTitle = document.getElementById("videoTitle");
const videoDuration = document.getElementById("videoDuration");
const videoUploader = document.getElementById("videoUploader");
const qualitySection = document.querySelector(".quality-section");

document.addEventListener("DOMContentLoaded", () => {
  validateBtn.addEventListener("click", handleValidate);
  downloadBtn.addEventListener("click", handleDownload);

  const downloadTypeRadios = document.querySelectorAll('input[name="downloadType"]');
  downloadTypeRadios.forEach((radio) => {
    radio.addEventListener("change", (e) => {
      if (e.target.value === "audio") {
        downloadBtnText.textContent = "Baixar áudio (MP3)";
        qualitySection.style.display = "none";
      } else {
        downloadBtnText.textContent = "Baixar vídeo";
        qualitySection.style.display = "block";
      }
    });
  });

  urlInput.addEventListener("keypress", (e) => {
    if (e.key === "Enter") {
      handleValidate();
    }
  });

  urlInput.addEventListener("input", () => {
    hideAllMessages();
  });
});

async function handleValidate() {
  const url = urlInput.value.trim();

  if (!url) {
    showError("Cole uma URL do YouTube para continuar.");
    return;
  }

  if (!isValidYouTubeUrl(url)) {
    showError("URL inválida. Informe um link válido do YouTube.");
    return;
  }

  hideAllMessages();
  showDownloadStatus(true, "Validando URL e carregando informações...");
  showLoader(true);
  disableButtons(true, "Validando...");

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
      showDownloadStatus(false);
      showSuccess("Vídeo identificado. Revise as opções e inicie o download.");
    } else {
      throw new Error(data.error || "Erro desconhecido");
    }
  } catch (error) {
    console.error("Erro na validação:", error);
    showDownloadStatus(false);
    showError(error.message || "Não foi possível processar o vídeo. Tente novamente.");
  } finally {
    showLoader(false);
    disableButtons(false);
  }
}

async function handleDownload() {
  if (!currentVideoData) {
    showError("Nenhum vídeo disponível para download. Valide uma URL primeiro.");
    return;
  }

  const quality = qualitySelect.value;
  const url = currentVideoData.url;
  const downloadType = document.querySelector('input[name="downloadType"]:checked').value;

  hideAllMessages();
  showDownloadStatus(
    true,
    downloadType === "audio"
      ? "Baixando áudio. Aguarde a geração do arquivo..."
      : "Baixando vídeo. Aguarde a preparação do arquivo...",
  );
  disableButtons(true, "Processando...");

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

    const blob = await response.blob();

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
        ? "Áudio baixado com sucesso. Confira sua pasta de downloads."
        : "Vídeo baixado com sucesso. Confira sua pasta de downloads.";
    showSuccess(successMsg);
  } catch (error) {
    console.error("Erro no download:", error);
    showError(error.message || "Falha ao concluir o download. Tente novamente.");
  } finally {
    showDownloadStatus(false);
    disableButtons(false);
  }
}

function displayVideoPreview(data) {
  videoThumbnail.src = data.thumbnail;
  videoThumbnail.alt = data.title;
  videoTitle.textContent = data.title;
  videoDuration.querySelector(".text").textContent = data.duration_string;
  videoUploader.querySelector(".text").textContent = data.uploader;

  qualitySelect.innerHTML = "";
  data.qualities.forEach((quality) => {
    const option = document.createElement("option");
    option.value = quality.value;
    option.textContent = `${quality.label} ${quality.note ? "- " + quality.note : ""}`;
    qualitySelect.appendChild(option);
  });

  videoPreview.style.display = "block";
  videoPreview.scrollIntoView({ behavior: "smooth", block: "nearest" });
}

function isValidYouTubeUrl(url) {
  const patterns = [
    /^(https?:\/\/)?(www\.)?(youtube\.com\/watch\?v=|youtu\.be\/)[a-zA-Z0-9_-]{11}/,
    /^(https?:\/\/)?(www\.)?youtube\.com\/embed\/[a-zA-Z0-9_-]{11}/,
    /^(https?:\/\/)?(www\.)?youtube\.com\/v\/[a-zA-Z0-9_-]{11}/,
  ];

  return patterns.some((pattern) => pattern.test(url));
}

function sanitizeFilename(filename) {
  return filename
    .replace(/[<>:"/\\|?*]/g, "")
    .replace(/\s+/g, "_")
    .substring(0, 200);
}

function showError(message) {
  errorText.textContent = message;
  errorMessage.style.display = "flex";
}

function showSuccess(message) {
  successText.textContent = message;
  successMessage.style.display = "flex";

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

  validateBtn.querySelector("svg").style.display = disabled ? "none" : "inline";
  validateBtn.lastChild.textContent = disabled ? " Aguarde..." : " Validar e carregar";
}

console.log(`${PROJECT_NAME} inicializado`);
console.log("API URL:", API_BASE_URL);
