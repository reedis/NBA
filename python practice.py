import numpy
import pandas

mylist = [1,2,3]

list(range(0,11,2))

index_count = 0
for letter in 'abcde':
    print('at index {} the letter is {}'.format(index_count,letter))
    index_count += 1

#simplified
word = 'abcde'
#for letter in word:
#    print(word[index_count])
#    index_count += 1

#with enumerate
for item in enumerate(word):
    print(item)
#puts letters in form of tuples ie (0, a), (1, b), etc.

#aip function (opposite of enumerate)

list1 = [1,2,3,4,5]
list2 = ['a','b','c','d','e']

for item in zip(list1,list2):
    print(item)
    # (1, 'a'), (2, 'b'), etc.
    # if lists have unequal # of items, it will ignore extras

#flattened out for loop
mylist = [num**2 for num in range(0,11)]
print(mylist)

#2 equivalent results from these:

celsius = [0,10,20,34.5]

fahrenheit = [( (9/5)*temp + 32) for temp in celsius]

print(fahrenheit)

fahrenheit = []

for temp in celsius:
    fahrenheit.append(((9/5)*temp + 32))

print(fahrenheit)

