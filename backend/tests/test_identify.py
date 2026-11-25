import pytest
from app.services.identify import identify

def test_github(): assert identify('https://github.com/ollama/ollama') == ('github','ollama','ollama')
def test_hf_model(): assert identify('https://huggingface.co/google/gemma-2-2b') == ('model','google','gemma-2-2b')
def test_hf_dataset(): assert identify('https://huggingface.co/datasets/stanfordnlp/imdb') == ('dataset','stanfordnlp','imdb')
def test_hf_space(): assert identify('https://huggingface.co/spaces/gradio/hello_world') == ('space','gradio','hello_world')
def test_invalid():
    with pytest.raises(ValueError): identify('https://example.com/foo/bar')
