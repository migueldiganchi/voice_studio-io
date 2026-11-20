import subprocess, sys, re

# Install required libraries automatically
for pkg in ["gradio", "edge_tts", "num2words"]:
    try:
        __import__(pkg)
    except ImportError:
        subprocess.check_call([sys.executable, "-m", "pip", "install", pkg])

import gradio as gr
import edge_tts
import asyncio
import inspect
from edge_tts.exceptions import NoAudioReceived
from num2words import num2words

# ------------------------------------------------------------------
# Question intonation
# Same pitch rise for ALL questions (Latin American Spanish voices).
# Adjust this value for a stronger or weaker effect (e.g. "+15Hz" or "+35Hz").
# It has to be in Hz; the service does not accept percentages here.
# ------------------------------------------------------------------
QUESTION_PITCH_RISE = "+25Hz"

PATCH_OK = False
try:
    import edge_tts.communicate as _ec
    _MKSSML_ORIGINAL = getattr(_ec, "mkssml", None)
    if _MKSSML_ORIGINAL is not None and "mkssml" in inspect.getsource(_ec.Communicate):
        def _mkssml_with_questions(*args, **kwargs):
            ssml = _MKSSML_ORIGINAL(*args, **kwargs)
            if not isinstance(ssml, str):
                return ssml
            return (ssml.replace("[[Q]]", f'<prosody pitch="{QUESTION_PITCH_RISE}">')
                        .replace("[[/Q]]", "</prosody>"))
        _ec.mkssml = _mkssml_with_questions
        PATCH_OK = True
except Exception:
    PATCH_OK = False

