import timeit
import os
import gc
import sys
import logging

N = 100
REPEATS = 5
FONT_NAME = 'tests/futuram.ttf'
FONT_SIZE = 96

setup = f'''
from spyke.resources import Font;
f = Font(0, "{FONT_NAME}");
'''
statement = f'''
f._load(size={FONT_SIZE});
'''

print(f'Running performance test {__file__}')
print(f'__debug__={__debug__}')

results = timeit.repeat(statement, setup, number=N, repeat=REPEATS)

print(f'\nProfiling results for font {FONT_NAME} with size {FONT_SIZE}:')
print(f'Accumulated execution time: {sum(results)}s')

averages = []
for i in range(REPEATS):
    time = results[i]
    avg = time / N

    print(f'\nProfiling pass: {i}')
    print(f'Repetitions: {N}')
    print(f'Execution time: {time}')
    print(f'Average time: {avg}')

    averages.append(avg)

print(f'\nAverage execution time: {sum(averages) / REPEATS}s')

print(f'Memory performance for single call:')
exec(setup, globals(), locals())

gc.collect()
gc.disable()

exec(statement, globals(), locals())

objects_counts = gc.get_count()
print('\nGC objects:')
for idx, count in enumerate(objects_counts):
    print(f'\nGeneration {idx}:')
    print(f'Count: {count}')

    objects = gc.get_objects(idx)
    size = sum([sys.getsizeof(obj) for obj in objects])
    print(f'Size: {size} bytes')

gc.enable()
gc.collect()

os.system('pause')
