py.importlib.import_module('main');

py.main.create_users(20,123);
py.main.simulate_transmission(py.main.create_users(20,123),120, 24, py.csma_simulation.print_mode{2})