# ------------------------------------------------------------------
# Languages, voices and num2words code for each one
# ------------------------------------------------------------------
LANGUAGES = {
    "Español": {
        "num2words": "es",
        "voices": [
            ("es-ES-AlvaroNeural", "🇪🇸 España - Álvaro (Hombre)"),
            ("es-ES-ElviraNeural", "🇪🇸 España - Elvira (Mujer)"),
            ("es-MX-JorgeNeural", "🇲🇽 México - Jorge (Hombre)"),
            ("es-MX-DaliaNeural", "🇲🇽 México - Dalia (Mujer)"),
            ("es-AR-TomasNeural", "🇦🇷 Argentina - Tomás (Hombre)"),
            ("es-AR-ElenaNeural", "🇦🇷 Argentina - Elena (Mujer)"),
            ("es-CO-GonzaloNeural", "🇨🇴 Colombia - Gonzalo (Hombre)"),
            ("es-CO-SalomeNeural", "🇨🇴 Colombia - Salomé (Mujer)"),
        ],
    },
    "Inglés": {
        "num2words": "en",
        "voices": [
            ("en-US-AriaNeural", "🇺🇸 Estados Unidos - Aria (Mujer)"),
            ("en-US-GuyNeural", "🇺🇸 Estados Unidos - Guy (Hombre)"),
            ("en-GB-SoniaNeural", "🇬🇧 Reino Unido - Sonia (Mujer)"),
            ("en-GB-RyanNeural", "🇬🇧 Reino Unido - Ryan (Hombre)"),
            ("en-AU-NatashaNeural", "🇦🇺 Australia - Natasha (Mujer)"),
            ("en-AU-WilliamNeural", "🇦🇺 Australia - William (Hombre)"),
            ("en-CA-ClaraNeural", "🇨🇦 Canadá - Clara (Mujer)"),
            ("en-CA-LiamNeural", "🇨🇦 Canadá - Liam (Hombre)"),
            ("en-IN-NeerjaNeural", "🇮🇳 India - Neerja (Mujer)"),
            ("en-IN-PrabhatNeural", "🇮🇳 India - Prabhat (Hombre)"),
        ],
    },
    "Italiano": {
        "num2words": "it",
        "voices": [
            ("it-IT-ElsaNeural", "🇮🇹 Italia - Elsa (Mujer)"),
            ("it-IT-IsabellaNeural", "🇮🇹 Italia - Isabella (Mujer)"),
            ("it-IT-DiegoNeural", "🇮🇹 Italia - Diego (Hombre)"),
            ("it-IT-GiuseppeNeural", "🇮🇹 Italia - Giuseppe (Hombre)"),
        ],
    },
    "Portugués": {
        "num2words": "pt",
        "voices": [
            ("pt-BR-FranciscaNeural", "🇧🇷 Brasil - Francisca (Mujer)"),
            ("pt-BR-AntonioNeural", "🇧🇷 Brasil - Antônio (Hombre)"),
            ("pt-PT-RaquelNeural", "🇵🇹 Portugal - Raquel (Mujer)"),
            ("pt-PT-DuarteNeural", "🇵🇹 Portugal - Duarte (Hombre)"),
        ],
    },
    "Francés": {
        "num2words": "fr",
        "voices": [
            ("fr-FR-DeniseNeural", "🇫🇷 Francia - Denise (Mujer)"),
            ("fr-FR-HenriNeural", "🇫🇷 Francia - Henri (Hombre)"),
            ("fr-CA-SylvieNeural", "🇨🇦 Canadá - Sylvie (Mujer)"),
            ("fr-CA-JeanNeural", "🇨🇦 Canadá - Jean (Hombre)"),
            ("fr-BE-CharlineNeural", "🇧🇪 Bélgica - Charline (Mujer)"),
            ("fr-BE-GerardNeural", "🇧🇪 Bélgica - Gérard (Hombre)"),
            ("fr-CH-ArianeNeural", "🇨🇭 Suiza - Ariane (Mujer)"),
            ("fr-CH-FabriceNeural", "🇨🇭 Suiza - Fabrice (Hombre)"),
        ],
    },
    "Ruso": {
        "num2words": "ru",
        "voices": [
            ("ru-RU-SvetlanaNeural", "🇷🇺 Rusia - Svetlana (Mujer)"),
            ("ru-RU-DmitryNeural", "🇷🇺 Rusia - Dmitry (Hombre)"),
        ],
    },
    "Alemán": {
        "num2words": "de",
        "voices": [
            ("de-DE-KatjaNeural", "🇩🇪 Alemania - Katja (Mujer)"),
            ("de-DE-ConradNeural", "🇩🇪 Alemania - Conrad (Hombre)"),
            ("de-AT-IngridNeural", "🇦🇹 Austria - Ingrid (Mujer)"),
            ("de-AT-JonasNeural", "🇦🇹 Austria - Jonas (Hombre)"),
            ("de-CH-LeniNeural", "🇨🇭 Suiza - Leni (Mujer)"),
            ("de-CH-JanNeural", "🇨🇭 Suiza - Jan (Hombre)"),
        ],
    },
    "Neerlandés": {
        "num2words": "nl",
        "voices": [
            ("nl-NL-FennaNeural", "🇳🇱 Países Bajos - Fenna (Mujer)"),
            ("nl-NL-ColetteNeural", "🇳🇱 Países Bajos - Colette (Mujer)"),
            ("nl-NL-MaartenNeural", "🇳🇱 Países Bajos - Maarten (Hombre)"),
            ("nl-BE-DenaNeural", "🇧🇪 Bélgica - Dena (Mujer)"),
            ("nl-BE-ArnaudNeural", "🇧🇪 Bélgica - Arnaud (Hombre)"),
        ],
    },
}

# Terms pronounced differently in Spanish (only applies when the language is Español)
SPANISH_REPLACEMENTS = {
    r'\bpodcast\b': 'pódcast',
    r'\bpodcasts\b': 'pódcasts',
    r'\bYouTube\b': 'Iutub',
    r'\bsoftware\b': 'sófuer',
    r'\bOrion\b': 'Orión',
}

