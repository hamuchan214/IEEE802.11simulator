clearAllMemoizedCaches

int8 n;
n = 20;
int8 seed;
seed = 123;

pyrun("import csma");
pyrun("n = 20")
pyrun("seed = 123")
pyrun("users = csma.create_users(n, seed)");
pyrun("csma.simulate_transmission(users, 120, 24,print_output=csma.print_mode[2])")