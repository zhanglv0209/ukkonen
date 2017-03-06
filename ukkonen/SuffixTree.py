from SuffixTreeNode import SuffixTreeNode

class SuffixTree:
	def __init__(self, string):
		self.root = SuffixTreeNode(start=-1, end=-1, suffixLink=None)
		self.string = string + '$'

		self.activeNode = self.root
		self.activeEdge = None
		self.activeLength = 0

		self.END = EndValue()
		self.REMAINING_SUFFIX_COUNT = RemainingSuffixCount()

		self.lastInternalNode = None

		self._construct_suffix_tree()
		self._set_suffix_index_by_dfs(self.root, labelLength=0)

	def search(self, string):
		isSubstring, nextNode = self._traverse_against_pattern(string)

		if not isSubstring:
			return []
		else:
			return self._get_leaf_indices_below(nextNode)

	def substring(self, string):
		return len(self.search(string)) != 0

	def longest_repeated_substring(self, k=2):
		_, maxSubstring = self._longest_repeated_substring_helper(self.root, k, [], '')

		return maxSubstring

	def suffix_array(self):
		indices = []
		self._get_suffix_indices_by_lexicographical_dfs(self.root, indices)
		return indices[1:]

	def _get_suffix_indices_by_lexicographical_dfs(self, node, indices):
		if node.is_leaf():
			indices.append(node.get_suffix_index())
		else:
			for child in node.get_children_lexicographically():
				self._get_suffix_indices_by_lexicographical_dfs(child, indices)

	def _longest_repeated_substring_helper(self, node, k, substringFragments, maxSubstring):
		if node.get_leaf_count() < k:
			return substringFragments, maxSubstring
		else:
			substring = ''.join(substringFragments)
			if len(substring) > len(maxSubstring):
				maxSubstring = substring

			for child in node.get_children():
				substringFragments.append(self.string[child.get_start_position():child.get_end_position()+1])
				substringFragments, maxSubstring = self._longest_repeated_substring_helper(child, k, substringFragments, maxSubstring)
				substringFragments.pop()

			return substringFragments, maxSubstring

	def _get_leaf_indices_below(self, node):
		indices = []
		self._get_leaf_indices_below_helper(node, indices)
		return list(sorted(indices))

	def _get_leaf_indices_below_helper(self, node, indices):
		if node.is_leaf():
			indices.append(node.get_suffix_index())

		else:
			for child in node.get_children():
				self._get_leaf_indices_below_helper(child, indices)

	def _traverse_against_pattern(self, string):
		i = j = 0
		nextNode = self.root
		currentEdge = ''

		while i < len(string):
			if j == len(currentEdge):
				if nextNode.has_outgoing_edge_starting_with(character=string[i]):
					nextNode = nextNode.get_child(edge=string[i])
					currentEdge = self.string[nextNode.get_start_position():nextNode.get_end_position()+1]
					j = 0
				else:
					return False, None

			if string[i] == currentEdge[j]:
				i += 1
				j += 1
			else:
				return False, None

		return True, nextNode

	def print_edges(self):
		self._print_edges_helper(self.root)

	def _print_edges_helper(self, node):
		for child in node.get_children():
			print(self.string[child.get_start_position():child.get_end_position()+1])
			self._print_edges_helper(child)

	def _construct_suffix_tree(self):
		for position, character in enumerate(self.string):
			self.END.increment()
			self.REMAINING_SUFFIX_COUNT.increment()

			while self.REMAINING_SUFFIX_COUNT > 0:
				if self.activeLength == 0:
					self._active_point_change_for_active_length_zero(position)

				activeEdgeCharacter = self.string[self.activeEdge]

				if self.activeNode.has_outgoing_edge_starting_with(activeEdgeCharacter):
					walkDownDone = self._active_point_change_for_walk_down(currNode=self.activeNode.get_child(activeEdgeCharacter))
					if walkDownDone:
						continue

					nextCharacterIndex = self.activeNode.get_character_index_on_edge(edge=activeEdgeCharacter, distance=self.activeLength+1)
					nextCharacter = self.string[nextCharacterIndex]
					
					if nextCharacter == character:
						if self.lastInternalNode:
							self.lastInternalNode.set_suffix_link_to(self.activeNode)
							self.lastInternalNode = None

						# Rule 3 applied, terminate the phase immediately
						self._active_point_change_for_extension_rule_3()
						break
					else:
						# Rule 2 applied
						self._split(activeEdgeCharacter, character, position)

				else:
					self.activeNode.set_new_child(edge=activeEdgeCharacter, start=position, end=self.END)

					if self.lastInternalNode:
						self.lastInternalNode.set_suffix_link_to(self.activeNode)
						self.lastInternalNode = None

				self.REMAINING_SUFFIX_COUNT.decrement()

				if self.activeNode.is_root() and self.activeLength > 0:
					self._active_point_change_for_extension_rule_2_case_1(position)
				elif not self.activeNode.is_root():
					self._active_point_change_for_extension_rule_2_case_2()

	def _split(self, activeEdgeCharacter, character, position):
		splitEndIndex = self.activeNode.get_character_index_on_edge(edge=activeEdgeCharacter, distance=self.activeLength)
		nextNode = self.activeNode.get_child(edge=activeEdgeCharacter)

		# Note that suffix link of an internal node is initially set to the root
		newNode = SuffixTreeNode(start=nextNode.get_start_position(), end=splitEndIndex, suffixLink=self.root)
		self.activeNode.set_child(edge=activeEdgeCharacter, node=newNode)
		
		# Insert new node
		nextNode.set_start_position(nextNode.get_start_position() + self.activeLength)
		newNode.set_new_child(edge=character, start=position, end=self.END)
		newNode.set_child(edge=self.string[nextNode.get_start_position()], node=nextNode)

		# Set suffix link of the previous internal node to new node
		if self.lastInternalNode:
			self.lastInternalNode.set_suffix_link_to(newNode)

		self.lastInternalNode = newNode

	def _get_active_point(self):
		return (self.activeNode, self.string[self.activeEdge], self.activeLength)

	def _active_point_change_for_extension_rule_3(self):
		self.activeLength += 1

	def _active_point_change_for_walk_down(self, currNode):
		if self.activeLength < currNode.get_edge_length():
			return False  # we don't need walk down

		self.activeEdge += currNode.get_edge_length()
		self.activeLength -= currNode.get_edge_length()
		self.activeNode = currNode
		return True

	def _active_point_change_for_active_length_zero(self, position):
		self.activeEdge = position

	def _active_point_change_for_extension_rule_2_case_1(self, position):
		self.activeLength -= 1
		self.activeEdge = position - self.REMAINING_SUFFIX_COUNT + 1

	def _active_point_change_for_extension_rule_2_case_2(self):
		self.activeNode = self.activeNode.follow_suffix_link()

	def _set_suffix_index_by_dfs(self, node, labelLength):
		if node.is_leaf():
			node.set_suffix_index(len(self.string) - labelLength)
			return 1

		else:
			leafCount = 0
			for child in node.get_children():
				newLabelLength = labelLength + child.get_edge_length()
				leafCount += self._set_suffix_index_by_dfs(node=child, labelLength=newLabelLength)

			node.set_leaf_count(leafCount)
			return leafCount


def singleton(class_):
	'''http://stackoverflow.com/questions/6760685/creating-a-singleton-in-python'''
	instances = {}
	def getinstance(*args, **kwargs):
		if class_ not in instances:
			instances[class_] = class_(*args, **kwargs)
		return instances[class_]
	return getinstance


class GlobalIntValue:
	def __init__(self):
		self.value = 0

	def __str__(self):
		return str(self.value)

	def __add__(self, other):
		return self.value + other

	def __radd__(self, other):
		return self.value + other

	def __sub__(self, other):
		return self.value - other

	def __rsub__(self, other):
		return other - self.value

	def __gt__(self, other):
		return self.value > other

	def decrement(self):
		self.value -= 1

	def increment(self):
		self.value += 1


@singleton
class EndValue(GlobalIntValue):
	def __init__(self):
		self.value = -1


@singleton
class RemainingSuffixCount(GlobalIntValue):
	def __iter__(self):
		for i in range(self.value):
			yield i


if __name__ == '__main__':
	# st = SuffixTree('abcabxabcd')
	# st = SuffixTree('AATCGGGTTCAATCGGGGT')
	st = SuffixTree('mississippi')
	# st.print_edges()
	# print(st.substring('issi'))
	print(st.suffix_array())