# How each currency is spoken in every language (key = currency code)
CURRENCIES = {
    "USD": {"es": "dólares", "en": "dollars", "it": "dollari", "pt": "dólares",
            "fr": "dollars", "ru": "долларов", "de": "Dollar", "nl": "dollar"},
    "EUR": {"es": "euros", "en": "euros", "it": "euro", "pt": "euros",
            "fr": "euros", "ru": "евро", "de": "Euro", "nl": "euro"},
    "ARS": {"es": "pesos argentinos", "en": "argentine pesos", "it": "pesos argentini",
            "pt": "pesos argentinos", "fr": "pesos argentins", "ru": "аргентинских песо",
            "de": "argentinische Pesos", "nl": "Argentijnse peso"},
}

# Currency marks: symbols/codes (u$d, u$s, US$, USD, AR$, ARS, €, EUR, $)
_LETTERS = r'a-zA-ZáéíóúüñÁÉÍÓÚÜÑ'
_SYMBOLS = r'u\$s|u\$d|us\$|usd|ar\$|ars|eur|€|\$'
# Also currencies written as words (dólares, euros, pesos argentinos, etc.)
_WORD_USD = r'dólar(?:es)?|dolar(?:es)?|dollars?|dollari|dollaro|долларов?'
_WORD_EUR = r'euros?|евро'
_WORD_ARS = r'pesos?\s+argentinos?|pesos?'
_WORDS = r'(?:' + _WORD_USD + r'|' + _WORD_EUR + r'|' + _WORD_ARS + r')'

# A mark before the number accepts symbols or words, with or without spaces in between
_MARK_BEFORE = r'(?:' + _SYMBOLS + r'|' + _WORDS + r')'
# The same after the number, except a lone "$" (to avoid false matches)
_MARK_AFTER = r'(?:' + _SYMBOLS.replace(r'|\$', '') + r'|' + _WORDS + r')'
money_pattern = re.compile(
    r'(?<![' + _LETTERS + r'])'
    r'(?:(?P<prefix>' + _MARK_BEFORE + r')\s*)?'
    r'(?P<number>\d+(?:[.,]\d+)*)\b'
    r'(?:\s*(?P<suffix>' + _MARK_AFTER + r')(?![' + _LETTERS + r']))?',
    re.IGNORECASE,
)
number_pattern = re.compile(r'\b\d+(?:[.,]\d+)*\b')

# Last word of each question (the one that gets the pitch rise)
question_end_pattern = re.compile(r'([^\s¿?¡!]+)(\?+)')
marker_pattern = re.compile(r'\[\[/?Q\]\]')

_UPPERCASE = r'A-ZÁÉÍÓÚÜÑ'
initials_pattern = re.compile(
    r'\b(?:[' + _LETTERS + r']\.){1,}[' + _LETTERS + r']\b\.?(?!\.?[' + _LETTERS + r'])'
)
uppercase_pattern = re.compile(r'[' + _UPPERCASE + r']{2,}')


def _currency_code(mark):
    mark = mark.lower()
    if "peso" in mark or mark in ("ar$", "ars"):
        return "ARS"
    if "euro" in mark or "евро" in mark or mark == "€":
        return "EUR"
    return "USD"


def _split_integer_decimal(token):
    """Split the integer part from the decimals by guessing the number format:
    33.000.000 (thousands) / 33.000.000,50 (European) / 33,000,000.50 (US)."""
    has_dot = "." in token
    has_comma = "," in token
    if has_dot and has_comma:
        decimal_sep = "." if token.rfind(".") > token.rfind(",") else ","
        thousands_sep = "," if decimal_sep == "." else "."
        integer, _, decimal = token.rpartition(decimal_sep)
        return integer.replace(thousands_sep, ""), decimal
    if has_dot or has_comma:
        sep = "." if has_dot else ","
        parts = token.split(sep)
        if len(parts) > 2:
            return "".join(parts), None
        integer, decimal = parts
        # One separator with 3 trailing digits and up to 3 leading digits: thousands
        if len(decimal) == 3 and 0 < len(integer) <= 3:
            return integer + decimal, None
        return integer, decimal
    return token, None


