import pytest
from app.services.recommendations import canonical,historical,external

def test_canonical():
    assert canonical('https://huggingface.co/models/a/b?x=1')=='https://huggingface.co/a/b'

def test_history_counts():
    a={'url':'https://github.com/a/a','resource_type':'github','raw_data':{'repository':{'topics':['ai']}}}
    b={**a,'url':'https://github.com/b/b'}
    result=historical(a,[a['url'],b['url'],b['url']],{b['url']:b})
    assert len(result)==1 and result[0]['count']==2

def test_history_empty():
    assert historical({'url':'https://github.com/a/a'},[],{})==[]
