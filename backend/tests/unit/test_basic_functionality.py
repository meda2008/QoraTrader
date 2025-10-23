"""Basic functionality tests that don't depend on numpy/pandas"""

def test_basic_math():
    """Test basic mathematical operations"""
    assert 1 + 1 == 2
    assert 2 * 3 == 6
    assert 10 / 2 == 5

def test_basic_string_operations():
    """Test basic string operations"""
    text = "Hello, QoraTrader!"
    assert text.startswith("Hello")
    assert "Qora" in text
    assert text.upper() == "HELLO, QORATRADER!"
    
def test_list_operations():
    """Test basic list operations"""
    my_list = [1, 2, 3, 4, 5]
    assert len(my_list) == 5
    assert sum(my_list) == 15
    assert 3 in my_list
    
def test_dictionary_operations():
    """Test basic dictionary operations"""
    my_dict = {"name": "QoraTrader", "type": "quantitative trading system"}
    assert "name" in my_dict
    assert my_dict["name"] == "QoraTrader"
    assert len(my_dict) == 2