/**
 * Text-to-Speech Service for Novel Reading
 * Supports Vietnamese voices with speed control, pause/resume
 */

class NovelTextToSpeech {
  constructor() {
    this.synth = window.speechSynthesis;
    this.utterance = null;
    this.isPlaying = false;
    this.isPaused = false;
    this.currentParagraph = 0;
    this.paragraphs = [];
    this.voices = [];
    this.selectedVoice = null;
    this.speed = 1.0;
    this.pitch = 1.0;
    this.volume = 1.0;

    // Auto-scroll settings
    this.autoScroll = true;
    this.scrollOffset = 100;

    this.init();
  }

  init() {
    // Load voices
    this.loadVoices();

    // Voice list changes on some browsers
    if (speechSynthesis.onvoiceschanged !== undefined) {
      speechSynthesis.onvoiceschanged = () => this.loadVoices();
    }

    // Resume settings from localStorage
    this.loadSettings();
  }

  loadVoices() {
    this.voices = this.synth.getVoices();

    // Prefer Vietnamese voices, then prioritize local voices
    const vietnameseVoices = this.voices.filter(
      (voice) =>
        voice.lang.startsWith("vi") ||
        voice.name.toLowerCase().includes("vietnam")
    );

    if (vietnameseVoices.length > 0) {
      // Prefer local Vietnamese voices over online ones
      const localViVoices = vietnameseVoices.filter((v) => v.localService);
      this.selectedVoice =
        localViVoices.length > 0 ? localViVoices[0] : vietnameseVoices[0];
    } else {
      // Fallback to any local voice, then any available voice
      const localVoices = this.voices.filter((v) => v.localService);
      this.selectedVoice =
        localVoices.length > 0 ? localVoices[0] : this.voices[0] || null;
    }

    // Update UI if voice selector exists
    this.updateVoiceSelector();

    console.log(
      `Loaded ${this.voices.length} voices. Selected: ${
        this.selectedVoice?.name || "None"
      }`
    );
  }

  loadSettings() {
    const savedSpeed = localStorage.getItem("tts-speed");
    const savedAutoScroll = localStorage.getItem("tts-autoScroll");
    const savedVoice = localStorage.getItem("tts-voice");

    if (savedSpeed) this.speed = parseFloat(savedSpeed);
    if (savedAutoScroll !== null) this.autoScroll = savedAutoScroll === "true";
    if (savedVoice) {
      const voice = this.voices.find((v) => v.name === savedVoice);
      if (voice) this.selectedVoice = voice;
    }
  }

  saveSettings() {
    localStorage.setItem("tts-speed", this.speed);
    localStorage.setItem("tts-autoScroll", this.autoScroll);
    if (this.selectedVoice) {
      localStorage.setItem("tts-voice", this.selectedVoice.name);
    }
  }

