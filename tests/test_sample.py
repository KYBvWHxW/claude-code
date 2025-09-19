def test_basic():
    # 基础数学测试
    assert 1 + 1 == 2

def test_graph_import():
    from graph import build_graph
    graph = build_graph()
    assert graph is not None

def test_llm_import():
    import llm
    assert hasattr(llm, 'chat')