def _number_to_words(token, lang_code):
    """Convert a number to text, respecting thousands and decimal separators."""
    integer_str, decimal_str = _split_integer_decimal(token)
    try:
        text = num2words(int(integer_str), lang=lang_code)
    except (ValueError, NotImplementedError):
        return None
    if decimal_str:
        try:
            decimal_txt = num2words(int(decimal_str), lang=lang_code)
        except (ValueError, NotImplementedError):
            return None
        connector = "point" if lang_code == "en" else "con"
        text = f"{text} {connector} {decimal_txt}"
    return text


def number_to_words(match, lang_code):
    text = _number_to_words(match.group(0), lang_code)
    return text if text is not None else match.group(0)


def _money_to_words(match, lang_code):
    """Read monetary amounts: detect the currency, build the number and append its name."""
    prefix, suffix = match.group("prefix"), match.group("suffix")
    if not prefix and not suffix:
        return match.group(0)  # not money: handled by the number pass
    integer_str, decimal_str = _split_integer_decimal(match.group("number"))
    try:
        integer_num = int(integer_str)
        integer_txt = num2words(integer_num, lang=lang_code)
    except (ValueError, NotImplementedError):
        return match.group(0)

    currency = CURRENCIES[_currency_code(prefix or suffix)].get(lang_code) or CURRENCIES[_currency_code(prefix or suffix)]["es"]
    if integer_num == 0 and decimal_str:
        result = ""
    else:
        # In Spanish use "de" when the figure ends in millón / millones
        link_word = " de " if (lang_code == "es" and (integer_txt.endswith("millón") or integer_txt.endswith("millones"))) else " "
        result = f"{integer_txt}{link_word}{currency}"

    if decimal_str:
        try:
            decimal_txt = num2words(int(decimal_str), lang=lang_code)
        except (ValueError, NotImplementedError):
            return result or match.group(0)
        if lang_code == "en":
            result = (result + f" and {decimal_txt} cents").strip()
        else:
            result = (result + f" con {decimal_txt} centavos").strip()
    return result


def _spell_out_initials(match):
    token = match.group(0)
    letters = re.findall(r'[' + _LETTERS + r']', token)
    return " ".join(letter.upper() for letter in letters) + ("." if token.endswith(".") else "")


def _normalize_uppercase(match):
    return match.group(0).capitalize()


def correct_text(text, language):
    lang_code = LANGUAGES[language]["num2words"]
    text = initials_pattern.sub(_spell_out_initials, text)
    # Money first, so "u$d33.000.000" includes the currency name
    text = money_pattern.sub(lambda m: _money_to_words(m, lang_code), text)
    text = number_pattern.sub(lambda m: number_to_words(m, lang_code), text)
    text = uppercase_pattern.sub(_normalize_uppercase, text)

    if language == "Español":
        for pattern, replacement in SPANISH_REPLACEMENTS.items():
            text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)

    return text


def mark_questions(text):
    """Mark the last word of each question with a pitch rise (the same for all).
    The markers become real SSML only after edge_tts has escaped the text,
    so they are never read out loud."""
    return question_end_pattern.sub(r'[[Q]]\1[[/Q]]\2', text)


async def generate_audio(text, language, voice_label):
    if not text.strip() or not voice_label:
        return None

    voice_id = next(v_id for v_id, label in LANGUAGES[language]["voices"] if label == voice_label)
    plain_text = correct_text(text, language)

    # Question pitch rise: only Latin American Spanish voices (the Spain ones already sound fine)
    use_intonation = PATCH_OK and language == "Español" and not voice_id.startswith("es-ES")

    if use_intonation:
        try:
            text_with_markers = mark_questions(plain_text)
            await edge_tts.Communicate(text_with_markers, voice_id).save("salida.mp3")
            return "salida.mp3"
        except NoAudioReceived:
            # If the service rejects the pitch tags, retry without them
            pass

    await edge_tts.Communicate(marker_pattern.sub("", plain_text), voice_id).save("salida.mp3")
    return "salida.mp3"