  updateVoiceSelector() {
    const voiceSelect = document.getElementById("tts-voice-select");
    if (!voiceSelect) return;

    // Clear existing options
    voiceSelect.innerHTML = "";

    if (this.voices.length === 0) {
      const option = document.createElement("option");
      option.textContent = "Đang tải giọng đọc...";
      voiceSelect.appendChild(option);
      return;
    }

    // Group voices by language with better categorization
    const groupedVoices = {
      vi: [],
      en: [],
      zh: [],
      ja: [],
      ko: [],
      fr: [],
      de: [],
      es: [],
      other: [],
    };

    this.voices.forEach((voice) => {
      const lang = voice.lang.toLowerCase();
      if (lang.startsWith("vi")) {
        groupedVoices["vi"].push(voice);
      } else if (lang.startsWith("en")) {
        groupedVoices["en"].push(voice);
      } else if (lang.startsWith("zh") || lang.startsWith("cmn")) {
        groupedVoices["zh"].push(voice);
      } else if (lang.startsWith("ja")) {
        groupedVoices["ja"].push(voice);
      } else if (lang.startsWith("ko")) {
        groupedVoices["ko"].push(voice);
      } else if (lang.startsWith("fr")) {
        groupedVoices["fr"].push(voice);
      } else if (lang.startsWith("de")) {
        groupedVoices["de"].push(voice);
      } else if (lang.startsWith("es")) {
        groupedVoices["es"].push(voice);
      } else {
        groupedVoices["other"].push(voice);
      }
    });

    // Helper function to create option with detailed info
    const createVoiceOption = (voice) => {
      const option = document.createElement("option");
      option.value = voice.name;

      // Determine gender from voice name (heuristic)
      let genderIcon = "";
      const nameLower = voice.name.toLowerCase();
      if (
        nameLower.includes("female") ||
        nameLower.includes("woman") ||
        nameLower.includes("girl") ||
        nameLower.includes("zira") ||
        nameLower.includes("huyen") ||
        nameLower.includes("hazel")
      ) {
        genderIcon = "♀️";
      } else if (
        nameLower.includes("male") ||
        nameLower.includes("man") ||
        nameLower.includes("boy") ||
        nameLower.includes("david") ||
        nameLower.includes("minh")
      ) {
        genderIcon = "♂️";
      }

      const serviceType = voice.localService ? "📍 Local" : "☁️ Online";
      option.textContent = `${genderIcon} ${voice.name} (${serviceType})`;

      if (this.selectedVoice && voice.name === this.selectedVoice.name) {
        option.selected = true;
      }

      return option;
    };

    // Add voices by language groups
    const languageGroups = [
      { key: "vi", label: "🇻🇳 Tiếng Việt", voices: groupedVoices.vi },
      { key: "en", label: "🇬🇧 English", voices: groupedVoices.en },
      { key: "zh", label: "🇨🇳 中文 (Chinese)", voices: groupedVoices.zh },
      { key: "ja", label: "🇯🇵 日本語 (Japanese)", voices: groupedVoices.ja },
      { key: "ko", label: "🇰🇷 한국어 (Korean)", voices: groupedVoices.ko },
      { key: "fr", label: "🇫🇷 Français (French)", voices: groupedVoices.fr },
      { key: "de", label: "🇩🇪 Deutsch (German)", voices: groupedVoices.de },
      { key: "es", label: "🇪🇸 Español (Spanish)", voices: groupedVoices.es },
      { key: "other", label: "🌐 Ngôn ngữ khác", voices: groupedVoices.other },
    ];

    languageGroups.forEach(({ label, voices }) => {
      if (voices.length > 0) {
        const group = document.createElement("optgroup");
        group.label = `${label} (${voices.length})`;

        // Sort voices: Local first, then alphabetically
        voices.sort((a, b) => {
          if (a.localService && !b.localService) return -1;
          if (!a.localService && b.localService) return 1;
          return a.name.localeCompare(b.name);
        });

        voices.forEach((voice) => {
          group.appendChild(createVoiceOption(voice));
        });

        voiceSelect.appendChild(group);
      }
    });

    // Add info message if no voices available
    if (this.voices.length === 0) {
      const option = document.createElement("option");
      option.textContent = "⚠️ Không có giọng đọc nào";
      voiceSelect.appendChild(option);
    }
  }

  setVoice(voiceName) {
    const voice = this.voices.find((v) => v.name === voiceName);
    if (voice) {
      this.selectedVoice = voice;
      this.saveSettings();
    }
  }

  setSpeed(speed) {
    this.speed = Math.max(0.5, Math.min(2.0, parseFloat(speed)));
    if (this.utterance) {
      this.utterance.rate = this.speed;
    }
    this.saveSettings();
  }

  setPitch(pitch) {
    this.pitch = Math.max(0.5, Math.min(2.0, parseFloat(pitch)));
    if (this.utterance) {
      this.utterance.pitch = this.pitch;
    }
  }

  setVolume(volume) {
    this.volume = Math.max(0, Math.min(1, parseFloat(volume)));
    if (this.utterance) {
      this.utterance.volume = this.volume;
    }
  }

  setAutoScroll(enabled) {
    this.autoScroll = enabled;
    this.saveSettings();
  }

  extractParagraphs(contentElement) {
    const paragraphElements = contentElement.querySelectorAll("p");
    this.paragraphs = Array.from(paragraphElements)
      .map((p, index) => ({
        element: p,
        text: p.textContent.trim(),
        index: index,
      }))
      .filter((p) => p.text.length > 0);
  }

  scrollToParagraph(index) {
    if (!this.autoScroll || index >= this.paragraphs.length) return;

    const paragraph = this.paragraphs[index];
    if (paragraph && paragraph.element) {
      const elementTop = paragraph.element.offsetTop;
      const offset = this.scrollOffset;

      window.scrollTo({
        top: elementTop - offset,
        behavior: "smooth",
      });

      // Highlight current paragraph
      this.highlightParagraph(index);
    }
  }

  highlightParagraph(index) {
    // Remove previous highlights
    this.paragraphs.forEach((p) => {
      p.element.classList.remove("tts-reading");
    });

    // Add highlight to current
    if (index < this.paragraphs.length) {
      this.paragraphs[index].element.classList.add("tts-reading");
    }
  }

