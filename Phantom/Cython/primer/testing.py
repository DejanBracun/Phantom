
import timeit

cy = timeit.timeit('''example_cython.test(50000)''',setup='import example_cython',number=1000)
py = timeit.timeit('''example_original.test(50000)''',setup='import example_original', number=1000)

print(cy, py)
print('Cython is {}x faster'.format(py/cy))