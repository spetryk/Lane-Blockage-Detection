
class Test():
	def __init__(self, value):
		self.value=value

class SubTest():
	def __init__(self, subValue):
		self.subValue = subValue


def make_dict():
	a = Test([5])
	b = Test([6])
	a_key = SubTest(a)
	b_key = SubTest(b)

	my_dict = {a_key:a, b_key:b}
	return my_dict

my_dict = make_dict()

def change_dict(some_dict):
	for key in some_dict:
		test_obj = some_dict[key]
		test_obj.value.append(0)


def main():
	global my_dict
	print(my_dict)	

	for key in my_dict.keys():
		print(key)
		print(key.subValue)
		print(key.subValue.value)

	change_dict(my_dict)

	for key in my_dict.keys():
		print(key)
		print(key.subValue)
		print(key.subValue.value)



if __name__=='__main__':
	main()