  speak(text, onEnd) {
    return new Promise((resolve, reject) => {
      // Cancel any ongoing speech
      this.synth.cancel();

      this.utterance = new SpeechSynthesisUtterance(text);
      this.utterance.voice = this.selectedVoice;
      this.utterance.rate = this.speed;
      this.utterance.pitch = this.pitch;
      this.utterance.volume = this.volume;
      this.utterance.lang = this.selectedVoice
        ? this.selectedVoice.lang
        : "vi-VN";

      this.utterance.onend = () => {
        if (onEnd) onEnd();
        resolve();
      };

      this.utterance.onerror = (event) => {
        console.error("Speech synthesis error:", event);
        reject(event);
      };

      this.synth.speak(this.utterance);
    });
  }

  async play(contentElement) {
    if (this.isPlaying) {
      return;
    }

    if (this.isPaused) {
      this.resume();
      return;
    }

    // Extract paragraphs if not already done
    if (this.paragraphs.length === 0) {
      this.extractParagraphs(contentElement);
    }

    if (this.paragraphs.length === 0) {
      console.error("No text content found");
      return;
    }

    this.isPlaying = true;
    this.isPaused = false;
    this.updateUI();

    await this.readFromParagraph(this.currentParagraph);
  }

  async readFromParagraph(startIndex) {
    for (let i = startIndex; i < this.paragraphs.length; i++) {
      if (!this.isPlaying) break;

      this.currentParagraph = i;
      this.scrollToParagraph(i);

      try {
        await this.speak(this.paragraphs[i].text);

        // Small pause between paragraphs
        await new Promise((resolve) => setTimeout(resolve, 300));
      } catch (error) {
        console.error("Error reading paragraph:", error);
        break;
      }
    }

    // Finished reading all paragraphs
    this.stop();
  }

  pause() {
    if (this.isPlaying && !this.isPaused) {
      this.synth.pause();
      this.isPaused = true;
      this.isPlaying = false;
      this.updateUI();
    }
  }

  resume() {
    if (this.isPaused) {
      this.synth.resume();
      this.isPaused = false;
      this.isPlaying = true;
      this.updateUI();
    }
  }

  stop() {
    this.synth.cancel();
    this.isPlaying = false;
    this.isPaused = false;
    this.currentParagraph = 0;

    // Remove all highlights
    this.paragraphs.forEach((p) => {
      p.element.classList.remove("tts-reading");
    });

    this.updateUI();
  }

  skipForward() {
    if (this.currentParagraph < this.paragraphs.length - 1) {
      this.synth.cancel();
      this.currentParagraph++;

      if (this.isPlaying) {
        this.readFromParagraph(this.currentParagraph);
      }
    }
  }

  skipBackward() {
    if (this.currentParagraph > 0) {
      this.synth.cancel();
      this.currentParagraph--;

      if (this.isPlaying) {
        this.readFromParagraph(this.currentParagraph);
      }
    }
  }

  updateUI() {
    const playBtn = document.getElementById("tts-play-btn");
    const pauseBtn = document.getElementById("tts-pause-btn");
    const stopBtn = document.getElementById("tts-stop-btn");
    const statusText = document.getElementById("tts-status");

    if (playBtn) {
      playBtn.disabled = this.isPlaying;
      playBtn.innerHTML = this.isPaused
        ? '<i class="fas fa-play"></i> Tiếp tục'
        : '<i class="fas fa-play"></i> Phát';
    }

    if (pauseBtn) {
      pauseBtn.disabled = !this.isPlaying || this.isPaused;
    }

    if (stopBtn) {
      stopBtn.disabled = !this.isPlaying && !this.isPaused;
    }

    if (statusText) {
      if (this.isPlaying) {
        statusText.textContent = `Đang đọc đoạn ${this.currentParagraph + 1}/${
          this.paragraphs.length
        }`;
        statusText.className = "text-success";
      } else if (this.isPaused) {
        statusText.textContent = "Đã tạm dừng";
        statusText.className = "text-warning";
      } else {
        statusText.textContent = "Đã dừng";
        statusText.className = "text-muted";
      }
    }
  }

  getProgress() {
    if (this.paragraphs.length === 0) return 0;
    return Math.round((this.currentParagraph / this.paragraphs.length) * 100);
  }
}

// Export for use in templates
if (typeof module !== "undefined" && module.exports) {
  module.exports = NovelTextToSpeech;
}