def update_voices(language):
    choices = [label for _, label in LANGUAGES[language]["voices"]]
    return gr.update(choices=choices, value=choices[0])


# ------------------------------------------------------------------
# Interface
# ------------------------------------------------------------------
CSS = """
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700&display=swap');

:root {
    --radius-lg: 22px;
    --radius-md: 14px;
    --grad: linear-gradient(135deg, #7C5CFF 0%, #46C2FF 100%);
    --select-active-bg: #1E3A8A;
    --select-active-bg-hover: #1E40AF;
    --select-active-ink: #FFFFFF;
    --select-active-edge: #46C2FF;
}

* { font-family: 'Outfit', sans-serif !important; box-sizing: border-box; }

html, body {
    margin: 0 !important;
    padding: 0 !important;
    width: 100% !important;
    height: auto !important;
    min-height: 100vh !important;
    background: #0a0a16 !important;
    overflow: visible !important;
}

gradio-app {
    display: block !important;
    width: 100% !important;
}

gradio-app, .gradio-container, .main, .contain, #root {
    width: 100% !important;
    min-height: 100vh !important;
    height: auto !important;
    overflow: visible !important;
    background: radial-gradient(circle at top, #14152b 0%, #0a0a16 65%) !important;
    display: flex !important;
    align-items: center !important;
    align-items: safe center !important;
    justify-content: center !important;
    justify-content: safe center !important;
}

.main, .contain { background: transparent !important; }

.main { padding-top: 0 !important; padding-bottom: 0 !important; }

footer { display: none !important; }

#card {
    display: flex !important;
    flex-direction: column !important;
    gap: 6px !important;
    width: 92vw;
    margin: 30px 0 !important;
    max-width: 400px;
    overflow: visible !important;
    background: #16172c;
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: var(--radius-lg);
    padding: 22px 22px 24px 22px;
    box-shadow: 0 16px 40px rgba(0,0,0,0.4);
}

#card > * { margin: 0 !important; }

#card .block { border: none !important; box-shadow: none !important; background: transparent !important; }

#title {
    text-align: center;
    font-weight: 700;
    font-size: 1.3em;
    background: var(--grad);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

#subtitle {
    text-align: center;
    color: #ececff !important;
    -webkit-text-fill-color: #ececff !important;
    font-size: 1.5em;
    font-weight: 500 !important;
    margin-bottom: 6px !important;
}

#select-language .wrap,
#select-voice .wrap {
    background: var(--select-active-bg) !important;
    border-color: #3B82F6 !important;
    box-shadow: 0 4px 14px rgba(30, 58, 138, 0.32), inset 0 1px 0 rgba(255,255,255,0.16) !important;
}

#select-language .wrap:focus-within,
#select-voice .wrap:focus-within {
    background: var(--select-active-bg-hover) !important;
    border-color: var(--select-active-edge) !important;
    box-shadow: 0 0 0 3px rgba(70, 194, 255, 0.28), 0 4px 14px rgba(30, 58, 138, 0.38) !important;
}

#select-language input[role="combobox"],
#select-voice input[role="combobox"],
#select-language .icon-wrap,
#select-voice .icon-wrap {
    color: var(--select-active-ink) !important;
    -webkit-text-fill-color: var(--select-active-ink) !important;
}

#select-language input[role="combobox"],
#select-voice input[role="combobox"] {
    font-weight: 600 !important;
    letter-spacing: 0.01em;
}

li[role="option"][aria-selected="true"] {
    color: var(--select-active-ink) !important;
    -webkit-text-fill-color: var(--select-active-ink) !important;
    font-weight: 600 !important;
    background: var(--select-active-bg) !important;
    border-radius: 8px !important;
    box-shadow: inset 3px 0 0 var(--select-active-edge), inset 0 0 0 1px rgba(255,255,255,0.14) !important;
}

li[role="option"][aria-selected="true"]:hover,
li[role="option"][aria-selected="true"].active {
    background: var(--select-active-bg-hover) !important;
}

li[role="option"][aria-selected="true"] span {
    color: var(--select-active-ink) !important;
    -webkit-text-fill-color: var(--select-active-ink) !important;
}

.step {
    display: flex;
    align-items: center;
    gap: 8px;
    margin: 8px 0 2px 0 !important;
}

.step-number {
    width: 20px; height: 20px;
    border-radius: 50%;
    background: var(--grad);
    color: white;
    font-size: 0.68em;
    font-weight: 600;
    display: flex; align-items: center; justify-content: center;
    flex-shrink: 0;
}

.step-text {
    color: #9a9ab8;
    font-weight: 500;
    letter-spacing: 0.3px;
    text-transform: uppercase;
    font-size: 0.68em;
}

.gr-box, select, input, .wrap.svelte-1cl284s {
    border-radius: var(--radius-md) !important;
    border: 1px solid rgba(255,255,255,0.1) !important;
    background: #0f1022 !important;
}

input, select, .wrap.svelte-1cl284s { padding: 10px 14px !important; min-height: 44px !important; }

textarea {
    background: #0f1022 !important;
    color: #eaeaf7 !important;
    border-radius: var(--radius-md) !important;
    border: 1px solid rgba(255,255,255,0.1) !important;
    padding: 12px 14px !important;
    overflow-y: hidden !important;
}

button.primary {
    background: var(--grad) !important;
    border: none !important;
    border-radius: 999px !important;
    padding: 11px 0 !important;
    min-height: 44px !important;
    font-weight: 600 !important;
    font-size: 0.92em !important;
    box-shadow: 0 8px 22px rgba(124,92,255,0.35) !important;
    transition: transform 0.15s ease !important;
}

#card > button.primary {
    margin-top: 18px !important;
}

button.primary:hover { transform: translateY(-1px) scale(1.01); }

label span { color: #9a9ab8 !important; font-size: 0.8em !important; }

audio { border-radius: var(--radius-md) !important; }
"""

