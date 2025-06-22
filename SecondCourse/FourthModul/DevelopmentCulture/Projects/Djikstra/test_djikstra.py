import pytest
from djikstra import Graph, Vertex, Edge, dijkstra

@pytest.fixture
def setup_graph():
    vertices = {name: Vertex(name) for name in "ABCDEFGH"}
    adj_list = {
        vertices["A"]: [Edge(1.8, vertices["B"]), Edge(1.5, vertices["C"]), Edge(1.4, vertices["D"])],
        vertices["B"]: [Edge(1.8, vertices["A"]), Edge(1.6, vertices["E"])],
        vertices["C"]: [Edge(1.5, vertices["A"]), Edge(1.8, vertices["E"]), Edge(2.1, vertices["F"])],
        vertices["D"]: [Edge(1.4, vertices["A"]), Edge(2.7, vertices["F"]), Edge(2.4, vertices["G"])],
        vertices["E"]: [Edge(1.6, vertices["B"]), Edge(1.8, vertices["C"]), Edge(1.4, vertices["F"]), Edge(1.6, vertices["H"])],
        vertices["F"]: [Edge(2.1, vertices["C"]), Edge(2.7, vertices["D"]), Edge(1.4, vertices["E"]), Edge(1.3, vertices["G"]), Edge(1.2, vertices["H"])],
        vertices["G"]: [Edge(2.4, vertices["D"]), Edge(1.3, vertices["F"]), Edge(1.5, vertices["H"])],
        vertices["H"]: [Edge(1.6, vertices["E"]), Edge(1.2, vertices["F"]), Edge(1.5, vertices["G"])],
    }
    return Graph(adj_list), vertices


def test_dijkstra_shortest_path(setup_graph):
    graph, vertices = setup_graph
    start, end = vertices["A"], vertices["C"]
    
    expected_path = ["A", "C"]
    expected_distance = 1.5  # Подставьте правильное значение по вашим расчетам
    
    result_distance, result_path = dijkstra(graph, start, end)
    
    assert result_distance == pytest.approx(expected_distance, 0.1)
    assert result_path == expected_path

def test_dijkstra_same_start_end(setup_graph):
    graph, vertices = setup_graph
    start = vertices["C"]
    
    result_distance, result_path = dijkstra(graph, start, start)
    
    assert result_distance == 0
    print(result_path)
    assert result_path == ["C"]

def test_dijkstra_unreachable_node(setup_graph):
    graph, vertices = setup_graph
    isolated_vertex = Vertex("X")
    
    result = dijkstra(graph, vertices["A"], isolated_vertex)
    
    assert result is None