# VoiceStudio

Text-to-speech (TTS) generator with a web interface, built on [Gradio](https://www.gradio.app/) and `edge-tts`. It turns any text into MP3 audio, lets you pick the language and voice, and automatically fixes how numbers, money amounts, acronyms and questions are read so they sound natural.

## Features

- **47 voices in 9 languages** (Spanish, English, Italian, Portuguese, French, Russian, German and Dutch).
- **Text normalization** before synthesis:
  - Numbers to words, respecting thousands and decimal separators (`1.250,50` → `mil doscientos cincuenta con cincuenta`).
  - Money amounts with symbols or words (`u$d33.000.000`, `US$ 10.50`, `€ 200`, `20 pesos argentinos`).
  - Initials spelled out (`EE.UU.` → `E E U U`) and capitalized acronyms (`NASA` → `Nasa`).
  - Spanish pronunciation tweaks: `podcast` → `pódcast`, `YouTube` → `Iutub`, `software` → `sófuer`, `Orion` → `Orión`.
- **Rising intonation for questions** with Latin American Spanish voices, using SSML `<prosody>` tags injected after the text is escaped.
- **Automatic fallback**: if the service rejects the intonation, it retries with plain text.
- **Dependency installation at startup**: if `gradio`, `edge_tts` or `num2words` is missing, the script installs it with `pip`.
- Responsive interface with a dark theme and a guided three-step flow.

## Requirements

- Python 3.
- Internet connection: synthesis uses Microsoft's service through `edge-tts`.

## Installation

```bash
git clone https://github.com/migueldiganchi/voice_studio-io.git
cd voice_studio-io
python -m pip install gradio edge-tts num2words
```

> `voice_builder.py` itself installs any missing dependencies the first time it runs, so the `pip` step is optional (but recommended).

## Usage

```bash
python voice_builder.py
```

A browser tab opens automatically. Then:

1. Choose the **language**.
2. Choose the **voice** (the list updates automatically when the language changes).
3. Type or paste the **text**.
4. Press **Generate audio** and listen to the result.

The file is saved as `salida.mp3` in the project directory and overwritten on every generation.

## Languages and voices

| Language | `num2words` code | Voices | Variants |
| --- | --- | ---: | --- |
| Spanish | `es` | 8 | Spain, Mexico, Argentina, Colombia |
| English | `en` | 10 | United States, United Kingdom, Australia, Canada, India |
| Italian | `it` | 4 | Italy |
| Portuguese | `pt` | 4 | Brazil, Portugal |
| French | `fr` | 8 | France, Canada, Belgium, Switzerland |
| Russian | `ru` | 2 | Russia |
| German | `de` | 6 | Germany, Austria, Switzerland |
| Dutch | `nl` | 5 | Netherlands, Belgium |

## How it works

The `generate_audio()` flow is:

1. `correct_text()` applies, in order, the rules for initials, money, numbers, acronyms and Spanish-specific replacements.
2. `mark_questions()` inserts `[[Q]]` markers around the last word of each question.
3. `edge_tts.Communicate` builds the SSML and a patch over `mkssml` turns those markers into `<prosody pitch="+25Hz">`.
4. The MP3 is saved. If `NoAudioReceived` is raised, it retries without the intonation tags.

The pitch rise is applied only to Latin American Spanish voices; the Spain voices (`es-ES-*`) already sound fine without it. The value is adjusted with the `QUESTION_PITCH_RISE` constant.

## Project structure

```
.
├── voice_builder.py   # normalization, synthesis, and Gradio interface logic
├── README.md          # this document
└── .gitignore         # ignores the Python cache and generated audio files
```

## Limitations

- Requires an Internet connection; without it `edge-tts` cannot generate audio.
- `salida.mp3` is overwritten on every generation: copy the file if you want to keep it.
- Voices depend on Microsoft's catalog and may change without notice.
- The SSML patch depends on the internal structure of `edge_tts.communicate`; if a future version changes it, the app still works but without question intonation.

## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss the scope.

## License

No license has been defined for this project yet.