with gr.Blocks(css=CSS, theme=gr.themes.Base(primary_hue="violet", neutral_hue="slate", spacing_size="sm", radius_size="lg")) as interface:
    with gr.Column(elem_id="card"):
        gr.Markdown("Generador TTS", elem_id="title")
        gr.Markdown("Convertí cualquier texto en audio, en el idioma que quieras", elem_id="subtitle")

        gr.HTML('<div class="step"><div class="step-number">1</div><div class="step-text">Idioma</div></div>')
        language = gr.Dropdown(choices=list(LANGUAGES.keys()), value="Español", show_label=False, container=False, elem_id="select-language")

        gr.HTML('<div class="step"><div class="step-number">2</div><div class="step-text">Voz</div></div>')
        voice = gr.Dropdown(
            choices=[label for _, label in LANGUAGES["Español"]["voices"]],
            value=LANGUAGES["Español"]["voices"][0][1],
            show_label=False,
            container=False,
            elem_id="select-voice",
        )

        gr.HTML('<div class="step"><div class="step-number">3</div><div class="step-text">Texto</div></div>')
        text = gr.Textbox(
            lines=5,
            max_lines=100000,
            show_label=False,
            container=False,
            placeholder="Escribí o pegá el texto acá...",
        )

        button = gr.Button("Generar audio", variant="primary")
        output = gr.Audio(show_label=False)

        language.change(fn=update_voices, inputs=language, outputs=voice)
        button.click(
            fn=lambda: gr.update(interactive=False, value="Generando..."),
            inputs=None,
            outputs=button,
        ).then(
            fn=lambda t, i, v: asyncio.run(generate_audio(t, i, v)),
            inputs=[text, language, voice],
            outputs=output,
        ).then(
            fn=lambda: gr.update(interactive=True, value="Generar audio"),
            inputs=None,
            outputs=button,
        )

interface.launch(inbrowser=True)
