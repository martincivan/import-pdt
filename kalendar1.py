with open("input") as f:
    pole = list(map(lambda x: int(x), f.readlines()))
    s = 0
    t = 2020
    for i in pole:
        for j in pole:
            for k in pole:
                if (i + j + k == t):
                    print(f"hotovo: {i} {j} {k} ")
