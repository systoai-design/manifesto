"""Locate the local model weights the audio scripts need, without hard-coding
one machine's folders into the skill.

The voice and transcription scripts used to open `D:/kokoro/...` and
`D:/hf-cache` directly. That works on exactly one computer and fails everywhere
else with an unhandled exception from inside the library, which tells the reader
nothing about what to install or where to put it.

Resolution order, first hit wins:

  1. the environment variable named below
  2. `models/<name>/` beside the project being built (cwd)
  3. `models/<name>/` beside this skill

Nothing is downloaded here. These are large weights with their own licences and
the decision to fetch them belongs to the person running the build, so a miss
raises with the variable to set and the file that was expected.
"""
import os
import sys

SKILL_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _candidates(name, env):
    """Directories to search for a model, most specific first."""
    out = []
    if os.environ.get(env):
        out.append(os.environ[env])
    out.append(os.path.join(os.getcwd(), 'models', name))
    out.append(os.path.join(SKILL_ROOT, 'models', name))
    return out


def model_dir(name, env, needs):
    """Return the first candidate directory holding every file in `needs`.

    Raises SystemExit with an actionable message rather than letting the caller
    fail deep inside a model loader.
    """
    tried = []
    for d in _candidates(name, env):
        tried.append(d)
        if all(os.path.exists(os.path.join(d, f)) for f in needs):
            return d
    sys.exit(
        'could not find the %s model files (%s).\n'
        'Set %s to the directory holding them, or put them in ./models/%s/.\n'
        'Looked in:\n  %s'
        % (name, ', '.join(needs), env, name, '\n  '.join(tried))
    )


def kokoro_files():
    """(model, voices) for kokoro-onnx. KOKORO_HOME overrides."""
    d = model_dir('kokoro', 'KOKORO_HOME',
                  ['kokoro-v1.0.onnx', 'voices-v1.0.bin'])
    return os.path.join(d, 'kokoro-v1.0.onnx'), os.path.join(d, 'voices-v1.0.bin')


def hf_cache():
    """Where faster-whisper may download and cache weights.

    Unlike the kokoro files this one is allowed to not exist yet, because the
    library will populate it. It only needs to be somewhere with room, and on a
    machine with a small system drive that is emphatically not the default
    under the user profile.
    """
    d = (os.environ.get('HF_HOME')
         or os.environ.get('MANIFESTO_HF_CACHE')
         or os.path.join(os.getcwd(), 'models', 'hf-cache'))
    os.makedirs(d, exist_ok=True)
    os.environ.setdefault('HF_HOME', d)
    return d
