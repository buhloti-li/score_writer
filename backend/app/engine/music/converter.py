from pathlib import Path


class ConverterError(Exception):
    pass


def musicxml_to_lilypond(musicxml_path: str | Path, output_path: str | Path) -> Path:
    """Convert MusicXML to LilyPond format using music21."""
    try:
        import music21
    except ImportError:
        raise ConverterError("music21 is not installed. Run: pip install music21")

    input_path = Path(musicxml_path)
    out_path = Path(output_path)

    if not input_path.exists():
        raise ConverterError(f"Input file not found: {input_path}")

    score = music21.converter.parse(str(input_path))
    score.write("lilypond", fp=str(out_path))

    if not out_path.exists():
        raise ConverterError(f"Failed to generate LilyPond file: {out_path}")

    return out_path


def musicxml_to_midi(musicxml_path: str | Path, output_path: str | Path) -> Path:
    """Convert MusicXML to MIDI format using music21."""
    try:
        import music21
    except ImportError:
        raise ConverterError("music21 is not installed. Run: pip install music21")

    input_path = Path(musicxml_path)
    out_path = Path(output_path)

    if not input_path.exists():
        raise ConverterError(f"Input file not found: {input_path}")

    score = music21.converter.parse(str(input_path))
    score.write("midi", fp=str(out_path))

    if not out_path.exists():
        raise ConverterError(f"Failed to generate MIDI file: {out_path}")

    return out_path


def analyze_musicxml(musicxml_path: str | Path) -> dict:
    """Analyze MusicXML file and return basic metadata."""
    try:
        import music21
    except ImportError:
        raise ConverterError("music21 is not installed. Run: pip install music21")

    input_path = Path(musicxml_path)
    if not input_path.exists():
        raise ConverterError(f"Input file not found: {input_path}")

    score = music21.converter.parse(str(input_path))

    key = score.analyze("key")
    time_sig = None
    for ts in score.recurse().getElementsByClass("TimeSignature"):
        time_sig = str(ts)
        break

    parts = []
    for part in score.parts:
        parts.append(part.partName or "Unknown")

    measures = 0
    for part in score.parts:
        part_measures = len(part.getElementsByClass("Measure"))
        measures = max(measures, part_measures)

    return {
        "key": str(key),
        "time_signature": time_sig,
        "parts": parts,
        "num_parts": len(parts),
        "num_measures": measures,
    }
